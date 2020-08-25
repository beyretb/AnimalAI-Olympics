import sys
sys.path.insert(0, "/media/home/ludovico/aai/animalai")
sys.path.insert(1, "/media/home/ludovico/aai/animalai_train")

from raw_learned import Pipeline
from collections import namedtuple
from animalai.envs.arena_config import ArenaConfig

if __name__=="__main__":
	margs = namedtuple('args', 'env arena_config num_episodes inference')
	env_path = 'linux_builds/bb2.x86_64'
	args = margs(env=env_path, arena_config=None, num_episodes=120, inference=False)
	pipe = Pipeline(args)
	res = pipe.test_run("../competition_configurations/")