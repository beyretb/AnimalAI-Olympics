import numpy as np
from mlagents.tf_utils import tf

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

from utils import load_pb, preprocess
from logic import Grounder
from collections import deque

goal_visible = Grounder().goal_visible # Func

class RollingChecks:
    @staticmethod
    def visible(state, obj_id):
        if any(i[1]in['goal','goal1'] for i in state['obj']):
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
        x = x[0]
        res = np.zeros(6)
        res[:2] = state['velocity']
        try:

            res[2:] = next(i[0] for i in state['obj'] if i[3]==x)
        except StopIteration:
            res[2:] = [0,0,0,0]
        return res

    @staticmethod
    def interact(state, x):
        """Go to object x. x is an id."""
        x = x[0]
        res = np.zeros(6)
        res[:2] = state['velocity']
        try:
            res[2:] = next(i[0] for i in state['obj'] if i[3]==x)
        except StopIteration:
            res[2:] = [0,0,0,0]
        return res

class MacroAction:
    def __init__(self, env, ct, state, step_results, action):
        self.env = env
        self.ct = ct
        self.state = state
        self.step_results = step_results
        if isinstance(action['initiate'][0],str):
            self.action = action['initiate'][0]
            self.action_args = None
        else:
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

    def rotate_clever(self):
        # print("Rotating 360")
        tracker_onset = None
        tracker_offset = 0
        for c in range(50):
            self.step_results = self.env.step([[0, 1]])
            self.reward = self.step_results[1]
            self.state = preprocess(self.ct, self.step_results, self.micro_step)
            self.state['micro_step'] = self.micro_step
            self.micro_step += 1
            self.reward = self.step_results[1]
            # Rotate
            if '42' not in goal_visible(0, self.state): #0 is placeholder macro step, has no effect
                # print("Goal visible")
                return self.step_results, self.state, self.macro_stats(
                    "Goal visible, end rotation"), self.micro_step
            if self.state['obj']:
                if tracker_onset is None:
                    tracker_onset = c
                else:
                    tracker_offset = c
        # If no goal was visible rerotate to where something was visible
        if tracker_onset is None:
            return None
        point_to_object = tracker_onset + int((tracker_offset-tracker_onset)/2)
        if point_to_object > 25:
            num_rotations = 50 - point_to_object
            direction = 2
        else:
            num_rotations = point_to_object
            direction = 1
        for _ in range(num_rotations): # add extra 2 rotations to be looking straight at object
            self.step_results = self.env.step([[0, direction]])
            self.reward = self.step_results[1]
            self.state = preprocess(self.ct, self.step_results, self.micro_step)
            self.state['micro_step'] = self.micro_step
            self.micro_step += 1
        return self.step_results, self.state, self.macro_stats(
            "Object visible, rotating to it"), self.micro_step

    def rotate(self):
        """Rotate to first visible object"""
        # print("Rotating 360")
        tracker_onset = None
        tracker_offset = 0
        for c in range(50):
            self.step_results = self.env.step([[0, 1]])
            self.reward = self.step_results[1]
            self.state = preprocess(self.ct, self.step_results, self.micro_step)
            self.state['micro_step'] = self.micro_step
            self.micro_step += 1
            self.reward = self.step_results[1]
            # Rotate
            if self.state['obj']: #0 is placeholder macro step, has no effect
                # print("Object visible")
                break # and run a few more rotations to point to it
        for _ in range(3): # add extra 3 rotations to be looking straight at object
            self.step_results = self.env.step([[0, 1]])
            self.reward = self.step_results[1]
            self.state = preprocess(self.ct, self.step_results, self.micro_step)
            self.state['micro_step'] = self.micro_step
            self.micro_step += 1
        return self.step_results, self.state, self.macro_stats(
            "Object visible, rotating to it"), self.micro_step

    def run(self):
        if self.action=='rotate':
            return self.rotate_clever()
        # print(self.action)
        state_parser = getattr(MacroConfig(), self.action)

        # Get model path
        if self.action == 'explore':
            bbox = state_parser(self.state, self.action_args)[2:]
            model_path = f"macro_actions/raw/{self.action}"

            if (bbox[0]+bbox[2]/2)>0.5: # If obj is on right, go around left side
                model_path+= "_right.pb"
                # print('right')
            else:
                model_path+= "_left.pb"
                # print('left')
        else:
            model_path = f"macro_actions/raw/{self.action}.pb"


        self.graph = load_pb(model_path)

        go = True
        monitor_speed = deque(maxlen=5)
        while go:
            vector_obs = state_parser(self.state, self.action_args)
            monitor_speed.append(vector_obs[:2])
            action = self.get_action(vector_obs)
            self.step_results = self.env.step(action)
            self.state = preprocess(self.ct, self.step_results, self.micro_step)
            self.state['micro_step'] = self.micro_step
            self.micro_step += 1
            go, stats = self.checks_clean()
            self.reward = self.step_results[1]
            if np.mean(monitor_speed)<1: #i.e. we're stuck
                if "explore" in model_path:
                    if "right" in model_path:
                        self.graph = load_pb("macro_actions/raw/explore_left.pb")
                    else:
                        self.graph = load_pb("macro_actions/raw/explore_right.pb")


        return self.step_results, self.state, stats, self.micro_step

