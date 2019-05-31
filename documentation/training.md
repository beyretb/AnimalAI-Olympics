# Training

## Overview

Training happens very much like with a regular gym environment. We provide you with both the compiled 
environment and the Python libraries needed for training. You will also find an example of training agent 
using [ML-Agents' PPO](https://github.com/Unity-Technologies/ml-agents/blob/master/docs/Training-PPO.md).

## Observations and actions

Before looking at the environment itself, we define here the actions the agent can take and the observations it collects:

- **Actions**: the agent can move forward/backward and rotate left/right, just like in play mode. Therefore the 
actions are discrete of dimension `2`, each component can take 3 values (`(nothing, forward, backward)` and `(nothing, left,right)`).
- **Observations** are made of two components: visual observations which are pixel based and of dimension `84x84x3`, as 
well as the speed of the agent which is continuous of dimension `3` (speed along axes `(x,y,z)` in this order).
- **Rewards**: in case of an episode of finite length `T`, each step carries a small negative reward `-1/T`. In case of 
an episode with no time limite (`T=0`), no reward is returned for each step. Other rewards come from the rewards objects 
(see details [here](definitionsOfObjects.md)).

## The Unity Environment

Much like a gym environment, you can create a `UnityEnvironment` that manages all communications with 
the environment. You will first need to instantiate the environement, you can then reset it, take steps and collect 
observations. All the codebase for this is in `animalai/envs/environment.py`. Below is a quick description of these components.

### Instantiation

For example, you can call::

```
env= UnityEnvironment(
        file_name='env/AnimalAI',   # Path to the environment
        worker_id=1,                # Unique ID for running the environment (used for connection)
        seed=0,                     # The random seed 
        docker_training=False,      # Whether or not you are training inside a docker
        no_graphics=False,          # Always set to False
        n_arenas=4,                 # Number of arenas in your environment
        play=False                  # Set to False for training                
    )
```

Note that the path to the executable file should be stripped of its extension. The `no_graphics` parameter should always 
be set to `False` as it impacts the collection of visual obeservations, which we rely on.

### Reset

We have modified this functionality compared to the mlagents codebase. Here we add the possibility to pass a new `ArenaConfiguration` 
as an argument to reset the environment. The environment will use the new configuration for this reset, as well as all the 
following ones until a new configuration is passed. The syntax is:

```
env.reset(arenas_configurations=arena_config,     # A new ArenaConfig to use for reset, leave empty to use the last one provided
        train_mode=True                                 # True for training
        )
```


**Note**: as mentioned above, the environment will change the configuration of an arena if it receives a new `ArenaConfig` 
from a `env.reset()` call. Therefore, should you have created several arenas and want to only change one (or more) arena 
configuration(s), you can do so by only providing an `ArenaConfig` that contains configuration(s) for the associated arena(s). 
For example, if you only want to modify arena number 3, you could create an `ArenaConfig` from the following `YAML`:

```
arenas:
  3: !Arena
    t: 0
    rand_all_colors: true
    rand_all_sizes: true
    items:
    - !Item
        (...)
```

### Step

Taking a step returns a data structure named `BrainInfo` which is defined in `animalai/envs/brain` and basically contains 
all the information returned by the environment after taking a step, including the observations. For example:
 
```
info = env.step(vector_action=take_action_vector)
```

You can pass more parameters to the environment depending on what you need for training, to learn about this and the 
format of the `BrainInfo`, see the [official mal-agents' documentation](https://github.com/Unity-Technologies/ml-agents/blob/master/docs/Python-API.md#interacting-with-a-unity-environment).

### Close

Don't forget to close the environment once training is done so that all communications are closed properly and ports 
are not left open (which can prevent future connections).

```
env.close()
```

## Notes

Some important points to note for training:

- Instantiating an environment will open a window showing the environment from above. The size of this window will 
influence the speed of training: the smaller the window, the faster the simulation and therefore the training. You can 
resize the window during training but we advise to keep it small as much as possible.
