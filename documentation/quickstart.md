# Quick Start Guide

The format of this competition may be a little different to the standard machine learning model. We do not provide a single training set that you can train on out of the box and we do not provide full information about the testing set in advance. Instead, you will need to choose for yourself what you expect to be useful configurations of our training environment in order to train an agent capable of robust food retrieval behaviour.

To facilitate working with this new paradigm we created tools you can use to easily setup and visualize your training environment.

## Running the standalone arena

The basic environment is made of a single agent in an enclosed arena that resembles an environment that could be used for experimenting with animals. In this environment you can add objects the agents can interact with, as well as goals or rewards the agent must collect or avoid. To see what this looks like, you can run the executable environment directly. This will spawn an arena filled with randomly placed objects. Of course, this is a very messy environment to begin training on, so we provide a configuration file where you choose what to spawn (see below).

You can toggle the camera between First Person and Bird's eye view using the `C` key on your keyboard. The agent can 
then be controlled using `W,A,S,D` on your keyboard. Hitting `R` or collecting certain rewards (green or red) will reset the arena.

## Running a specific configuration file

Once you are familiarized with the environment and its physics, you can start building and visualizing your own. Assuming you followed the [installation instruction](../README.md#requirements), go to the `examples/` folder and run 
`python visualizeArena.py configs/exampleConfig.yaml`. This loads the `configs/exampleConfig.yaml` configuration for the 
arena and lets you play as the agent. 

Have a look at the [configuration file](../examples/configs/exampleConfig.yaml) which specifies the objects to place. You can select 
objects, their size, location, rotation and color, randomizing any of these parameters as you like. For more details on the configuration options and syntax please read the relevant documentation:
 - The [configuration file documentation page](configFile.md) which explains how to write the configuration files.
 - The [definitions of objects page](definitionsOfObjects.md) which contains a detailed list of all the objects and their 
 characteristics.


## Start training your agent

Once you're happy with your arena configurations you can start training your agent. The `animalai` package includes several features to help with this:

- It is possible to **change the environment configuration between episodes** (allowing for techniques such as curriculum learning).
- You can **choose the length of length of each episode** as part of the configuration files, even having infinite episodes.
- You can **have several arenas in a single environment instance**, each with an agent you control independently from the other, and each with its own configuration allowing for collecting observations faster.

We provide examples of training using the `animalai-train` package, you can of course start from scratch and submit agents that do not rely on this library. To understand how training an `animalai` environment we provide scripts in the 
`examples/` folder:

- `trainDopamine.py` uses the `dopamine` implementation of Rainbow to train a single agent using the gym interface. This 
is a good starting point if you want to try another training algorithm that works as a plug-and-play with Gym. **Note that using the gym interface only allows for training with a single arena and agent in the environment at a time.** We do offer to train with several agents in a gym environment but this will require modifying your code to accept more than one observation at a time. 
- `trainMLAgents.py` uses the `ml-agents` implementation of PPO to train one or more agents at a time, using the 
`UnityEnvironment`. This is a great starting point if you don't mind reading some code as it directly allows to use the 
functionalities described above, out of the box.

You can find more details about this in the [training documentation](training.md).
