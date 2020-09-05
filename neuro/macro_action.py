import numpy as np
from mlagents.tf_utils import tf

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

from utils import load_pb, preprocess, dual_process, get_distance
from logic import Grounder
from collections import deque
import time
import cv2
goal_visible = Grounder().goal_visible # Func

test=True
class RollingChecks:
    @staticmethod
    def visible(state, obj_id):
        if any(i[1]in['goal','goal1'] for i in state['obj']):
            return True, f"Success: Object {obj_id} now visible"
        return False, f"Object {obj_id} still not visible"

    @staticmethod
    def time(state, limit=250):
        t = state["micro_step"]
        if t >= limit:
            return True, f"Failure: Time out, timestep {t}/{limit}"
        return False, f"Timestep {t}/{limit}"


# def goal_over(bb1, bb2):
#     if 'goal' in bb2[1]:
#         return False
#     if get_distance(bb1[0], bb2[0])<0.02:
#         # print('ye')
#         if bb1[0][1]<bb2[0][1]:
#             # print('naa')
#             return True
#     return False

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

        # obj = [i for i in state['obj'] if abs((i[0][-1]/i[0][-2])-1)<0.3]
        # obj = []
        # for i in state['obj']:
        #     if not 'goal' in i[1]:
        #         continue
        #     if any(goal_over(i, i2) for i2 in state['obj']):
        #         print("Not valid")
        #         continue
        #     else:
        #         obj.append(i)
        obj = state['obj']
        # print([i[1] for i in state['obj']])
        try:
            res[2:] = next(i[0] for i in obj if i[3]==x)
        except StopIteration:

            if any('goal1' in i[1] for i in obj):
                    res[2:] = [i[0] for i in obj if 'goal1' in i[1]][0]
            else:
                res[2:] = [0,0,0,0]

        return res
    @staticmethod
    def avoid_red(state, x):
        """Go to object x while avoiding red. x is an id."""
        res = np.zeros(6)
        res[:2] = state['velocity']
        img, _ = dual_process(state['visual_obs'])

        try:
            res[2:] = next(i[0] for i in state['obj'] if i[1]=='goal')
        except StopIteration:

            if any(i[1]=="goal1" for i in state['obj']):
                    res[2:] = state['obj'][0][0]
            else:
                res[2:] = [0,0,0,0]

        return img, res

def choose_action_probability(predictions_exp):
    return np.random.choice(list(range(3)), 1, p=predictions_exp)[0]

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
            action_masks = self.graph.get_tensor_by_name("action_masks:0")

            mask_constant = np.array([1, 1, 1, 1, 1, 1]).reshape(1, -1)

            if isinstance(vector_obs, tuple):
                visual_node = self.graph.get_tensor_by_name("visual_observation_0:0")
                visual_obs, vector_obs = vector_obs 
                if visual_obs.shape[0]!=84:
                    visual_obs = cv2.cv2.resize(visual_obs, dsize=(84, 84), interpolation=cv2.INTER_CUBIC)
                vector_obs = vector_obs.reshape(1, -1)
                visual_obs = visual_obs.reshape(1, 84, 84, 1)

                feed_dict = {input_node: vector_obs,
                            action_masks: mask_constant,
                            visual_node: visual_obs}

            else:
                vector_obs = vector_obs.reshape(1, -1)
                feed_dict = {input_node: vector_obs, action_masks: mask_constant}

            prediction = sess.run(
                output_node,
                feed_dict=feed_dict,
            )[0]

            prediction = np.exp(prediction)

            action = [choose_action_probability(prediction[:3]), choose_action_probability(prediction[3:])]

        return np.array(action).reshape((1, 2))

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
        return True, self.macro_stats("GREEN")

    def rotate_clever(self):
        # print("Rotating 360")
        tracker_onset = None
        tracker_offset = 0
        for c in range(50):
            self.step_results = self.env.step([[0, 1]])
            self.state = preprocess(self.ct, self.step_results, self.micro_step, self.state['reward'])
            self.state['micro_step'] = self.micro_step
            self.micro_step += 1
            # Rotate
            if '42' not in goal_visible(0, self.state): #0 is placeholder macro step, has no effect
                # print("Goal visible")
                return self.step_results, self.state, self.macro_stats(
                    "Goal visible, end rotation"), self.micro_step
            if tracker_offset and not self.state['obj']:
                continue
            if self.state['obj']:
                # print(self.state['obj'])
                if tracker_onset is None:
                    tracker_onset = c
                else:
                    tracker_offset = c
        # If no goal was visible rerotate to where something was visible
        if tracker_onset is None:

            # for c in range(15):
            #     self.step_results = self.env.step([[1, 0]])
            #     self.state = preprocess(self.ct, self.step_results, self.micro_step)
            #     self.state['micro_step'] = self.micro_step
            #     self.micro_step += 1
            return self.step_results, self.state, self.macro_stats(
            "No object was visible"), self.micro_step
        # print(tracker_onset, tracker_offset)
        point_to_object = tracker_onset + int((tracker_offset-tracker_onset)/2)
        # print('pt', point_to_object)
        if point_to_object > 25:
            num_rotations = 50 - point_to_object
            direction = 2
        else:
            num_rotations = point_to_object
            direction = 1
        # print("numrot", num_rotations)
        time.sleep(1)
        go = True
        more_step = 0
        while go: # add extra 2 rotations to be looking straight at object
            self.step_results = self.env.step([[0, direction]])
            self.state = preprocess(self.ct, self.step_results, self.micro_step, self.state['reward'])
            self.state['micro_step'] = self.micro_step
            self.micro_step += 1
            more_step+=1
            if (more_step>=num_rotations)&bool(self.state['obj']):
                go = False
        # print("Going out of here")
        time.sleep(1)
        return self.step_results, self.state, self.macro_stats(
            "Object visible, rotating to it"), self.micro_step

    def rotate(self):
        """Rotate to first visible object"""
        # print("Rotating 360")
        tracker_onset = None
        tracker_offset = 0
        for c in range(50):
            self.step_results = self.env.step([[0, 1]])
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

    def run(self, pass_mark):
        if self.action=='rotate':
            if test:
                return self.rotate_clever()
            return self.rotate()

        state_parser = getattr(MacroConfig(), self.action)

        # Get model path
        if self.action == 'explore':
            bbox = state_parser(self.state, self.action_args)[2:]
            model_path = f"macro_actions/v2/{self.action}"

            if (bbox[0]+bbox[2]/2)>0.5: # If obj is on right, go around left side
                model_path+= "_right.pb"
                # print('right')
            else:
                model_path+= "_left.pb"
                # print('left')
        else:
            model_path = f"macro_actions/v2/{self.action}.pb"

        # print(model_path)
        self.graph = load_pb(model_path)

        if self.action == 'interact':
            count = [i for i in self.state['obj'] if 'goal' in i[1]]
            if len(count)>1:
                left = [i for i in count if i[0][0]<0.5]
                right = [i for i in count if i[0][0]>0.5]
                if len(left) > len(right):
                    # print("More on left")
                    self.action_args = [left[0][3]]
                elif len(left)==len(right):
                    size_left = sum([i[2] for i in left])
                    size_right  = sum([i[2] for i in right])
                    if size_left > size_right:
                        # print('bigger left')
                        self.action_args = [left[0][3]]
                    else:
                        # print('bigger right')
                        self.action_args = [right[0][3]]
                else:
                    # print("more on right")
                    self.action_args = [right[0][3]]


        go = True
        monitor_speed = deque(maxlen=20)
        monitor_sight = deque(maxlen=10)
        for i in range(20):
            monitor_sight.append(1)
            monitor_speed.append(np.array(1))
        while go:
            vector_obs = state_parser(self.state, self.action_args)
            if self.action != 'avoid_red':
                monitor_speed.append(abs(vector_obs[0]))
                monitor_sight.append(any(vector_obs[2:]))
            action = self.get_action(vector_obs)
            self.step_results = self.env.step(action)
            self.state = preprocess(self.ct, self.step_results, self.micro_step, self.state['reward'])
            self.state['micro_step'] = self.micro_step
            self.micro_step += 1
            go, stats = self.checks_clean()

            if test:
                # If got a reward then interact was successful
                if self.action=='interact':
                    if self.reward<self.step_results[1]:
                        return self.step_results, self.state, self.macro_stats(
                            "interact succeded"), self.micro_step
                    if not any(monitor_sight):
                        return self.step_results, self.state, self.macro_stats(
                            "interact failed"), self.micro_step

                # When we are stuck
                if np.mean(monitor_speed)<0.01:
                    if "explore" in model_path:
                        monitor_speed.clear() # clear deque
                        for i in range(20):
                            monitor_speed.append(1)
                        if "right" in model_path:
                            self.graph = load_pb("macro_actions/v2/explore_left.pb")
                        else:
                            self.graph = load_pb("macro_actions/v2/explore_right.pb")
                    if 'interact' in model_path:
                        for i in range(4):
                            self.step_results = self.env.step([2,0])
                            self.state = preprocess(self.ct, self.step_results, self.micro_step, self.state['reward'])
                            self.state['micro_step'] = self.micro_step
                            self.micro_step += 1
                        monitor_speed.clear() # clear deque


            self.reward = self.step_results[1]
            if self.state['reward'] > pass_mark:
                break

        return self.step_results, self.state, stats, self.micro_step

