import time
import numpy as np

from animalai.envs import UnityEnvironment
from animalai.envs.exception import UnityEnvironmentException
from animalai.envs.arena_config import ArenaConfig

from animalai_train.neuro.agent import Agent

import random

env_path = '../env/AnimalAI'
worker_id = random.randint(1, 100)
arena_config = ArenaConfig('configs/1-Food.yaml')
run_id = f'neuro_{worker_id}'
model_path = f'./models/{run_id}'
save_freq = 5000
trainer_config = {
            'episode_length': 1000,
            'batch_size': 128,
            't_network_update_rate': 50,
            'dqn': {
                'gamma':0.9,
                'learning_rate': 0.001
            },
            'delta': 3e-5,
            'slow_delta': 2e-5, # For when epsilon is under 0.1
            'buffer': {
                'alpha': 0.7,
                'eps': 10e-4
            }
        }

def create_env():
    env = AnimalAIEnv(environment_filename=env_path,
                  worker_id=worker_id,
                  n_arenas=1,
                  arenas_configurations=arena_config,
                  docker_training=False,
                  retro=False,
                    seed=seed,
                     greyscale=False)
    return env

def create_agent(sess, env, summary_writer):
    return Agent()

# Main entry point
if __name__ == "__main__":

    # Create a random environment
    environment = create_env()

    # Create an agent
    agent = create_agent()

    # Get the initial state
    state = environment.step({'Learner':(0,0)})

    # Determine the time at which training will stop, i.e. in 10 minutes (600 seconds) time
    start_time = time.time()
    end_time = start_time + 600

    # Train the agent, until the time is up
    try:
        while time.time() < end_time:
            # If the action is to start a new episode, then reset the state
            # if agent.has_finished_episode():
            #     state = environment.init_state
            # Get the action from the agent
            action = agent.get_next_action(state)
            # Get the next state and info from env
            obs, reward, done, info = environment.step({'Learner':action})
            # Return this to the agent
            agent.process_state_action(obs, reward, done)
            # Set what the new state is
            state = next_state
            # Optionally, show the environment


    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        print(agent.rb.weights)
        np.save('weights.npy',agent.rb.weights)
        pass

    np.save('weights_out.npy',agent.rb.weights)
    # Test the agent for 100 steps, using its greedy policy
    state = environment.init_state
    has_reached_goal = False
    display_on = True
    # Test the agent for 100 steps, using its greedy policy
    state = environment.init_state
    has_reached_goal = False
    for step_num in range(100):
        action = agent.get_greedy_action(state)
        next_state, distance_to_goal = environment.step(action)
        # The agent must achieve a maximum distance of 0.03 for use to consider it "reaching the goal"
        if distance_to_goal < 0.03:
            has_reached_goal=True
            break
        state = next_state

    # Print out the result
    if has_reached_goal:
        print('Reached goal in ' + str(step_num) + ' steps.')
    else:
        print('Did not reach goal. Final distance = ' + str(distance_to_goal))

    environment.close()