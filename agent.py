from animalai.envs.brain import BrainInfo


class Agent(object):

    def __init__(self):
        """
         Load your agent here and initialize anything needed
        """
        pass

    def reset(self, t=250):
        """
        Reset is called before each episode begins
        Leave blank if nothing needs to happen there
        :param t the number of timesteps in the episode
        """

    def step(self, brain_info: BrainInfo) -> list[float]:
        """
        A single step the agent should take based on the current
        :param brain_info:  a single BrainInfo containing the observations and reward for a single step for one agent
        :return:            a list of actions to execute (of size 2)
        """

        self.action = [0, 0]

        return self.action

    def destroy(self):
        pass
