from animalai_train.trainers.trainer_controller import TrainerController
from animalai.envs import UnityEnvironment
from animalai_train.trainers.meta_curriculum import MetaCurriculum
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
maybe_meta_curriculum = MetaCurriculum(curriculum_file)

trainer_config = yaml.load(open(trainer_config_path))
env = UnityEnvironment(
    n_arenas=1,  # Change this to train on more arenas
    file_name=env_path,
    worker_id=worker_id,
    seed=seed,
    docker_training=False,
    play=False
)

external_brains = {brain: env.brains[brain] for brain in env.external_brain_names}

tc = TrainerController(model_path, summaries_dir, run_id + '-' + str(sub_id),
                       save_freq, maybe_meta_curriculum,
                       load_model, train_model,
                       keep_checkpoints, lesson, external_brains, run_seed)
tc.start_learning(env, trainer_config)
