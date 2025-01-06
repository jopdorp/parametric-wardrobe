# %%
# Jupyter cell configuration
# The markers "# %%" separate code blocks for execution (cells) 
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%
from build123d import (
    BuildPart,
    Box,
    Location,
    Compound,
    copy,
    mirror,
    Plane,
    Cylinder,
    Axis,
    import_step,
    Matrix,
    Color,
    Part
)
from ocp_vscode import show

###############################################################################
#                              GLOBAL PARAMETERS                              #
#                    CUSTOMIZE THE SIZES TO FIT YOUR NEEDS                    #
###############################################################################
thickness = 1.8
back_thickness = 1.2

width = 174.5
height = 264.5
depth_budget = 59.0
mirror_thickness = 0.4
sub_depth = 30.0
inner_margin = 0.6

wheel_height = 2.8
rail_height = 1.9

sub_back_thickness = 1.8

# Plank system parameters
bottom_height = 12.0
pants_width = 34.5
dress_height = 102.5
bar_height = 3.0
bar_width = 1.5
bar_spacing = 4.5

pants_height_left = 73.0
pants_height_right = 63.0

# Derived parameters
door_thickness = thickness + mirror_thickness
depth = depth_budget + door_thickness
inner_depth = depth - back_thickness
offset = thickness / 2
back_offset = back_thickness / 2
side_height = height - thickness

plank_width = width / 2 - sub_depth - 2 * thickness - inner_margin * 2

plank_horizontal_location = plank_width / 2 + thickness


sub_height = side_height - thickness * 2 - wheel_height - rail_height
sub_lift = offset + wheel_height

sub_back_offset = sub_back_thickness / 2

sub_plank_depth = sub_depth - sub_back_thickness
sub_plank_width = inner_depth - thickness * 2

open_sub_depth = inner_depth / 2


def get_plank_heights(pants_height):
    bottom_y = bottom_height + offset
    pants_y = bottom_y + pants_height + thickness
    dress_y = pants_y + dress_height + thickness
    return bottom_y, pants_y, dress_y


# %%
###############################################################################
#                             MAIN FRAME ASSEMBLY                             #
#                   Includes sides, top, back, and rails                      #
###############################################################################
with BuildPart() as side:
    Box(thickness, inner_depth, side_height)

with BuildPart() as top:
    Box(width, inner_depth, thickness)

with BuildPart() as back:
    Box(width, back_thickness, height)

sides_right = Part(Compound(children=[
    copy.copy(side.part).locate(
        Location((width - offset, inner_depth / 2, side_height / 2))
    ),
    copy.copy(side.part).locate(
        Location((
            width - thickness - offset - plank_width,
            inner_depth / 2,
            side_height / 2
        ))
    ),
]))

frame = Compound(children=[
    copy.copy(side.part).locate(
        Location((offset, inner_depth / 2, side_height / 2))
    ),
    copy.copy(side.part).locate(
        Location((
            plank_width + thickness + offset,
            inner_depth / 2,
            side_height / 2
        ))
    ),
    sides_right,
    copy.copy(top.part).locate(
        Location((width / 2, inner_depth / 2, side_height + offset))
    ),
    copy.copy(back.part).locate(
        Location((width / 2, depth - back_offset, height / 2))
    )
])

frame.color = Color(0.7, 0.5, 0.2)
show(frame)
# %%
###############################################################################
#                                    RAILS                                    #
#                      Connects the subclosets to the frame                   #
###############################################################################
sub_rail = import_step("rail.stp")
sub_rail = Part(sub_rail.children[0])
sub_rail = sub_rail.rotate(axis=Axis.X, angle=-90)

rails = Compound(children=[
    copy.copy(sub_rail).transform_geometry(Matrix(
        (
            (0.1, 0, 0, 0),
            (0, 0.055, 0, 0),
            (0, 0, 0.1, 0),
            (0, 0, 0, 1)
        )
    )).locate(
        Location((
            width / 2 - sub_depth / 2 + sub_back_offset - 2/3 * inner_margin,
            inner_depth,
            side_height
        ))
    ),
    copy.copy(sub_rail).transform_geometry(Matrix(
        (
            (0.1, 0, 0, 0),
            (0, 0.073, 0, 0),
            (0, 0, 0.1, 0),
            (0, 0, 0, 1)
        )
    )).locate(
        Location((
            width / 2 + sub_depth / 2 - sub_back_offset + 2/3 * inner_margin,
            inner_depth,
            side_height
        ))
    )
])
show(rails)

# %%
with BuildPart() as bar_cylinder:
    Cylinder(bar_width / 2, plank_width, rotation=(0, 90, 0))

with BuildPart() as bar_box:
    Box(plank_width, bar_width, bar_height - bar_width)

bar = Part(shapes=[
    copy.copy(bar_cylinder.part) +
    copy.copy(bar_cylinder.part).locate(
        Location((
            0,
            0,
            bar_width
        ))
    ) +
    bar_box.part.locate(
        Location((
            0,
            0,
            bar_width / 2
        ))
    )
])


_, _, dress_y_left = get_plank_heights(pants_height_left)

bar_left = copy.copy(bar).locate(
    Location((
        plank_horizontal_location,
        inner_depth / 2,
        dress_y_left - offset - bar_height / 2 - bar_spacing - bar_width / 2
    ))
),

_, _, dress_y_right = get_plank_heights(pants_height_right)

bar_right = copy.copy(bar).locate(
    Location((
        width - plank_horizontal_location,
        inner_depth / 2,
        dress_y_right - offset - bar_height / 2 - bar_spacing - bar_width / 2
    ))
),
show(bar_left, bar_right)
# %%
###############################################################################
#                            HARDWARE ASSEMBLY                                #
#                         Includes hangers and bars                           #
###############################################################################
hardware = Compound(children=[
    rails,
    Compound(bar_left),
    Compound(bar_right)
])
hardware.color = Color(0.7, 0.7, 0.7)
show(hardware)
# %%
###############################################################################
#                          PLANK SYSTEM ASSEMBLY                              #
#              Creates internal organization system and hangers               #
###############################################################################


def create_planks(pants_height):
    bottom_y, pants_y, dress_y = get_plank_heights(pants_height)
    with BuildPart() as full_plank:
        Box(plank_width, inner_depth, thickness)

    with BuildPart() as bottom_front_plank:
        Box(plank_width, thickness, bottom_height)

    pants_plank_width = pants_width + thickness
    with BuildPart() as pants_plank:
        Box(pants_plank_width, inner_depth - thickness, thickness)

    with BuildPart() as pants_side:
        Box(thickness, inner_depth - thickness, pants_height)

    plank_children = [
        copy.copy(full_plank.part).locate(
            Location((
                plank_horizontal_location,
                inner_depth / 2,
                bottom_y
            ))
        ),
        copy.copy(bottom_front_plank.part).locate(
            Location((
                plank_horizontal_location,
                thickness / 2,
                bottom_height / 2
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
    return Compound(children=plank_children)


planks_left = create_planks(pants_height_left)
planks_left.color = Color(0.8, 0.7, 0.5)
planks_right = create_planks(pants_height_right)
planks_right = Part(mirror(planks_right, about=Plane.YZ))
planks_right.color = Color(0.8, 0.7, 0.5)

show(planks_left, planks_right)
# %%

###############################################################################
#                           SUB CLOSET ASSEMBLY                               #
#                 Creates the smaller storage compartments                    #
###############################################################################
with BuildPart() as sub_back:
    Box(sub_back_thickness, inner_depth, sub_height)

with BuildPart() as sub_side:
    Box(sub_depth - sub_back_thickness, thickness, sub_height)

with BuildPart() as sub_top:
    Box(sub_depth, inner_depth, thickness)

with BuildPart() as sub_plank:
    Box(sub_plank_depth, sub_plank_width, thickness)

sub_plank_count = 10

sub_closet_children = [
    copy.copy(sub_back.part).locate(
        Location((
            sub_depth - sub_back_thickness,
            inner_depth / 2,
            sub_height / 2 + sub_lift + offset
        ))
    ),
    copy.copy(sub_side.part).locate(
        Location((
            sub_depth / 2 - sub_back_thickness,
            inner_depth - offset,
            sub_height / 2 + sub_lift + offset
        ))
    ),
    copy.copy(sub_side.part).locate(
        Location((
            sub_depth / 2 - sub_back_thickness,
            offset,
            sub_height / 2 + sub_lift + offset
        ))
    ),
    copy.copy(sub_top.part).locate(
        Location((
            sub_depth / 2 - sub_back_offset,
            inner_depth / 2,
            sub_height + sub_lift + thickness
        ))
    ),
    copy.copy(sub_top.part).locate(
        Location((
            sub_depth / 2 - sub_back_offset,
            inner_depth / 2,
            sub_lift
        ))
    ),
] + [
    copy.copy(sub_plank.part).locate(
        Location((
            sub_plank_depth / 2 - back_offset,
            inner_depth / 2,
            (i + 1) * sub_height / sub_plank_count + sub_lift + thickness
        ))
    ) for i in range(sub_plank_count) if i < sub_plank_count - 1
]


sub_closet = Compound(children=sub_closet_children)
sub_closet.color = Color(0.7, 0.5, 0.3)
sub_closet_left = copy.copy(sub_closet).locate(
    Location((
        width / 2 - sub_depth + sub_back_offset - 2/3 * inner_margin,
        -open_sub_depth,
        0
    ))
)

sub_closet_right = mirror(copy.copy(sub_closet), about=Plane.YZ).locate(
    Location((
        width / 2 + sub_depth - sub_back_offset + 2/3 * inner_margin,
        -inner_depth,
        0
    ))
)
sub_closet_right.color = Color(0.7, 0.5, 0.3)

show(sub_closet_left, sub_closet_right)
# %%

###############################################################################
#                          FINAL CLOSET ASSEMBLY                              #
#                    Combines and mirrors all components                      #
###############################################################################

# mirror twice to group together in exploded view.

closet_children = [
    frame,
    hardware,
    planks_left,
    planks_right.locate(
        Location((width, 0, 0))
    ),
    sub_closet_left,
    sub_closet_right,
]
closet = Compound(children=closet_children)


show(closet_children)
# %%