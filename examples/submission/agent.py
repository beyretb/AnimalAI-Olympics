import yaml
from animalai_train.trainers.ppo.policy import PPOPolicy
from animalai.envs.brain import BrainParameters


class Agent(object):

    def __init__(self):
        """
         Load your agent here and initialize anything needed
        """

        # Load the configuration and model using ABSOLUTE PATHS
        self.configuration_file = '/aaio/data/trainer_config.yaml'
        self.model_path = '/aaio/data/1-Food/Learner'

        self.brain = BrainParameters(brain_name='Learner',
                                     camera_resolutions=[{'height': 84, 'width': 84, 'blackAndWhite': False}],
                                     num_stacked_vector_observations=1,
                                     vector_action_descriptions=['', ''],
                                     vector_action_space_size=[3, 3],
                                     vector_action_space_type=0,  # corresponds to discrete
                                     vector_observation_space_size=3
                                     )
        self.trainer_params = yaml.load(open(self.configuration_file))['Learner']
        self.trainer_params['keep_checkpoints'] = 0
        self.trainer_params['model_path'] = self.model_path
        self.trainer_params['use_recurrent'] = False

        self.policy = PPOPolicy(brain=self.brain,
                                seed=0,
                                trainer_params=self.trainer_params,
                                is_training=False,
                                load=True)

    def reset(self, t=250):
        """
        Reset is called before each episode begins
        Leave blank if nothing needs to happen there
        :param t the number of timesteps in the episode
        """

    def step(self, obs, reward, done, info):
        """
        :param obs: agent's observation of the current environment
        :param reward: amount of reward returned after previous action
        :param done: whether the episode has ended.
        :param info: contains auxiliary diagnostic information, including BrainInfo.
        :return: the action to take, a list or size 2
        """

        brain_info = info['brain_info']
        action = self.policy.evaluate(brain_info=brain_info)['action']

        return action
