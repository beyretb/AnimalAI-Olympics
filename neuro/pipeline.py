import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from clyngor import ASP, solve
import tensorflow as tf
import sys
from animalai.envs.gym.environment import AnimalAIGym
from animalai.envs.arena_config import ArenaConfig
import yaml
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

obs_dim_mapper = {
	'explore' : 20,
	'interact':10
}
obj_mapper = [
             "Cardbox1",
             "Cardbox2",
             "CylinderTunnelTransparent",
             "CylinderTunnel",
             "DeathZone",
             "GoodGoalMulti",
             "GoodGoal",
             "LObject",
             "LObject2",
             "Ramp",
             "UObject",
             "WallTransparent",
             "Wall",
              "BadGoal",
              "HotZone"]
def load_pb(path_to_pb):
    with tf.gfile.GFile(path_to_pb, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name='')
        return graph
def preprocess(step_results, visualize=False):
	step_results = step_results[3]['batched_step_result']
	res = step_results.obs[1].flatten()[6:146].reshape(-1,14)
	df = pd.DataFrame(res)
	df.rename(inplace=True, columns={0: 'id', 1:'class', 2: 'visible', 3:'abs_pos_x', 4:'abs_pos_y', 5:'abs_pos_z', 6: 'rel_pos_x', 7: 'rel_pos_y', 8:'rel_pos_z', 9:'abs_rot', 10:'rel_rot', 11:'size_x', 12:'size_y', 13:'size_z'})
	df['class'] = df['class'].apply(lambda x: obj_mapper[int(x)] if x!=-1.0 else 'null')
	df = df[df['id']!=-1].set_index('id')

	df_a = pd.DataFrame(step_results.obs[1].flatten()[0:6]).T
	df_a.rename(inplace=True, columns={0: 'vel_x', 1:'vel_z', 2:'rot_y', 3:'abs_pos_x', 4:'abs_pos_y', 5:'abs_pos_z'})
	if visualize:
		img = step_results.obs[0][0]
		plt.axis('off')
		plt.imshow(res)
	return df

class RollingChecks:
	def visible(state, t, obj_id):
		if state.loc[obj_id]=!-1.0:
			return True
		return False
	def timeout(state, t, limit=250):
		if t>=limit:
			return True
		return False

class MacroConfig:
"""
	Needs:
	1) Name of action
	2) Kwargs the action needs to filter state
	3) State
"""
	def go_behind(self, state, x):
		"""Go behind object x. x is an id."""
		state.loc[x]

class MacroAction:
	def __init__(self, env, step_results, action):
		self.env = env
		self.step_results = step_results
		self.action = action['initiate'][0]
		self.checks = action['checks']

	def get_action(self, vector_obs):
		with tf.compat.v1.Session(graph=graph) as sess:
		    output_node = graph.get_tensor_by_name('action:0')
		    input_node = graph.get_tensor_by_name('vector_observation:0')
		    vector_obs = vector_obs.reshape(1, -1)
		    mask_constant = np.array([1,1,1,1,1,1]).reshape(1,-1)
		    action_masks = graph.get_tensor_by_name('action_masks:0')
		    model_result = sess.run(output_node , feed_dict ={input_node : vector_obs,
		                                                     action_masks: mask_constant})
			action = [model_result[0,:3].argmax(), model_result[0, 3:].argmax()]
		return action

	def checks_clean(self):
		if self.step_results.done:
			print("Success, episode done")
			return False, "SUCCESS"
		state = preprocess(self.step_results)
		for check in self.checks:
			check_bool, check_stats = getattr(RollingChecks, check)(state):
			if check_bool:
				return True, "GREEN"
		return False, f"Failure: {check_stats}"

	def run(env):
		model_path = f"macro_actions/{self.action}/frozen_graph_def.pb"
		model = load_pb(model_path)
		state_parser = getattr(StateParser, self.action)
		micro_step = 0
		go = True
		while go:
			state = state_parser(self.step_results)
			action = self.get_action(state)
			self.step_results = env.step(action)
			micro_step += 1
			go, check_stats = self.checks_clean(self.step_results)
		return self.step_results, check_stats, micro_step



class Pipeline:
	def __init__(self, visualize=False):
		self.visualize = visualize

    @staticmethod
    def visible(df):
		df1 = df[['class', 'visible', 'id']]
		df1 = df1.applymap(lambda x:round(x) if not isinstance(x,str) else x)[df1['id']!=-1].astype(str)
		visible = ""
		for r in df1.index:
		    if df1.loc[r]['visible']!='-1':
		        visible += f"visible({','.join(df1.loc[r])})\n"
		return visible

    def grounder(self, df):
    	visible = self.visible(df)

    	return visible

	def logic(self, bk):
		answers = ASP(f"""
				{bk}
				present(X):- visible(X).
				obstructs(X,Y) :- present(X), present(Y), visible(X), not visible(Y).
				initiate(explore(X,Y)) :- visible(X), obstructs(X,Y).
				initiate(interact(a)):- visible(a).

				check(visible(Y)), check(time):- initiate(explore(X,Y)).
				check(reached(a)), check(time):- initiate(interact(a)).
				""")

		return answers
	@staticmethod
	def split_predicate(x):
	    predicate = x.split('(')[0]
	    if '(' in x:
	        var = x.split('(')[1].split(')')[0]
	    else:
	        var = '-'
	    return [predicate, var]
	def macro_processing(self, answer_sets):
		# Get out of clyngor obj type
		answer_sets = list(list(answer_sets)[0])
		# Fetch initiate and checks
		kw = ['initiate', 'check', 'terminate']
		filtered_answer_sets = {
		    k: [self.split_predicate(i[1][0]) for i in answer_sets if i[0] ==k] for k in kw
		}

		assert len(filtered_answer_sets['initiate'])==1, "Can only support one action at at a time"
		return filtered_answer_sets

	def take_macro_step(self, env, step_results, macro_action):
		ma = MacroAction(env, step_results, macro_action)
		step_results, macro_stats, micro_step = ma.initiate()
		return step_results, micro_step

	def episode_over(self, env):
		return True

		return False
	def run(self, args):
		env_path = agrs.env
		worker_id = 1
		seed = 1
		arena_path = args.arena_config
		ac = ArenaConfig(arena_path)
		# Load Unity environment based on config file with Gym or ML agents wrapper
		env = AnimalAIGym(environment_filename=env_path,
		              worker_id=worker_id,
		              n_arenas=1,
		              arenas_configurations=ac,
		                seed=seed,
		                 grayscale=False)	
		# Take 0,0 step
		step_results = env.step([[0,0]])
		global_steps = 0
		while not self.episode_over(env):
			data = self.preprocess(step_results)
			ground_atoms = self.grounder(data)
			answer_sets = self.logic(ground_atoms)
			macro_action = self.macro_processing(answer_sets)
			step_results, micro_step = self.take_macro_step(env, global_steps, step_results, macro_actions)
			global_steps += micro_step
