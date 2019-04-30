## The Objects

The objects you can spawn in an arena are split among three categories:
- movable
- immovable
- rewards

Below is a list of objects you can spawn. For each we describe the name you should use to refer to in your configuration files 
or in Python directly, as well as their default characteristics and range of values you can assign to them.

#### Immovable

These are objects that are fixed and will not be impacted by the agent or other objects:

- <img align="left" height="100" src="PrefabsPictures/Immovable/Beam1.png"> a metal beam that sticks out of the ground
    - name: `Beam1`
    - default size `(1,1,1)`
    - can rotate 360 degrees
    - size range `(0.1,0.1,1)-(5,5,15)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Immovable/Beam2.png"> another metal beam that sticks out of the ground
    - name: `Beam2`
    - default size `(1,1,1)`
    - can rotate 360 degrees
    - size range `(0.1,0.1,1)-(5,5,15)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Immovable/CubeTunnel.png"> a rectangular tunnel
    - name: `CubeTunnel`
    - default size `(1,1,1)`
    - can rotate 360 degrees
    - size range `(3,3,3)-(10,10,10)`
    - can randomize color
- <img align="left" height="100" src="PrefabsPictures/Immovable/Cylinder.png"> a cylinder tunnel
    - name: `Cylinder`
    - default size `(2,2,2)`
    - can rotate 360 degrees
    - size range `(0.5,2.5,2.5)-(5,5,5)`
    - can randomize color
- <img align="left" height="100" src="PrefabsPictures/Immovable/Ramp.png"> a ramp the agent can climb on
    - name: `Ramp`
    - default size `(1,1,1)`
    - can rotate 360 degrees
    - size range `(0.5,0.5,0.5)-(10,5,10)`
    - can randomize color
    - **can only spawn on the ground**
- <img align="left" height="100" src="PrefabsPictures/Immovable/Wall.png"> a wall
    - name: `Wall`
    - default size `(4,5,1)`
    - can rotate 360 degrees
    - size range `(1,1,1)-(40,40,40)`
    - can randomize color
- <img align="left" height="100" src="PrefabsPictures/Immovable/WallTransparent.png"> a transparent wall
    - name: `WallTransparent`
    - default size `(4,5,1)`
    - can rotate 360 degrees
    - size range `(1,1,1)-(40,40,40)`
    - cannot randomize color
    
#### Movable

These are objects the agent can move and which will be affected by each other, fixed objects and rewards if they collide
     
- <img align="left" height="100" src="PrefabsPictures/Movable/Cube.png"> a cube that can be pushed
    - name: `CubeRigid`
    - default size `(2,2,2)`
    - can rotate 360 degrees
    - size range `(1,1,1)-(10,10,10)`
    - can randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/CubeTransparent.png"> a transparent cube that can be pushed
    - name: `CubeTransparent`
    - default size `(2,2,2)`
    - can rotate 360 degrees
    - size range `(1,1,1)-(10,10,10)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/Cardbox1.png"> a carbox that can be pushed
    - name: `Cardbox1`
    - default size `(1,1,1)`
    - can rotate 360 degrees
    - size range `(1,1,1)-(10,10,10)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/Cardbox2.png"> a carbox that can be pushed
    - name: `Cardbox2`
    - default size `(1,1,1)`
    - can rotate 360 degrees
    - size range `(1,1,1)-(10,10,10)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/WoodLog.png"> a wood log
    - name: `WoodLog`
    - default size `(2,2,2)`
    - can rotate 360 degrees
    - size range `(1,1,1)-(10,10,10)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/UItem.png"> a U-shaped object
    - name: `UItem`
    - default size `(?,?,?)`
    - can rotate 360 degrees
    - size range `(?,?,?)-(?,?,?)`
    - cannot randomize color
- <img align="left" height="100" src="PrefabsPictures/Movable/LItem.png"> a L-shaped object
    - name: `LItem`
    - default size `(?,?,?)`
    - can rotate 360 degrees
    - size range `(?,?,?)-(?,?,?)`
    - cannot randomize color
    
#### Rewards

Objects that may terminate the event if the agents collides with one:

- <img align="left" height="100" src="PrefabsPictures/Rewards/GoodGoal.png"> a good reward with reward 1
    - name: `GoodGoal`
    - default size `(1,1,1)`
    - can rotate 360 degrees
    - size range `(0.5,0.5,0.5)-(10,10,10)`
    - cannot randomize color
    - terminates episode
- <img align="left" height="100" src="PrefabsPictures/Rewards/BadGoal.png"> a bad reward with reward -1
    - name: `BadGoal`
    - default size `(1,1,1)`
    - can rotate 360 degrees
    - size range `(0.5,0.5,0.5)-(10,10,10)`
    - cannot randomize color
    - terminates episode
- <img align="left" height="100" src="PrefabsPictures/Rewards/DeathZone.png"> a deathzone with reward -1
    - name: `DeathZone`
    - default size `(1,0,1)`
    - can rotate 360 degrees
    - size range `(1,0,1)-(40,0,40)`
    - cannot randomize color
    - **the deathzone is always flat and located on the ground**
    - terminates episode
- <img align="left" height="100" src="PrefabsPictures/Rewards/GoodGoalMulti.png"> a good goal with reward 1 that will only 
terminate the episode once all of them are retrieved
    - name: `GoodGoalMulti`
    - default size `(1,1,1)`
    - can rotate 360 degrees
    - size range `(0.5,0.5,0.5)-(5,5,5)`
    - cannot randomize color
    - terminates episode only when all GoodGoalsMulti (and a GoodGoal if present) are collected