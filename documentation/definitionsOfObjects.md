## The Objects

The objects you can spawn in an arena are split among three categories:
- movable
- immovable
- rewards

Below is a list of objects you can spawn. For each we describe the name you should use to refer to in your configuration files 
or in Python directly, as well as their default characteristics and range of values you can assign to them.

Each object has an orientation, we provide the three axes for all of those that are not symmetrical. The color code of the 
axes is as depicted below:

<img height="200" src="PrefabsPictures/Referential.png">

**Note:** as depicted above the vertical axis is th **Y axis**, we will use Z as the forward axis (both conventions are 
the ones used in Unity). 

#### Immovable

These are objects that are fixed and will not be impacted by the agent or other objects:

- <img align="left" height="100" src="PrefabsPictures/Immovable/Beam1.png"> a metal beam that sticks out of the ground
    - name: `Beam1`
    - can rotate 360 degrees
    - size range `(0.1,0.1,1)-(5,5,15)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Immovable/Beam2.png"> another metal beam that sticks out of the ground
    - name: `Beam2`
    - can rotate 360 degrees
    - size range `(0.1,0.1,1)-(5,5,15)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Immovable/CubeTunnel.png"> a rectangular tunnel
    - name: `CubeTunnel`
    - can rotate 360 degrees
    - size range `(3,3,3)-(10,10,10)`
    - can randomize color
- <img align="left" height="100" src="PrefabsPictures/Immovable/Cylinder.png"> a cylinder tunnel
    - name: `Cylinder`
    - can rotate 360 degrees
    - size range `(0.5,2.5,2.5)-(5,5,5)`
    - can randomize color
- <img align="left" height="100" src="PrefabsPictures/Immovable/Ramp.png"> a ramp the agent can climb on
    - name: `Ramp`
    - can rotate 360 degrees
    - size range `(0.5,0.5,0.5)-(10,5,10)`
    - can randomize color
    - **can only spawn on the ground**
- <img align="left" height="100" src="PrefabsPictures/Immovable/Wall.png"> a wall
    - name: `Wall`
    - can rotate 360 degrees
    - size range `(1,1,1)-(40,10,40)`
    - can randomize color
- <img align="left" height="100" src="PrefabsPictures/Immovable/WallTransparent.png"> a transparent wall
    - name: `WallTransparent`
    - can rotate 360 degrees
    - size range `(1,1,1)-(40,10,40)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Immovable/MazeGenerator.png"> a randomly generated maze of size 
`16x16` with two entrances. Note this takes quite some room and will be hard to generate last on an arena.
    - name: `MazeGenerator`
    - can rotate 360 degrees
    - size range constant
    - can randomize color
    
#### Movable

These are objects the agent can move and which will be affected by each other, fixed objects and rewards if they collide
     
- <img align="left" height="100" src="PrefabsPictures/Movable/Cube.png"> a cube that can be pushed
    - name: `Cube`
    - can rotate 360 degrees
    - size range `(1,1,1)-(10,10,10)`
    - can randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/CubeTransparent.png"> a transparent cube that can be pushed
    - name: `CubeTransparent`
    - can rotate 360 degrees
    - size range `(1,1,1)-(10,10,10)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/Cardbox1.png"> a carbox that can be pushed
    - name: `Cardbox1`
    - can rotate 360 degrees
    - size range `(1,1,1)-(10,10,10)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/Cardbox2.png"> a carbox that can be pushed
    - name: `Cardbox2`
    - can rotate 360 degrees
    - size range `(1,1,1)-(10,10,10)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/WoodLog.png"> a wood log
    - name: `WoodLog`
    - can rotate 360 degrees
    - size range `(1,1,1)-(10,10,10)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/UItem.png"> a U-shaped object
    - name: `UObject`
    - can rotate 360 degrees
    - size range `(3,3,3)-(20,4,10)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/LItem.png"> a L-shaped object
    - name: `LObject`
    - can rotate 360 degrees
    - size range `(3,3,3)-(20,4,10)`
    - cannot randomize color
    
#### Rewards

Objects that may terminate the event if the agents collides with one:

- Good goals: green spheres with a reward of 1
    - <img align="left" height="100" src="PrefabsPictures/Rewards/GoodGoal.png"> Fixed good reward
        - name: `GoodGoal`
        - can rotate 360 degrees
        - size range `(0.5,0.5,0.5)-(10,10,10)`
        - cannot randomize color
        - terminates episode
    - <img align="left" height="100" src="PrefabsPictures/Rewards/GoodGoal.png">A good reward moving in a straight line,
     which stops moving as soon as it hits another object. Will start moving in the direction provided by the rotation 
     parameter
        - name: `GoodGoalMove`
        - can rotate 360 degrees
        - size range fixed as `(1,1,1)`
        - cannot randomize color
        - terminates episode
    - <img align="left" height="100" src="PrefabsPictures/Rewards/GoodGoal.png"> A good reward bouncing on objects. Will
     start moving in the direction provided by the rotation parameter
        - name: `GoodGoalBounce`
        - can rotate 360 degrees
        - size range fixed as `(1,1,1)`
        - cannot randomize color
        - terminates episode
- Bad goals: red spheres with a reward of -1
    - <img align="left" height="100" src="PrefabsPictures/Rewards/BadGoal.png">  Fixed bad reward
        - name: `BadGoal`
        - can rotate 360 degrees
        - size range `(0.5,0.5,0.5)-(10,10,10)`
        - cannot randomize color
        - terminates episode
    - <img align="left" height="100" src="PrefabsPictures/Rewards/BadGoal.png">  A bad reward moving in a straight line,
     which stops moving as soon as it hits another object. Will start moving in the direction provided by the rotation 
     parameter
        - name: `BadGoalMove`
        - can rotate 360 degrees
        - size range fixed as `(1,1,1)`
        - cannot randomize color
        - terminates episode
    - <img align="left" height="100" src="PrefabsPictures/Rewards/BadGoal.png"> A bad reward bouncing on objects. Will 
    start moving in the direction provided by the rotation parameter
        - name: `BadGoalBounce`
        - can rotate 360 degrees
        - size range fixed as `(1,1,1)`
        - cannot randomize color
        - terminates episode
-  Good goals multi: golden spheres with a reward of 1 that will only terminate the episode once all of them are 
retrieved (and a GoodGoal if present):
    - <img align="left" height="100" src="PrefabsPictures/Rewards/GoodGoalMulti.png"> Fixed good reward multi
        - name: `GoodGoalMulti`
        - can rotate 360 degrees
        - size range `(0.5,0.5,0.5)-(10,10,10)`
        - cannot randomize color
        - terminates episode
    - <img align="left" height="100" src="PrefabsPictures/Rewards/GoodGoalMulti.png"> A good reward moving in a straight
     line, which stops moving as soon as it hits another object. Will start moving in the direction provided by the 
     rotation parameter
        - name: `GoodGoalMultiMove`
        - can rotate 360 degrees
        - size range fixed as `(1,1,1)`
        - cannot randomize color
        - terminates episode
    - <img align="left" height="100" src="PrefabsPictures/Rewards/GoodGoalMulti.png"> A bad reward bouncing on objects. 
    Will start moving in the direction provided by the rotation parameter
        - name: `GoodGoalMultiBounce`
        - can rotate 360 degrees
        - size range fixed as `(1,1,1)`
        - cannot randomize color
        - terminates episode
- <img align="left" height="100" src="PrefabsPictures/Rewards/DeathZone.png"> a deathzone with reward -1
    - name: `DeathZone`
    - can rotate 360 degrees
    - size range `(1,0,1)-(40,0,40)`
    - cannot randomize color
    - **the deathzone is always flat and located on the ground**
    - terminates episode

