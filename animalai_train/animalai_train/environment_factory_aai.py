import numpy as np
from typing import Callable, Optional, List

from mlagents_envs.base_env import BaseEnv
from mlagents_envs.side_channel.side_channel import SideChannel
from mlagents_envs.exception import UnityEnvironmentException

# from mlagents.trainers.learn import prepare_for_docker_run

from animalai.envs.arena_config import ArenaConfig
from animalai.envs.environment import AnimalAIEnvironment


def create_environment_factory_aai(
    env_path: Optional[str],
    # docker_target_name: Optional[str],
    seed: Optional[int],
    start_port: int,
    n_arenas_per_env: int,
    arenas_configurations: ArenaConfig,
    resolution: Optional[int],
) -> Callable[[int, List[SideChannel]], BaseEnv]:
    if env_path is not None:
        launch_string = AnimalAIEnvironment.validate_environment_path(env_path)
        if launch_string is None:
            raise UnityEnvironmentException(
                f"Couldn't launch the {env_path} environment. Provided filename does not match any environments."
            )
    # docker_training = docker_target_name is not None
    # if docker_training and env_path is not None:
    #     #     Comments for future maintenance:
    #     #         Some OS/VM instances (e.g. COS GCP Image) mount filesystems
    #     #         with COS flag which prevents execution of the Unity scene,
    #     #         to get around this, we will copy the executable into the
    #     #         container.
    #     # Navigate in docker path and find env_path and copy it.
    #     env_path = prepare_for_docker_run(docker_target_name, env_path)
    seed_count = 10000
    seed_pool = [np.random.randint(0, seed_count) for _ in range(seed_count)]

    def create_unity_environment(
        worker_id: int, side_channels: List[SideChannel]
    ) -> AnimalAIEnvironment:
        env_seed = seed
        if not env_seed:
            env_seed = seed_pool[worker_id % len(seed_pool)]
        return AnimalAIEnvironment(
            file_name=env_path,
            worker_id=worker_id,
            base_port=start_port,
            seed=env_seed,
            # docker_training=docker_training,
            n_arenas=n_arenas_per_env,
            arenas_configurations=arenas_configurations,
            resolution=resolution,
            side_channels=side_channels,
        )

    return create_unity_environment
