import numpy as np
import pandas as pd
import math
from clyngor import ASP

# import sys
from animalai.envs.gym.environment import AnimalAIGym
from animalai.envs.arena_config import ArenaConfig
from mlagents.tf_utils import tf

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

obs_dim_mapper = {"explore": 20, "interact": 10}
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
    "HotZone",
]


def transform(matrix, obj):
    """Transform world position of vector to local position relative to agent"""
    # obj = np.matrix(obj/40 - agent)
    obj.resize(4, refcheck=False)  # adds
    res = matrix * obj.reshape(4, 1)
    return res


def load_pb(path_to_pb):
    with tf.gfile.GFile(path_to_pb, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name="")
        return graph


def obs2state(vector_obs):
    obj_df = pd.DataFrame(vector_obs[6:146].reshape(-1, 14))
    obj_df.rename(
        inplace=True,
        columns={
            0: "id",
            1: "class",
            2: "visible",
            3: "abs_pos_x",
            4: "abs_pos_y",
            5: "abs_pos_z",
            6: "rel_pos_x",
            7: "rel_pos_y",
            8: "rel_pos_z",
            9: "abs_rot",
            10: "rel_rot",
            11: "size_x",
            12: "size_y",
            13: "size_z",
        },
    )
    obj_df["class"] = obj_df["class"].apply(
        lambda x: obj_mapper[int(x)] if x != -1.0 else "null"
    )
    obj_df = obj_df[obj_df["id"] != -1]
    obj_df["id"] = (obj_df["id"] * -1).astype(int)
    obj_df = obj_df.set_index("id")

    # columns={0: 'vel_x', 1:'vel_z', 2:'rot_y', 3:'abs_pos_x', 4:'abs_pos_y', 5:'abs_pos_z'})

    rays = vector_obs[146:151].flatten()
    wtlm = np.matrix(vector_obs[151:167].flatten()).reshape(4, 4)

    res = {
        "agent": vector_obs[0:6],  # df
        "objects": obj_df,  # df
        "rays": rays,  # np
        "transform": wtlm,  # np
    }
    return res


def preprocess(step_results):
    vector_obs = step_results[3]["batched_step_result"].obs[1].flatten()
    tmin1 = obs2state(vector_obs[:167])
    t = obs2state(vector_obs[167:])

    res = {
        "t-1": tmin1,  # df
        "t": t,  # df
        "reward": step_results[1],  # float
        "done": step_results[2],  # bool
        "step": step_results[-1],
    }
    return res


class RollingChecks:
    @staticmethod
    def visible(state, obj_id):
        if state["t"]["objects"].loc[int(obj_id), "visible"] != -1.0:
            return True, f"Success: Object {obj_id} now visible"
        return False, f"Object {obj_id} still not visible"

    @staticmethod
    def time(state, limit=220):
        t = state["step"]
        if t >= limit:
            return True, f"Failure: Time out, timestep {t}/{limit}"
        return False, f"Timestep {t}/{limit}"


class MacroConfig:
    @staticmethod
    def go_behind(step_results, x):
        """Go behind object x. x is an id. x comes in as "x,y"""
        x = int(x.split(",")[0])
        res = np.zeros(20)
        mstate = preprocess(step_results)
        for c, timestep in enumerate(["t-1", "t"]):
            state = mstate[timestep]
            ooi_pos = np.array(
                state["objects"].loc[x, ["abs_pos_x", "abs_pos_y", "abs_pos_z"]]
            )
            agent_pos = state["agent"][3:6]
            rel_pos = ooi_pos - agent_pos
            magn = np.linalg.norm(rel_pos)
            behind_pos = rel_pos * (magn + 0.3) / magn  # 0.125 => 5units in world
            local_behind_pos = transform(state["transform"], behind_pos)
            # rel_rot = math.atan2(local_behind_pos[0], local_behind_pos[1])
            res[0 + (10 * c) : 2 + (10 * c)] = state["agent"][:2]
            res[2 + (10 * c)] = state["objects"].loc[x, "rel_rot"]
            res[3 + (10 * c) : 5 + (10 * c)] = [
                local_behind_pos[0],
                local_behind_pos[2],
            ]  # only want x,z
            res[5 + (10 * c) : 10 + (10 * c)] = state["rays"]
        return res

    @staticmethod
    def interact(step_results, x):
        """Go to object x. x is an id."""
        res = np.zeros(10)
        x = int(x)
        mstate = preprocess(step_results)
        for c, timestep in enumerate(["t-1", "t"]):
            state = mstate[timestep]
            obj = state["objects"].loc[
                x, ["rel_pos_x", "rel_pos_y", "rel_pos_z", "rel_rot"]
            ]
            res[0 + (5 * c) : 2 + (5 * c)] = state["agent"][:2]
            res[2 + (5 * c)] = obj["rel_rot"]
            res[3 + (5 * c) : 5 + (5 * c)] = [obj["rel_pos_x"], obj["rel_pos_z"]]
        return res


class MacroAction:
    def __init__(self, env, step_results, action):
        self.env = env
        self.step_results = step_results
        self.action = action["initiate"][0][0]
        self.action_args = action["initiate"][0][1]
        self.checks = action["check"]
        model_path = f"macro_actions/{self.action}.pb"
        self.graph = load_pb(model_path)
        self.reward = 0
        self.micro_step = 0

    def macro_stats(self, checks=None):
        success = self.step_results[1] > self.reward
        self.reward = self.step_results[1]
        res = {
            "success": success,
            "micro_step": self.micro_step,
            "reward": self.reward,
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
        if self.step_results[2]:
            return False, self.macro_stats(None)
        state = preprocess(self.step_results)
        for check in self.checks:
            if check[1] != "-":
                check_bool, check_stats = getattr(RollingChecks, check[0])(
                    state, check[1]
                )
            else:
                check_bool, check_stats = getattr(RollingChecks, check[0])(state)

            if check_bool:
                return False, self.macro_stats(check_stats)
        return True, "GREEN"

    def run(self):
        state_parser = getattr(MacroConfig(), self.action)
        go = True
        while go:
            state = state_parser(self.step_results, self.action_args)
            action = self.get_action(state)
            self.step_results = self.env.step(action)
            self.step_results += tuple([self.micro_step])
            self.micro_step += 1
            go, stats = self.checks_clean()
            self.reward = self.step_results[1]
        return self.step_results, stats, self.micro_step


class Pipeline:
    def __init__(self, args):
        self.args = args
        self.bk = ""
        self.gg_id = 0
        env_path = args.env
        worker_id = 1
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
        )
    @staticmethod
    def visible(df):
        df1 = df["visible"]
        df1 = df1[df1 != -1].index.tolist()
        visible = "\n"
        for i in df1:
            visible += f"visible({round(i)}).\n"
        return visible

    def grounder(self, df):
        visible = self.visible(df)
        self.gg_id = int(df[df["class"] == "GoodGoal"].index[0])
        return visible

    def logic(self):
        lp = f"""
                {self.bk}
                present({self.gg_id}).
                present(X):- visible(X).
                obstructs(X,Y) :- present(X), present(Y), visible(X), not visible(Y).
                initiate(go_behind(X,Y)) :- visible(X), obstructs(X,Y).
                initiate(interact({self.gg_id})):- visible({self.gg_id}).

                check(visible(Y)):- initiate(go_behind(X,Y)).
                check(time):- initiate(go_behind(X,Y)).
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
        ), "Can only support one action at at a time"
        if len(filtered_answer_sets["initiate"]) < 1:
            return None
        return filtered_answer_sets

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

    def take_macro_step(self, env, step_results, macro_action):
        ma = MacroAction(env, step_results, macro_action)
        print(f"Initiating macro_action: {macro_action['initiate']}")
        step_results, macro_stats, micro_step = ma.run()
        print(f"Results: {self.format_macro_results(macro_stats)}")
        return step_results, micro_step, macro_stats["success"]

    def episode_over(self, done):
        if done:
            return True
        return False

    def rotate(self, step_results):
        print("Rotating 360")
        for _ in range(50):
            data = preprocess(step_results)
            ground_atoms = self.grounder(data["t"]["objects"])
            if ground_atoms not in self.bk:
                self.bk += ground_atoms
            step_results = self.env.step([[0, 1]])  # Take 0,0 step
        return step_results

    def run(self):
        success_count = 0
        for i in range(self.args.num_episodes):
            print(f"======Running episode {i}=====")
            step_results = self.env.step([[0, 0]])  # Take 0,0 step
            global_steps = 0
            self.bk = ""  # Reset bk each episode
            while not self.episode_over(step_results[2]):
                data = preprocess(step_results)
                ground_atoms = self.grounder(data["t"]["objects"])
                self.bk += ground_atoms
                answer_sets = self.logic()
                macro_action = self.macro_processing(answer_sets)
                if macro_action is None:
                    self.rotate(step_results)
                    global_steps += 50
                    continue
                step_results, micro_step, success = self.take_macro_step(
                    self.env, step_results, macro_action
                )
                global_steps += micro_step
            nl_success = "Success" if success else "Failure"
            print(f"Episode was a {nl_success}")
            success_count += success

        print(
            f"Final results: {success_count}/{self.args.num_episodes} episodes were completed successfully"
        )
