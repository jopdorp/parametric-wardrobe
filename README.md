# Kledingkast Project

This project provides a parametric wardrobe design built with Python and the build123d library.  
Follow these steps to run:

1. Install dependencies (see requirements.txt).  
2. Execute kledingkast.py with a Python environment that supports Jupyter cells.  
3. Modify global parameters to customize the design.  
4. Render and export as needed.

## Closet Design System Architecture

This framework takes a modular, parametric approach to designing custom wardrobes:

- **Parametric Design**: All dimensions are controlled through variables, allowing for complete customization while maintaining proper relationships between components.
- **Modular Components**: The system divides the wardrobe into logical sections (frame, shelves, drawers, doors) that work together.
- **Hardware Integration**: Real-world hardware components (rails, dowels, screws) are represented virtually for accurate modeling.
- **Jupyter Workflow**: Interactive cell-based execution lets you visualize changes in real-time as you modify parameters.

### Core Components

1. **Frame Assembly**: The structural foundation including sides, top, back panels
2. **Interior Organization**: Shelving, dividers, and hanging sections
3. **Sub-closets**: Smaller compartments that slide out
4. **Door System**: Front-facing panels with mirrors
5. **Hardware**: Dowels, rails, screws, and other connectors

## How to Use & Customize

### Getting Started

1. Clone this repository and install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Open `kledingkast.py` in Visual Studio Code with Jupyter extension or another Jupyter-compatible environment.

3. Run the notebook cell-by-cell (Shift+Enter) to see each component build up.

### Customizing Dimensions

The `GLOBAL PARAMETERS` section (around line 50) contains all primary dimensions:

```python
thickness = 1.8            # Standard panel thickness (cm)
width = 174.5              # Total closet width
height = 264.5             # Total closet height
depth_budget = 59.0        # Maximum depth including doors
sub_depth = 30.5           # Depth of sliding compartments
# ...and many more parameters
```

Modify these values to match your specific requirements. Derived parameters automatically update to maintain proper relationships.

### Creating Your Own Design

To create a completely new design:

1. **Start with the frame**: Modify the `make_frame()` function to create your desired frame structure.

2. **Configure internal organization**: 
   - Adjust `create_planks()` for shelf placement
   - Modify height distributions in `get_plank_heights()`
   - Change panel counts and spacing patterns

3. **Customize sub-closets**: Edit the `create_sub_closet()` function to change drawer size, number of shelves, etc.

4. **Adapt the door system**: Modify door dimensions, mirror thicknesses, and placement.

5. **Add hardware**: Use the hardware placement functions to add dowels, rails, and screws between components.

### Advanced Customization

For more extensive changes:

1. **Component Creation**: Study the BuildPart pattern used throughout the code:
   ```python
   with BuildPart() as my_panel:
       Box(width, height, thickness)  # Create basic shape
       # Optional: Add features like holes, fillets, etc.
   ```

2. **Assembly Logic**: Follow patterns in existing functions like `create_planks()` to:
   - Create basic components
   - Position them with `Location()` 
   - Add connectors like dowels

3. **Hardware Integration**: Use the `create_between_panels()` function to add connection hardware between components:
   ```python
   dowels = create_dowels_between_panels(panel_a, panel_b, spacing=15)
   ```

## Working with build123d
dowel_length
This system leverages key build123d concepts:

- **Part Creation**: Uses BuildPart context manager to create solid objects
- **Transformations**: Utilizes Location, rotate, and mirror to position parts
- **Compounds**: Organizes related parts into logical groups
- **Part Operations**: Uses addition and subtraction to create complex shapes
- **Visualization**: Uses the show() function to render components

## Hardware Integration

The system includes accurate representations of real-world hardware from the included hardware.txt file. This includes:

- Mirror attachments
- Door rails and slides
- Pants rails and storage solutions
- Clothing rods and hangers
- Dowel connections between panels

Update the hardware models or parameters to match your available components.

## Export and Production

After finalizing your design:

1. Run the wood parts exporter cell to generate a complete cut list with dimensions.
2. Export individual components as needed for manufacturing.
3. Follow the dimensions and assembly sequence for construction.

## Tips for Success

- Run cells in sequence to see how components build up
- Make small changes and visualize before making major modifications
- Keep hardware limitations in mind when adjusting dimensions
- Maintain proper clearances for moving parts
- Consider material thickness when designing joinery

## Extending the System

To extend the framework with new features:

1. Create new component classes following existing patterns
2. Add new parameter sections for your components
3. Integrate into the main closet assembly
4. Add any specialized hardware or connectors needed
