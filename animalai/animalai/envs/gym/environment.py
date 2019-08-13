import logging
from PIL import Image
import itertools
import gym
import numpy as np
from animalai.envs import UnityEnvironment
from gym import error, spaces


class UnityGymException(error.Error):
    """
    Any error related to the gym wrapper of ml-agents.
    """
    pass


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gym_unity")


class AnimalAIEnv(gym.Env):
    """
    Provides Gym wrapper for Unity Learning Environments.
    Multi-agent environments use lists for object types, as done here:
    https://github.com/openai/multiagent-particle-envs
    """

    def __init__(self,
                 environment_filename: str,
                 worker_id=0,
                 docker_training=False,
                 n_arenas=1,
                 seed=0,
                 arenas_configurations=None,
                 greyscale=False,
                 retro=True,
                 inference=False,
                 resolution=None):
        """
        Environment initialization
        :param environment_filename: The UnityEnvironment path or file to be wrapped in the gym.
        :param worker_id: Worker number for environment.
        :param docker_training: Whether this is running within a docker environment and should use a virtual
            frame buffer (xvfb).
        :param n_arenas: number of arenas to create in the environment (one agent per arena)
        :param arenas_configurations: an ArenaConfig to configure the items present in each arena, will spawn random
            objects randomly if not provided
        :param greyscale: whether the visual observations should be grayscaled or not
        :param retro: Resize visual observation to 84x84 (int8) and flattens action space.
        """
        self._env = UnityEnvironment(file_name=environment_filename,
                                     worker_id=worker_id,
                                     seed=seed,
                                     docker_training=docker_training,
                                     n_arenas=n_arenas,
                                     arenas_configurations=arenas_configurations,
                                     inference=inference,
                                     resolution=resolution)
        self.name = 'aaio'
        self.vector_obs = None
        self.inference = inference
        self.resolution = resolution
        self._current_state = None
        self._n_agents = None
        self._flattener = None
        self._greyscale = greyscale or retro
        # self._seed = None
        self.retro = retro
        self.game_over = False  # Hidden flag used by Atari environments to determine if the game is over
        self.arenas_configurations = arenas_configurations

        self.flatten_branched = self.retro
        self.uint8_visual = self.retro

        # Check brain configuration
        if len(self._env.brains) != 1:
            raise UnityGymException(
                "There can only be one brain in a UnityEnvironment "
                "if it is wrapped in a gym.")
        self.brain_name = self._env.external_brain_names[0]
        brain = self._env.brains[self.brain_name]

        if brain.number_visual_observations == 0:
            raise UnityGymException("Environment provides no visual observations.")

        if brain.num_stacked_vector_observations != 1:
            raise UnityGymException("Environment provides no vector observations.")

        # Check for number of agents in scene.
        initial_info = self._env.reset(arenas_configurations=arenas_configurations)[self.brain_name]
        self._check_agents(len(initial_info.agents))

        if self.retro and self._n_agents > 1:
            raise UnityGymException("Only one agent is allowed in retro mode, set n_agents to 1.")

        # Set observation and action spaces
        if len(brain.vector_action_space_size) == 1:
            self._action_space = spaces.Discrete(brain.vector_action_space_size[0])
        else:
            if self.flatten_branched:
                self._flattener = ActionFlattener(brain.vector_action_space_size)
                self._action_space = self._flattener.action_space
            else:
                self._action_space = spaces.MultiDiscrete(brain.vector_action_space_size)

        # high = np.array([np.inf] * brain.vector_observation_space_size)
        self.action_meanings = brain.vector_action_descriptions

        # if self.visual_obs:
        if self._greyscale:
            depth = 1
        else:
            depth = 3

        if self.retro:
            image_space_max = 255
            image_space_dtype = np.uint8
            camera_height = 84
            camera_width = 84

            image_space = spaces.Box(
                0, image_space_max,
                dtype=image_space_dtype,
                shape=(camera_height, camera_width, depth)
            )

            self._observation_space = image_space
        else:
            image_space_max = 1.0
            image_space_dtype = np.float32
            camera_height = brain.camera_resolutions[0]["height"]
            camera_width = brain.camera_resolutions[0]["width"]
            max_float = np.finfo(np.float32).max

            image_space = spaces.Box(
                0, image_space_max,
                dtype=image_space_dtype,
                shape=(self._n_agents, camera_height, camera_width, depth)
            )
            vector_space = spaces.Box(-max_float, max_float,
                                      shape=(self._n_agents, brain.vector_observation_space_size))
            self._observation_space = spaces.Tuple((image_space, vector_space))

    def reset(self, arenas_configurations=None):
        """Resets the state of the environment and returns an initial observation.
        In the case of multi-agent environments, this is a list.
        Returns: observation (object/list): the initial observation of the
            space.
        """
        info = self._env.reset(arenas_configurations=arenas_configurations)[self.brain_name]
        n_agents = len(info.agents)
        self._check_agents(n_agents)
        self.game_over = False

        if self._n_agents == 1:
            obs, reward, done, info = self._single_step(info)
        else:
            obs, reward, done, info = self._multi_step(info)
        return obs

    def step(self, action):
        """Run one timestep of the environment's dynamics. When end of
        episode is reached, you are responsible for calling `reset()`
        to reset this environment's state.
        Accepts an action and returns a tuple (observation, reward, done, info).
        In the case of multi-agent environments, these are lists.
        Args:
            action (object/list): an action provided by the environment
        Returns:
            observation (object/list): agent's observation of the current environment
            reward (float/list) : amount of reward returned after previous action
            done (boolean/list): whether the episode has ended.
            info (dict): contains auxiliary diagnostic information, including BrainInfo.
        """

        # Use random actions for all other agents in environment.
        if self._n_agents > 1:
            if not isinstance(action, list):
                raise UnityGymException("The environment was expecting `action` to be a list.")
            if len(action) != self._n_agents:
                raise UnityGymException(
                    "The environment was expecting a list of {} actions.".format(self._n_agents))
            else:
                if self._flattener is not None:
                    # Action space is discrete and flattened - we expect a list of scalars
                    action = [self._flattener.lookup_action(_act) for _act in action]
                action = np.array(action)
        else:
            if self._flattener is not None:
                # Translate action into list
                action = self._flattener.lookup_action(action)

        info = self._env.step(action)[self.brain_name]
        n_agents = len(info.agents)
        self._check_agents(n_agents)
        self._current_state = info

        if self._n_agents == 1:
            obs, reward, done, info = self._single_step(info)
            self.game_over = done
        else:
            obs, reward, done, info = self._multi_step(info)
            self.game_over = all(done)
        return obs, reward, done, info

    def _single_step(self, info):

        self.visual_obs = self._preprocess_single(info.visual_observations[0][0, :, :, :])
        self.vector_obs = info.vector_observations[0]

        if self._greyscale:
            self.visual_obs = self._greyscale_obs_single(self.visual_obs)

        if self.retro:
            self.visual_obs = self._resize_observation(self.visual_obs)
            default_observation = self.visual_obs
        else:
            default_observation = self.visual_obs, self.vector_obs

        return default_observation, info.rewards[0], info.local_done[0], {
            "text_observation": info.text_observations[0],
            "brain_info": info}

    def _preprocess_single(self, single_visual_obs):
        if self.uint8_visual:
            return (255.0 * single_visual_obs).astype(np.uint8)
        else:
            return single_visual_obs

    def _multi_step(self, info):

        self.visual_obs = self._preprocess_multi(info.visual_observations)
        self.vector_obs = info.vector_observations

        if self._greyscale:
            self.visual_obs = self._greyscale_obs_multi(self.visual_obs)

        default_observation = self.visual_obs

        return list(default_observation), info.rewards, info.local_done, {
            "text_observation": info.text_observations,
            "brain_info": info}

    def _preprocess_multi(self, multiple_visual_obs):
        if self.uint8_visual:
            return [(255.0 * _visual_obs).astype(np.uint8) for _visual_obs in multiple_visual_obs]
        else:
            return multiple_visual_obs

    def render(self, mode='rgb_array'):
        return self.visual_obs

    def close(self):
        """Override _close in your subclass to perform any necessary cleanup.
        Environments will automatically close() themselves when
        garbage collected or when the program exits.
        """
        self._env.close()

    def get_action_meanings(self):
        return self.action_meanings

    def seed(self, seed=None):
        """Sets the seed for this env's random number generator(s).
        Currently not implemented.
        """
        logger.warning("Could not seed environment %s", self.name)
        return

    @staticmethod
    def _resize_observation(observation):
        """
        Re-sizes visual observation to 84x84
        """
        obs_image = Image.fromarray(observation)
        obs_image = obs_image.resize((84, 84), Image.NEAREST)
        return np.array(obs_image)

    def _greyscale_obs_single(self, obs):
        new_obs = np.floor(np.expand_dims(np.mean(obs, axis=2), axis=2)).squeeze().astype(np.uint8)
        return new_obs

    def _greyscale_obs_multi(self, obs):
        new_obs = [np.floor(np.expand_dims(np.mean(o, axis=2), axis=2)).squeeze().astype(np.uint8) for o in obs]
        return new_obs

    def _check_agents(self, n_agents):
        # if n_agents > 1:
        #     raise UnityGymException(
        #         "The environment was launched as a single-agent environment, however"
        #         "there is more than one agent in the scene.")
        # elif self._multiagent and n_agents <= 1:
        #     raise UnityGymException(
        #         "The environment was launched as a mutli-agent environment, however"
        #         "there is only one agent in the scene.")
        if self._n_agents is None:
            self._n_agents = n_agents
            logger.info("{} agents within environment.".format(n_agents))
        elif self._n_agents != n_agents:
            raise UnityGymException("The number of agents in the environment has changed since "
                                    "initialization. This is not supported.")

    @property
    def metadata(self):
        return {'render.modes': ['rgb_array']}

    @property
    def reward_range(self):
        return -float('inf'), float('inf')

    @property
    def spec(self):
        return None

    @property
    def action_space(self):
        return self._action_space

    @property
    def observation_space(self):
        return self._observation_space

    @property
    def number_agents(self):
        return self._n_agents


class ActionFlattener:
    """
    Flattens branched discrete action spaces into single-branch discrete action spaces.
    """

    def __init__(self, branched_action_space):
        """
        Initialize the flattener.
        :param branched_action_space: A List containing the sizes of each branch of the action
        space, e.g. [2,3,3] for three branches with size 2, 3, and 3 respectively.
        """
        self._action_shape = branched_action_space
        self.action_lookup = self._create_lookup(self._action_shape)
        self.action_space = spaces.Discrete(len(self.action_lookup))

    @classmethod
    def _create_lookup(self, branched_action_space):
        """
        Creates a Dict that maps discrete actions (scalars) to branched actions (lists).
        Each key in the Dict maps to one unique set of branched actions, and each value
        contains the List of branched actions.
        """
        possible_vals = [range(_num) for _num in branched_action_space]
        all_actions = [list(_action) for _action in itertools.product(*possible_vals)]
        # Dict should be faster than List for large action spaces
        action_lookup = {_scalar: _action for (_scalar, _action) in enumerate(all_actions)}
        return action_lookup

    def lookup_action(self, action):
        """
        Convert a scalar discrete action into a unique set of branched actions.
        :param: action: A scalar value representing one of the discrete actions.
        :return: The List containing the branched actions.
        """
        return self.action_lookup[action]
