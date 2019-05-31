import json
import jsonpickle
import yaml
import copy

from animalai.communicator_objects import UnityRLResetInput, ArenaParametersProto

yaml.Dumper.ignore_aliases = lambda *args: True


class Vector3(yaml.YAMLObject):
    yaml_tag = u'!Vector3'

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def to_proto(self):
        res = ArenaParametersProto.ItemsToSpawn.Vector3()
        res.x = self.x
        res.y = self.y
        res.z = self.z

        return res


class RGB(yaml.YAMLObject):
    yaml_tag = u'!RGB'

    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def to_proto(self):
        res = ArenaParametersProto.ItemsToSpawn.Vector3()
        res.x = self.r
        res.y = self.g
        res.z = self.b

        return res


class Item(yaml.YAMLObject):
    yaml_tag = u'!Item'

    def __init__(self, name='', positions=None, rotations=None, sizes=None, colors=None):
        self.name = name
        self.positions = positions if positions is not None else []
        self.rotations = rotations if rotations is not None else []
        self.sizes = sizes if sizes is not None else []
        self.colors = colors if colors is not None else []


class Arena(yaml.YAMLObject):
    yaml_tag = u'!Arena'

    def __init__(self, t=1000, items=None, blackouts=None):
        self.t = t
        self.items = items if items is not None else {}
        self.blackouts = blackouts if blackouts is not None else []


class ArenaConfig(yaml.YAMLObject):
    yaml_tag = u'!ArenaConfig'

    def __init__(self, yaml_path=None):

        if yaml_path is not None:
            self.arenas = yaml.load(open(yaml_path, 'r'), Loader=yaml.Loader).arenas
        else:
            self.arenas = {}

    def save_config(self, json_path):
        out = jsonpickle.encode(self.arenas)
        out = json.loads(out)
        json.dump(out, open(json_path, 'w'), indent=4)

    def dict_to_arena_config(self) -> UnityRLResetInput:
        config_out = UnityRLResetInput()

        for k in self.arenas:
            config_out.arenas[k].CopyFrom(ArenaParametersProto())
            config_out.arenas[k].t = self.arenas[k].t
            config_out.arenas[k].blackouts.extend(self.arenas[k].blackouts)
            for item in self.arenas[k].items:
                to_spawn = config_out.arenas[k].items.add()
                to_spawn.name = item.name
                to_spawn.positions.extend([v.to_proto() for v in item.positions])
                to_spawn.rotations.extend(item.rotations)
                to_spawn.sizes.extend([v.to_proto() for v in item.sizes])
                to_spawn.colors.extend([v.to_proto() for v in item.colors])

        return config_out

    def update(self, arenas_configurations):

        if arenas_configurations is not None:
            for arena_i in arenas_configurations.arenas:
                self.arenas[arena_i] = copy.copy(arenas_configurations.arenas[arena_i])


def constructor_arena(loader, node):
    fields = loader.construct_mapping(node)
    return Arena(**fields)


def constructor_item(loader, node):
    fields = loader.construct_mapping(node)
    return Item(**fields)


yaml.add_constructor(u'!Arena', constructor_arena)
yaml.add_constructor(u'!Item', constructor_item)
