# %%

# The markers "# %%" separate code blocks for execution (cells) 
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%

from build123d import BuildPart, Box, Location, Compound, copy, mirror, Plane
from ocp_vscode import show

thickness = 1.8

width = 174.5
height = 264.5
depth = 59
inner_depth = 59 - thickness
sub_depth = 30
offset = thickness / 2

side_height = height - thickness

with BuildPart() as side:
    Box(thickness, inner_depth, side_height)

with BuildPart() as top:
    Box(width, inner_depth, thickness)

with BuildPart() as back:
    Box(width, thickness, height)

frame = Compound(children=[
    copy.copy(side.part).locate(
        Location((offset, inner_depth / 2, side_height / 2))
    ),
    copy.copy(side.part).locate(
        Location((width - offset, inner_depth / 2, side_height / 2))
    ),
    copy.copy(side.part).locate(
        Location((width / 2 - sub_depth - offset, inner_depth / 2, side_height / 2))
    ),
    copy.copy(side.part).locate(
        Location((width / 2 + sub_depth + offset, inner_depth / 2, side_height / 2))
    ),
    copy.copy(top.part).locate(
        Location((width / 2, inner_depth / 2, side_height + offset))
    ),
    copy.copy(back.part).locate(
        Location((width / 2, depth - offset, height / 2))
    ),
])

show(frame)

# %%


bottom_height = 12
pants_height = 67
pants_width = 35
dress_height = 102

plank_width = width / 2 - sub_depth - 2 * thickness
plank_horizontal_location = plank_width / 2 + thickness

with BuildPart() as full_plank:
    Box(plank_width, inner_depth, thickness)

bottom_y = bottom_height + offset
pants_y = bottom_y + pants_height + thickness

pants_plank_width = pants_width + thickness
with BuildPart() as pants_plank:
    Box(pants_plank_width, inner_depth - thickness, thickness)

with BuildPart() as pants_side:
    Box(thickness, inner_depth - thickness, pants_height)

dress_y = pants_y + dress_height + thickness

plank_children = [
    copy.copy(full_plank.part).locate(
        Location((
            plank_horizontal_location,
            inner_depth / 2,
            bottom_y
        ))
    ),
    copy.copy(pants_plank.part).locate(
        Location((
            -pants_plank_width / 2 + thickness + plank_width,
            inner_depth / 2,
            pants_y
        ))
    ),
    copy.copy(pants_side.part).locate(
        Location((
            plank_width - pants_plank_width + offset + thickness,
            inner_depth / 2,
            bottom_y + pants_height / 2 + offset
        ))
    ),
]

top_section_height = side_height - dress_y
plank_count = 3
top_plank_space = (top_section_height + offset) / plank_count

plank_children += [
    copy.copy(full_plank.part).locate(
        Location((
            plank_horizontal_location,
            inner_depth / 2,
            top_plank_space * i + dress_y
        ))
    ) for i in range(plank_count)
]
planks = Compound(children=plank_children)

show(planks)

# %%

wheel_height = 2.8
rail_height = 4
sub_height = side_height - thickness * 2 - wheel_height - rail_height
sub_lift = offset + wheel_height
sub_plank_width = sub_depth - thickness

with BuildPart() as sub_back:
    Box(thickness, inner_depth, sub_height)

with BuildPart() as sub_side:
    Box(sub_depth - thickness, thickness, sub_height)

with BuildPart() as sub_top:
    Box(sub_depth, inner_depth, thickness)

with BuildPart() as sub_plank:
    Box(sub_plank_width, inner_depth - thickness * 2, thickness)

sub_plank_count = 10

sub_closet_children = [
    copy.copy(sub_back.part).locate(
        Location((
            sub_depth - thickness,
            inner_depth / 2,
            sub_height / 2 + sub_lift + offset
        ))
    ),
    copy.copy(sub_side.part).locate(
        Location((
            sub_depth / 2 - thickness,
            inner_depth - offset,
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
            inner_depth / 2,
            sub_height + sub_lift + thickness
        ))
    ),
    copy.copy(sub_top.part).locate(
        Location((
            sub_depth / 2 - offset,
            inner_depth / 2,
            sub_lift
        ))
    ),
] + [
    copy.copy(sub_plank.part).locate(
        Location((
            sub_plank_width / 2 - offset,
            inner_depth / 2,
            (i + 1) * sub_height / sub_plank_count + sub_lift + thickness
        ))
    ) for i in range(sub_plank_count) if i < sub_plank_count - 1
]

sub_closet = Compound(children=sub_closet_children)

show(sub_closet)
# %%

open_sub_depth = inner_depth / 2

# mirror twice to group together in exploded view.
closet = Compound(children=[
    mirror(mirror(copy.copy(frame))),
    mirror(mirror(copy.copy(planks))),
    mirror(copy.copy(planks), about=Plane.YZ).locate(
        Location((width, 0, 0))
    ),
    mirror(mirror(copy.copy(sub_closet).locate(
        Location((width / 2 - sub_depth + offset, - open_sub_depth, 0))
    ))),
    mirror(copy.copy(sub_closet), about=Plane.YZ).locate(
        Location((width / 2 + sub_depth - offset, - inner_depth, 0))
    ),
])

show(closet)
# %%