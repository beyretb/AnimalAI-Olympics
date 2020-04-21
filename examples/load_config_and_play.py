from animalai.envs.arena_config import ArenaConfig
from animalai.envs.environment import AnimalAIEnvironment

env_path = "env/aaio"
port = 5005
configuration_file = "configurations/arena_configurations/hard/3-28-1.yml"
configuration = ArenaConfig(configuration_file)

environment = AnimalAIEnvironment(
    file_name=env_path,
    base_port=port,
    arenas_configurations=configuration,
    play=True
)

try:
    while environment.proc1:
        continue
except KeyboardInterrupt:
    pass
finally:
    environment.close()
