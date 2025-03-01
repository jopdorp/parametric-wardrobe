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
    Part,
    chamfer,
)
from ocp_vscode import show
import math

# Manually set port
from ocp_vscode.comms import CMD_PORT, set_port
set_port(3939)  # Use a specific port number
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
sub_depth = 30.05
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
door_margin = 0.2

depth = depth_budget - door_thickness
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
sub_plank_width = inner_depth - thickness + mirror_thickness
sub_width = inner_depth + door_thickness

open_sub_depth = inner_depth / 2


def get_plank_heights(pants_height):
    bottom_y = bottom_height + offset
    pants_y = bottom_y + pants_height + thickness
    dress_y = pants_y + dress_height + thickness
    return bottom_y, pants_y, dress_y

# %%

# Define standard dowel sizes based on 12mm & 18mm wood thickness
# METRIC_DOWEL_SIZES = {
#     "6mm": (0.6, 3),  # Diameter, Length
#     "8mm": (0.8, 4),
#     "10mm": (1, 5),
# }

# class WoodenDowel(Part):
#     def __init__(self, size: str):
#         """Create a wooden dowel with rounded ends.

#         Args:
#             size (str): The dowel size (6mm, 8mm, or 10mm).
#         """
#         if size not in METRIC_DOWEL_SIZES:
#             raise ValueError(f"Invalid size {size}. Choose from {list(METRIC_DOWEL_SIZES.keys())}")

#         diameter, length = METRIC_DOWEL_SIZES[size]
#         radius = diameter / 2
#         filletlength = radius * 0.5  # Adjust rounding for realistic dowel ends

#         with BuildPart() as dowel:
#             Cylinder(radius, length)  # Create main dowel
            
#             # Select circular edges at the top and bottom
#             top_edge = dowel.edges().sort_by(Axis.Z)[-1]  # Highest edge
#             bottom_edge = dowel.edges().sort_by(Axis.Z)[0]  # Lowest edge

#             # Apply fillet correctly using the function, not as a method
#             chamfer([top_edge, bottom_edge], angle=30, length=filletlength)

#         super().__init__(dowel.part)

# # Example: Create an 8mm dowel for 18mm wood
# dowel_8mm = WoodenDowel("8mm")
# show(dowel_8mm)

# # %%

# ###############################################################################
# #                            DOWEL PLACEMENT                                 #
# #              Adding dowels along edges where panels connect                #
# ###############################################################################
# def face_normal(face):
#     verts = face.vertices()
#     if len(verts) < 3:
#         return (0, 0, 1)
#     # Use the first three vertices to compute a normal.
#     v1, v2, v3 = verts[:3]
#     a = (v2.X - v1.X, v2.Y - v1.Y, v2.Z - v1.Z)
#     b = (v3.X - v1.X, v3.Y - v1.Y, v3.Z - v1.Z)
#     # Cross product
#     cross = (a[1]*b[2] - a[2]*b[1],
#              a[2]*b[0] - a[0]*b[2],
#              a[0]*b[1] - a[1]*b[0])
#     mag = math.sqrt(cross[0]**2 + cross[1]**2 + cross[2]**2)
#     if mag == 0:
#         return (0, 0, 1)
#     return (cross[0]/mag, cross[1]/mag, cross[2]/mag)

# def vector_angle(v1, v2):
#     # Compute the angle between two normalized vectors.
#     dot = sum(a*b for a, b in zip(v1, v2))
#     # Clamp to avoid precision errors.
#     dot = max(min(dot, 1), -1)
#     return math.acos(dot)

# def cross_product(v1, v2):
#     return (
#         v1[1]*v2[2] - v1[2]*v2[1],
#         v1[2]*v2[0] - v1[0]*v2[2],
#         v1[0]*v2[1] - v1[1]*v2[0]
#     )

# from OCP.gp import gp_Ax1, gp_Pnt, gp_Dir

# def tuple_to_ax1(axis_tuple):
#     # Convert a tuple (x, y, z) to a gp_Ax1, setting the origin at (0,0,0)
#     return gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(*axis_tuple))

# def create_dowels_between_panels(panel_side_dowels, panel_front_dowels, spacing=10):
#     front_center = panel_front_dowels.center()
#     all_faces = panel_side_dowels.faces()
#     closest_face = min(all_faces, key=lambda face: vector_distance(face.center(), front_center))
    
#     closest_face_short_edge = closest_face.edges().sort_by(Axis.Y)[0]
#     center = closest_face_short_edge.center()
    
#     long_edge = closest_face.edges().sort_by(Axis.Y)[1]
#     length = long_edge.length
#     dowel_count = int(length / spacing) - 1
#     dowels = [
#         WoodenDowel("8mm").locate(
#             Location((
#                 center.X,
#                 center.Y + 1 + i * spacing,
#                 center.Z
#             ))
#         )
#         for i in range(dowel_count)
#     ]
    
#     # Rotate dowels so they are perpendicular to the face.
#     default_axis = (0, 0, 1)
#     n = face_normal(closest_face)
#     angle = vector_angle(default_axis, n)
#     rot_axis = cross_product(default_axis, n)
#     if math.sqrt(sum(c * c for c in rot_axis)) != 0:
#         rotation_axis = tuple_to_ax1(rot_axis)
#         for dowel in dowels:
#             dowel.rotate(axis=rotation_axis, angle=angle)
        
#     return Compound(dowels)
    
# # Example: Create dowels between two panels
# with BuildPart() as panel_side:
#     Box(2, 200, 20)
#     panel_side.part.label = "Side panel"

# with BuildPart() as panel_front:
#     Box(2, 200, 20)
#     panel_front.part.label = "Front panel"

# # rotate and locate the panels
# panel_side = copy(panel_side.part).rotate(axis=Axis.Y, angle=90)
# panel_front = copy(panel_front.part).locate(Location((11, 0, 9)))

# dowels = create_dowels_between_panels(panel_side, panel_front)
# show([panel_front, panel_side, dowels])
# %%
def vector_distance(v1, v2):
    return ((v1.X - v2.X)**2 + (v1.Y - v2.Y)**2 + (v1.Z - v2.Z)**2)**0.5

# %%
###############################################################################
#                             MAIN FRAME ASSEMBLY                             #
#                   Includes sides, top, back, and rails                      #
###############################################################################
def make_frame():
    with BuildPart() as side:
        Box(thickness, inner_depth, side_height)
        side.part.label = "Side panel"

    with BuildPart() as top:
        Box(width, inner_depth, thickness)
        top.part.label = "Top panel"

    with BuildPart() as back:
        Box(width, back_thickness, height)
        back.part.label = "Back panel"

    # Define panel positions
    left_side_pos = (offset, inner_depth / 2, side_height / 2)
    middle_left_pos = (plank_width + thickness + offset, inner_depth / 2, side_height / 2)
    middle_right_pos = (width - thickness - offset - plank_width, inner_depth / 2, side_height / 2)
    right_side_pos = (width - offset, inner_depth / 2, side_height / 2)
    top_pos = (width / 2, inner_depth / 2, side_height + offset)
    back_pos = (width / 2, depth - back_offset, height / 2)

    frame_left_side = copy(side.part).locate(Location(left_side_pos))
    frame_middle_left = copy(side.part).locate(Location(middle_left_pos))
    frame_middle_right = copy(side.part).locate(Location(middle_right_pos))
    frame_right_side = copy(side.part).locate(Location(right_side_pos))
    frame_top = copy(top.part).locate(Location(top_pos))
    frame_back = copy(back.part).locate(Location(back_pos))


    # left_top_dowels = create_dowels_between_panels(frame_left_side, frame_top)
    # create_dowels_between_panels(frame_middle_left, frame_top)
    # create_dowels_between_panels(frame_middle_right, frame_top)
    # create_dowels_between_panels(frame_right_side, frame_top)

    # create_dowels_between_panels(frame_left_side, frame_back)
    # create_dowels_between_panels(frame_middle_left, frame_back)
    # create_dowels_between_panels(frame_middle_right, frame_back)
    # create_dowels_between_panels(frame_right_side, frame_back)

    # show(left_top_dowels)

    return Compound(children=[
        frame_left_side,
        frame_middle_left,
        frame_middle_right,
        frame_right_side,
        frame_top,
        frame_back,
    ]) 

# Create the frame
frame = make_frame()
show(frame)


# %%
###############################################################################
#                                    RAILS                                    #
#                      Connects the subclosets to the frame                   #
###############################################################################

sub_rail = import_step("rail.stp")

sub_rail_right = Part(sub_rail.children[0])
sub_rail_left = Part(sub_rail.children[1])

sub_rail_right = sub_rail_right.rotate(axis=Axis.X, angle=-90)
sub_rail_left = sub_rail_left.rotate(axis=Axis.X, angle=-90)

rails = Compound(children=[
    copy(sub_rail_left).transform_geometry(Matrix(
        (
            (0.1, 0, 0, 0),
            (0, 0.06, 0, 0),
            (0, 0, 0.1, 0),
            (0, 0, 0, 1)
        )
    )).locate(
        Location((
            width / 2 - sub_depth / 2 + sub_back_offset - 2/3 * inner_margin - 22,
            inner_depth + 32,
            side_height
        ))
    ),
    copy(sub_rail_right).transform_geometry(Matrix(
        (
            (0.1, 0, 0, 0),
            (0, 0.06, 0, 0),
            (0, 0, 0.1, 0),
            (0, 0, 0, 1)
        )
    )).locate(
        Location((
            width / 2 + sub_depth / 2 - sub_back_offset + 2/3 * inner_margin,
            inner_depth - 6,
            side_height
        ))
    )
])
show(rails)

# %%
###############################################################################
#                               HANGING BARS                                  #
###############################################################################
with BuildPart() as bar_cylinder:
    Cylinder(bar_width / 2, plank_width, rotation=(0, 90, 0))

with BuildPart() as bar_box:
    Box(plank_width, bar_width, bar_height - bar_width)

bar = Part([
    copy(bar_cylinder.part) +
    copy(bar_cylinder.part).locate(
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

bar_left = copy(bar).locate(
    Location((
        plank_horizontal_location,
        inner_depth / 2,
        dress_y_left - offset - bar_height / 2 - bar_spacing - bar_width / 2
    ))
),

_, _, dress_y_right = get_plank_heights(pants_height_right)

bar_right = copy(bar).locate(
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
hardware = Compound([
    rails,
    Compound(bar_left),
    Compound(bar_right)
])
hardware.color = Color(0.7, 0.7, 0.7)
show(hardware)


# %%
##############################################################################
#                            DOOR SYSTEM ASSEMBLY                            #
#                Creates the doors with mirrors and handles                  #
##############################################################################
door_width = plank_width + thickness * 2 - door_margin * 2
with BuildPart() as door_wood:
    Box(door_width, thickness, height)
    door_wood.part.label = "Door"

with BuildPart() as door_mirror:
    Box(door_width, mirror_thickness, height)

door = Compound([
    copy(door_wood.part),
    copy(door_mirror.part).locate(
        Location((
            0,
            -thickness/2 - mirror_thickness/2,
            0,
        ))
    )
])

door_left = copy(door).locate(
    Location((
        plank_horizontal_location,
        -thickness/2 - door_margin,
        height/2
    ))
)
door_left.color = Color(0.8, 0.8, 0.8)
door_left.label = "Door"

door_right = mirror(copy(door), about=Plane.YZ).locate(
    Location((
        width - plank_horizontal_location,
        -thickness/2 - door_margin,
        height/2
    ))
)
door_right.color = Color(0.8, 0.8, 0.8)
door_right.label = "Door"

doors = Compound(children=[door_left, door_right])
show(doors)


# %%
###############################################################################
#                          PLANK SYSTEM ASSEMBLY                              #
#              Creates internal organization system and hangers               #
###############################################################################
def create_planks(pants_height):
    bottom_y, pants_y, dress_y = get_plank_heights(pants_height)
    with BuildPart() as full_plank:
        Box(plank_width, inner_depth, thickness)
        full_plank.part.label = "Full plank"

    with BuildPart() as bottom_front_plank:
        Box(plank_width, thickness, bottom_height)
        bottom_front_plank.part.label = "Bottom front plank"

    pants_plank_width = pants_width + thickness
    with BuildPart() as pants_plank:
        Box(pants_plank_width, inner_depth - thickness, thickness)
        pants_plank.part.label = "Pants plank"

    with BuildPart() as pants_side:
        Box(thickness, inner_depth - thickness, pants_height)
        pants_side.part.label = "Pants side"

    plank_children = [
        copy(full_plank.part).locate(
            Location((
                plank_horizontal_location,
                inner_depth / 2,
                bottom_y
            ))
        ),
        copy(bottom_front_plank.part).locate(
            Location((
                plank_horizontal_location,
                thickness / 2,
                bottom_height / 2
            ))
        ),
        copy(pants_plank.part).locate(
            Location((
                -pants_plank_width / 2 + thickness + plank_width,
                inner_depth / 2,
                pants_y
            ))
        ),
        copy(pants_side.part).locate(
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
        copy(full_plank.part).locate(
            Location((
                plank_horizontal_location,
                inner_depth / 2,
                top_plank_space * i + dress_y
            ))
        ) for i in range(plank_count)
    ]
    return Compound(plank_children)


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
    Box(sub_back_thickness, sub_width, sub_height)
    sub_back.part.label = "Sub closet back"

with BuildPart() as sub_side:
    Box(sub_depth - sub_back_thickness, thickness, sub_height)
    sub_side.part.label = "Sub closet side"

with BuildPart() as sub_top:
    Box(sub_depth,  sub_width, thickness)
    sub_top.part.label = "Sub closet top/bottom"

with BuildPart() as sub_plank:
    Box(sub_plank_depth, sub_plank_width, thickness)
    sub_plank.part.label = "Sub closet plank"

sub_plank_count = 10

sub_closet_children = [
    copy(sub_back.part).locate(
        Location((
            sub_depth - sub_back_thickness,
            sub_width / 2,
            sub_height / 2 + sub_lift + offset
        ))
    ),
    copy(sub_side.part).locate(
        Location((
            sub_depth / 2 - sub_back_thickness,
            sub_width - offset,
            sub_height / 2 + sub_lift + offset
        ))
    ),
    copy(sub_side.part).locate(
        Location((
            sub_depth / 2 - sub_back_thickness,
            0 + offset,
            sub_height / 2 + sub_lift + offset
        ))
    ),
    copy(sub_top.part).locate(
        Location((
            sub_depth / 2 - sub_back_offset,
            sub_width / 2,
            sub_height + sub_lift + thickness
        ))
    ),
    copy(sub_top.part).locate(
        Location((
            sub_depth / 2 - sub_back_offset,
            sub_width / 2,
            sub_lift
        ))
    ),
] + [
    copy(sub_plank.part).locate(
        Location((
            sub_plank_depth / 2 - sub_back_offset,
            sub_width / 2,
            (i + 1) * sub_height / sub_plank_count + sub_lift + thickness
        ))
    ) for i in range(sub_plank_count) if i < sub_plank_count - 1
]


sub_closet = Compound(children=sub_closet_children)
sub_closet.color = Color(0.7, 0.5, 0.3)
sub_closet_left = copy(sub_closet).locate(
    Location((
        width / 2 - sub_depth + sub_back_offset - 2/3 * inner_margin,
        - door_thickness,
        0
    ))
)

sub_closet_right = mirror(copy(sub_closet), about=Plane.YZ).locate(
    Location((
        width / 2 + sub_depth - sub_back_offset + 2/3 * inner_margin,
        -depth - offset,
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
    doors
]
closet = Compound(closet_children)


show(closet_children)


# %%
###############################################################################
#                           WOOD PARTS EXPORTER                               #
#                Extracts all wooden parts from the closet model              #
#           and prints a list of unique parts with their dimensions           #
###############################################################################
class WoodPart:
    def __init__(self, width, height, thickness, name=""):
        # Round dimensions to 1 decimal place and sort width/height
        self.width = round(min(width, height), 1)
        self.height = round(max(width, height), 1)
        self.thickness = round(thickness, 1)
        self.name = name

    def __eq__(self, other):
        return (abs(self.width - other.width) < 0.1 and 
                abs(self.height - other.height) < 0.1 and 
                abs(self.thickness - other.thickness) < 0.1)

    def __hash__(self):
        # Use rounded values for hash
        return hash((
            round(self.width),
            round(self.height),
            round(self.thickness)
        ))


def flatten(part):
    parts = []

    if isinstance(part, Compound):
        comps = part.children if len(part.children) else part.compounds()
        for child in comps:
            if child is not part:
                parts.extend(flatten(child))
            else:
                # Get bounding box dimensions
                bbox = part.bounding_box()
                dims = [
                    bbox.max.X - bbox.min.X,
                    bbox.max.Y - bbox.min.Y,
                    bbox.max.Z - bbox.min.Z
                ]
                dims = [d * 10 for d in dims]  # Convert to mm
                dims.sort()
                thickness = dims[0]

                # Only include wooden parts that match known thicknesses
                wood_thicknesses = [
                    thickness * 10,
                    back_thickness * 10,
                    sub_back_thickness * 10
                ]
                if any(abs(d - t) < 0.1 
                       for d in dims for t in wood_thicknesses):
                    # Try to get name from part's label attribute if it exists
                    name = getattr(part, "label", "")
                    parts.append(WoodPart(dims[1], dims[2], thickness, name))
    else:
        print(f"Skipping part of type {type(part)}")

    return parts


def export_wood_parts(part):
    parts = flatten(part)

    part_counts = {}
    for part in parts:
        if part in part_counts:
            part_counts[part][0] += 1
            if part.name and part.name not in part_counts[part][1]:
                part_counts[part][1].append(part.name)
        else:
            part_counts[part] = [1, [part.name] if part.name else []]

    sorted_parts = sorted(
        part_counts.items(),
        key=lambda x: (-x[1][0], x[0].thickness, x[0].width, x[0].height)
    )

    print("\nWood parts list (dimensions in mm):")
    print("------------------------------------")
    max_dims_len = max(
        len(f"{p[0].width:.1f}x{p[0].height:.1f}") for p in sorted_parts
    )

    for part, (count, names) in sorted_parts:
        dims = f"{part.width:.1f}x{part.height:.1f}".ljust(max_dims_len)
        names_str = ", ".join(filter(None, names))
        print(
            f"{str(count).rjust(2)} * \
{dims} (thickness: {part.thickness:.1f}mm) - {names_str}"
        )


# Call the function on the closet
export_wood_parts(closet)


# %%