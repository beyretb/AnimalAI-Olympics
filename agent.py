from animalai.envs.brain import BrainInfo

class Agent(object):

    def __init__(self, configuration_to_load: str):

        """
         Load your agent here and initialize anything needed
        :param configuration_to_load: path to your model to load
        """
        pass

    def step(self, brain_info: BrainInfo) -> list[float]:

        """
        A single step the agent should take based on the current
        :param brain_info:  a single BrainInfo containing the observations and reward for a single step for one agent
        :return:            a list of actions to execute (of size 2)
        """

        self.action = []

        return self.action

    def destroy(self):

        pass
