# %%

# The markers "# %%" separate code blocks for execution (cells) 
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%

from build123d import BuildPart, Box, Location, Compound, copy, mirror, Plane
from ocp_vscode import show

width = 174.5
height = 264.5
depth = 59
thickness = 1.8
sub_depth = 30
offset = thickness / 2

side_height = height - thickness
with BuildPart() as side:
    Box(thickness, depth, side_height)

with BuildPart() as top:
    Box(width, depth, thickness)

frame = Compound(children=[
    copy.copy(side.part).locate(
        Location((offset, depth / 2, side_height / 2))
    ),
    copy.copy(side.part).locate(
        Location((width - offset, depth / 2, side_height / 2))
    ),
    copy.copy(side.part).locate(
        Location((width / 2 - sub_depth - offset, depth / 2, side_height / 2))
    ),
    copy.copy(side.part).locate(
        Location((width / 2 + sub_depth + offset, depth / 2, side_height / 2))
    ),
    copy.copy(top.part).locate(
        Location((width / 2, depth / 2, side_height + offset))
    ),
])

show(frame)

# %%

plank_width = width / 2 - sub_depth - 2 * thickness
plank_horizontal_location = plank_width / 2 + thickness
with BuildPart() as full_plank:
    Box(plank_width, depth, thickness)

bottom_drawers_height = 22
pants_height = 63
dress_height = 110

planks = Compound(children=[
    copy.copy(full_plank.part).locate(
        Location((
            plank_horizontal_location,
            depth / 2,
            bottom_drawers_height + offset
        ))
    ),
    copy.copy(full_plank.part).locate(
        Location((
            plank_horizontal_location,
            depth / 2,
            bottom_drawers_height + pants_height + offset
        ))
    ),
    copy.copy(full_plank.part).locate(
        Location((
            plank_horizontal_location,
            depth / 2,
            bottom_drawers_height + pants_height + dress_height + offset
        ))
    ),
])
show(planks)

# %%

wheel_height = 2.8
sub_height = side_height - thickness * 2 - wheel_height
sub_lift = offset + wheel_height
sub_plank_width = sub_depth - thickness

with BuildPart() as sub_back:
    Box(thickness, depth, sub_height)

with BuildPart() as sub_side:
    Box(sub_depth - thickness, thickness, sub_height)

with BuildPart() as sub_top:
    Box(sub_depth, depth, thickness)

with BuildPart() as sub_plank:
    Box(sub_plank_width, depth - thickness * 2, thickness)

sub_plank_count = 10

sub_closet_children = [
    copy.copy(sub_back.part).locate(
        Location((
            sub_depth - thickness,
            depth / 2,
            sub_height / 2 + sub_lift + offset
        ))
    ),
    copy.copy(sub_side.part).locate(
        Location((
            sub_depth / 2 - thickness,
            depth - offset,
            sub_height / 2 + sub_lift + offset
        ))
    ),
    copy.copy(sub_side.part).locate(
        Location((
            sub_depth / 2 - thickness,
            offset,
            sub_height / 2 + sub_lift + offset
        ))
    ),
    copy.copy(sub_top.part).locate(
        Location((
            sub_depth / 2 - offset,
            depth / 2,
            sub_height + sub_lift + thickness
        ))
    ),
    copy.copy(sub_top.part).locate(
        Location((
            sub_depth / 2 - offset,
            depth / 2,
            sub_lift
        ))
    ),
] + [
    copy.copy(sub_plank.part).locate(
        Location((
            sub_plank_width / 2 - offset,
            depth / 2,
            (i + 1) * sub_height / sub_plank_count + sub_lift + thickness
        ))
    ) for i in range(sub_plank_count) if i < sub_plank_count - 1
]

sub_closet = Compound(children=sub_closet_children)

# %%

open_sub_depth = depth / 2

closet = Compound(children=[
    frame,
    planks,
    copy.copy(planks).locate(
        Location((width / 2 + sub_depth, 0, 0))
    ),
    copy.copy(sub_closet).locate(
        Location((width / 2 - sub_depth + offset, - open_sub_depth, 0))
    ),
    mirror(copy.copy(sub_closet), about=Plane.YZ).locate(
        Location((width / 2 + sub_depth - offset, - depth, 0))
    ),
])

show(closet)
# %%