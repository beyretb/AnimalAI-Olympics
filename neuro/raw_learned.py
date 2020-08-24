import sys
import json

sys.path.insert(0, "/Users/ludo/Desktop/animalai/animalai/animalai_train")
sys.path.insert(1, "/Users/ludo/Desktop/animalai/animalai/animalai")

from animalai.envs.gym.environment import AnimalAIGym
from animalai.envs.arena_config import ArenaConfig
from centroidtracker import CentroidTracker

from macro_action import MacroAction
from logic import Logic
from utils import preprocess, object_types
from config import COMPETITION_CONFIGS as comp

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

    def comp_stats(self):
        pass

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

    def test_run(self):
        success_count = 0
        choice = 'random'
        for idx in range(self.args.num_episodes):
            self.env.reset(self.arenas[0])
        # for idx,arena in enumerate(self.arenas):
        #     self.env.reset(arena)
            # print(f"======Running episode {idx}=====")
            step_results = self.env.step([[0, 0]])  # Take 0,0 step
            global_steps = 0
            macro_step = 0
            self.ct = {ot: CentroidTracker() for ot in object_types} # Initialise tracker
            actions_buffer = []
            observables_buffer = []
            if (idx%30==0)&(idx!=0):
                choice = 'ilasp'
                self.logic.update_learned_lp(macro_step)

            while not self.episode_over(step_results[2]):
                if global_steps >= 1000:
                    success = False
                    print("Exceeded max global steps")
                    break
                state = preprocess(self.ct, step_results, global_steps)
                macro_action, observables = self.logic.run(
                    macro_step,
                    state,
                    choice=choice)
                # print(macro_action)
                step_results, state, micro_step, success = self.take_macro_step(
                    self.env, state, step_results, macro_action
                )
                global_steps += micro_step
                macro_step +=1
                actions_buffer.append(macro_action['raw'][0])
                observables_buffer.append(observables)


            # Update examples after every episode
            # Filter action and observable buffer based on what has already been update_learned_lp
            filtered_action_buffer = []
            filtered_observables_buffer = []
            for ma, obs in zip(actions_buffer, observables_buffer):
                if any(i in ma for i in self.logic.ilasp.macro_actions_learned):
                    continue
                else:
                    filtered_action_buffer.append(ma)
                    filtered_observables_buffer.append(obs)
            self.logic.update_examples(filtered_observables_buffer[-1:], filtered_action_buffer[-1:], success)

            nl_success = "Success" if success else "Failure"
            # print(f"Episode was a {nl_success}")
            success_count += success

        print(
            f"Final results: {success_count}/{self.args.num_episodes} episodes were completed successfully"
        )
    def test_run(self, comp_fpath:str):


        test_results = {
            k: [{
            "success":0,
            "ma": []}] for k,v in comp.items()
        }
        success_count = 0
        for cogn_trait, test_set in comp.items():
            for arena in test_set:
                ac = ArenaConfig(arena)
                self.env.reset(ac)
                step_results = self.env.step([[0, 0]])  # Take 0,0 step
                global_steps = 0
                macro_step = 0
                self.ct = {ot: CentroidTracker() for ot in object_types} # Initialise tracker
                actions_buffer = []
                observables_buffer = []
                if (idx%30==0)&(idx!=0):
                    choice = 'ilasp'
                    self.logic.update_learned_lp(macro_step)

                while not self.episode_over(step_results[2]):
                    if global_steps >= 1000:
                        success = False
                        print("Exceeded max global steps")
                        break
                    state = preprocess(self.ct, step_results, global_steps)
                    macro_action, observables = self.logic.run(
                        macro_step,
                        state,
                        choice=choice)
                    # print(macro_action)
                    step_results, state, micro_step, success = self.take_macro_step(
                        self.env, state, step_results, macro_action
                    )
                    global_steps += micro_step
                    macro_step +=1
                    actions_buffer.append(macro_action['raw'][0])
                    observables_buffer.append(observables)
                # Update examples after every episode
                if success:
                    self.logic.update_examples(observables_buffer[-1:], actions_buffer[-1:], success)
                else:
                    self.logic.update_examples(observables_buffer[-1:], actions_buffer[-1:], success)

                nl_success = "Success" if success else "Failure"
                # print(f"Episode was a {nl_success}")
                success_count += success

        print(
            f"Final results: {success_count} episodes were completed successfully"
        )
        json_dump = json.dumps(test_results)
        return test_results
