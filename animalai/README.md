# AnimalAI Python API

This package provides the Python API used for training agents for the Animal AI Olympics competition. It is mostly an 
extension of [Unity's MLAgents env](https://github.com/Unity-Technologies/ml-agents/tree/master/ml-agents-envs).

It contains two ways of interfacing with the Unity environments:

- `animalai.envs.environment` contains the `UnityEnvironment` which is similar to the one found in `mlagents` but with 
a few adaptations to allow for more custom communications between Python and Unity.

- `animalai.envs.gym.environment` contains the `AnimalAIEnv` which provides a gym environment to use directly with 
baselines.

For more details and documentation have a look at the [AnimalAI documentation](../documentation)