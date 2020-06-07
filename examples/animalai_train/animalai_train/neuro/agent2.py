import torch
import numpy as np

from animalai_train.neuro.pipeline import FeatureExtractor as FE

# The Network class inherits the torch.nn.Module class, which represents a neural network.
class Network(torch.nn.Module):

    # The class initialisation function. This takes as arguments the dimension of the network's input (i.e. the dimension of the state), and the dimension of the network's output (i.e. the dimension of the action).
    def __init__(self, input_dimension, output_dimension):
        # Call the initialisation function of the parent class.
        super(Network, self).__init__()
        # Define the network layers. This example network has two hidden layers, each with 100 units.
        self.layer_1 = torch.nn.Linear(in_features=input_dimension, out_features=100)
        self.layer_2 = torch.nn.Linear(in_features=100, out_features=100)
        self.output_layer = torch.nn.Linear(in_features=100, out_features=output_dimension)

    # Function which sends some input data through the network and returns the network's output. In this example, a ReLU activation function is used for both hidden layers, but the output layer has no activation function (it is just a linear layer).
    def forward(self, input):
        layer_1_output = torch.nn.functional.relu(self.layer_1(input))
        layer_2_output = torch.nn.functional.relu(self.layer_2(layer_1_output))
        output = self.output_layer(layer_2_output)
        return output


# The DQN class determines how to train the above neural network.
class DQN:

    # The class initialisation function.
    def __init__(self, cfg):
        # Contains all the cfg with hyperparameters
        self.cfg = cfg
        # Create a Q-network, which predicts the q-value for a particular state.
        self.q_network = Network(input_dimension=21, output_dimension=6)
        # Create target network
        self.t_network = Network(input_dimension=21, output_dimension=6)
        # Define the optimiser which is used when updating the Q-network. The learning rate determines how big each gradient step is during backpropagation.
        self.optimiser = torch.optim.Adam(self.q_network.parameters(), lr=cfg['learning_rate'])


    # Update t netowrk by copying weights of q to t netowrk
    def update_t_network(self):
        q_weights = self.q_network.state_dict()
        t_weights = self.t_network.load_state_dict(q_weights)

    # Function that is called whenever we want to train the Q-network. Each call to this function takes in a transition tuple containing the data we use to update the Q-network.
    def train_q_network(self, transition):
        # Set all the gradients stored in the optimiser to zero.
        self.optimiser.zero_grad()
        # Calculate the loss for this transition.
        loss = self._calculate_loss(transition)
        # Compute the gradients based on this loss, i.e. the gradients of the loss with respect to the Q-network parameters.
        loss.backward()
        # Take one gradient step to update the Q-network.
        self.optimiser.step()
        # Return the loss as a scalar
        return loss.item()

    # Function to calculate the loss for a particular transition.
    def _calculate_loss(self, transition):
        # Convert all transition variables into tensor columns
        tensors = [
                    torch.tensor([
                        i[col] for i in transition
                        ]) for col in range(0,4)
                ]
        state, action, reward, next_state = tensors

        # Reshape appropriately
        action = action.unsqueeze(1)
        reward = reward.reshape(-1, 1)

        # Q(s,a) q network predictions
        s_network_prediction = self.q_network.forward(state).gather(1, action)
        # Q(s',a) target network predictions
        s_prime_network_prediction = self.t_network.forward(next_state).max(1)[0].unsqueeze(1)
        # Bellman equation
        batch_labels = (reward + self.cfg['gamma'] * s_prime_network_prediction)
        # Final loss
        loss = torch.nn.MSELoss()(s_network_prediction, batch_labels)
        return loss

    # Get detached q values
    def get_q_values(self, state):
        return self.q_network.forward(torch.tensor(state)).detach().numpy()

class ReplayBuffer:
    def __init__(self, cfg):
        self.container = []
        self.weights = np.array([], dtype=np.float32)
        self.eps = cfg['eps']
        self.alpha = cfg['alpha']

    # Return size of replay buffer
    def __len__(self):
        return len(self.container)

    # Append new transition to replay buffer
    def append(self, transition):
        self.container.append(transition)
        # Initialise new weights with the max weight from the weights array
        if len(self.weights)!=0:
            self.weights = np.append(self.weights, max(self.weights))
        # If this is the first transition, initialise first weight with eps
        else:
            self.weights = np.append(self.weights, self.eps)

    # Completely random sample
    def sample(self, batch_size):
        cont = np.array(self.container)
        idx = np.random.choice(len(self.container), batch_size)
        sample = cont[idx]
        return sample

    # Update batch weights with new losses calculated during training
    def update_weights(self, idx, loss):
        self.weights[idx] = np.ones(len(idx))*(abs(loss)+self.eps)

    # Retrieve weighted sample from replay buffer
    def weighted_sample(self, batch_size):
        # Size of replay buffer
        total_range = range(len(self))
        # These need to be arrays for advanced indexing
        container = np.array(self.container)
        # Augment weights with small number eps and scale importance of prioritised sampling by alpha
        scaled_weights = (self.weights+self.eps)**self.alpha
        # Normalise weights
        p = (scaled_weights)/np.sum(scaled_weights)
        # Get random weighted sample indices
        sample_idxs = np.random.choice(total_range, p=p, size=batch_size)
        # Populate new tranisition batch with weighted indices 
        sample = container[sample_idxs]
        return sample, sample_idxs

class Agent:

    # Function to initialise the agent
    def __init__(self, cfg):
        # Reset the total number of steps which the agent has taken
        self.num_steps_taken = 0
        # The state variable stores the latest state of the agent in the environment
        self.state = None
        # The action variable stores the latest action which the agent has applied to the environment
        self.action = None
        # Config dictionary
        self.cfg = cfg
        # Transition history replay buffer
        self.rb = ReplayBuffer(self.cfg['buffer'])
        # DQN
        self.dqn = DQN(self.cfg['dqn'])
        # Image feature extractor
        self.fe = FE()

        # Tracker variable initialisation
        self.e = 1 # epsilon
        self.reached_goal = False # Whether the goal has been reached
        self.reach_goal_under_100 = 0 # How many times the goal has been reached in under 100 steps
        self.try_greedy = False # Boolean indicating whether its time to try greedy policy

    # Function to check whether the agent has reached the end of an episode
    def has_finished_episode(self):

        # Try a completely greedy policy and stop training if reaching the goal in under 100 steps
        if self.try_greedy:

            if (self.num_steps_taken>100)|(self.reached_goal):
                # Greedy was successful, freeze dqn and stop training
                if (self.num_steps_taken<100)&(self.reached_goal):
                    self.try_greedy = True
                else: # Unsuccessful greedy, keep training
                    self.try_greedy = False
                # Reset counters
                self.num_steps_taken = 0
                self.reach_goal_under_100=0
                return True
            else: # Greedy was unsuccessful, keep training
                return False


        # Episode length reached, restart episode
        if (self.num_steps_taken % self.cfg['episode_length'] == 0):
            # Reset counters
            self.num_steps_taken = 0
            return True

        # Goal reached, restart episode
        elif self.reached_goal:
            # Progressively increase delta based on how fast agent reaches goal
            if self.num_steps_taken<100:
                self.reach_goal_under_100+=1
                self.cfg['delta'] += 5e-5 # Increase delta 
                self.cfg['episode_length'] = 150 # Set lower episode length
            else:
                self.reach_goal_under_100=0
                if self.num_steps_taken<200:
                    self.cfg['delta'] += 5e-6 # Increase delta
                    self.cfg['episode_length'] = 250 # Set lower episode length

                elif self.num_steps_taken<400:
                    self.cfg['delta'] += 5e-7 # Increase delta
                    self.cfg['episode_length'] = 450 # Set lower episode length

            # Reset counters
            self.num_steps_taken = 0
            return True
        else: # Episode not over, keep training

            return False

    # Function to get the next action, using whatever method you like
    def get_next_action(self, state):

        # Pure greedy policy run, return greedy action
        if self.try_greedy:
            action = self.get_greedy_action(state)
            self.num_steps_taken+=1
            return action

        # Use e_greedy policy to get action
        p = [self.e, 1-self.e] #random, greedy
        greedy_action = self.get_greedy_action(state)
        rand_a1 = np.random.choice([0,1,2])
        rand_a2 = np.random.choice([0,1,2])
        a1 = np.random.choice([rand_a1,greedy_action], p=p)
        a2 = np.random.choice([rand_a2,greedy_action], p=p)

        # Update the number of steps which the agent has taken
        self.num_steps_taken += 1
        # Store the state; this will be used later, when storing the transition
        self.state = state
        # Store the action; this will be used later, when storing the transition
        self.action = (a1, a2)
        return self.action

    # Function to process the consequences of self.action
    def process_state_action(self, next_state, reward, done):

        # Process observations
        # img, speed = next_state
        # features = self.fe.run(img)

        # Update reached goal boolean
        if done:
            self.reached_goal = True

        # Skip the rest of function, we don't want to train network when running greedy policy
        if self.try_greedy:
            return

        # Create a transition
        transition = (self.state, self.action, reward, next_state)
        # Send transition through training process
        self.learn(transition)

    # Returns the action with the highest Q-value
    def get_greedy_action(self, state):
        # Returns the action with the highest Q-value
        q_values = self.dqn.get_q_values(state)
        a1 = np.argmax(q_values[:3]) # returns 0,1,2 motion
        a2 = np.argmax(q_values[3:]) # returns 0,1,2 rotation
        return (a1,a2)

    # Updates the t network weights to equal the q netowork weights
    def update_t_network(self):
        if self.num_steps_taken % self.cfg['t_network_update_rate']==0:
            self.dqn.update_t_network()

    # High level method dealing with all the learning of the agent
    def learn(self, transition):

        # Add single new transition to replay buffer
        self.rb.append(transition)

        # Check if mini_batch is big enough to start training
        if len(self.rb)<self.cfg['batch_size']:
            return

        # Update t network if appropriate
        self.update_t_network()

        # Sample mini_batch with prioritised replay
        mini_batch, idx = self.rb.weighted_sample(self.cfg['batch_size'])

        # Train network on mini batch
        loss = self.dqn.train_q_network(mini_batch)

        # Update transition weights in buffer according to loss
        self.rb.update_weights(idx, loss)

        # Decay epsilon after every step
        if self.e<0.1: # Different decay for last episodes 
            # If we are consistently reaching the goal in under 100 steps,
            # try a greedy policy on the next run
            if self.reach_goal_under_100>=1:
                self.try_greedy = True
            else:
                # Decay epsilon more slowly than before to enhance convergence
                self.e = self.e-self.cfg['slow_delta']
                # Don't allow epsilon to fall under 0
                if self.e<0:
                    self.e = 0.01
        else: # Decay epsilon as usual
            self.e = self.e - self.cfg['delta']





