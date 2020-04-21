from animalai.envs.gym.environment import AnimalAIGym
from animalai.envs.arena_config import ArenaConfig
from baselines.common.vec_env.subproc_vec_env import SubprocVecEnv
from baselines.bench import Monitor
from baselines import logger
import baselines.ppo2.ppo2 as ppo2

import os

try:
    from mpi4py import MPI
except ImportError:
    MPI = None


def make_aai_env(env_directory, num_env, arenas_configurations, start_index=0):
    """
    Create a wrapped, monitored Unity environment.
    """

    def make_env(rank, arena_configuration):  # pylint: disable=C0111
        def _thunk():
            env = AnimalAIGym(
                environment_filename=env_directory,
                worker_id=rank,
                flatten_branched=True,
                arenas_configurations=arena_configuration,
                uint8_visual=True)
            env = Monitor(env, logger.get_dir() and os.path.join(logger.get_dir(), str(rank)))
            return env

        return _thunk

    return SubprocVecEnv([make_env(i + start_index, arenas_configurations) for i in range(num_env)])


def main():
    arenas_configurations = ArenaConfig("configurations/arena_configurations/train_ml_agents_arenas.yml")
    env = make_aai_env('/home/ben/AnimalAI/builds-ml-agents-aaio/aaio',2, arenas_configurations)
    ppo2.learn(
        network="cnn",
        env=env,
        total_timesteps=100000,
        lr=1e-3,
    )


if __name__ == '__main__':
    main()
