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


def constructor_arena(loader, node) :
    fields = loader.construct_mapping(node)
    return Arena(**fields)


def constructor_item(loader, node) :
    fields = loader.construct_mapping(node)
    return Item(**fields)


yaml.add_constructor(u'!Arena', constructor_arena)
yaml.add_constructor(u'!Item', constructor_item)


# conf = ArenaConfig()
#
# arena1 = Arena()
# arena2 = Arena()
# arena3 = Arena()
# arena4 = Arena()
#
# pos1 = Vector3(10,0,10)
# pos2 = Vector3(-10,0,10)
# pos3 = Vector3(-10,0,-10)
# pos4 = Vector3(30,0,5)
# pos5 = Vector3(10.5,0,0.854)
# pos6 = Vector3(22,0,-12)
# rot1 = 10.5
# rot2 = 70.5
# rot3 = 142.5
# rot4 = -95.5
# rot5 = 360.5
# scale1 = Vector3(1,2,3)
# scale2 = Vector3(0.5,0.5,0.5)
#
#
# item1 = Item(name='Cardbox1', rand_color=False, rand_scale=False, positions=[pos1], rotations=[rot1], scales=[scale2])
# item2 = Item(name='Cardbox2', rand_color=False, rand_scale=False, positions=[pos2],)
# item3 = Item(name='Woodbox1', rand_color=False, rand_scale=False)
# item4 = Item(name='Woodbox2', rand_color=False, rand_scale=False, positions=[pos2,pos3], rotations=[rot2,rot3],
#              scales=[scale2,scale1])
# item5 = Item(name='Woodbox3', rand_scale=True)
# item6 = Item(name='CubeRigid', rand_color=False, rand_scale=False,positions=[pos4,pos5])
# item7 = Item(name='InnerWall', rand_color=True)
# item8 = Item(name='Cylinder', rand_color=True, rand_scale=True)
# item9 = Item(name='CubeTunnel', rand_color=True, rand_scale=False, positions=[pos6])
# item10 = Item(name='MazeGenerator', rand_color=True, positions=[pos1])
#
# arena1.items = [item1, item2]
# arena2.items = [item3, item4]
# arena3.items = [item5, item6, item7, item1]
# arena4.items = [item10]
#
# conf.arenas = {0:arena1, 1: arena2, 2: arena3, 3: arena4}
#
# # yaml.dump(conf, open('configArenas.yaml', 'w'))
#
# arenasOut = yaml.load(open('configArenas.yaml','r'), Loader=yaml.Loader)
# print('ok')