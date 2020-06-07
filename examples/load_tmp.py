import sys
import random
import os
from typing import List
from animalai.envs.arena_config import ArenaConfig
from animalai.envs.environment import AnimalAIEnvironment

"""

"""


def load_config_and_play(configurations: List[str]) -> None:
    """
    Loads a configuration file for a single arena and lets you play manually
    :param configuration_file: str path to the yaml configuration
    :return: None
    """
    env_path = "env/AnimalAI"
    # for configuration in configurations:
    port =5005 + random.randint(
                0, 10
            )
    new_configurations = []
    for conf in configurations:
        with open(conf,'r') as f:
            if 'Cardbox' in f.read():
                new_configurations.append(conf)
    # for cat in range(10,11):
    #     for exp in range(18,31):
    for configuration in new_configurations:
        try:
            port+=random.randint(0, 10) # use a random port to allow relaunching the script rapidly
            # configuration = ArenaConfig(configuration_file)

            competition_folder = "../competition_configurations/"
            # configuration = competition_folder+f'{cat}-{exp}-1.yml'

            environment = AnimalAIEnvironment(
                file_name=env_path,
                base_port=port,
                arenas_configurations=ArenaConfig(configuration),
                play=True,
            )
            # print(f'{cat}-{exp}-1.yml')
            print(configuration)
            input()
            environment.close()
        except AttributeError:
            pass
        # try:
        #     print(configuration)
        #     while environment.proc1:
        #         pass
        # except KeyboardInterrupt:
        #     environment.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        configuration_file = sys.argv[1]
    else:
        competition_folder = "../competition_configurations/"
        configuration_files = os.listdir(competition_folder)
        full_confs = [competition_folder + conf for conf in configuration_files if "1.yml" in conf]
        load_config_and_play(configurations=full_confs)
        # configuration_random = random.randint(0, len(configuration_files))
