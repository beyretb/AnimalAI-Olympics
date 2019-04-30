# Animal-AI Olympics

## Overview

Welcome to the repository for the Animal-AI Olympics competition where you will find all the code needed to compete in 
this new challenge. Currently we have only released the environment (v0.1) that will be used for the competition. 
The competition itself goes live at the end of June and until then we will be updating with bug fixes and small changes 
to environment. For more information on the competition itself, head to the 
[Competition Website](http://www.animalaiolympics.com/).

The environment is made of an agent enclosed in a fixed sized arena. Objects can spawn in this arena, including positive and 
negative rewards. The **main idea of this environment** is that all tests we will evaluate your agents on can be reproduced 
using the obejcts provided in the training environment. All cognitive skills can be tested using this setup. Therefore, 
the challenge is to **design both a learning environment as well as an learning agent** in order to perform well on the 
tests. You can train several agents in parallel.

The goal of this first release is to **seek feedback from the community**. The final design of the environment itself will be 
very similar to this one, however we are open to suggestion and especially bugs report! Head over the the 
[issues page](https://github.com/beyretb/AnimalAI/issues) and open a ticket using the `suggestion` or `bug` labels 
respectively.

To get started install the requirements below, and then follow the [Quick Start Guide](documentation/quickstart.md). 
A more in depth documentation <!--, including a primer on animal cognition,--> can be found on the 
[Documentation Page](documentation/documentation.md).

## Requirements

The Animal-AI package works on most platforms. Below is the basic installation on Ubuntu. Description for 
other platforms coming soon. <!--, for cloud engines check out [this cloud documentation](documentation/cloud.md).-->

First of all your will need `python3.6` installed. You will find a list of requirements in the `requirements*.txt` files. 
Using `pip` you can run:

on Linux and mac:
```
pip install -r requirementsOthers.txt
```

on windows:
```
pip install -r requirementsWindows.txt
```

You will need to download the environment for your system:

| OS | Environment link |
| --- | --- |
| Linux |  [download here](https://www.doc.ic.ac.uk/~bb1010/animalAI/env_linux.zip) |
| MacOS |  coming soon |
| Windows | [download here](https://www.doc.ic.ac.uk/~bb1010/animalAI/env_windows.zip)  |

You can now unzip the content of the archive to the `env` folder and you're ready to go! Head over to 
[Quick Start Guide](documentation/quickstart.md) for a quick overview of how the environment works.

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

## Unity ML-Agents

The Animal-AI Olympics was built using [Unity's ML-Agents Toolkit.](https://github.com/Unity-Technologies/ml-agents)

The Python library located in [animalai](animalai) is almost identical to 
[ml-agents v0.7](https://github.com/Unity-Technologies/ml-agents/tree/master/ml-agents-envs). We only added the possibility 
to change the configuration of arenas between episodes. For issues related to any other feature that this one, please 
refer to the documentation [here](https://github.com/Unity-Technologies/ml-agents/blob/master/docs/Python-API.md)

Juliani, A., Berges, V., Vckay, E., Gao, Y., Henry, H., Mattar, M., Lange, D. (2018). [Unity: A General Platform for 
Intelligent Agents.](https://arxiv.org/abs/1809.02627) *arXiv preprint arXiv:1809.02627*

## Version History
v0.1 - Initial Release

