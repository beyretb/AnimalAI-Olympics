import json
import jsonpickle
import yaml
import copy
import numpy as np

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

    def __init__(self, t=1000, rand_all_colors=False, items=None, blackouts=None):
        self.t = t
        self.rand_all_colors = rand_all_colors
        self.items = items if items is not None else {}
        self.blackouts = blackouts if blackouts is not None else []
        self.generate_blackout_steps()

    def generate_blackout_steps(self):
        # Transform a list of steps at which we turn on/off the light into a list of 1/0 of size t for each step

        if self.blackouts is not None and len(self.blackouts) > 0:
            if self.blackouts[0]>0:
                self.blackouts_steps = np.ones(self.t)
                light = True
                for i in range(len(self.blackouts) - 1):
                    self.blackouts_steps[self.blackouts[i]:self.blackouts[i + 1]] = not light
                    light = not light
                self.blackouts_steps[self.blackouts[-1]:] = not light
            else:
                flip_every = -self.blackouts[0]
                self.blackouts_steps = np.array(([1]*flip_every + [0]*flip_every)*(self.t//(2*flip_every)+1))[:self.t]
        else:
            self.blackouts_steps = np.ones(self.t)


class ArenaConfig(yaml.YAMLObject):
    yaml_tag = u'!ArenaConfig'

    def __init__(self, yaml_path=None):

        if yaml_path is not None:
            self.arenas = yaml.load(open(yaml_path, 'r'), Loader=yaml.Loader).arenas
            for arena in self.arenas.values():
                arena.generate_blackout_steps()
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
            for item in self.arenas[k].items:
                to_spawn = config_out.arenas[k].items.add()
                to_spawn.name = item.name
                to_spawn.rand_color = item.rand_color
                to_spawn.positions.extend([v.to_proto() for v in item.positions])
                to_spawn.rotations.extend(item.rotations)
                to_spawn.sizes.extend([v.to_proto() for v in item.sizes])

        return config_out

    def update(self, arenas_configurations_input):

        if arenas_configurations_input is not None:
            for arena_i in arenas_configurations_input.arenas:
                self.arenas[arena_i] = copy.copy(arenas_configurations_input.arenas[arena_i])
                self.arenas[arena_i].generate_blackout_steps()


def constructor_arena(loader, node):
    fields = loader.construct_mapping(node)
    return Arena(**fields)


def constructor_item(loader, node):
    fields = loader.construct_mapping(node)
    return Item(**fields)


yaml.add_constructor(u'!Arena', constructor_arena)
yaml.add_constructor(u'!Item', constructor_item)
