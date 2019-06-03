from animalai.envs.environment import UnityEnvironment
from animalai.envs.arena_config import ArenaConfig
import sys
import random

env_path = '../env/AnimalAI'
worker_id = random.randint(0, 200)
run_seed = 1
docker_target_name = None
no_graphics = False


def init_environment(env_path, docker_target_name, no_graphics, worker_id, seed):
    if env_path is not None:
        # Strip out executable extensions if passed
        env_path = (env_path.strip()
                    .replace('.app', '')
                    .replace('.exe', '')
                    .replace('.x86_64', '')
                    .replace('.x86', ''))
    docker_training = docker_target_name is not None

    return UnityEnvironment(
        n_arenas=1,
        file_name=env_path,
        worker_id=worker_id,
        seed=seed,
        docker_training=docker_training,
        play=True
    )


# If no configuration file is provided we default to all objects placed randomly
if len(sys.argv) > 1:
    arena_config_in = ArenaConfig(sys.argv[1])
else:
    arena_config_in = ArenaConfig('configs/allObjectsRandom.yaml')

env = init_environment(env_path, docker_target_name, no_graphics, worker_id, run_seed)

# We can pass a different configuration at each env.reset() call. You can therefore load different YAML files between
# episodes or directly amend the arena_config_in which contains a dictionary of configurations for all arenas.
# See animalai/envs/arena_config.py for the syntax
env.reset(arenas_configurations =arena_config_in)

try:
    while True:
        continue
except KeyboardInterrupt:
    env.close()
