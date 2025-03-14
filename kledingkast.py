# %%
# Jupyter cell configuration
# The markers "# %%" separate code blocks for execution (cells) 
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%
###############################################################################
#                                CLOSET DESIGN                                 #
#                   Customizable closet design with parameters                #
#                               and hardware setup                             #
###############################################################################

# Import required classes and functions
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
    Vector
)
from bd_warehouse.fastener import CounterSunkScrew

from ocp_vscode import show

# Manually set port
from ocp_vscode.comms import CMD_PORT, set_port
set_port(3939)  # Use a specific port number


# %%
###############################################################################
#                              GLOBAL PARAMETERS                              #
#                    CUSTOMIZE THE SIZES TO FIT YOUR NEEDS                    #
###############################################################################
thickness = 1.8
back_thickness = 1.2

width = 174.5
height = 264.5
depth_budget = 59.0
mirror_thickness = .4
sub_depth = 30.5
inner_margin = .6

wheel_height = 2.8
rail_height = 1.9

sub_back_thickness = 1.2

# Plank system parameters
bottom_height = 12.0
pants_width = 34.5
dress_height = 102.5
bar_height = 3.0
bar_width = 1.5
bar_spacing = 4.5

pants_height_left = 73.0
pants_height_right = 63.0

# Doors
door_margin = .2

# Hardware parameters
dowel_size = "8mm"

# Define standard dowel sizes based on 12mm & 18mm wood thickness
METRIC_DOWEL_SIZES = {
    "6mm": (.6, 3.0),  # Diameter, Length
    "8mm": (.8, 4.0),
    "10mm": (1.0, 5.0),
}

# Derived parameters
dowel_length = METRIC_DOWEL_SIZES[dowel_size][1]

door_thickness = thickness + mirror_thickness

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
###############################################################################
#                             WOODEN DOWEL CLASS                              #
#                 Create a wooden dowel with rounded ends                     #
###############################################################################

class WoodenDowel(Part):
    def __init__(self, size: str):
        """Create a wooden dowel with rounded ends.

        Args:
            size (str): The dowel size (6mm, 8mm, or 10mm).
        """
        if size not in METRIC_DOWEL_SIZES:
            raise ValueError(f"Invalid size {size}. Choose from {list(METRIC_DOWEL_SIZES.keys())}")

        diameter, length = METRIC_DOWEL_SIZES[size]
        radius = diameter / 2
        filletlength = radius * 0.5  # Adjust rounding for realistic dowel ends

        with BuildPart() as dowel:
            Cylinder(radius, length)  # Create main dowel
            
            # Select circular edges at the top and bottom
            top_edge = dowel.edges().sort_by(Axis.Z)[-1]  # Highest edge
            bottom_edge = dowel.edges().sort_by(Axis.Z)[0]  # Lowest edge

            # Apply fillet correctly using the function, not as a method
            chamfer([top_edge, bottom_edge], angle=30, length=filletlength)

        super().__init__(dowel.part)

# Example: Create an 8mm dowel for 18mm wood
dowel_8mm = WoodenDowel("8mm")
show(dowel_8mm)

# %%
###############################################################################
#                           HARDWARE PLACEMENT                                #
#              Adding hardware along edges where panels connect               #
###############################################################################

def get_side_face(panel_side, panel_front):
    front_center = panel_front.center()
    all_faces = panel_side.faces()
    
    # Debug information
    # print(f"Panel front center: {front_center}")
    # for i, face in enumerate(all_faces):
    #     print(f"Face {i} center: {face.center()}, distance: {face.center().sub(front_center).length}")
    
    # Find the face closest to the front panel
    closest_face = min(all_faces, key=lambda face: face.center().sub(front_center).length)
    return closest_face

def decompose_face(side_face):
    # Get all edges on the face
    edges = side_face.edges()
    
    # Identify the longest and shortest edges to determine orientation
    sorted_edges = sorted(edges, key=lambda e: e.length)
    
    # Get the two longest edges (should be parallel to each other)
    long_edge1 = sorted_edges[-1]  # Longest edge
    long_edge2 = sorted_edges[-2]  # Second longest edge (should be parallel)
    
    # Get center of the face
    center = side_face.center()
    
    # Length is from the longest edge
    length = long_edge1.length
    
    # Direction is along the longest edge
    edge_start = long_edge1.start_point()
    edge_end = long_edge1.end_point()
    direction = (edge_end - edge_start).normalized()
    
    # For better centering, find the midline between the two long edges
    e1_mid = (long_edge1.start_point() + long_edge1.end_point()) * 0.5
    e2_mid = (long_edge2.start_point() + long_edge2.end_point()) * 0.5
    
    # Use the midpoint between the two long edges as the center line
    # This ensures better centering of dowels along the face
    adjusted_center = (e1_mid + e2_mid) * 0.5
    
    # Normal is perpendicular to the face
    normal = side_face.normal_at(center)
    
    return adjusted_center, direction, normal, length

def position_dowel(pos, normal, front_thickness, length, is_center_aligned=True):
    if is_center_aligned:
        return pos - normal * (length / 2 - (front_thickness * 0.75)) 
    else:
        return pos - normal * (-front_thickness) 

def get_rotation(normal):
    rotation_angle = 0
    z_axis = Vector(0, 0, 1)
    
    # Calculate angle between vectors
    rotation_angle = z_axis.get_angle(normal)
    
    # Handle parallel vectors case
    if abs(abs(z_axis.dot(normal)) - 1.0) < 1e-10:  # Vectors are parallel
        # If vectors point in same direction, no rotation needed
        if z_axis.dot(normal) > 0:
            return Vector(1, 0, 0), 0
        # If vectors point in opposite directions, rotate 180° around X axis
        else:
            return Vector(1, 0, 0), 180
    
    # Normal case - vectors are not parallel
    rotation_axis = z_axis.cross(normal)
    rotation_axis = rotation_axis.normalized()
    return rotation_axis, rotation_angle

def create_between_panels(part_factory, part_length, panel_side, panel_front, spacing=20.0, front_thickness=1.8, is_center_aligned=True, offset=.0):
    side_face = get_side_face(panel_side, panel_front)
    center, direction, normal, length = decompose_face(side_face)

    # Calculate how many dowels we need
    dowel_count = max(1, int(length / spacing) - 1)
    
    # Calculate the total space taken by the dowels + spacing
    total_length = spacing * (dowel_count - 1)
    
    # Calculate offset from edge to center the dowels
    edge_offset = (length - total_length) / 2
    
    # Position for the penetration depth
    pos = position_dowel(Vector(
        center.X,
        center.Y,
        center.Z
    ), normal, front_thickness, part_length, is_center_aligned)
    
    rotation_axis, rotation_angle = get_rotation(normal)
    
    # Start position for the first dowel at the centered starting point
    start_pos = pos - direction * (total_length / 2) + direction * offset
    
    dowels = []
    for i in range(dowel_count):
        # Calculate position for each dowel
        dowel_pos = start_pos + direction * (i * spacing)
        dowel = part_factory().locate(
            Location(dowel_pos, rotation_axis, rotation_angle)
        )
        dowels.append(dowel)
    
    return Compound(dowels)

# %%
###############################################################################
#                             DOWEL PLACEMENT                                 #
#              Adding dowels between panels for extra strength                #
###############################################################################
def create_dowels_between_panels(panel_side, panel_front, spacing=20.0, front_thickness=1.8):
    dow_sz = dowel_size
    dow_len = dowel_length
    if front_thickness < 1.8:
        dow_sz = "6mm"
        dow_len = 3.0
    return create_between_panels(lambda: WoodenDowel(dow_sz), dow_len, panel_side, panel_front, spacing=spacing, front_thickness=front_thickness)

# Example: Create two panels
# rotate and locate the panels
with BuildPart() as panel_side:
    Box(thickness, 200.0, 20.0)
    panel_side.part.label = "Side panel"

with BuildPart() as panel_front:
    Box(thickness, 200.0, 20.0)
    panel_front.part.label = "Front panel"

panel_side = copy(panel_side.part).rotate(axis=Axis.Y, angle=90)
panel_front = copy(panel_front.part).locate(Location((11.0, .0, 9.0)))

dowels = create_dowels_between_panels(panel_side, panel_front)

def create_screws_between_panels(panel_side, panel_front):
    def create_screw():
        return CounterSunkScrew(fastener_type="iso14581", size="M4-0.7", length=35).scale(.1)
    return create_between_panels(create_screw, 3.5, panel_side, panel_front, spacing=40.0, front_thickness=thickness, is_center_aligned=False, offset=10.0)

screws = create_screws_between_panels(panel_side, panel_front)
show([panel_front, panel_side, screws, dowels])

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
        Box(width, depth, thickness)
        top.part.label = "Top panel"

    with BuildPart() as back:
        Box(width, back_thickness, height - thickness)
        back.part.label = "Back panel"

    # Define panel positions
    left_side_pos = (offset, inner_depth / 2, side_height / 2)
    middle_left_pos = (plank_width + thickness + offset, inner_depth / 2, side_height / 2)
    middle_right_pos = (width - thickness - offset - plank_width, inner_depth / 2, side_height / 2)
    right_side_pos = (width - offset, inner_depth / 2, side_height / 2)
    top_pos = (width / 2, depth / 2, side_height + offset)
    back_pos = (width / 2, depth - back_offset, (height - thickness) / 2)

    frame_left_side = copy(side.part).locate(Location(left_side_pos))
    frame_middle_left = copy(side.part).locate(Location(middle_left_pos))
    frame_middle_right = copy(side.part).locate(Location(middle_right_pos))
    frame_right_side = copy(side.part).locate(Location(right_side_pos))
    frame_top = copy(top.part).locate(Location(top_pos))
    frame_back = copy(back.part).locate(Location(back_pos))


    left_top_dowels = create_dowels_between_panels(frame_left_side, frame_top, spacing=15)
    middle_left_top_dowels = create_dowels_between_panels(frame_middle_left, frame_top, spacing=15)
    middle_right_top_dowels = create_dowels_between_panels(frame_middle_right, frame_top, spacing=15)
    right_top_dowels = create_dowels_between_panels(frame_right_side, frame_top, spacing=15)

    left_back_dowels = create_dowels_between_panels(frame_left_side, frame_back, spacing=20, front_thickness=back_thickness)
    middle_left_back_dowels = create_dowels_between_panels(frame_middle_left, frame_back, spacing=20, front_thickness=back_thickness)
    middle_right_back_dowels = create_dowels_between_panels(frame_middle_right, frame_back, spacing=20, front_thickness=back_thickness)
    right_back_dowels = create_dowels_between_panels(frame_right_side, frame_back, spacing=20, front_thickness=back_thickness)

    top_back_dowels = create_dowels_between_panels(frame_back, frame_top, spacing=20, front_thickness=back_thickness)
    # show(left_top_dowels)

    return Compound(children=[
        frame_left_side,
        frame_middle_left,
        frame_middle_right,
        frame_right_side,
        frame_top,
        frame_back,
        left_top_dowels,
        middle_left_top_dowels,
        middle_right_top_dowels,
        right_top_dowels,
        left_back_dowels,
        middle_left_back_dowels,
        middle_right_back_dowels,
        right_back_dowels,
        top_back_dowels
    ]) 

# Create the frame
frame = make_frame()
show(frame)


# %%
###############################################################################
#                                    RAILS                                    #
#                      Connects the subclosets to the frame                   #
###############################################################################

def create_rails():
    sub_rail = import_step("rail.stp")

    sub_rail_right = Part(sub_rail.children[0])
    sub_rail_left = Part(sub_rail.children[1])

    sub_rail_right = sub_rail_right.rotate(axis=Axis.X, angle=-90)
    sub_rail_left = sub_rail_left.rotate(axis=Axis.X, angle=-90)

    return Compound(children=[
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

if not "rails" in globals():
    global rails
    rails = create_rails()
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
def create_sub_closet():
    with BuildPart() as sub_back:
        Box(sub_back_thickness, sub_width, sub_height)
        sub_back.part.label = "Sub closet back"

    with BuildPart() as sub_side:
        Box(sub_depth - sub_back_thickness, thickness, sub_height)
        sub_side.part.label = "Sub closet side"

    with BuildPart() as sub_bottom_top:
        Box(sub_depth,  sub_width, thickness)
        sub_bottom_top.part.label = "Sub closet top/bottom"

    with BuildPart() as sub_plank:
        Box(sub_plank_depth, sub_plank_width, thickness)
        sub_plank.part.label = "Sub closet plank"

    # locate the sub closet parts
    sub_back = copy(sub_back.part).locate(
        Location((
            sub_depth - sub_back_thickness,
            sub_width / 2,
            sub_height / 2 + sub_lift + offset
        ))
    )
    sub_left = copy(sub_side.part).locate(
        Location((
            sub_depth / 2 - sub_back_thickness,
            sub_width - offset,
            sub_height / 2 + sub_lift + offset
        ))
    )
    sub_right = copy(sub_side.part).locate(
        Location((
            sub_depth / 2 - sub_back_thickness,
            0 + offset,
            sub_height / 2 + sub_lift + offset
        ))
    )
    sub_top = copy(sub_bottom_top.part).locate(
        Location((
            sub_depth / 2 - sub_back_offset,
            sub_width / 2,
            sub_height + sub_lift + thickness
        ))
    )
    sub_bottom = copy(sub_bottom_top.part).locate(
        Location((
            sub_depth / 2 - sub_back_offset,
            sub_width / 2,
            sub_lift
        ))
    )

    dowels_top_left = create_dowels_between_panels(sub_left, sub_top, spacing=8)
    dowels_top_right = create_dowels_between_panels(sub_right, sub_top, spacing=8)
    dowels_top_back = create_dowels_between_panels(sub_back, sub_top, spacing=10)
    
    dowels_bottom_left = create_dowels_between_panels(sub_left, sub_bottom, spacing=8)
    dowels_bottom_right = create_dowels_between_panels(sub_right, sub_bottom, spacing=8)
    dowels_bottom_back = create_dowels_between_panels(sub_back, sub_bottom, spacing=10)

    dowels_left_back = create_dowels_between_panels(sub_left, sub_back, spacing=20)
    dowels_right_back = create_dowels_between_panels(sub_right, sub_back, spacing=20)

    sub_plank_count = 10

    sub_closet_children = [
        sub_back,
        sub_left,
        sub_right,
        sub_top,
        sub_bottom,
        dowels_top_left,
        dowels_top_right,
        dowels_top_back,
        dowels_bottom_left,
        dowels_bottom_right,
        dowels_bottom_back,
        dowels_left_back,
        dowels_right_back
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
    return sub_closet

sub_closet_left = create_sub_closet().locate(
    Location((
        width / 2 - sub_depth + sub_back_offset - 2/3 * inner_margin,
        - door_thickness,
        0
    ))
)

sub_closet_right = mirror(create_sub_closet(), about=Plane.YZ).locate(
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