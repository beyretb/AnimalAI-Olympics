import json
import jsonpickle
import yaml

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


class Item(yaml.YAMLObject):
    yaml_tag = u'!Item'

    def __init__(self, name='', rand_color=False, positions=None, rotations=None, sizes=None):
        self.name = name
        self.rand_color = rand_color
        self.positions = positions if positions is not None else []
        self.rotations = rotations if rotations is not None else []
        self.sizes = sizes if sizes is not None else []


class Arena(yaml.YAMLObject):
    yaml_tag = u'!Arena'

    def __init__(self, t=1000, rand_all_colors=False, rand_all_sizes=False, items=None):
        self.t = t
        self.rand_all_colors = rand_all_colors
        self.rand_all_sizes = rand_all_sizes
        self.items = items if items is not None else {}


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
            config_out.arenas[k].rand_all_colors = self.arenas[k].rand_all_colors
            config_out.arenas[k].rand_all_sizes = self.arenas[k].rand_all_sizes
            for item in self.arenas[k].items:
                to_spawn = config_out.arenas[k].items.add()
                to_spawn.name = item.name
                to_spawn.rand_color = item.rand_color
                to_spawn.positions.extend([v.to_proto() for v in item.positions])
                to_spawn.rotations.extend(item.rotations)
                to_spawn.sizes.extend([v.to_proto() for v in item.sizes])

        return config_out


def constructor_arena(loader, node):
    fields = loader.construct_mapping(node)
    return Arena(**fields)


def constructor_item(loader, node):
    fields = loader.construct_mapping(node)
    return Item(**fields)


yaml.add_constructor(u'!Arena', constructor_arena)
yaml.add_constructor(u'!Item', constructor_item)
