import numpy as np
from clyngor import ASP

import sys
sys.path.insert(0, "/Users/ludo/Desktop/animalai/animalai/animalai_train")
sys.path.insert(1, "/Users/ludo/Desktop/animalai/animalai/animalai")

from animalai.envs.cvis import ExtractFeatures
from animalai.envs.gym.environment import AnimalAIGym
from animalai.envs.arena_config import ArenaConfig
from mlagents.tf_utils import tf
from centroidtracker import CentroidTracker

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
ef = ExtractFeatures(display=False, training=False)


def load_pb(path_to_pb):
    with tf.gfile.GFile(path_to_pb, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name="")
        return graph

def preprocess(ct, step_results):
    visual_obs = step_results[3]["batched_step_result"].obs[0][0] # last 0 idx bc batched
    vector_obs = step_results[3]["batched_step_result"].obs[1][0]
    bboxes = ef.run(visual_obs)
    ids = ct.update([i[0] for i in bboxes])
    obj = [(i[0], i[1], j) for i,j in zip(bboxes, ids)]
    res = {
        "obj": obj, # list of tuples
        "velocity": vector_obs,  # array
        "reward": step_results[1],  # float
        "done": step_results[2],  # bool
        # "step": step_results[-1],
    }
    return res

class RollingChecks:
    @staticmethod
    def visible(state, obj_id):
        if any(i[1]=='goal' for i in state['obj']):
            return True, f"Success: Object {obj_id} now visible"
        return False, f"Object {obj_id} still not visible"

    @staticmethod
    def time(state, limit=220):
        t = state["micro_step"]
        if t >= limit:
            return True, f"Failure: Time out, timestep {t}/{limit}"
        return False, f"Timestep {t}/{limit}"


class MacroConfig:
    @staticmethod
    def explore(state, x):
        """Go behind object x. x is an id. x comes in as "x,y"""
        x = int(x.split(",")[0])
        res = np.zeros(6)
        res[:2] = state['velocity']
        try:
            res[2:] = next(i[0] for i in state['obj'] if i[2]==x)
        except StopIteration:
            res[2:] = [0,0,0,0]
        return res

    @staticmethod
    def interact(state, x):
        """Go to object x. x is an id."""
        x = int(x)
        res = np.zeros(6)
        res[:2] = state['velocity']
        try:
            res[2:] = next(i[0] for i in state['obj'] if i[2]==x)
        except StopIteration:
            res[2:] = [0,0,0,0]
        return res


class MacroAction:
    def __init__(self, env, ct, state, step_results, action):
        self.env = env
        self.ct = ct
        self.state = state
        self.step_results = step_results
        self.action = action["initiate"][0][0]
        self.action_args = action["initiate"][0][1]
        self.checks = action["check"]
        self.graph = None
        self.reward = 0
        self.micro_step = 0

    def macro_stats(self, checks=None):
        success = self.state['reward'] > self.reward
        res = {
            "success": success,
            "micro_step": self.micro_step,
            "reward": self.state['reward'],
            "checks": checks,
        }
        return res

    def get_action(self, vector_obs):
        with tf.compat.v1.Session(graph=self.graph) as sess:
            output_node = self.graph.get_tensor_by_name("action:0")
            input_node = self.graph.get_tensor_by_name("vector_observation:0")
            vector_obs = vector_obs.reshape(1, -1)
            mask_constant = np.array([1, 1, 1, 1, 1, 1]).reshape(1, -1)
            action_masks = self.graph.get_tensor_by_name("action_masks:0")
            model_result = sess.run(
                output_node,
                feed_dict={input_node: vector_obs, action_masks: mask_constant},
            )
            action = [model_result[0, :3].argmax(), model_result[0, 3:].argmax()]
        return action

    def checks_clean(self):
        if self.state['done']:
            return False, self.macro_stats(None)
        for check in self.checks:
            if check[1] != "-":
                check_bool, check_stats = getattr(RollingChecks, check[0])(
                    self.state, check[1]
                )
            else:
                check_bool, check_stats = getattr(RollingChecks, check[0])(self.state)

            if check_bool:
                return False, self.macro_stats(check_stats)
        return True, "GREEN"

    def run(self):
        state_parser = getattr(MacroConfig(), self.action)

        # Get model path
        if self.action == 'explore':
            bbox = state_parser(self.state, self.action_args)
            model_path = f"macro_actions/raw/{self.action}"
            if (bbox[0]+bbox[2]/2)>0.5: # If obj is on right, go around left side
                model_path+= "_left.pb"
                print('left')
            else:
                model_path+= "_right.pb"
                print('right')
        else:
            model_path = f"macro_actions/raw/{self.action}.pb"

        # Load graph
        self.graph = load_pb(model_path)

        go = True
        while go:
            vector_obs = state_parser(self.state, self.action_args)
            action = self.get_action(vector_obs)
            self.step_results = self.env.step(action)
            self.state = preprocess(self.ct, self.step_results)
            self.state['micro_step'] = self.micro_step
            self.micro_step += 1
            go, stats = self.checks_clean()
            self.reward = self.step_results[1]
        return self.step_results, self.state, stats, self.micro_step


class Pipeline:
    def __init__(self, args):
        self.args = args
        self.ct = None
        self.bk = ""
        self.gg_id = 0
        env_path = args.env
        worker_id = 0
        seed = 1
        arena_path = args.arena_config
        ac = ArenaConfig(arena_path)
        # Load Unity environment based on config file with Gym or ML agents wrapper
        self.env = AnimalAIGym(
            environment_filename=env_path,
            worker_id=worker_id,
            n_arenas=1,
            arenas_configurations=ac,
            seed=seed,
            grayscale=False,
            inference=True
        )


    @staticmethod
    def visible(state):
        visible = ""
        for _, _, _id in state['obj']:
            visible += f"visible({_id}).\n"
        return visible

    def goal_visible(self, state):
        try:
            self.gg_id = next(i[2] for i in state['obj'] if i[1]=='goal')
            return True
        except StopIteration:
            self.gg_id = 42
            return False
    def grounder(self, state):
        visible = self.visible(state)
        self.goal_visible(state)
        return visible

    def logic(self):
        lp = f"""
                {self.bk}
                present({self.gg_id}).
                present(X):- visible(X).
                obstructs(X,Y) :- present(X), present(Y), visible(X), not visible(Y).
                initiate(explore(X,Y)) :- visible(X), obstructs(X,Y).
                initiate(interact({self.gg_id})):- visible({self.gg_id}).

                check(visible(Y)):- initiate(explore(X,Y)).
                check(time):- initiate(explore(X,Y)).
                check(time):- initiate(interact({self.gg_id})).
                """
        answers = ASP(lp)

        return answers

    @staticmethod
    def split_predicate(x):
        predicate = x.split("(")[0]
        if "(" in x:
            var = x.split("(")[1].split(")")[0]
        else:
            var = "-"
        return [predicate, var]

    def format_macro_results(self, stats):
        res = """
        Success: {success}
        Micro steps taken: {micro_step}
        Total reward: {reward}
        Checks satisfied: {checks}
        """.format(
            **stats
        )
        return res

    def macro_processing(self, answer_sets):
        # Get out of clyngor obj type
        answer_sets = list(list(answer_sets)[0])
        # Fetch initiate and checks
        kw = ["initiate", "check", "terminate"]
        filtered_answer_sets = {
            k: [self.split_predicate(i[1][0]) for i in answer_sets if i[0] == k]
            for k in kw
        }
        assert (
            not len(filtered_answer_sets["initiate"]) > 1
        ), f"Can only support one action at at a time: {filtered_answer_sets['initiate']}"
        if len(filtered_answer_sets["initiate"]) < 1:
            return None
        return filtered_answer_sets

    def take_macro_step(self, env, state, step_results, macro_action):
        ma = MacroAction(env, self.ct, state, step_results, macro_action)
        print(f"Initiating macro_action: {macro_action['initiate']}")
        step_results, state, macro_stats, micro_step = ma.run()
        print(f"Results: {self.format_macro_results(macro_stats)}")
        return step_results, state, micro_step, macro_stats["success"]

    def episode_over(self, done):
        if done:
            return True
        return False

    def rotate(self):
        print("Rotating 360")
        tracker_onset = None
        tracker_offset = 0
        for c in range(50):
            # ground_atoms = self.grounder(state)
            # if ground_atoms not in self.bk:
            #     self.bk += ground_atoms
            step_results = self.env.step([[0, 1]])
            state = preprocess(self.ct, step_results)  # Rotate
            if self.goal_visible(state):
                print("Goal visible")
                return step_results
            if state['obj']:
                if tracker_onset is None:
                    tracker_onset = c
                else:
                    tracker_offset = c
        # If no goal was visible rerotate to where something was visible
        point_to_object = tracker_onset + int((tracker_offset-tracker_onset)/2)
        if point_to_object > 25:
            num_rotations = 50 - point_to_object
            direction = 2
        else:
            num_rotations = point_to_object
            direction = 1
        for i in range(num_rotations): # add extra 2 rotations to be looking straight at object
            step_results = self.env.step([[0, direction]])
            _ = preprocess(self.ct, step_results)
        return step_results

    def run(self):
        success_count = 0
        for i in range(self.args.num_episodes):
            print(f"======Running episode {i}=====")
            step_results = self.env.step([[0, 0]])  # Take 0,0 step
            global_steps = 0
            while not self.episode_over(step_results[2]):
                self.bk = ""  # Reset bk each new macroaction
                self.ct = CentroidTracker() # Initialise tracker
                state = preprocess(self.ct, step_results)
                ground_atoms = self.grounder(state)
                self.bk += ground_atoms
                answer_sets = self.logic()
                macro_action = self.macro_processing(answer_sets)
                if macro_action is None:
                    step_results = self.rotate()
                    global_steps += 50
                    continue
                step_results, state, micro_step, success = self.take_macro_step(
                    self.env, state, step_results, macro_action
                )
                global_steps += micro_step
            nl_success = "Success" if success else "Failure"
            print(f"Episode was a {nl_success}")
            success_count += success

        print(
            f"Final results: {success_count}/{self.args.num_episodes} episodes were completed successfully"
        )