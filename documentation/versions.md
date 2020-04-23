# Previous versions details

- v1.1.1
    - Hotfix curriculum loading in the wrong order
    
- v1.1.0
    - Add curriculum learning to `animalai-train` to use yaml configurations

- v1.0.5
    - ~~Adds customisable resolution during evaluation~~ (removed, evaluation is only `84x84`)
    - Update `animalai-train` to tf 1.14 to fix `gin` broken dependency
    - Release source code for the environment (no support to be provided on this for now)
    - Fixes some legacy dependencies and typos in both libraries
    
- v1.0.3
    - Adds inference mode to Gym environment
    - Adds seed to Gym Environment
    - Submission example folder containing a trained agent
    - Provide submission details for the competition
    - Documentation for training on AWS

- v1.0.2
    - Adds custom resolution for docker training as well
    - Fix version checker

- v1.0.0
    - Adds custom resolution to both Unity and Gym environments
    - Adds inference mode to the environment to visualize trained agents
    - Prizes announced
    - More details about the competition

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
