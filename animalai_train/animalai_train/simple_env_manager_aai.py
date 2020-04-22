from typing import Dict, List

from mlagents.trainers.env_manager import EnvironmentStep
from mlagents.trainers.simple_env_manager import SimpleEnvManager
from mlagents_envs.side_channel.float_properties_channel import FloatPropertiesChannel
from mlagents.trainers.action_info import ActionInfo

from animalai.envs.arena_config import ArenaConfig
from animalai.envs.environment import AnimalAIEnvironment


class SimpleEnvManagerAAI(SimpleEnvManager):
    def __init__(
        self, env: AnimalAIEnvironment, float_prop_channel: FloatPropertiesChannel
    ):
        self.shared_float_properties = float_prop_channel
        self.env = env
        self.previous_step: EnvironmentStep = EnvironmentStep.empty(0)
        self.previous_all_action_info: Dict[str, ActionInfo] = {}

    def _reset_env(self, config: ArenaConfig = None) -> List[EnvironmentStep]:
        self.env.reset(arenas_configurations=config)
        all_step_result = self._generate_all_results()
        self.previous_step = EnvironmentStep(all_step_result, 0, {})
        return [self.previous_step]
