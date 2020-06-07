from typing import NamedTuple, Dict, Optional
from animalai.envs.arena_config import ArenaConfig


class RunOptionsAAI(NamedTuple):
    trainer_config: Dict = None
    debug: bool = False
    seed: int = 0
    env_path: Optional[str] = None
    run_id: str = "ppo"
    load_model: bool = False
    train_model: bool = True
    save_freq: int = 50000
    keep_checkpoints: int = 5
    base_port: int = 5005
    num_envs: int = 1
    curriculum_config: str = None
    lesson: int = 0
    # multi_gpu: bool = False   # Will be added in later version
    # docker_target_name: Optional[str] = None
    cpu: bool = False
    width: int = 84
    height: int = 84
    n_arenas_per_env: int = 1
    arena_config: ArenaConfig = None
    resolution: int = 84

    """
    trainer_config:     Hyperparameters for your training model
    debug:              Whether to run in debug mode with detailed logging
    seed:               Random seed used for training
    env_path:           Path to the AnimalAI executable
    run_id:             The directory name for model and summary statistics
    load_model:         Whether to load the model or randomly initialize
    train_model:        Whether to train model, or only run inference
    save_freq:          Frequency at which to save model
    keep_checkpoints:   How many model checkpoints to keep
    base_port:          Base port for environment communication
    num_envs:           Number of parallel environments to use for training
    curriculum_config:  Path to curriculum training folder
    lesson:             Start learning from this lesson if using curriculum
    multi_gpu:          Whether or not to use multiple GPU (not in current version)
    cpu:                Run with CPU only
    width:              The width of the executable window of the environment(s)
    height:             The height of the executable window of the environment(s)
    n_arenas_per_env:   Number of arenas (number of agents) per env environment instance
    arena_config:       Configuration file for the training arenas
    resolution:         Resolution for the visual observation camera of the agent (NxN if resolution=N)
    """
