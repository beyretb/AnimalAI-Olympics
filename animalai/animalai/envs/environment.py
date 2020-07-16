from animalai.envs.arena_config import ArenaConfig
from animalai.envs.cvis import ExtractFeatures
import atexit
import glob
import uuid
from typing import NamedTuple
from typing import Optional, List
import logging
import numpy as np
import os
import subprocess
from typing import Dict, List, Optional, Any

import mlagents_envs
from mlagents_envs.side_channel.side_channel import SideChannel, IncomingMessage

from mlagents_envs.base_env import (
    BaseEnv,
    BatchedStepResult,
    AgentGroupSpec,
    AgentGroup,
    AgentId,
)
from mlagents_envs.timers import timed, hierarchical_timer
from mlagents_envs.exception import (
    UnityEnvironmentException,
    UnityCommunicationException,
    UnityActionException,
    UnityTimeOutException,
)

from mlagents_envs.communicator_objects.command_pb2 import STEP, RESET
from mlagents_envs.rpc_utils import (
    agent_group_spec_from_proto,
    batched_step_result_from_proto,
)

from mlagents_envs.communicator_objects.unity_rl_input_pb2 import UnityRLInputProto
from mlagents_envs.communicator_objects.unity_rl_output_pb2 import UnityRLOutputProto
from mlagents_envs.communicator_objects.agent_action_pb2 import AgentActionProto
from mlagents_envs.communicator_objects.unity_output_pb2 import UnityOutputProto
from mlagents_envs.communicator_objects.unity_rl_initialization_input_pb2 import (
    UnityRLInitializationInputProto,
)

from mlagents_envs.communicator_objects.unity_input_pb2 import UnityInputProto

from mlagents_envs.rpc_communicator import RpcCommunicator
from sys import platform
import signal
import struct

from mlagents_envs.side_channel.engine_configuration_channel import (
    EngineConfig,
    EngineConfigurationChannel,
)
from mlagents_envs.side_channel.side_channel import (
    SideChannel,
    IncomingMessage,
    OutgoingMessage,
)
from mlagents_envs.side_channel.raw_bytes_channel import RawBytesChannel

logger = logging.getLogger("mlagents_envs")

class UnityEnvironment(BaseEnv):
    SCALAR_ACTION_TYPES = (int, np.int32, np.int64, float, np.float32, np.float64)
    SINGLE_BRAIN_ACTION_TYPES = SCALAR_ACTION_TYPES + (list, np.ndarray)

    # Communication protocol version.
    # When connecting to C#, this must match Academy.k_ApiVersion
    # Currently we require strict equality between the communication protocol
    # on each side, although we may allow some flexibility in the future.
    # This should be incremented whenever a change is made to the communication protocol.
    API_VERSION = "0.15.0"

    # Default port that the editor listens on. If an environment executable
    # isn't specified, this port will be used.
    DEFAULT_EDITOR_PORT = 5004

    # Command line argument used to pass the port to the executable environment.
    PORT_COMMAND_LINE_ARG = "--mlagents-port"

    def __init__(
        self,
        file_name: Optional[str] = None,
        worker_id: int = 0,
        base_port: int = 5005,
        seed: int = 0,
        docker_training: bool = False,
        no_graphics: bool = False,
        timeout_wait: int = 60,
        args: Optional[List[str]] = None,
        side_channels: Optional[List[SideChannel]] = None,
        alter_obs = True
    ):
        """
        Starts a new unity environment and establishes a connection with the environment.
        Notice: Currently communication between Unity and Python takes place over an open socket without authentication.
        Ensure that the network where training takes place is secure.

        :string file_name: Name of Unity environment binary.
        :int base_port: Baseline port number to connect to Unity environment over. worker_id increments over this.
        :int worker_id: Number to add to communication port (5005) [0]. Used for asynchronous agent scenarios.
        :bool docker_training: Informs this class whether the process is being run within a container.
        :bool no_graphics: Whether to run the Unity simulator in no-graphics mode
        :int timeout_wait: Time (in seconds) to wait for connection from environment.
        :list args: Addition Unity command line arguments
        :list side_channels: Additional side channel for no-rl communication with Unity
        """
        print("USING LOCAL LIBRARY")
        args = args or []
        atexit.register(self._close)
        self.port = base_port + worker_id
        self._buffer_size = 12000
        # If true, this means the environment was successfully loaded
        self._loaded = False
        # The process that is started. If None, no process was started
        self.proc1 = None
        self.timeout_wait: int = timeout_wait
        self.communicator = self.get_communicator(worker_id, base_port, timeout_wait)
        self.worker_id = worker_id
        self.side_channels: Dict[uuid.UUID, SideChannel] = {}
        if side_channels is not None:
            for _sc in side_channels:
                if _sc.channel_id in self.side_channels:
                    raise UnityEnvironmentException(
                        "There cannot be two side channels with the same channel id {0}.".format(
                            _sc.channel_id
                        )
                    )
                self.side_channels[_sc.channel_id] = _sc

        # If the environment name is None, a new environment will not be launched
        # and the communicator will directly try to connect to an existing unity environment.
        # If the worker-id is not 0 and the environment name is None, an error is thrown
        if file_name is None and worker_id != 0:
            raise UnityEnvironmentException(
                "If the environment name is None, "
                "the worker-id must be 0 in order to connect with the Editor."
            )
        if file_name is not None:
            self.executable_launcher(file_name, docker_training, no_graphics, args)
        else:
            logger.info(
                f"Listening on port {self.port}. "
                f"Start training by pressing the Play button in the Unity Editor."
            )
        self._loaded = True

        rl_init_parameters_in = UnityRLInitializationInputProto(
            seed=seed,
            communication_version=self.API_VERSION,
            package_version=mlagents_envs.__version__,
        )
        try:
            aca_output = self.send_academy_parameters(rl_init_parameters_in)
            aca_params = aca_output.rl_initialization_output
            self.aca_output = aca_output
        except UnityTimeOutException:
            self._close()
            raise

        unity_communicator_version = aca_params.communication_version
        if unity_communicator_version != UnityEnvironment.API_VERSION:
            self._close()
            raise UnityEnvironmentException(
                f"The communication API version is not compatible between Unity and python. "
                f"Python API: {UnityEnvironment.API_VERSION}, Unity API: {unity_communicator_version}.\n "
                f"Please go to https://github.com/Unity-Technologies/ml-agents/releases/tag/latest_release "
                f"to download the latest version of ML-Agents."
            )
        else:
            logger.info(
                f"Connected to Unity environment with package version {aca_params.package_version} "
                f"and communication version {aca_params.communication_version}"
            )
        self._env_state: Dict[str, BatchedStepResult] = {}
        self._env_specs: Dict[str, AgentGroupSpec] = {}
        self._env_actions: Dict[str, np.ndarray] = {}
        self._is_first_message = True
        self.alter_obs = alter_obs
        self._update_group_specs(aca_output)
        self.ef = ExtractFeatures()

    @staticmethod
    def get_communicator(worker_id, base_port, timeout_wait):
        return RpcCommunicator(worker_id, base_port, timeout_wait)

    @staticmethod
    def validate_environment_path(env_path: str) -> Optional[str]:
        # Strip out executable extensions if passed
        env_path = (
            env_path.strip()
            .replace(".app", "")
            .replace(".exe", "")
            .replace(".x86_64", "")
            .replace(".x86", "")
        )
        true_filename = os.path.basename(os.path.normpath(env_path))
        logger.debug("The true file name is {}".format(true_filename))

        if not (glob.glob(env_path) or glob.glob(env_path + ".*")):
            return None

        cwd = os.getcwd()
        launch_string = None
        true_filename = os.path.basename(os.path.normpath(env_path))
        if platform == "linux" or platform == "linux2":
            candidates = glob.glob(os.path.join(cwd, env_path) + ".x86_64")
            if len(candidates) == 0:
                candidates = glob.glob(os.path.join(cwd, env_path) + ".x86")
            if len(candidates) == 0:
                candidates = glob.glob(env_path + ".x86_64")
            if len(candidates) == 0:
                candidates = glob.glob(env_path + ".x86")
            if len(candidates) > 0:
                launch_string = candidates[0]

        elif platform == "darwin":
            candidates = glob.glob(
                os.path.join(cwd, env_path + ".app", "Contents", "MacOS", true_filename)
            )
            if len(candidates) == 0:
                candidates = glob.glob(
                    os.path.join(env_path + ".app", "Contents", "MacOS", true_filename)
                )
            if len(candidates) == 0:
                candidates = glob.glob(
                    os.path.join(cwd, env_path + ".app", "Contents", "MacOS", "*")
                )
            if len(candidates) == 0:
                candidates = glob.glob(
                    os.path.join(env_path + ".app", "Contents", "MacOS", "*")
                )
            if len(candidates) > 0:
                launch_string = candidates[0]
        elif platform == "win32":
            candidates = glob.glob(os.path.join(cwd, env_path + ".exe"))
            if len(candidates) == 0:
                candidates = glob.glob(env_path + ".exe")
            if len(candidates) > 0:
                launch_string = candidates[0]
        return launch_string

    def executable_launcher(self, file_name, docker_training, no_graphics, args):
        launch_string = self.validate_environment_path(file_name)
        if launch_string is None:
            self._close()
            raise UnityEnvironmentException(
                f"Couldn't launch the {file_name} environment. Provided filename does not match any environments."
            )
        else:
            logger.debug("This is the launch string {}".format(launch_string))
            # Launch Unity environment
            if not docker_training:
                subprocess_args = [launch_string]
                if no_graphics:
                    subprocess_args += ["-nographics", "-batchmode"]
                subprocess_args += [
                    UnityEnvironment.PORT_COMMAND_LINE_ARG,
                    str(self.port),
                ]
                subprocess_args += args
                try:
                    self.proc1 = subprocess.Popen(
                        subprocess_args,
                        # start_new_session=True means that signals to the parent python process
                        # (e.g. SIGINT from keyboard interrupt) will not be sent to the new process on POSIX platforms.
                        # This is generally good since we want the environment to have a chance to shutdown,
                        # but may be undesirable in come cases; if so, we'll add a command-line toggle.
                        # Note that on Windows, the CTRL_C signal will still be sent.
                        start_new_session=True,
                    )
                except PermissionError as perm:
                    # This is likely due to missing read or execute permissions on file.
                    raise UnityEnvironmentException(
                        f"Error when trying to launch environment - make sure "
                        f"permissions are set correctly. For example "
                        f'"chmod -R 755 {launch_string}"'
                    ) from perm

            else:
                # Comments for future maintenance:
                #     xvfb-run is a wrapper around Xvfb, a virtual xserver where all
                #     rendering is done to virtual memory. It automatically creates a
                #     new virtual server automatically picking a server number `auto-servernum`.
                #     The server is passed the arguments using `server-args`, we are telling
                #     Xvfb to create Screen number 0 with width 640, height 480 and depth 24 bits.
                #     Note that 640 X 480 are the default width and height. The main reason for
                #     us to add this is because we'd like to change the depth from the default
                #     of 8 bits to 24.
                #     Unfortunately, this means that we will need to pass the arguments through
                #     a shell which is why we set `shell=True`. Now, this adds its own
                #     complications. E.g SIGINT can bounce off the shell and not get propagated
                #     to the child processes. This is why we add `exec`, so that the shell gets
                #     launched, the arguments are passed to `xvfb-run`. `exec` replaces the shell
                #     we created with `xvfb`.
                #
                docker_ls = (
                    f"exec xvfb-run --auto-servernum --server-args='-screen 0 640x480x24'"
                    f" {launch_string} {UnityEnvironment.PORT_COMMAND_LINE_ARG} {self.port}"
                )

                self.proc1 = subprocess.Popen(
                    docker_ls,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                )
    def _alter_observations(self, rl_output, agent_name='AnimalAI?team=0',mode='octx'):
        # agent_name ='AnimalAI?team=0'
        # Reformat observations for each agent
        agent_infos = rl_output.agentInfos
        for agent in range(0, len(agent_infos[
            agent_name].value)):
            agent_obs = agent_infos[
                agent_name].value[agent].observations
            # 1) Change vector observations to desired size
            vector_obs = agent_obs[1]
            vector_obs.shape.remove(2)
            if mode == 'gtg':
                vector_obs.shape.extend([6])
            elif mode == 'octx':
                vector_obs.shape.extend([10])
            else:
                raise Exception(f"Mode {mode} not supported")
            # 2) Extract image in bytes and then remove visual observations
            img = agent_obs[0].compressed_data
            self.img = img
            del agent_obs[0]

            #3) Run CV and retrieve bounding boxes as a list
            res = self.ef.run(img)
            vector_obs.float_data.data.extend(res)

    def _update_group_specs(self, output: UnityOutputProto) -> None:
        init_output = output.rl_initialization_output
        rl_output = output.rl_output
        if self.alter_obs:
            self._alter_observations(rl_output)
        for brain_param in init_output.brain_parameters:
            # Each BrainParameter in the rl_initialization_output should have at least one AgentInfo
            # Get that agent, because we need some of its observations.
            agent_infos = output.rl_output.agentInfos[brain_param.brain_name]
            if agent_infos.value:
                agent = agent_infos.value[0]
                new_spec = agent_group_spec_from_proto(brain_param, agent)
                self.new_spec = new_spec
                self._env_specs[brain_param.brain_name] = new_spec
                logger.info(f"Connected new brain:\n{brain_param.brain_name}")

    def _update_state(self, output: UnityRLOutputProto) -> None:
        """
        Collects experience information from all external brains in environment at current step.
        """
        for brain_name in self._env_specs.keys():
            if brain_name in output.agentInfos:
                agent_info_list = output.agentInfos[brain_name].value
                self._env_state[brain_name] = batched_step_result_from_proto(
                    agent_info_list, self._env_specs[brain_name]
                )
            else:
                self._env_state[brain_name] = BatchedStepResult.empty(
                    self._env_specs[brain_name]
                )
        self._parse_side_channel_message(self.side_channels, output.side_channel)

    def reset(self) -> None:
        if self._loaded:
            outputs = self.communicator.exchange(self._generate_reset_input())
            if outputs is None:
                raise UnityCommunicationException("Communicator has stopped.")
            self._update_group_specs(outputs)
            rl_output = outputs.rl_output
            self._update_state(rl_output)
            self._is_first_message = False
            self._env_actions.clear()
        else:
            raise UnityEnvironmentException("No Unity environment is loaded.")


    @timed
    def step(self) -> None:
        if self._is_first_message:
            return self.reset()
        if not self._loaded:
            raise UnityEnvironmentException("No Unity environment is loaded.")
        # fill the blanks for missing actions
        for group_name in self._env_specs:
            if group_name not in self._env_actions:
                n_agents = 0
                if group_name in self._env_state:
                    n_agents = self._env_state[group_name].n_agents()
                self._env_actions[group_name] = self._env_specs[
                    group_name
                ].create_empty_action(n_agents)
        step_input = self._generate_step_input(self._env_actions)
        with hierarchical_timer("communicator.exchange"):
            outputs = self.communicator.exchange(step_input)
        if outputs is None:
            raise UnityCommunicationException("Communicator has stopped.")

        self._update_group_specs(outputs)
        rl_output = outputs.rl_output
        self._update_state(rl_output)
        self._env_actions.clear()

    def get_agent_groups(self) -> List[AgentGroup]:
        return list(self._env_specs.keys())

    def _assert_group_exists(self, agent_group: str) -> None:
        if agent_group not in self._env_specs:
            raise UnityActionException(
                "The group {0} does not correspond to an existing agent group "
                "in the environment".format(agent_group)
            )

    def set_actions(self, agent_group: AgentGroup, action: np.ndarray) -> None:
        self._assert_group_exists(agent_group)
        if agent_group not in self._env_state:
            return
        spec = self._env_specs[agent_group]
        expected_type = np.float32 if spec.is_action_continuous() else np.int32
        expected_shape = (self._env_state[agent_group].n_agents(), spec.action_size)
        if action.shape != expected_shape:
            raise UnityActionException(
                "The group {0} needs an input of dimension {1} but received input of dimension {2}".format(
                    agent_group, expected_shape, action.shape
                )
            )
        if action.dtype != expected_type:
            action = action.astype(expected_type)
        self._env_actions[agent_group] = action

    def set_action_for_agent(
        self, agent_group: AgentGroup, agent_id: AgentId, action: np.ndarray
    ) -> None:
        self._assert_group_exists(agent_group)
        if agent_group not in self._env_state:
            return
        spec = self._env_specs[agent_group]
        expected_shape = (spec.action_size,)
        if action.shape != expected_shape:
            raise UnityActionException(
                "The Agent {0} in group {1} needs an input of dimension {2} but received input of dimension {3}".format(
                    agent_id, agent_group, expected_shape, action.shape
                )
            )
        expected_type = np.float32 if spec.is_action_continuous() else np.int32
        if action.dtype != expected_type:
            action = action.astype(expected_type)

        if agent_group not in self._env_actions:
            self._env_actions[agent_group] = spec.create_empty_action(
                self._env_state[agent_group].n_agents()
            )
        try:
            index = np.where(self._env_state[agent_group].agent_id == agent_id)[0][0]
        except IndexError as ie:
            raise IndexError(
                "agent_id {} is did not request a decision at the previous step".format(
                    agent_id
                )
            ) from ie
        self._env_actions[agent_group][index] = action

    def get_step_result(self, agent_group: AgentGroup) -> BatchedStepResult:
        self._assert_group_exists(agent_group)
        return self._env_state[agent_group]

    def get_agent_group_spec(self, agent_group: AgentGroup) -> AgentGroupSpec:
        self._assert_group_exists(agent_group)
        return self._env_specs[agent_group]

    def close(self):
        """
        Sends a shutdown signal to the unity environment, and closes the socket connection.
        """
        if self._loaded:
            self._close()
        else:
            raise UnityEnvironmentException("No Unity environment is loaded.")

    def _close(self):
        self._loaded = False
        self.communicator.close()
        if self.proc1 is not None:
            # Wait a bit for the process to shutdown, but kill it if it takes too long
            try:
                self.proc1.wait(timeout=self.timeout_wait)
                signal_name = self.returncode_to_signal_name(self.proc1.returncode)
                signal_name = f" ({signal_name})" if signal_name else ""
                return_info = f"Environment shut down with return code {self.proc1.returncode}{signal_name}."
                logger.info(return_info)
            except subprocess.TimeoutExpired:
                logger.info("Environment timed out shutting down. Killing...")
                self.proc1.kill()
            # Set to None so we don't try to close multiple times.
            self.proc1 = None

    @classmethod
    def _flatten(cls, arr: Any) -> List[float]:
        """
        Converts arrays to list.
        :param arr: numpy vector.
        :return: flattened list.
        """
        if isinstance(arr, cls.SCALAR_ACTION_TYPES):
            arr = [float(arr)]
        if isinstance(arr, np.ndarray):
            arr = arr.tolist()
        if len(arr) == 0:
            return arr
        if isinstance(arr[0], np.ndarray):
            # pylint: disable=no-member
            arr = [item for sublist in arr for item in sublist.tolist()]
        if isinstance(arr[0], list):
            # pylint: disable=not-an-iterable
            arr = [item for sublist in arr for item in sublist]
        arr = [float(x) for x in arr]
        return arr

    @staticmethod
    def _parse_side_channel_message(
        side_channels: Dict[uuid.UUID, SideChannel], data: bytes
    ) -> None:
        offset = 0
        while offset < len(data):
            try:
                channel_id = uuid.UUID(bytes_le=bytes(data[offset : offset + 16]))
                offset += 16
                message_len, = struct.unpack_from("<i", data, offset)
                offset = offset + 4
                message_data = data[offset : offset + message_len]
                offset = offset + message_len
            except Exception:
                raise UnityEnvironmentException(
                    "There was a problem reading a message in a SideChannel. "
                    "Please make sure the version of MLAgents in Unity is "
                    "compatible with the Python version."
                )
            if len(message_data) != message_len:
                raise UnityEnvironmentException(
                    "The message received by the side channel {0} was "
                    "unexpectedly short. Make sure your Unity Environment "
                    "sending side channel data properly.".format(channel_id)
                )
            if channel_id in side_channels:
                incoming_message = IncomingMessage(message_data)
                side_channels[channel_id].on_message_received(incoming_message)
            else:
                logger.warning(
                    "Unknown side channel data received. Channel type "
                    ": {0}.".format(channel_id)
                )

    @staticmethod
    def _generate_side_channel_data(
        side_channels: Dict[uuid.UUID, SideChannel]
    ) -> bytearray:
        result = bytearray()
        for channel_id, channel in side_channels.items():
            for message in channel.message_queue:
                result += channel_id.bytes_le
                result += struct.pack("<i", len(message))
                result += message
            channel.message_queue = []
        return result

    @timed
    def _generate_step_input(
        self, vector_action: Dict[str, np.ndarray]
    ) -> UnityInputProto:
        rl_in = UnityRLInputProto()
        for b in vector_action:
            n_agents = self._env_state[b].n_agents()
            if n_agents == 0:
                continue
            for i in range(n_agents):
                action = AgentActionProto(vector_actions=vector_action[b][i])
                rl_in.agent_actions[b].value.extend([action])
                rl_in.command = STEP
        rl_in.side_channel = bytes(self._generate_side_channel_data(self.side_channels))
        return self.wrap_unity_input(rl_in)

    def _generate_reset_input(self) -> UnityInputProto:
        rl_in = UnityRLInputProto()
        rl_in.command = RESET
        rl_in.side_channel = bytes(self._generate_side_channel_data(self.side_channels))
        return self.wrap_unity_input(rl_in)

    def send_academy_parameters(
        self, init_parameters: UnityRLInitializationInputProto
    ) -> UnityOutputProto:
        inputs = UnityInputProto()
        inputs.rl_initialization_input.CopyFrom(init_parameters)
        return self.communicator.initialize(inputs)

    @staticmethod
    def wrap_unity_input(rl_input: UnityRLInputProto) -> UnityInputProto:
        result = UnityInputProto()
        result.rl_input.CopyFrom(rl_input)
        return result

    @staticmethod
    def returncode_to_signal_name(returncode: int) -> Optional[str]:
        """
        Try to convert return codes into their corresponding signal name.
        E.g. returncode_to_signal_name(-2) -> "SIGINT"
        """
        try:
            # A negative value -N indicates that the child was terminated by signal N (POSIX only).
            s = signal.Signals(-returncode)  # pylint: disable=no-member
            return s.name
        except Exception:
            # Should generally be a ValueError, but catch everything just in case.
            return None

class PlayTrain(NamedTuple):
    play: int
    train: int


class AnimalAIEnvironment(UnityEnvironment):
    # Default values for configuration parameters of the environment, can be changed if needed
    # Increasing the timescale value for training might speed up the process on powefull machines
    # but take care as the higher the timescale the more likely the physics might break
    WINDOW_WIDTH = PlayTrain(play=1200, train=1200)
    WINDOW_HEIGHT = PlayTrain(play=800, train=800)
    QUALITY_LEVEL = PlayTrain(play=5, train=100)
    TIMESCALE = PlayTrain(play=1, train=300)
    TARGET_FRAME_RATE = PlayTrain(play=60, train=-1)
    ARENA_CONFIG_SC_UUID = "9c36c837-cad5-498a-b675-bc19c9370072"
    ARENA_OBJ_CONFIG_SC_UUID = "9c36c837-cad5-498a-b675-bc19c9370071"

    def __init__(
        self,
        file_name: Optional[str] = None,
        worker_id: int = 0,
        base_port: int = 5004,
        seed: int = 0,
        # docker_training: bool = False, # Will be removed in final version
        n_arenas: int = 1,
        play: bool = False,
        arenas_configurations: ArenaConfig = None,
        inference: bool = False,
        resolution: int = None,
        grayscale: bool = False,
        side_channels: Optional[List[SideChannel]] = None,
        alter_obs: bool = False
    ):

        args = self.executable_args(n_arenas, play, resolution, grayscale)
        self.play = play
        self.inference = inference
        self.timeout = 10 if play else 60
        self.side_channels = side_channels if side_channels else []
        self.arenas_parameters_side_channel = None
        self.arenas_obj_config_side_channel = ArenaObjConfigSideChannel()

        self.configure_side_channels(self.side_channels)
        self.side_channels += [self.arenas_obj_config_side_channel]
        super().__init__(
            file_name=file_name,
            worker_id=worker_id,
            base_port=base_port,
            seed=seed,
            no_graphics=False,
            timeout_wait= self.timeout,
            args=args,
            side_channels=self.side_channels,
            alter_obs=alter_obs
        )
        self.reset(arenas_configurations)
        self.arenas_obj_config_side_channel.send_string("Fetch Data")

    def configure_side_channels(self, side_channels: List[SideChannel]) -> None:

        contains_engine_config_sc = any(
            [isinstance(sc, EngineConfigurationChannel) for sc in side_channels]
        )
        if not contains_engine_config_sc:
            self.side_channels.append(self.create_engine_config_side_channel())
        contains_arena_config_sc = any(
            [sc.channel_id == self.ARENA_CONFIG_SC_UUID for sc in side_channels]
        )
        if not contains_arena_config_sc:
            self.arenas_parameters_side_channel = RawBytesChannel(
                channel_id=uuid.UUID(self.ARENA_CONFIG_SC_UUID)
            )
            self.side_channels.append(self.arenas_parameters_side_channel)

    def create_engine_config_side_channel(self) -> EngineConfigurationChannel:

        if self.play or self.inference:
            engine_configuration = EngineConfig(
                width=self.WINDOW_WIDTH.play,
                height=self.WINDOW_HEIGHT.play,
                quality_level=self.QUALITY_LEVEL.play,
                time_scale=self.TIMESCALE.play,
                target_frame_rate=self.TARGET_FRAME_RATE.play,
            )
        else:
            engine_configuration = EngineConfig(
                width=self.WINDOW_WIDTH.train,
                height=self.WINDOW_HEIGHT.train,
                quality_level=self.QUALITY_LEVEL.train,
                time_scale=self.TIMESCALE.train,
                target_frame_rate=self.TARGET_FRAME_RATE.train,
            )
        engine_configuration_channel = EngineConfigurationChannel()
        engine_configuration_channel.set_configuration(engine_configuration)
        return engine_configuration_channel

    def reset(self, arenas_configurations: ArenaConfig = None) -> None:
        if arenas_configurations:
            arenas_configurations_proto = arenas_configurations.to_proto()
            arenas_configurations_proto_string = arenas_configurations_proto.SerializeToString(
                deterministic=True
            )
            self.arenas_parameters_side_channel.send_raw_data(
                bytearray(arenas_configurations_proto_string)
            )
        try:
            super().reset()
        except UnityTimeOutException as timeoutException:
            if self.play:
                pass
            else:
                raise timeoutException


    def close(self):
        if self.play:
            self.communicator.close()
            if self.proc1:
                self.proc1.kill()
        else:
            super().close()

    @staticmethod
    def executable_args(
        n_arenas: int = 1,
        play: bool = False,
        resolution: int = 84,
        grayscale: bool = False,
    ) -> List[str]:
        args = ["--playerMode"]
        if play:
            args.append("1")
        else:
            args.append("0")
        args.append("--numberOfArenas")
        args.append(str(n_arenas))
        if resolution:
            args.append("--resolution")
            args.append(str(resolution))
        if grayscale:
            args.append("--grayscale")
        return args

# Create the StringLogChannel class
class ArenaObjConfigSideChannel(SideChannel):

    def __init__(self) -> None:
        super().__init__(uuid.UUID("9c36c837-cad5-498a-b675-bc19c9370071"))
        self.last_msg = None
        self.arenas_config = None

    @staticmethod
    def obj_parser(obj):
        obj = obj.split('|')
        obj = {
            'name':obj[0],
            'position': eval(obj[1]),
            'rotation':eval(obj[2]),
            'size':eval(obj[3]),
            # 'color':eval(obj[4])
        }
        return obj

    def parse_msg(self, msg):
        obj_types = ['Agent', 'Wall', 'Ramp', 'WallTransparent', 'CylinderTunnel','CylinderTunnelTransparent',
                    'Cardbox1','Cardbox2','UObject','LObject','LObject2','GoodGoal',
                    'GoodGoalBounce','BadGoal','BadGoalBounce','GoodGoalMulti','GoodGoalMultiBounce',
                    'DeathZone','HotZone']
        arenas = [i for i in msg.split('\n') if 'ArenaTrain(Clone)' in i]
        blacklist = ["Walls", "WallOut", "AgentCamMid"]
        filtered_arenas = [
        [
            j.replace('(Clone)', ''
            ) for j in i.split('\t'
            ) if any(k in j for k in obj_types
            ) & all(l not in j for l in blacklist)] for i in arenas
            ]

        res = {
            c: [self.obj_parser(obj) for obj in arena] for c, arena in enumerate(filtered_arenas)
        }
        return res

    def on_message_received(self, msg: IncomingMessage) -> None:
        """
        Note: We must implement this method of the SideChannel interface to
        receive messages from Unity
        """
        # We simply read a string from the message and print it.
        self.last_msg = msg.read_string()
        self.arenas_config = self.parse_msg(self.last_msg)

    def send_string(self, data: str) -> None:
        # Add the string to an OutgoingMessage
        msg = OutgoingMessage()
        msg.write_string(data)
        # We call this method to queue the data we want to send
        super().queue_message_to_send(msg)
