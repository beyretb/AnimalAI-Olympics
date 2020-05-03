# Examples

## Notebooks
To run the notebooks you can simply install the requirements by running (we recommend using a virtual environment):

```
pip install -r requirements.txt
```

Then you can start a jupyter notebook by running `jupyter notebook` from your terminal.

## Designing arenas

You can use `load_config_and_play.py` to visualize a `yml` configuration for an environment arena. Make sure `animalai` 
is [installed](../README.md#requirements) and run `python load_config_and_play.py your_configuration_file.yml` which will open the environment in 
play mode (control with W,A,S,D or the arrows), close the environment by pressing CTRL+C in the terminal.

## Animalai-train examples

We provide two scripts which show how to use `animalai_train` to train agents:
- `train_ml_agents.py` uses ml-agents' PPO implementation (or SAC) and can run multiple environments in parralel to speed up 
the training process
- `train_curriculum.py` shows how you can add a curriculum to your training loop

To run either of these make sure you have `animalai-train` [installed](../README.md#requirements).

## OpenAI Gym and Baselines

You can use the OpenAI Gym interface to train using Baselines or other similar libraries (including 
[Dopamine](https://github.com/google/dopamine) and [Stable Baselines](https://github.com/hill-a/stable-baselines)). To 
do so you'll need to install:

On Linux:
```
sudo apt-get update && sudo apt-get install cmake libopenmpi-dev python3-dev zlib1g-dev &&
pip install tensorflow==1.14 &&
pip install git+https://github.com/openai/baselines.git@master#egg=baselines-0.1.6
```

On Mac: TODO

You can then run `train_baselines_dqn.py` or `train_baselines_ppo2.py` for examples.