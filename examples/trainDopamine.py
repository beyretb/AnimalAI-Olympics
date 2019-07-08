from animalai.envs.gym.environment import AnimalAIEnv
from animalai.envs.arena_config import ArenaConfig
from dopamine.agents.rainbow import rainbow_agent
from dopamine.discrete_domains import run_experiment


import random

env_path = '../env/AnimalAI'
worker_id = random.randint(1, 100)
arena_config_in = ArenaConfig('configs/1-Food.yaml')
base_dir = 'models/dopamine'
gin_files = ['configs/rainbow.gin']


def create_env_fn():
    env = AnimalAIEnv(environment_filename=env_path,
                      worker_id=worker_id,
                      n_arenas=1,
                      arenas_configurations=arena_config_in,
                      docker_training=False,
                      retro=True)
    return env


def create_agent_fn(sess, env, summary_writer):
    return rainbow_agent.RainbowAgent(sess=sess, num_actions=env.action_space.n, summary_writer=summary_writer)


run_experiment.load_gin_configs(gin_files, None)
runner = run_experiment.Runner(base_dir=base_dir,
                               create_agent_fn=create_agent_fn,
                               create_environment_fn=create_env_fn)
runner.run_experiment()
