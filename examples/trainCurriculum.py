from animalai_train.trainers.trainer_controller import TrainerController
from animalai.envs import UnityEnvironment
from animalai.envs.exception import UnityEnvironmentException
from animalai.envs.arena_config import ArenaConfig
import random
import yaml
import sys

# ML-agents parameters for training
env_path = '../env/AnimalAI'
worker_id = random.randint(1, 100)
seed = 10
base_port = 5005
sub_id = 1
run_id = 'train_example_curriculum'
save_freq = 5000
curriculum_file = 'configs/curriculum/'
load_model = False
train_model = True
keep_checkpoints = 5000
lesson = 0
run_seed = 1
trainer_config_path = 'configs/trainer_config.yaml'
model_path = './models/{run_id}'.format(run_id=run_id)
summaries_dir = './summaries'
maybe_meta_curriculum = None


def init_environment(env_path, docker_target_name, worker_id, seed):
    if env_path is not None:
        # Strip out executable extensions if passed
        env_path = (env_path.strip()
                    .replace('.app', '')
                    .replace('.exe', '')
                    .replace('.x86_64', '')
                    .replace('.x86', ''))
    docker_training = docker_target_name is not None

    return

trainer_config = yaml.load(open(trainer_config_path))
env = UnityEnvironment(
    n_arenas=1,  # Change this to train on more arenas
    file_name=env_path,
    worker_id=worker_id,
    seed=seed,
    docker_training=False,
    play=False
)

external_brains = {}
for brain_name in env.external_brain_names:
    external_brains[brain_name] = env.brains[brain_name]

# Create controller and begin training.
tc = TrainerController(model_path, summaries_dir, run_id + '-' + str(sub_id),
                       save_freq, maybe_meta_curriculum,
                       load_model, train_model,
                       keep_checkpoints, lesson, external_brains, run_seed)
tc.start_learning(env, trainer_config)
