from typing import List, Callable, Optional, Dict
import cloudpickle

from multiprocessing import Process, Pipe
from mlagents_envs.exception import UnityCommunicationException, UnityTimeOutException
from multiprocessing import Queue
from multiprocessing.connection import Connection
from mlagents_envs.base_env import BaseEnv
from mlagents.trainers.env_manager import EnvironmentStep, AllStepResult
from mlagents_envs.timers import reset_timers, get_timer_root
from mlagents_envs.side_channel.float_properties_channel import FloatPropertiesChannel
from mlagents_envs.side_channel.engine_configuration_channel import (
    EngineConfigurationChannel,
    EngineConfig,
)
from mlagents_envs.side_channel.side_channel import SideChannel
from mlagents.trainers.brain_conversion_utils import group_spec_to_brain_parameters
from mlagents.trainers.subprocess_env_manager import (
    logger,
    SubprocessEnvManager,
    EnvironmentCommand,
    EnvironmentResponse,
    StepResponse,
    UnityEnvWorker,
)
from animalai.envs.environment import AnimalAIEnvironment


def worker_aai(
    parent_conn: Connection,
    step_queue: Queue,
    pickled_env_factory: str,
    worker_id: int,
    engine_configuration: EngineConfig,
) -> None:
    env_factory: Callable[
        [int, List[SideChannel]], AnimalAIEnvironment
    ] = cloudpickle.loads(pickled_env_factory)
    shared_float_properties = FloatPropertiesChannel()
    engine_configuration_channel = EngineConfigurationChannel()
    engine_configuration_channel.set_configuration(engine_configuration)
    env: AnimalAIEnvironment = env_factory(
        worker_id, [shared_float_properties, engine_configuration_channel]
    )

    def _send_response(cmd_name, payload):
        parent_conn.send(EnvironmentResponse(cmd_name, worker_id, payload))

    def _generate_all_results() -> AllStepResult:
        all_step_result: AllStepResult = {}
        for brain_name in env.get_agent_groups():
            all_step_result[brain_name] = env.get_step_result(brain_name)
        return all_step_result

    def external_brains():
        result = {}
        for brain_name in env.get_agent_groups():
            result[brain_name] = group_spec_to_brain_parameters(
                brain_name, env.get_agent_group_spec(brain_name)
            )
        return result

    try:
        while True:
            cmd: EnvironmentCommand = parent_conn.recv()
            if cmd.name == "step":
                all_action_info = cmd.payload
                for brain_name, action_info in all_action_info.items():
                    if len(action_info.action) != 0:
                        env.set_actions(brain_name, action_info.action)
                env.step()
                all_step_result = _generate_all_results()
                # The timers in this process are independent from all the processes and the "main" process
                # So after we send back the root timer, we can safely clear them.
                # Note that we could randomly return timers a fraction of the time if we wanted to reduce
                # the data transferred.
                # TODO get gauges from the workers and merge them in the main process too.
                step_response = StepResponse(all_step_result, get_timer_root())
                step_queue.put(EnvironmentResponse("step", worker_id, step_response))
                reset_timers()
            elif cmd.name == "external_brains":
                _send_response("external_brains", external_brains())
            elif cmd.name == "get_properties":
                reset_params = shared_float_properties.get_property_dict_copy()
                _send_response("get_properties", reset_params)
            elif cmd.name == "reset":
                env.reset(arenas_configurations=cmd.payload)
                all_step_result = _generate_all_results()
                _send_response("reset", all_step_result)
            elif cmd.name == "close":
                break
    except (KeyboardInterrupt, UnityCommunicationException, UnityTimeOutException):
        logger.info(f"UnityEnvironment worker {worker_id}: environment stopping.")
        step_queue.put(EnvironmentResponse("env_close", worker_id, None))
    finally:
        # If this worker has put an item in the step queue that hasn't been processed by the EnvManager, the process
        # will hang until the item is processed. We avoid this behavior by using Queue.cancel_join_thread()
        # See https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Queue.cancel_join_thread for
        # more info.
        logger.debug(f"UnityEnvironment worker {worker_id} closing.")
        step_queue.cancel_join_thread()
        step_queue.close()
        env.close()
        logger.debug(f"UnityEnvironment worker {worker_id} done.")


class SubprocessEnvManagerAAI(SubprocessEnvManager):
    @staticmethod
    def create_worker(
        worker_id: int,
        step_queue: Queue,
        env_factory: Callable[[int, List[SideChannel]], BaseEnv],
        engine_configuration: EngineConfig,
    ) -> UnityEnvWorker:
        parent_conn, child_conn = Pipe()

        # Need to use cloudpickle for the env factory function since function objects aren't picklable
        # on Windows as of Python 3.6.
        pickled_env_factory = cloudpickle.dumps(env_factory)
        child_process = Process(
            target=worker_aai,
            args=(
                child_conn,
                step_queue,
                pickled_env_factory,
                worker_id,
                engine_configuration,
            ),
        )
        child_process.start()
        return UnityEnvWorker(child_process, worker_id, parent_conn)

    def _reset_env(self, config: Optional[Dict] = None) -> List[EnvironmentStep]:
        while any(ew.waiting for ew in self.env_workers):
            if not self.step_queue.empty():
                step = self.step_queue.get_nowait()
                self.env_workers[step.worker_id].waiting = False
        # First enqueue reset commands for all workers so that they reset in parallel
        for ew in self.env_workers:
            ew.send("reset", config)
        # Next (synchronously) collect the reset observations from each worker in sequence
        for ew in self.env_workers:
            ew.previous_step = EnvironmentStep(ew.recv().payload, ew.worker_id, {})
        return list(map(lambda ew: ew.previous_step, self.env_workers))
