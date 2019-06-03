# Visualization and Training

We provide in this folder a few examples for competing in the AnimalAI Olympics. You will first of all need to setup 
a training environment with a specific configuration. For this part we provide a script to visualize your configurations. 
You will then need to train an agent on this configuration, which can be done however you prefer, we provide here two 
examples, one for each interface provided.

## Visualizing configurations

Once you have [created a configuration file](../documentation/configFile.md), you may want to see what it actually look 
like. To do so you can simply run:

```
python visualizeArena.py configs/exampleCondig.yaml
```

replacing `exampleConfig.yaml` with the name of your file(s). Once this is launched, you can control the agent using the 
same keystrokes as described [here](../README.md#manual-control).

We also provide an example of what switching lights on/off looks like for the agent and how to configure this feature. 
Run `python visualizeLightsOff.py` and read `configs/lightsOff.yaml` to see how four different agents in the same 
environment can have different lights setups.

## Training agents

We strongly encourage you to read the code in the training files to familiarize yourself with the syntax of the two 
packages we provide. We will also release Jupyter notebooks in a future release to make this step more straightforward.

### Using ML Agents interface

You can run `python trainMLAgents.py` to start training using PPO and the default configuration 
`configs/exampleTraining.yaml`. This scripts instantiates 4 agents in a single environment, therefore collecting more 
observations at once and speeding up training.

### Using the Gym interface

Run `python trainDopamine.py` to run Rainbow a single agent using the Gym interface and Dopamine. The default Gym 
implementation does not support multiple agents and it might therefore be much slower to train on. We plan on adapting 
our library to allow for this feature while still being compatible with baselines.