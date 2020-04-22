import uuid
from typing import NamedTuple
from typing import Optional, List
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.rpc_communicator import UnityTimeOutException
from mlagents_envs.side_channel.raw_bytes_channel import RawBytesChannel
from mlagents_envs.side_channel.side_channel import SideChannel
from mlagents_envs.side_channel.engine_configuration_channel import (
    EngineConfig,
    EngineConfigurationChannel,
)
from animalai.envs.arena_config import ArenaConfig


class PlayTrain(NamedTuple):
    play: int
    train: int


class AnimalAIEnvironment(UnityEnvironment):
    # Default values for configuration parameters of the environment, can be changed if needed
    # Increasing the timescale value for training might speed up the process on powefull machines
    # but take care as the higher the timescale the more likely the physics might break
    WINDOW_WIDTH = PlayTrain(play=1200, train=80)
    WINDOW_HEIGHT = PlayTrain(play=800, train=80)
    QUALITY_LEVEL = PlayTrain(play=5, train=1)
    TIMESCALE = PlayTrain(play=1, train=300)
    TARGET_FRAME_RATE = PlayTrain(play=60, train=-1)
    ARENA_CONFIG_SC_UUID = "9c36c837-cad5-498a-b675-bc19c9370072"

    def __init__(
        self,
        file_name: Optional[str] = None,
        worker_id: int = 0,
        base_port: int = 5005,
        seed: int = 0,
        # docker_training: bool = False, # Will be removed in final version
        n_arenas: int = 1,
        play: bool = False,
        arenas_configurations: ArenaConfig = None,
        inference: bool = False,
        camera_width: int = None,
        camera_height: int = None,
        grayscale: bool = False,
        side_channels: Optional[List[SideChannel]] = None,
    ):

        args = self.executable_args(
            n_arenas, play, camera_height, camera_width, grayscale
        )
        self.play = play
        self.inference = inference
        self.timeout = 10 if play else 60
        self.side_channels = side_channels if side_channels else []
        self.arenas_parameters_side_channel = None

        self.configure_side_channels(self.side_channels)

        super().__init__(
            file_name=file_name,
            worker_id=worker_id,
            base_port=base_port,
            seed=seed,
            no_graphics=False,
            timeout_wait=self.timeout,
            args=args,
            side_channels=self.side_channels,
        )
        self.reset(arenas_configurations)

    def configure_side_channels(self, side_channels: List[SideChannel]) -> None:

        contains_engine_config_sc = any(
            [isinstance(sc, EngineConfigurationChannel) for sc in side_channels]
        )
        if not contains_engine_config_sc:
            self.side_channels.append(self.create_engine_config_side_channel())
        contains_arena_config_sc = any(
            [sc.channel_id == self.ARENA_CONFIG_SC_UUID for sc in side_channels]
        )
        if not contains_arena_config_sc:
            self.arenas_parameters_side_channel = RawBytesChannel(
                channel_id=uuid.UUID(self.ARENA_CONFIG_SC_UUID)
            )
            self.side_channels.append(self.arenas_parameters_side_channel)

    def create_engine_config_side_channel(self) -> EngineConfigurationChannel:

        if self.play or self.inference:
            engine_configuration = EngineConfig(
                width=self.WINDOW_WIDTH.play,
                height=self.WINDOW_HEIGHT.play,
                quality_level=self.QUALITY_LEVEL.play,
                time_scale=self.TIMESCALE.play,
                target_frame_rate=self.TARGET_FRAME_RATE.play,
            )
        else:
            engine_configuration = EngineConfig(
                width=self.WINDOW_WIDTH.train,
                height=self.WINDOW_HEIGHT.train,
                quality_level=self.QUALITY_LEVEL.train,
                time_scale=self.TIMESCALE.train,
                target_frame_rate=self.TARGET_FRAME_RATE.train,
            )
        engine_configuration_channel = EngineConfigurationChannel()
        engine_configuration_channel.set_configuration(engine_configuration)
        return engine_configuration_channel

    def reset(self, arenas_configurations: ArenaConfig = None) -> None:
        if arenas_configurations:
            arenas_configurations_proto = arenas_configurations.to_proto()
            arenas_configurations_proto_string = (
                arenas_configurations_proto.SerializeToString()
            )
            self.arenas_parameters_side_channel.send_raw_data(
                bytearray(arenas_configurations_proto_string)
            )
        try:
            super().reset()
        except UnityTimeOutException as timeoutException:
            if self.play:
                pass
            else:
                raise timeoutException

    @staticmethod
    def executable_args(
        n_arenas: int = 1,
        play: bool = False,
        camera_height: int = 84,
        camera_width: int = 84,
        grayscale: bool = False,
    ) -> List[str]:
        args = ["--playerMode"]
        if play:
            args.append("1")
        else:
            args.append("0")
        args.append("--numberOfArenas")
        args.append(str(n_arenas))
        if camera_width:
            args.append("--cameraWidth")
            args.append(str(camera_width))
        if camera_height:
            args.append("--cameraHeight")
            args.append(str(camera_height))
        if grayscale:
            args.append("--grayscale")
        return args
