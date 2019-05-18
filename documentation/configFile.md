# Arena Configuration Files

## TL;DR

Run `python visualizeArena.py configs/configExample.yaml` to get an understanding of how the `YAML` files configure the 
arenas for training. You will find a list of all objects you can add to an arena as well as the values for their 
parameters in [the definitions](definitionsOfObjects.md). You will find below all the technical details to create 
more complex training configurations.

## Intro
To configure training arenas you can use a simple **YAML file** and/or the **ArenaConfig structure** provided in 
`animalai/envs/ArenaConfig`. This makes training quite flexible and allows for the following:
- load and save configurations for reusability
- on the fly changes of configuration of one or more arenas between episodes, allowing for easy curriculum learning for example
- share configurations between participants

We provide a few custom configurations, but we expect designing good environments will be an important component of doing well in the competition.

We describe below the structure of the configuration file for an instance of the training environment, as well as all the 
parameters and the values they can take. For how to change the configuration during training see `animalai/envs/ArenaConfig.py`.

## The Arenas

<p align="center">
  <img height="400" src="PrefabsPictures/Arena.png">
</p>

A single arena is as shown above, it comes with a single agent (blue cube, black dot showing the front), a floor and four walls. It is a square of size 40x40, the 
origin of the arena is `(0,0)`, therefore you can provide coordinates for objects in the range `[0,40]x[0,40]` as floats.

For visualization you can only configure a single arena, however during training you can configure as many as you want, 
each will have its local set of coordinates as described above.

For a single arena you can provide the following parameters:
- `t` an `int`, the length of an episode which can change from one episode to the other. A value of `0` means that the episode will 
not terminate unlti a reward has been collected (setting `t=0` and having no reward will lead to an infinite episode)
- `rand_all_colors` a `bool`, whether all objects should have a random color or not
- `blackouts` [see below](##Blacktouts)

<!-- TODO: show (x,y,z) referential -->

## Objects

All the objects that will be used during training are provided to you for training. All objects can be configured in the 
same manner, using a set of parameters for each item:

- `name`: the name of the object you want to spawn
- `positions`: a list of `Vector3` positions within the arena where you want to spawn items, if the list 
is empty the position will be sampled randomly in the arena
- `sizes`: a list of `Vector3` sizes, if the list is empty the size will be sampled randomly
- `rotations`: a list of `float` in the range `[0,360]`, if the list is empty the rotation is sampled randomly
- `rand_color` a `bool` setting whether or not the color(s) of the objects should be randomized (some objects will not 
accept random colors)

**All values for the above fields can be found in [the definitions](definitionsOfObjects.md)**.

## Blackouts

Blackouts are parameters you can pass to each arena, which define between which frames of an episode should the lights 
be on or off. If omitted, this parameter automatically sets to have lights on for the entire episode. You can otherwise 
pass two types of arguments for this parameter:

- passing a list of frames `[5,10,15,20,25]` will start with the lights on, switch them off from frames 5 to 9 included, 
then back on from 15 to 19 included etc...
- passing a single negative argument `[-20]` will automatically switch lights on and off every 20 frames.

**Note**: in case of an episode with no time limit (`T=0`), the first option above would leave the lights off after the 
25th frame, the second one would indefinitely switch lights on and off.


## Rules and Notes
There are certain rules to follow when configuring and arena as well as some designs you should be aware of. If a 
configuration file does not behave as you expect make sure you're not breaking one of the following:

- Spawning objects:
    - **Objects can only spawn if they do not overlap with each other**
    - Attempting to spawn an object where another object already is will discard the latter.
    - The environment will attempt to spawn objects in the order they are provided in the file. In the case where any of the 
    components is randomized we attempt to spawn the object **up to 20 times**. if no valid spawning spot is found the object is discarded.
    - Due to the above point, the first objects in the list are more likely to spawn than the last ones
    - The `Agent` does not have to be provided in the configuration file, in which case it will spawn randomly.
    - If an `Agent` position is provided, be aware that the **agent spawns last** therefore it might cause problems if other objects
    randomly spawn where the agent should be
    - In case an object is present where the `Agent` should spawn the arena resets and the process starts all over
    - You can **spawn some objects on top of each others**, however be aware there is a `0.1` buffer automatically added to any height 
    you provide (to make sure things fall on each others nicely). 

- Configuration file values:
    - Objects' `name` have to match one of the names provided in [the definitions](definitionsOfObjects.md), if the name provided is not 
    found in this list, the object is ignored
    - Any component of `positions`, `sizes` and `rotations` can be randomized by providing a value sof `-1`.
    - Note that setting `positions.y = -1` will spawn the object at ground level.
    - Goals (except for the red zone) can only be scaled equally on all axes, therefore they will always remain spheres. If 
    a `Vector3` is provided for the scale of a sphere goal only the `x` component is used to scale all axes equally.
    
## Detailed example

Let's take a look at an example:

```
!ArenaConfig
arenas:
  0: !Arena
    t: 0
    rand_all_colors: false
    items:
    - !Item
      name: Cube
      positions: 
      - !Vector3 {x: 10, y: 0, z: 10}
      - !Vector3 {x: -1, y: 0, z: 30}
      rand_color: false
      rotations: [45]
      sizes: 
      - !Vector3 {x: -1, y: 5, z: -1}
    - !Item
      name: CylinderTunnel
      positions: []
      rand_color: true
      rotations: []
      sizes: []
```

First of all, we can see that the number of parameters for `positions`, `rotations` and `sizes` do not need to match. The 
environment will spawn `max( len(positions), len(rotations), len(sizes) )` objects, where `len()` is the length of the list. 
Any parameter missing will be sampled randomly.

In this case this will lead to:
- a `Cube` spawned in `[10,10]` on the groundm with rotation `45` and a size randomized on both `x` and `z` and of `y=5`
- a `Cube` spawnd on the ground, with a random `x` and `z=30`, both its rotation and size will be random
- a `CylinderTunnel` completely randomized, including its color
- the agent which position and rotation are randomized too

The arena will spawn these objects in this order.