from typing import Optional

from mlagents.trainers.trainer_controller import TrainerController
from mlagents.trainers.env_manager import EnvManager
from mlagents_envs.timers import timed
from mlagents.trainers.trainer_util import TrainerFactory
from mlagents.trainers.sampler_class import SamplerManager
from animalai_train.meta_curriculum_aai import MetaCurriculumAAI


class TrainerControllerAAI(TrainerController):
    def __init__(
        self,
        trainer_factory: TrainerFactory,
        model_path: str,
        summaries_dir: str,
        run_id: str,
        save_freq: int,
        meta_curriculum: Optional[MetaCurriculumAAI],
        train: bool,
        training_seed: int,
    ):
        # we remove the sampler manager as it is irrelevant for AAI
        super().__init__(
            trainer_factory=trainer_factory,
            model_path=model_path,
            summaries_dir=summaries_dir,
            run_id=run_id,
            save_freq=save_freq,
            meta_curriculum=meta_curriculum,
            train=train,
            training_seed=training_seed,
            sampler_manager=SamplerManager(reset_param_dict={}),
            resampling_interval=None,
        )

    @timed
    def _reset_env(self, env: EnvManager) -> None:
        """Resets the environment.

        Returns:
            A Data structure corresponding to the initial reset state of the
            environment.
        """
        new_meta_curriculum_config = (
            self.meta_curriculum.get_config() if self.meta_curriculum else None
        )
        env.reset(config=new_meta_curriculum_config)
