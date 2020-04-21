from baselines import deepq
from baselines import logger

from animalai.envs.gym.environment import AnimalAIGym
from animalai.envs.arena_config import ArenaConfig

def main():
    arenas_configurations = ArenaConfig("configurations/arena_configurations/train_ml_agents_arenas.yml")
    env = AnimalAIGym(
        environment_filename="/home/ben/AnimalAI/builds-ml-agents-aaio/aaio",
        worker_id=0,
        flatten_branched=True,
        uint8_visual=True,
        arenas_configurations=arenas_configurations)
    logger.configure('./logs') # Çhange to log in a different directory
    act = deepq.learn(
        env,
        "cnn", # conv_only is also a good choice for GridWorld
        lr=2.5e-4,
        total_timesteps=1000000,
        buffer_size=50000,
        exploration_fraction=0.05,
        exploration_final_eps=0.1,
        print_freq=20,
        train_freq=5,
        learning_starts=20000,
        target_network_update_freq=50,
        gamma=0.99,
        prioritized_replay=False,
        checkpoint_freq=1000,
        checkpoint_path='./logs', # Change to save model in a different directory
        dueling=True
    )
    print("Saving model to unity_model.pkl")
    act.save("unity_model.pkl")

if __name__ == '__main__':
    main()