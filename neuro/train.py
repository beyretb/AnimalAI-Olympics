import argparse
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

from mlagents.trainers.trainer_util import load_config;
from animalai_train.run_options_aai import RunOptionsAAI;
from animalai_train.run_training_aai import run_training_aai;

import warnings
warnings.filterwarnings('ignore')

def get_args():
    parser = argparse.ArgumentParser('AnimalAI training loop')
    parser.add_argument('-tc', '--train_config', type=str, default='no_vis_config', help='Prefix of training config file')
    parser.add_argument('-e', '--env_name', type=str, default='aai_no_vis', help='Env prefix name')
    parser.add_argument('-cc', '--curric_config', type=str, default='curriculum1', help='Curriculum prefix name')
    parser.add_argument('-r', '--run_id', type=str, default='run1', help='Curriculum prefix name')
    parser.add_argument('-ne', '--num_envs', type=int, default=1, help='Number of simultaneous envs open')
    parser.add_argument('-na', '--num_arenas', type=int, default=1, help='Number of simultaneous arenas on each env')
    
    args = parser.parse_args()
    return args

def train(opt):
    # Display training config
    trainer_config_path = f"configurations/training_configurations/{opt.train_config}.yaml"
    with open(trainer_config_path) as f:
        print(f.read())
    environment_path = f"linux_builds/{opt.env_name}.x86_64"
    curriculum_path = f"configurations/{opt.curric_config}"

    run_id = opt.run_id
    base_port = 5005
    number_of_environments = opt.num_envs
    number_of_arenas_per_environment = opt.num_arenas

    args = RunOptionsAAI(
        trainer_config=load_config(trainer_config_path),
        env_path=environment_path,
        run_id=run_id,
        base_port=base_port,
        num_envs=number_of_environments,
        curriculum_config=curriculum_path,
        n_arenas_per_env=number_of_arenas_per_environment,
    )

    print(
        f"Training now with {number_of_environments} envs each with {number_of_arenas_per_environment} arenas")
    run_training_aai(0, args)
    print("Done training")

if __name__ == '__main__':
    opt = get_args()
    train(opt)

# python3 -m train -e aai_no_vis1 -ne 4 -na 4 -r blindgotox1