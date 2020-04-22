# Quick Start Guide

You can find below some pointers to get started with the Animal-AI.

## Running the standalone arena

The basic environment is made of a single agent in an enclosed arena that resembles an environment that could be used for experimenting with animals. In this environment you can add objects the agents can interact with, as well as goals or rewards the agent must collect or avoid. To see what this looks like, you can run the executable environment directly. This will spawn an arena filled with randomly placed objects. Of course, this is a very messy environment to begin training on, so we provide a configuration file where you choose what to spawn (see below).

You can toggle the camera between first person, third person and Bird's eye view using the `C` key on your keyboard. The agent can 
then be controlled using `W,A,S,D` on your keyboard. Hitting `R` or collecting certain rewards (green or red) will reset the arena.

## Running a specific configuration file

Once you are familiarized with the environment and its physics, you can start building and visualizing your own. Assuming you followed the [installation instruction](../README.md#requirements), go to the `examples/` folder and run 
`python load_config_and_play.py`. This loads a random configuration from the competition for the arena and lets you play as the agent. 

Have a look at the [configuration files](../competition_configurations) which specifies the objects to place. You can select 
objects, their size, location, rotation and color, randomizing any of these parameters as you like. For more details on the configuration options and syntax please read the relevant documentation:
 - The [configuration file documentation page](configFile.md) which explains how to write the configuration files.
 - The [definitions of objects page](definitionsOfObjects.md) which contains a detailed list of all the objects and their 
 characteristics.


## Start training your agent

Once you're happy with your arena configurations you can start training your agent. The `animalai` package includes several features to help with this:

- It is possible to **change the environment configuration between episodes** (allowing for techniques such as curriculum learning).
- You can **choose the length of each episode** as part of the configuration files, even having infinite episodes.
- You can **have several arenas in a single environment instance**, each with an agent you control independently from the other, and each with its own configuration allowing for collecting observations faster.

We provide examples of training using the `animalai-train` package, you can of course start from scratch and submit agents that do not rely on this library. To understand how training an `animalai` environment we provide scripts in the 
[examples folder](../examples) which contains various training examples and a readme file to explain how these work.