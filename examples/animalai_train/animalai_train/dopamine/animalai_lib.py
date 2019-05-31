# coding=utf-8
# Copyright 2018 The Dopamine Authors.
# Modifications copyright 2019 Unity Technologies.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Obstacle Tower-specific utilities including Atari-specific network architectures.

This includes a class implementing minimal preprocessing, which
is in charge of:
  . Converting observations to greyscale.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math

from animalai.envs.gym.environment import AnimalAIEnv

import numpy as np
import tensorflow as tf

import gin.tf
import cv2

slim = tf.contrib.slim

NATURE_DQN_OBSERVATION_SHAPE = (84, 84)  # Size of downscaled Atari 2600 frame.
NATURE_DQN_DTYPE = tf.uint8  # DType of Atari 2600 observations.
NATURE_DQN_STACK_SIZE = 4  # Number of frames in the state stack.


@gin.configurable
def create_animalai_environment(environment_path=None):
    """Wraps the Animal AI environment with some basic preprocessing.

    Returns:
      An Animal AI environment with some standard preprocessing.
    """
    assert environment_path is not None
    env = AnimalAIEnv(environment_path, 0, n_arenas=1, retro=True)
    env = OTCPreprocessing(env)
    return env

@gin.configurable
def nature_dqn_network(num_actions, network_type, state):
    """The convolutional network used to compute the agent's Q-values.

    Args:
      num_actions: int, number of actions.
      network_type: namedtuple, collection of expected values to return.
      state: `tf.Tensor`, contains the agent's current state.

    Returns:
      net: _network_type object containing the tensors output by the network.
    """
    net = tf.cast(state, tf.float32)
    net = tf.div(net, 255.)
    net = slim.conv2d(net, 32, [8, 8], stride=4)
    net = slim.conv2d(net, 64, [4, 4], stride=2)
    net = slim.conv2d(net, 64, [3, 3], stride=1)
    net = slim.flatten(net)
    net = slim.fully_connected(net, 512)
    q_values = slim.fully_connected(net, num_actions, activation_fn=None)
    return network_type(q_values)

@gin.configurable
def rainbow_network(num_actions, num_atoms, support, network_type, state):
    """The convolutional network used to compute agent's Q-value distributions.

    Args:
      num_actions: int, number of actions.
      num_atoms: int, the number of buckets of the value function distribution.
      support: tf.linspace, the support of the Q-value distribution.
      network_type: namedtuple, collection of expected values to return.
      state: `tf.Tensor`, contains the agent's current state.

    Returns:
      net: _network_type object containing the tensors output by the network.
    """
    weights_initializer = slim.variance_scaling_initializer(
        factor=1.0 / np.sqrt(3.0), mode='FAN_IN', uniform=True)

    net = tf.cast(state, tf.float32)
    net = tf.div(net, 255.)
    net = slim.conv2d(
        net, 32, [8, 8], stride=4, weights_initializer=weights_initializer)
    net = slim.conv2d(
        net, 64, [4, 4], stride=2, weights_initializer=weights_initializer)
    net = slim.conv2d(
        net, 64, [3, 3], stride=1, weights_initializer=weights_initializer)
    net = slim.flatten(net)
    net = slim.fully_connected(
        net, 512, weights_initializer=weights_initializer)
    net = slim.fully_connected(
        net,
        num_actions * num_atoms,
        activation_fn=None,
        weights_initializer=weights_initializer)

    logits = tf.reshape(net, [-1, num_actions, num_atoms])
    probabilities = tf.contrib.layers.softmax(logits)
    q_values = tf.reduce_sum(support * probabilities, axis=2)
    return network_type(q_values, logits, probabilities)

@gin.configurable
def implicit_quantile_network(num_actions, quantile_embedding_dim,
                              network_type, state, num_quantiles):
    """The Implicit Quantile ConvNet.

    Args:
      num_actions: int, number of actions.
      quantile_embedding_dim: int, embedding dimension for the quantile input.
      network_type: namedtuple, collection of expected values to return.
      state: `tf.Tensor`, contains the agent's current state.
      num_quantiles: int, number of quantile inputs.

    Returns:
      net: _network_type object containing the tensors output by the network.
    """
    weights_initializer = slim.variance_scaling_initializer(
        factor=1.0 / np.sqrt(3.0), mode='FAN_IN', uniform=True)

    state_net = tf.cast(state, tf.float32)
    state_net = tf.div(state_net, 255.)
    state_net = slim.conv2d(
        state_net, 32, [8, 8], stride=4,
        weights_initializer=weights_initializer)
    state_net = slim.conv2d(
        state_net, 64, [4, 4], stride=2,
        weights_initializer=weights_initializer)
    state_net = slim.conv2d(
        state_net, 64, [3, 3], stride=1,
        weights_initializer=weights_initializer)
    state_net = slim.flatten(state_net)
    state_net_size = state_net.get_shape().as_list()[-1]
    state_net_tiled = tf.tile(state_net, [num_quantiles, 1])

    batch_size = state_net.get_shape().as_list()[0]
    quantiles_shape = [num_quantiles * batch_size, 1]
    quantiles = tf.random_uniform(
        quantiles_shape, minval=0, maxval=1, dtype=tf.float32)

    quantile_net = tf.tile(quantiles, [1, quantile_embedding_dim])
    pi = tf.constant(math.pi)
    quantile_net = tf.cast(tf.range(
        1, quantile_embedding_dim + 1, 1), tf.float32) * pi * quantile_net
    quantile_net = tf.cos(quantile_net)
    quantile_net = slim.fully_connected(quantile_net, state_net_size,
                                        weights_initializer=weights_initializer)
    # Hadamard product.
    net = tf.multiply(state_net_tiled, quantile_net)

    net = slim.fully_connected(
        net, 512, weights_initializer=weights_initializer)
    quantile_values = slim.fully_connected(
        net,
        num_actions,
        activation_fn=None,
        weights_initializer=weights_initializer)

    return network_type(quantile_values=quantile_values, quantiles=quantiles)

#
# @gin.configurable
# class AAIPreprocessing(object):
#     """A class implementing image preprocessing for OTC agents.
#
#     Specifically, this converts observations to greyscale. It doesn't
#     do anything else to the environment.
#     """
#
#     def __init__(self, environment):
#         """Constructor for an Obstacle Tower preprocessor.
#
#         Args:
#           environment: Gym environment whose observations are preprocessed.
#
#         """
#         self.environment = environment
#
#         self.game_over = False
#         self.lives = 0  # Will need to be set by reset().
#
#     @property
#     def observation_space(self):
#         return self.environment.observation_space
#
#     @property
#     def action_space(self):
#         return self.environment.action_space
#
#     @property
#     def reward_range(self):
#         return self.environment.reward_range
#
#     @property
#     def metadata(self):
#         return self.environment.metadata
#
#     def reset(self):
#         """Resets the environment. Converts the observation to greyscale,
#         if it is not.
#
#         Returns:
#           observation: numpy array, the initial observation emitted by the
#             environment.
#         """
#         observation = self.environment.reset()
#         if (len(observation.shape) > 2):
#             observation = cv2.cvtColor(observation, cv2.COLOR_RGB2GRAY)
#
#         return observation
#
#     def render(self, mode):
#         """Renders the current screen, before preprocessing.
#
#         This calls the Gym API's render() method.
#
#         Args:
#           mode: Mode argument for the environment's render() method.
#             Valid values (str) are:
#               'rgb_array': returns the raw ALE image.
#               'human': renders to display via the Gym renderer.
#
#         Returns:
#           if mode='rgb_array': numpy array, the most recent screen.
#           if mode='human': bool, whether the rendering was successful.
#         """
#         return self.environment.render(mode)
#
#     def step(self, action):
#         """Applies the given action in the environment. Converts the observation to
#         greyscale, if it is not.
#
#         Remarks:
#
#           * If a terminal state (from life loss or episode end) is reached, this may
#             execute fewer than self.frame_skip steps in the environment.
#           * Furthermore, in this case the returned observation may not contain valid
#             image data and should be ignored.
#
#         Args:
#           action: The action to be executed.
#
#         Returns:
#           observation: numpy array, the observation following the action.
#           reward: float, the reward following the action.
#           is_terminal: bool, whether the environment has reached a terminal state.
#             This is true when a life is lost and terminal_on_life_loss, or when the
#             episode is over.
#           info: Gym API's info data structure.
#         """
#
#         observation, reward, game_over, info = self.environment.step(action)
#         self.game_over = game_over
#         if (len(observation.shape) > 2):
#             observation = cv2.cvtColor(observation, cv2.COLOR_RGB2GRAY)
#         return observation, reward, game_over, info
