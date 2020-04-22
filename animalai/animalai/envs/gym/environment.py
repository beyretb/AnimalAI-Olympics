import numpy as np
from gym import spaces
from typing import Union, List

from gym_unity.envs import (
    UnityEnv,
    UnityGymException,
    GymStepResult,
    AgentIdIndexMapper,
    BatchedStepResult,
    ActionFlattener,
    logger,
)

from animalai.envs.environment import AnimalAIEnvironment
from animalai.envs.arena_config import ArenaConfig


class AnimalAIGym(UnityEnv):
    def __init__(
        self,
        environment_filename: str,
        worker_id: int = 0,
        uint8_visual: bool = False,
        flatten_branched: bool = False,
        n_arenas: int = 1,
        seed: int = 0,
        inference: bool = False,
        grayscale: bool = False,
        arenas_configurations: ArenaConfig = None,
    ):
        """
        Environment initialization
        :param environment_filename: The UnityEnvironment path or file to be wrapped in the gym.
        :param worker_id: Worker number for environment.
        :param use_visual: Whether to use visual observation or vector observation.
        :param uint8_visual: Return visual observations as uint8 (0-255) matrices instead of float (0.0-1.0).
        :param multiagent: Whether to run in multi-agent mode (lists of obs, reward, done).
        :param flatten_branched: If True, turn branched discrete action spaces into a Discrete space rather than
            MultiDiscrete.
        :param no_graphics: Whether to run the Unity simulator in no-graphics mode
        :param allow_multiple_visual_obs: If True, return a list of visual observations instead of only one.
        """
        base_port = 5005
        if environment_filename is None:
            base_port = AnimalAIEnvironment.DEFAULT_EDITOR_PORT

        self._env = AnimalAIEnvironment(
            file_name=environment_filename,
            worker_id=worker_id,
            base_port=base_port,
            seed=seed,
            n_arenas=n_arenas,
            inference=inference,
            arenas_configurations=arenas_configurations,
            grayscale=grayscale,
        )

        # Take a single step so that the brain information will be sent over
        if not self._env.get_agent_groups():
            self._env.step()

        self.visual_obs = None
        self._n_agents = -1

        self.agent_mapper = AgentIdIndexMapper()

        # Save the step result from the last time all Agents requested decisions.
        self._previous_step_result: BatchedStepResult = None
        self._multiagent = n_arenas > 1
        self._flattener = None
        # Hidden flag used by Atari environments to determine if the game is over
        self.game_over = False
        self._allow_multiple_visual_obs = n_arenas > 1

        # Check brain configuration
        if len(self._env.get_agent_groups()) != 1:
            raise UnityGymException(
                "There can only be one brain in a UnityEnvironment "
                "if it is wrapped in a gym."
            )

        self.brain_name = self._env.get_agent_groups()[0]
        self.name = self.brain_name
        self.group_spec = self._env.get_agent_group_spec(self.brain_name)

        if self._get_n_vis_obs() == 0:
            raise UnityGymException(
                "`use_visual` was set to True, however there are no"
                " visual observations as part of this environment."
            )
        self.use_visual = self._get_n_vis_obs() >= 1
        self.uint8_visual = uint8_visual

        # Check for number of agents in scene.
        self._env.reset()
        step_result = self._env.get_step_result(self.brain_name)
        self._check_agents(step_result.n_agents())
        self._previous_step_result = step_result
        self.agent_mapper.set_initial_agents(list(self._previous_step_result.agent_id))

        # Set observation and action spaces
        if self.group_spec.is_action_discrete():
            branches = self.group_spec.discrete_action_branches
            if self.group_spec.action_shape == 1:
                self._action_space = spaces.Discrete(branches[0])
            else:
                if flatten_branched:
                    self._flattener = ActionFlattener(branches)
                    self._action_space = self._flattener.action_space
                else:
                    self._action_space = spaces.MultiDiscrete(branches)

        else:
            if flatten_branched:
                logger.warning(
                    "The environment has a non-discrete action space. It will "
                    "not be flattened."
                )
            high = np.array([1] * self.group_spec.action_shape)
            self._action_space = spaces.Box(-high, high, dtype=np.float32)
        high = np.array([np.inf] * self._get_vec_obs_size())
        if self.use_visual:
            shape = self._get_vis_obs_shape()
            if uint8_visual:
                self._observation_space = spaces.Box(
                    0, 255, dtype=np.uint8, shape=shape
                )
            else:
                self._observation_space = spaces.Box(
                    0, 1, dtype=np.float32, shape=shape
                )

        else:
            self._observation_space = spaces.Box(-high, high, dtype=np.float32)

    def reset(
        self, arenas_configurations: ArenaConfig = None
    ) -> Union[List[np.ndarray], np.ndarray]:
        """Resets the state of the environment and returns an initial observation.
        In the case of multi-agent environments, this is a list.
        Returns: observation (object/list): the initial observation of the
        space.
        """
        step_result = self._step(True, arenas_configurations=arenas_configurations)
        n_agents = step_result.n_agents()
        self._check_agents(n_agents)
        self.game_over = False

        if not self._multiagent:
            res: GymStepResult = self._single_step(step_result)
        else:
            res = self._multi_step(step_result)
        return res[0]

    def _step(
        self, needs_reset: bool = False, arenas_configurations: ArenaConfig = None
    ) -> BatchedStepResult:
        if needs_reset:
            self._env.reset(arenas_configurations=arenas_configurations)
        else:
            self._env.step()
        info = self._env.get_step_result(self.brain_name)
        # Two possible cases here:
        # 1) all agents requested decisions (some of which might be done)
        # 2) some Agents were marked Done in between steps.
        # In case 2,  we re-request decisions until all agents request a real decision.
        while info.n_agents() - sum(info.done) < self._n_agents:
            if not info.done.all():
                raise UnityGymException(
                    "The environment does not have the expected amount of agents. "
                    + "Some agents did not request decisions at the same time."
                )
            for agent_id, reward in zip(info.agent_id, info.reward):
                self.agent_mapper.mark_agent_done(agent_id, reward)

            self._env.step()
            info = self._env.get_step_result(self.brain_name)
        return self._sanitize_info(info)
