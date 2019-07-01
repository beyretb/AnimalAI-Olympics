# Animal-AI Olympics

<p align="center">
  <img height="300" src="documentation/PrefabsPictures/steampunkFOURcrop.png">
</p>

**July 1st - November 1st** Entries will be available on EvalAI from July 8th.

The Animal-AI Olympics is an AI competition with tests inspired by animal cognition. Participants are given a small environment with just seven different classes of objects that can be placed inside. In each test, the agent needs to retrieve the food in the environment, but to do so there are obstacles to overcome, ramps to climb, boxes to push, and areas that must be avoided. The real challenge is that we don't provide the tests in advance. It's up to you to play with the environment and build interesting setups that can help create an agent that understands how the environment's physics work and the affordances that it has. The final submission should be an agent capable of robust food retrieval behaviour similar to that of many kinds of animals. We know the animals can pass these tests, it's time to see if AI can too.

## Prizes $32,000 (equivalent value)

* Overall Prizes
  * 1st place overall: **$7,500 total value** - $6,500 with up to $1,000 travel to speak at NeurIPS 2019.
  * 2nd place overall: **$6,000 total value** - $5,000 with up to $1,000 travel to speak at NeurIPS 2019.
  * 3rd place overall: **$1,500**.
* WBA-Prize: **$5,000 total value** - $4,000 with up to $1,000 travel to speak at NeurIPS 2019
* Category Prizes: **$200** For best performance in each category (cannot combine with other prizes - max 1 per team).
* **Mid-way AWS Research Credits**: The top 20 entries as of **September 1st** will be awarded **$500** of AWS credits.

See [competition launch page](https://mdcrosby.com/blog/animalailaunch.html) and official rules for further details.

**Important** Please check the competition rules [here](http://animalaiolympics.com/rules.html). Entry to the competition (via EvalAI) constitutes agreement with all competition rules.

## Overview

Here you will find all the code needed to compete in this new challenge. This repo contains **the training environment** (v1.0) that will be used for the competition. Please check back during the competition for minor bug-fixes and updates, but as of v1.0 the major features and contents are set in place. **Information for entering** will be added leading up to July 8th when the feedback will be available via the EvalAI website for the compeition.

For more information on the competition itself and to stay updated with any developments, head to the 
[Competition Website](http://www.animalaiolympics.com/) and follow [@MacroPhilosophy](https://twitter.com/MacroPhilosophy) 
and [@BenBeyret](https://twitter.com/BenBeyret) on twitter.

The environment contains an agent enclosed in a fixed sized arena. Objects can spawn in this arena, including positive 
and negative rewards (green, yellow and red spheres) that the agent must obtain (or avoid). All of the hidden tests that will appear in the competition are made using the objects in the training environment. We have provided some sample environment configurations that should be useful for training, but part of the challenge will be experimenting and designing new configurations.

To get started install the requirements below, and then follow the [Quick Start Guide](documentation/quickstart.md). 
More in depth documentation can be found on the [Documentation Page](documentation/README.md).

## Development Blog

You can read the launch post - with information about prizes and the categories in the competition here:

0. [Animal-AI Launch: July 1st](https://mdcrosby.com/blog/animalailaunch.html)

You can read the development blog [here](https://mdcrosby.com/blog). It covers further details about the competition as 
well as part of the development process.

1. [Why Animal-AI?](https://mdcrosby.com/blog/animalai1.html)

2. [The Syllabus (Part 1)](https://mdcrosby.com/blog/animalai2.html)

3. [The Syllabus (Part 2): Lights Out](https://mdcrosby.com/blog/animalai3.html)

## Requirements

The Animal-AI package works on Linux, Mac and Windows, as well as most Cloud providers. 
<!--, for cloud engines check out [this cloud documentation](documentation/cloud.md).-->

First of all your will need `python3.6` installed (we currently only support **python3.6**). We recommend using a virtual environment specifically for the competition. Clone this repository to run the examples we provide you with. We offer two packages for this competition:

- The main one is an API for interfacing with the Unity environment. It contains both a 
[gym environment](https://github.com/openai/gym) as well as an extension of Unity's 
[ml-agents environments](https://github.com/Unity-Technologies/ml-agents/tree/master/ml-agents-envs). You can install it
 via pip:
    ```
    pip install animalai
    ```
    Or you can install it from the source, head to `animalai/` folder and run `pip install -e .`

- We also provide a package that can be used as a starting point for training, and which is required to run most of the 
example scripts found in the `examples/` folder. It contains an extension of 
[ml-agents' training environment](https://github.com/Unity-Technologies/ml-agents/tree/master/ml-agents) that relies on 
[OpenAI's PPO](https://openai.com/blog/openai-baselines-ppo/), as well as 
[Google's dopamine](https://github.com/google/dopamine) which implements 
[Rainbow](https://www.aaai.org/ocs/index.php/AAAI/AAAI18/paper/download/17204/16680) (among others). You can also install 
this package using pip:
    ```
    pip install animalai-train
    ```
    Or you can install it from source, head to `examples/animalai_train` and run `pip install -e .`

Finally download the environment for your system:

| OS | Environment link |
| --- | --- |
| Linux |  [download v1.0.0](https://www.doc.ic.ac.uk/~bb1010/animalAI/env_linux_v1.0.0.zip) |
| MacOS |  [download v1.0.0](https://www.doc.ic.ac.uk/~bb1010/animalAI/env_mac_v1.0.0.zip) |
| Windows | [download v1.0.0](https://www.doc.ic.ac.uk/~bb1010/animalAI/env_windows_v1.0.0.zip)  |

You can now unzip the content of the archive to the `env` folder and you're ready to go! Make sure the executable 
`AnimalAI.*` is in `env/`. On linux you may have to make the file executable by running `chmod +x env/AnimalAI.x86_64`. 
Head over to [Quick Start Guide](documentation/quickstart.md) for a quick overview of how the environment works.

## Manual Control

If you launch the environment directly from the executable or through the VisualizeArena script it will launch in player 
mode. Here you can control the agent with the following:

| Keyboard Key  | Action    |
| --- | --- |
| W   | move agent forwards |
| S   | move agent backwards|
| A   | turn agent left     |
| D   | turn agent right    |
| C   | switch camera       |
| R   | reset environment   |

## Competition Tests

We will be releasing further details about the tests in the competition over the coming weeks. The tests will be split 
into multiple categories from the very simple (e.g. **food retrieval**, **preferences**, and **basic obstacles**) to 
the more complex (e.g. **working memory**, **spatial memory**, **object permanence**, and **object manipulation**). For 
now we have included multiple example config files that each relate to a different category. As we release further 
details we will also specify the rules for the type of tests that can appear in each category. Note that the example 
config files are just simple examples to be used as a guide. An agent that solves even all of these perfectly may still 
not be able to solve all the tests in the categories but it would be off to a very good start.

## Citing

For now please cite the [Nature: Machine Intelligence piece](https://rdcu.be/bBCQt) for any work involving the competition environment. Official Animal-AI Papers to follow:

Crosby, M., Beyret, B., Halina M. [The Animal-AI Olympics](https://www.nature.com/articles/s42256-019-0050-3) Nature 
Machine Intelligence 1 (5) p257 2019.

## Unity ML-Agents

The Animal-AI Olympics was built using [Unity's ML-Agents Toolkit.](https://github.com/Unity-Technologies/ml-agents)

The Python library located in [animalai](animalai) is almost identical to 
[ml-agents v0.7](https://github.com/Unity-Technologies/ml-agents/tree/master/ml-agents-envs). We only added the 
possibility to change the configuration of arenas between episodes. The documentation for ML-Agents can be found 
[here](https://github.com/Unity-Technologies/ml-agents/blob/master/docs/Python-API.md).

Juliani, A., Berges, V., Vckay, E., Gao, Y., Henry, H., Mattar, M., Lange, D. (2018). [Unity: A General Platform for 
Intelligent Agents.](https://arxiv.org/abs/1809.02627) *arXiv preprint arXiv:1809.02627*

## Known Issues

In play mode pressing `R` or `C` does nothing sometimes. This is due to the fact that we have synchronized these 
features with the agent's frames in order to have frames in line with the configuration files for elements such as blackouts. **Solution**: press the key again, several times if needed.

~~When a lot of objects are spawned randomly, extremely rarely, the agent will fall through the floor.~~ (fixed in 
v0.6.1)

## TODO

- [ ] Add custom resolutions
- [x] Add inference viewer to the environment
- [x] Offer a gym wrapper for training
- [x] Improve the way the agent spawns
- [x] Add lights out configurations.
- [x] Improve environment framerates
- [x] Add moving food

## Version History

- v1.0
    - Adds inference mode to the environment to visualize trained agents

- v0.6.1 (Environment only) 
    - Fix rare events of agent falling through the floor or objects flying in the air when resetting an arena

- v0.6.0 
    - Adds score in playmode (current and previous scores)
    - Playmode now incorporates lights off directly (in `examples` try: `python visualizeArena.py configs/lightsOff.yaml`)
    - To simplify the environment several unnecessary objects have been removed [see here](documentation/definitionsOfObjects.md)
    - **Several object properties have been changed** [also here](documentation/definitionsOfObjects.md)
    - Frames per action reduced from 5 to 3 (*i.e.*: for each action you send we repeat it for a certain number of frames 
    to ensure smooth physics)
    - Add versions compatibility check between the environment and API
    - Remove `step_number` argument from `animalai.environment.step`

- v0.5 Package `animalai`, gym compatible, dopamine example, bug fixes
    - Separate environment API and training API in Python
    - Release both as `animalai` and `animalai-train` PyPI packages (for `pip` installs)
    - Agent speed in play-mode constant across various platforms
    - Provide Gym environment
    - Add `trainBaselines,py` to train using `dopamine` and the Gym wrapper
    - Create the `agent.py` interface for agents submission
    - Add the `HotZone` object (equivalent to the red zone but without death)

- v0.4 - Lights off moved to Unity, colors configurations, proportional goals, bugs fixes
    - The light is now directly switched on/off within Unity, configuration files stay the same
    - Blackouts now work with infinite episodes (`t=0`)
    - The `rand_colors` configurations have been removed and the user can now pass `RGB` values, see 
    [here](documentation/configFile.md#objects)
    - Rewards for goals are now proportional to their size (except for the `DeathZone`), see 
    [here](documentation/definitionsOfObjects.md#rewards)
    - The agent is now a ball rather than a cube
    - Increased safety for spawning the agent to avoid infinite loops
    - Bugs fixes
    
- v0.3 - Lights off, remove Beams and add cylinder
    - We added the possibility to switch the lights off at given intervals, see 
    [here](documentation/configFile.md#blackouts)
    - visualizeLightsOff.py displays an example of lights off, from the agent's point of view
    - Beams objects have been removed
    - A `Cylinder` object has been added (similar behaviour to the `Woodlog`)
    - The immovable `Cylinder` tunnel has been renamed `CylinderTunnel`
    - `UnityEnvironment.reset()` parameter `config` renamed to `arenas_configurations_input`
    
- v0.2 - New moving food rewards, improved Unity performance and bug fixes 
    - Moving rewards have been added, two for each type of reward, see 
    [the details here](documentation/definitionsOfObjects.md#rewards).
    - Added details for the maze generator.
    - Environment performance improved.
    - [Issue #7](../../issues/7) (`-inf` rewards for `t: 0` configuration) is fixed.

- v0.1 - Initial Release

