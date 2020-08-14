import sys

sys.path.insert(0, "/Users/ludo/Desktop/animalai/animalai/animalai_train")
sys.path.insert(1, "/Users/ludo/Desktop/animalai/animalai/animalai")

from animalai.envs.gym.environment import AnimalAIGym
from centroidtracker import CentroidTracker

from macro_action import MacroAction
from logic import Logic
from utils import preprocess, object_types


class Pipeline:
    def __init__(self, args):
        self.args = args
        self.ct = None
        self.gg_id = 0
        env_path = args.env
        worker_id = 1
        seed = 2
        self.arenas = args.arena_config
        # ac = ArenaConfig(arena_path)
        # Load Unity environment based on config file with Gym or ML agents wrapper
        self.env = AnimalAIGym(
            environment_filename=env_path,
            worker_id=worker_id,
            n_arenas=1,
            arenas_configurations=self.arenas[0],
            seed=seed,
            grayscale=False,
            inference=args.inference
        )
        self.logic = Logic()

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

    def take_macro_step(self, env, state, step_results, macro_action):
        ma = MacroAction(env, self.ct, state, step_results, macro_action)
        # print(f"Initiating macro_action: {macro_action['initiate']}")
        step_results, state, macro_stats, micro_step = ma.run()
        # print(f"Results: {self.format_macro_results(macro_stats)}")
        return step_results, state, micro_step, macro_stats["success"]

    def episode_over(self, done):
        if done:
            return True
        return False


    def run(self):
        success_count = 0
        for idx in range(self.args.num_episodes):
            self.env.reset(self.arenas[0])
        # for idx,arena in enumerate(self.arenas):
        #     self.env.reset(arena)
            print(f"======Running episode {idx}=====")
            step_results = self.env.step([[0, 0]])  # Take 0,0 step
            global_steps = 0
            macro_step = 0
            self.ct = {ot: CentroidTracker() for ot in object_types} # Initialise tracker
            actions_buffer = []
            observables_buffer = []
            while not self.episode_over(step_results[2]):
                if global_steps >= 1000:
                    success = False
                    print("Exceeded max global steps")
                    break
                state = preprocess(self.ct, step_results, global_steps)
                macro_action, observables = self.logic.run(macro_step, state)
                step_results, state, micro_step, success = self.take_macro_step(
                    self.env, state, step_results, macro_action
                )
                global_steps += micro_step
                macro_step +=1
                actions_buffer.append(macro_action['raw'][0])
                observables_buffer.append(observables)
            self.logic.update_examples(observables_buffer, actions_buffer, success)
            nl_success = "Success" if success else "Failure"
            print(f"Episode was a {nl_success}")
            success_count += success

        print(
            f"Final results: {success_count}/{self.args.num_episodes} episodes were completed successfully"
        )
