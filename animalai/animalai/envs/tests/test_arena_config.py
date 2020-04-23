import pytest
import yaml
from unittest.mock import patch, mock_open

from animalai.envs.arena_config import (
    Vector3,
    RGB,
    Item,
    Arena,
    ArenaConfig,
    constructor_arena,
    constructor_item,
)

item_yaml = """
!Item
  name: Wall
  positions:
  - !Vector3 {x: 13.3, y: 0, z: 33}
  - !Vector3 {x: 26.6, y: 0, z: 33}
  sizes:
  - !Vector3 {x: 14, y: 3, z: 1}
  - !Vector3 {x: 14, y: 3, z: 1}
  - !Vector3 {x: 14, y: 3, z: 1}
  rotations: [90, 90,100,200]
  colors:
  - !RGB {r: 153, g: 153, b: 153}
"""

arena_yaml = """
!Arena
    pass_mark: 0
    t: 250
    blackouts: [50, 55, 75, 80, 100, 105, 115, 120, 125]
    items:
    - !Item
      name: WallTransparent
    - !Item
      name: GoodGoal
    - !Item
      name: Agent
"""

arena_config_yaml = """
!ArenaConfig
arenas:
  0: !Arena
    pass_mark: 2
    t: 250
    items:
    - !Item
      name: GoodGoalMulti
      sizes:
      - !Vector3 {x: 1, y: 1, z: 1}
      - !Vector3 {x: 1, y: 1, z: 1}
      - !Vector3 {x: 1, y: 1, z: 1}
  1: !Arena
    pass_mark: -1
    t: 250
    items:
    - !Item
      name: BadGoal
  2: !Arena
    pass_mark: 0
    t: 250
    items:
    - !Item
      name: GoodGoal
"""

arena_config_bad_yaml = """
!ArenaConfig
aaarenas:
  0: !Arena
    pass_mark: 2
    t: 250
    items:
    - !Item
      name: GoodGoalMulti
"""


@pytest.fixture(scope="session", autouse=True)
def yaml_config():
    print("called")
    yaml.add_constructor(u"!Arena", constructor_arena)
    yaml.add_constructor(u"!Item", constructor_item)


def test_vector3():
    vector3 = Vector3(x=10, y=15, z=20)
    assert vector3.x == 10
    assert vector3.y == 15
    assert vector3.z == 20

    vector3_proto = vector3.to_proto()
    assert vector3_proto.x == 10
    assert vector3_proto.y == 15
    assert vector3_proto.z == 20


def test_rgb():
    rgb = RGB(r=10, g=15, b=20)
    assert rgb.r == 10
    assert rgb.g == 15
    assert rgb.b == 20

    rgb_proto = rgb.to_proto()
    assert rgb_proto.x == 10
    assert rgb_proto.y == 15
    assert rgb_proto.z == 20


def test_item():
    item: Item = yaml.load(item_yaml, Loader=yaml.Loader)

    assert item.name == "Wall"
    assert len(item.positions) == 2
    assert len(item.sizes) == 3
    assert len(item.rotations) == 4
    assert len(item.colors) == 1

    item_proto = item.to_proto()
    assert item_proto.name == "Wall"
    assert len(item_proto.positions) == 2
    assert len(item_proto.sizes) == 3
    assert len(item_proto.rotations) == 4
    assert len(item_proto.colors) == 1


def test_arena():
    arena: Arena = yaml.load(arena_yaml, Loader=yaml.Loader)
    assert arena.pass_mark == 0
    assert arena.t == 250
    assert len(arena.blackouts) == 9
    assert len(arena.items) == 3

    arena_proto = arena.to_proto()
    assert arena.pass_mark == 0
    assert arena_proto.t == 250
    assert len(arena_proto.blackouts) == 9
    assert len(arena_proto.items) == 3


@patch("builtins.open", new_callable=mock_open, read_data=arena_config_yaml)
def test_arena_config(mock_yaml):

    arena_config = ArenaConfig(" ")
    assert len(arena_config.arenas) == 3

    arena_config_proto = arena_config.to_proto()
    assert len(arena_config_proto.arenas) == 3


@patch("builtins.open", new_callable=mock_open, read_data=arena_config_bad_yaml)
def test_bad_arena_config(mock_yaml):
    with pytest.raises(AttributeError):
        ArenaConfig(" ")


if __name__ == "__main__":
    pytest.main()
