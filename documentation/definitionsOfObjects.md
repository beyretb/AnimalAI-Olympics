## The Objects

There are 7 types of object split amongst three categories:
* Immovable
    * Walls
    * Ramps
    * Tunnels
* Movable
    * Cardboard Boxes
    * Shapes
* Rewards
    * Food
    * Zones

For each object we describe the object name to be used in a configuration file or in Python directly, as well as their default characteristics and the range of values you can assign to them. **All objects can be rotated `360` degrees.**

The axis below corresponds to that shown in the images for each individual object.

<img height="200" src="PrefabsPictures/Referential.png">

**Note:** the **Y axis** is the vertical axis and **Z** is the forward axis (following conventions used in Unity). 

#### Immovable

These objects are fixed and cannot be moved:

- <img align="left" height="100" src="PrefabsPictures/Immovable/Wall.png">a wall
    - name: `Wall`
    - size range `(0.1,0.1,0.1)-(40,10,40)`
    - can randomize color. 
For simplicity, walls in most test problems will be grey and set to RGB (r: 153, g: 153, b: 153). If a wall is used as a platform it will be blue and set to RGB (r: 0, g: 0, b: 255).
- <img align="left" height="100" src="PrefabsPictures/Immovable/WallTransparent.png">a transparent wall
    - name: `WallTransparent`
    - size range `(0.1,0.1,0.1)-(40,10,40)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Immovable/Ramp.png">a ramp the agent can climb on
    - name: `Ramp`
    - size range `(0.5,0.1,0.5)-(40,10,40)`
    - can randomize color. 
For simplicity, ramps in most test problems will be pink and set to RGB (r: 255, g: 0, b: 255).
- <img align="left" height="100" src="PrefabsPictures/Immovable/CylinderTunnel.png">a cylinder tunnel
    - name: `CylinderTunnel`
    - size range `(2.5,2.5,2.5)-(10,10,10)`
    - can randomize color
For simplicity, tunnels in most test problems will be grey and set to RGB (r: 153, g: 153, b: 153).
- <img align="left" height="100" src="PrefabsPictures/Immovable/CylinderTunnelTransparent.png">a transparent cylinder tunnel
    - name: `CylinderTunnelTransparent`
    - size range `(2.5,2.5,2.5)-(10,10,10)`
    - cannot randomize color
    
#### Movable

These are objects that are light enough to be easily moved by the agent (or other objects). Note that different object types weigh different amounts. Also note that since v0.6, all movable object have a fixed texture in order to make them easier to differentiate from non movable objects.     

- <img align="left" height="100" src="PrefabsPictures/Movable/Cardbox1.png">a light cardbox that can be pushed
    - name: `Cardbox1`
    - size range `(0.5,0.5,0.5)-(10,10,10)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/Cardbox2.png">a heavier cardbox that can be pushed
    - name: `Cardbox2`
    - size range `(0.5,0.5,0.5)-(10,10,10)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/UObject.png">a U-shaped object with a wooden texture
    - name: `UObject`
    - size range `(1,0.3,3)-(5,2,20)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/LObject.png">a L-shaped object with a wooden texture
    - name: `LObject`
    - size range `(1,0.3,3)-(5,2,20)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/LObject2.png">symmetric of the L-shaped object
    - name: `LObject2`
    - size range `(1,0.3,3)-(5,2,20)`
    - cannot randomize color
    
#### Rewards

Objects that give a reward and may terminate the event if the agents collides with one. **Important note:** for sphere goals the `y` and `z` components of the provided sizes are ignored and only `x` is used.

- **Good Goals**: Green spheres with a positive reward equal to their size. Ends the episode on collection.
    - <img align="left" height="100" src="PrefabsPictures/Rewards/GoodGoal.png">Stationary food with positive reward.
        - name: `GoodGoal`
        - size range `0.5-5`
        <br>
    - <img align="left" height="100" src="PrefabsPictures/Rewards/GoodGoal.png">Moving food with positive reward. Starts by moving in the direction provided by the rotation parameter.
        - name: `GoodGoalBounce`
        - size range `0.5-5`
        <br>
- **Bad Goals**: Red spheres with a negative reward equal to their size. Ends the episode on collection.
    - <img align="left" height="100" src="PrefabsPictures/Rewards/BadGoal.png"> Stationary food with negative reward.
        - name: `BadGoal`
        - size range `0.5-5`
        <br>
    - <img align="left" height="100" src="PrefabsPictures/Rewards/BadGoal.png">Moving food with negative reward. Starts by moving in the direction provided by the rotation parameter.
        - name: `BadGoalBounce`
        - size range `0.5-5`
        <br>
-  **Good Goal Multi**: Golden spheres with a positive reward equal to their size. Does **not** terminate the episode. However, the episode is terminated if all goals are collected. So, in an episode with only these rewards the episode will terminate when the last one is obtained.
    - <img align="left" height="100" src="PrefabsPictures/Rewards/GoodGoalMulti.png">Stationary food with positive reward (non-terminating).
        - name: `GoodGoalMulti`
        - size range `0.5-5`
        <br>
    - <img align="left" height="100" src="PrefabsPictures/Rewards/GoodGoalMulti.png">Moving food with positive reward (non-terminating). Starts by moving in the direction provided by the rotation parameter.
        - name: `GoodGoalMultiBounce`
        - size range `0.5-5`
- Deathzone: 
    - <img align="left" height="100" src="PrefabsPictures/Rewards/DeathZone.png">a red zone with reward -1 that terminates the episode on contact:
        - name: `DeathZone`
        - size range `(1,0,1)-(40,0,40)`
        - **the deathzone is always flat and located on the ground**
        - terminates an episode
- HotZone: 
    - <img align="left" height="100" src="PrefabsPictures/Rewards/HotZone.png">an orange zone with reward 
    `min(-10/T,-1e-5)` (or `-1e-5` if `T=0`) that **does not** end an episode
        - name: `HotZone`
        - size range `(1,0,1)-(40,0,40)`
        - **the hotzone is always flat and located on the ground**
        - does not terminate and episode
        -if a `DeathZone` and a `HotZone` overlap the `DeathZone` prevails
