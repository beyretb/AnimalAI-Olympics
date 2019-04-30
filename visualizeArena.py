from animalai.envs.environment import UnityEnvironment
from animalai.envs.ArenaConfig import ArenaConfig
import sys
import random
import time

env_path= './envs/AnimalAI'
# env_path =None
worker_id= random.randint(0,200)
# worker_id=0
seed=10
base_port = 5005

sub_id = 1
run_id = 'aa'
save_freq=5000000
curriculum_file= None
fast_simulation = True
load_model = False
train_model = True
keep_checkpoints = 1000000
lesson = 0
run_seed =1
docker_target_name = None
no_graphics = False
trainer_config_path = './trainer_config.yaml'

model_path = './models/{run_id}'.format(run_id=run_id)
summaries_dir = './summaries'
maybe_meta_curriculum = None

def init_environment(env_path, docker_target_name, no_graphics, worker_id, fast_simulation, seed):
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
        no_graphics=no_graphics,
        play=True
    )

if len(sys.argv)>1:
    arena_config_in = ArenaConfig(sys.argv[1])
else:
    arena_config_in = ArenaConfig('./configs/ramp.yaml')

env = init_environment(env_path, docker_target_name, no_graphics, worker_id, fast_simulation, run_seed)
env.reset(config= arena_config_in)
env.reset()
try:
    while True:
        continue
except KeyboardInterrupt:
    env.close()
