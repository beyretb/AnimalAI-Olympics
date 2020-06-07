from unittest.mock import patch, mock_open
import pytest

from animalai.envs.environment import AnimalAIEnvironment
from animalai.envs.arena_config import ArenaConfig
from mlagents_envs.mock_communicator import MockCommunicator
from mlagents_envs.base_env import BatchedStepResult

arena_config_yaml = """
!ArenaConfig
arenas:
  0: !Arena
    pass_mark: 2
    t: 250
    items:
    - !Item
      name: GoodGoalMulti
  1: !Arena
    pass_mark: -1
    t: 250
    items:
    - !Item
      name: BadGoal
"""


@patch("animalai.envs.environment.AnimalAIEnvironment.reset")
@patch("mlagents_envs.environment.UnityEnvironment.executable_launcher")
@patch("mlagents_envs.environment.UnityEnvironment.get_communicator")
def test_basic_initialization(mock_communicator, mock_launcher, mock_reset):
    mock_communicator.return_value = MockCommunicator(
        discrete_action=True, visual_inputs=1, num_agents=32, vec_obs_size=2
    )

    env = AnimalAIEnvironment(file_name=" ", n_arenas=32, resolution=126,)
    assert env.get_agent_groups() == ["RealFakeBrain"]
    mock_launcher.assert_called_once()
    launcher_args, _ = mock_launcher.call_args
    executable_args = launcher_args[3]
    assert executable_args == [
        "--playerMode",
        "0",
        "--numberOfArenas",
        "32",
        "--resolution",
        "126",
    ]
    env.close()


@patch("animalai.envs.environment.AnimalAIEnvironment.reset")
@patch("mlagents_envs.environment.UnityEnvironment.executable_launcher")
@patch("mlagents_envs.environment.UnityEnvironment.get_communicator")
def test_play_initialization(mock_communicator, mock_launcher, mock_reset):
    mock_communicator.return_value = MockCommunicator()

    env = AnimalAIEnvironment(file_name=" ", n_arenas=1, play=True)
    mock_launcher.assert_called_once()
    launcher_args, _ = mock_launcher.call_args
    executable_args = launcher_args[3]
    assert executable_args == ["--playerMode", "1", "--numberOfArenas", "1"]
    env.close()


@patch("builtins.open", new_callable=mock_open, read_data=arena_config_yaml)
@patch("mlagents_envs.side_channel.raw_bytes_channel.RawBytesChannel.send_raw_data")
@patch("mlagents_envs.environment.UnityEnvironment.executable_launcher")
@patch("mlagents_envs.environment.UnityEnvironment.get_communicator")
def test_reset_arena_config(
    mock_communicator, mock_launcher, mock_byte_channel, mock_yaml
):
    mock_communicator.return_value = MockCommunicator(
        discrete_action=True, visual_inputs=0, num_agents=2, vec_obs_size=2
    )
    arena_config = ArenaConfig(" ")
    env = AnimalAIEnvironment(
        file_name=" ", n_arenas=2, arenas_configurations=arena_config,
    )

    mock_byte_channel.assert_called_once()
    bytes_arg = bytes(arena_config.to_proto().SerializeToString(deterministic=True))
    # we cannot call assert_called_with
    mock_byte_channel.assert_called_with(bytes_arg)

    batched_step_result = env.get_step_result("RealFakeBrain")
    spec = env.get_agent_group_spec("RealFakeBrain")
    env.close()
    assert isinstance(batched_step_result, BatchedStepResult)
    assert len(spec.observation_shapes) == len(batched_step_result.obs)
    n_agents = batched_step_result.n_agents()
    for shape, obs in zip(spec.observation_shapes, batched_step_result.obs):
        assert (n_agents,) + shape == obs.shape


if __name__ == "__main__":
    pytest.main()
