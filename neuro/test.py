import sys
import os

sys.path.insert(0, "/media/home/ludovico/aai/animalai")
sys.path.insert(1, "/media/home/ludovico/aai/animalai_train")
from animalai.envs.gym.environment import AnimalAIGym
import random
from animalai.envs.arena_config import ArenaConfig

import yaml
import copy
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


# CONFIG
if __name__=="__main__":
	env_path = 'linux_builds/aai'
	worker_id = 0
	#random.randint(1, 100)
	# competition_envs = os.listdir('../competition_configurations/')

	seed = 1


	# yaml_path = '../neuro/configurations/curriculum2/0.yml'
	yaml_path = "../competition_configurations/5-11-3.yml" #'configurations/curriculum/0.yaml'

	ac = ArenaConfig(yaml_path)
	# arena_path = "competition_configurations/5-10-3.yml" #'configurations/curriculum/0.yaml'
	# ac = ArenaConfig(arena_path)
	# ac.arenas[1] = copy.deepcopy(ac.arenas[0])

	env = AnimalAIGym(environment_filename=env_path,
	              worker_id=worker_id,
	              n_arenas=1,
	              arenas_configurations=ac,
	#                 use_visual=False,
	                seed=seed,
	#                   play=True,
	                 grayscale=False,
	                 resolution = 1000)

	for i in range(10):
	    x = env.step([[0,0]])
	    print(x[3]['batched_step_result'].obs[1])
	plt.axis('off')
	plt.imshow(env.render())
	plt.savefig('/media/home/ludovico/aai/bam.png',bbox_inches='tight',transparent=True, pad_inches=0)
