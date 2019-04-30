
## The ArenaConfig Structure
TODO: rewrite better

- arenas: array of Arena
- Arena: configuration for a single arena
    - t: maximum steps per episode
    - rand_all_colors: whether or not all items should have random colors
    - rand_all_scales: whether or not all items should have random scales
    - items: a list of Item representing the items that can be spawned in the arena
- Item: an item that can be spawned in the arena and its characteristics
    - name: name of the item, see below for an exhaustive list of items
    - rand_color: whether or not the item should have random colors
    - rand_scale: whether or not the item should have random scales
    - positions: list of Vector3 for objects position, will place a single one randomly if left empty
    - rotations: list of floats for objects rotation, will rotate randomly if left empty
    - scales: list of Vector3 for objects scales, will scale randomly if left empty
- Vector3: a simple vector structure
    - x,y,z: floats representing the objects coordinates relative to the center of an arena
    
    