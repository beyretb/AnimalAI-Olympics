import yaml

from typing import List
from animalai.communicator_objects import (
    ArenasConfigurationsProto,
    ArenaConfigurationProto,
    ItemToSpawnProto,
    VectorProto,
)

yaml.Dumper.ignore_aliases = lambda *args: True


class Vector3(yaml.YAMLObject):
    yaml_tag = u"!Vector3"

    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = x
        self.y = y
        self.z = z

    def to_proto(self) -> VectorProto:
        vector_proto = VectorProto()
        vector_proto.x = self.x
        vector_proto.y = self.y
        vector_proto.z = self.z

        return vector_proto


class RGB(yaml.YAMLObject):
    yaml_tag = u"!RGB"

    def __init__(self, r: float = 0, g: float = 0, b: float = 0):
        self.r = r
        self.g = g
        self.b = b

    def to_proto(self) -> VectorProto:
        rgb_proto = VectorProto()
        rgb_proto.x = self.r
        rgb_proto.y = self.g
        rgb_proto.z = self.b

        return rgb_proto


class Item(yaml.YAMLObject):
    yaml_tag = u"!Item"

    def __init__(
        self,
        name: str = "",
        positions: List[Vector3] = None,
        rotations: List[float] = None,
        sizes: List[Vector3] = None,
        colors: List[RGB] = None,
    ):
        self.name = name
        self.positions = positions if positions is not None else []
        self.rotations = rotations if rotations is not None else []
        self.sizes = sizes if sizes is not None else []
        self.colors = colors if colors is not None else []

    def to_proto(self) -> ItemToSpawnProto:
        item_to_spawn_proto = ItemToSpawnProto()
        item_to_spawn_proto.name = self.name
        item_to_spawn_proto.positions.extend([v.to_proto() for v in self.positions])
        item_to_spawn_proto.rotations.extend(self.rotations)
        item_to_spawn_proto.sizes.extend([v.to_proto() for v in self.sizes])
        item_to_spawn_proto.colors.extend([v.to_proto() for v in self.colors])

        return item_to_spawn_proto


class Arena(yaml.YAMLObject):
    yaml_tag = u"!Arena"

    def __init__(
        self,
        t: int = 1000,
        items: List[Item] = None,
        pass_mark: float = 0,
        blackouts: List[int] = None,
    ):
        self.t = t
        self.items = items if items is not None else {}
        self.pass_mark = pass_mark
        self.blackouts = blackouts if blackouts is not None else []

    def to_proto(self) -> ArenaConfigurationProto:
        arena_configuration_proto = ArenaConfigurationProto()
        arena_configuration_proto.t = self.t
        arena_configuration_proto.pass_mark = self.pass_mark
        arena_configuration_proto.blackouts.extend(self.blackouts)
        arena_configuration_proto.items.extend([item.to_proto() for item in self.items])

        return arena_configuration_proto


class ArenaConfig(yaml.YAMLObject):
    yaml_tag = u"!ArenaConfig"

    def __init__(self, yaml_path: str = None):

        if yaml_path is not None:
            self.arenas = yaml.load(open(yaml_path, "r"), Loader=yaml.Loader).arenas
        else:
            self.arenas = {}

    # def save_config(self, json_path: str) -> None:
    #     out = jsonpickle.encode(self.arenas)
    #     out = json.loads(out)
    #     json.dump(out, open(json_path, "w"), indent=4)

    def to_proto(self, seed: int = -1) -> ArenasConfigurationsProto:
        arenas_configurations_proto = ArenasConfigurationsProto()
        arenas_configurations_proto.seed = seed

        for k in self.arenas:
            arenas_configurations_proto.arenas[k].CopyFrom(self.arenas[k].to_proto())

        return arenas_configurations_proto

    # def update(self, arenas_configurations:):
    #
    #     if arenas_configurations is not None:
    #         for arena_i in arenas_configurations.arenas:
    #             self.arenas[arena_i] = copy.copy(arenas_configurations.arenas[arena_i])


def constructor_arena(loader, node):
    fields = loader.construct_mapping(node)
    return Arena(**fields)


def constructor_item(loader, node):
    fields = loader.construct_mapping(node)
    return Item(**fields)


yaml.add_constructor(u"!Arena", constructor_arena)
yaml.add_constructor(u"!Item", constructor_item)
