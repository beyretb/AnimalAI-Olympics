import json
import math
import os

from mlagents.trainers.exception import (
    CurriculumConfigError,
    CurriculumError,
)
from mlagents.trainers.curriculum import Curriculum
import logging

from animalai.envs.arena_config import ArenaConfig

logger = logging.getLogger("mlagents.trainers")


class CurriculumAAI(Curriculum):
    def __init__(self, brain_name: str, curriculum_file: str):
        """
        Initializes a Curriculum object.
        :param brain_name: Name of the brain this Curriculum is associated with
        :param config: Dictionary of fields needed to configure the Curriculum
        """
        self.max_lesson_num = 0
        self.measure = None
        self._lesson_num = 0
        self.brain_name = brain_name

        try:
            with open(curriculum_file) as data_file:
                self.config = json.load(data_file)
        except IOError:
            raise CurriculumError(
                "The file {0} could not be found.".format(curriculum_file)
            )

        self.smoothing_value = 0.0
        for key in [
            "configuration_files",
            "measure",
            "thresholds",
            "min_lesson_length",
            "signal_smoothing",
        ]:
            if key not in self.config:
                raise CurriculumConfigError(
                    f"{brain_name} curriculum config does not contain a {key} field."
                )
        self.smoothing_value = 0
        self.measure = self.config["measure"]
        self.min_lesson_length = self.config["min_lesson_length"]
        self.max_lesson_num = len(self.config["thresholds"])

        configuration_files = self.config["configuration_files"]
        if len(configuration_files) != self.max_lesson_num + 1:
            raise CurriculumError(
                "The parameter {0} in the Curriculum must have {1} values "
                "but {2} were found".format(
                    key, self.max_lesson_num + 1, len(configuration_files)
                )
            )
        folder = os.path.dirname(curriculum_file)
        folder_yaml_files = os.listdir(folder)
        if not all([file in folder_yaml_files for file in configuration_files]):
            raise CurriculumError(
                "One or more configuration file(s) in the curriculum could not be found"
            )
        self.configurations = [
            ArenaConfig(os.path.join(folder, file)) for file in configuration_files
        ]

    def increment_lesson(self, measure_val: float) -> bool:
        """
        Increments the lesson number depending on the progress given.
        :param measure_val: Measure of progress (either reward or percentage
               steps completed).
        :return Whether the lesson was incremented.
        """
        if not self.config or not measure_val or math.isnan(measure_val):
            return False
        if self.config["signal_smoothing"]:
            measure_val = self.smoothing_value * 0.25 + 0.75 * measure_val
            self.smoothing_value = measure_val
        if self.lesson_num < self.max_lesson_num:
            if measure_val > self.config["thresholds"][self.lesson_num]:
                self.lesson_num += 1
                logger.info(
                    "{0} lesson changed. Now in lesson {1}: {2}".format(
                        self.brain_name,
                        self.lesson_num,
                        self.config["configuration_files"][self.lesson_num],
                    )
                )
                return True
        return False

    def get_config(self, lesson: int = None) -> ArenaConfig:
        """
        Returns reset parameters which correspond to the lesson.
        :param lesson: The lesson you want to get the config of. If None, the
               current lesson is returned.
        :return: The configuration of the reset parameters.
        """
        if not self.config:
            return None
        if lesson is None:
            lesson = self.lesson_num
        lesson = max(0, min(lesson, self.max_lesson_num))
        config = self.configurations[lesson]
        return config
