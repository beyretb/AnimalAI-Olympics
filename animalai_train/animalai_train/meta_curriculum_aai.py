"""Contains the MetaCurriculum class."""
import os
from typing import Dict
from mlagents.trainers.meta_curriculum import MetaCurriculum
from mlagents.trainers.exception import MetaCurriculumError
from animalai_train.curriculum_aai import CurriculumAAI

import logging

logger = logging.getLogger("mlagents.trainers")


class MetaCurriculumAAI(MetaCurriculum):
    """A MetaCurriculum holds curricula. Each curriculum is associated to a
    particular brain in the environment.
    """

    def __init__(self, curriculum_folder: str):
        """Initializes a MetaCurriculum object.

        :param curriculum_folder: Dictionary of brain_name to the
          Curriculum for each brain.
        """
        self._brains_to_curricula: Dict[str, CurriculumAAI] = {}
        try:
            json_files = [
                file
                for file in os.listdir(curriculum_folder)
                if ".json" in file.lower()
            ]
            for curriculum_filename in json_files:
                brain_name = curriculum_filename.split(".")[0]
                curriculum_filepath = os.path.join(
                    curriculum_folder, curriculum_filename
                )
                curriculum = CurriculumAAI(brain_name, curriculum_filepath)
                self._brains_to_curricula[brain_name] = curriculum
        except NotADirectoryError:
            raise MetaCurriculumError(
                curriculum_folder + " is not a "
                "directory. Refer to the ML-Agents "
                "curriculum learning docs."
            )

    def get_config(self):
        """Get the combined configuration of all curricula in this
        MetaCurriculum.

        :return: A dict from parameter to value.
        """
        config = None

        for _, curriculum in self.brains_to_curricula.items():
            config = curriculum.get_config()

        return config
