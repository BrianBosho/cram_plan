"""
Utility module for handling environment coloring in PyCRAM.
"""
from utils.color_wrapper import ColorWrapper
import traceback
import re

# Color constants as strings for ColorWrapper
SILVER_COLOUR = "silver"
WOOD_COLOUR = "wood"
GREEN_COLOUR = "green"
BLUE_COLOUR = "blue"
YELLOW_COLOUR = "yellow"
BLACK_COLOUR = "black"
RED_COLOUR = "red"
GRAY_COLOUR = "silver"  # Using silver as gray

# Pattern-based rules for coloring kitchen components
KITCHEN_COLOR_RULES = [
    # Kitchen island and wooden furniture
    (r"kitchen_island(?!.*handle)", WOOD_COLOUR),  # Kitchen island itself
    (r"kitchen_island.*handle", SILVER_COLOUR),    # Handles are silver
    (r".*drawer.*handle", SILVER_COLOUR),          # All drawer handles are silver
    (r".*drawer.*main", WOOD_COLOUR),              # Most drawer main bodies are wood
    
    # Sink area
    (r"sink_area$", WOOD_COLOUR),                  # Sink area base
    (r"sink_area_surface", SILVER_COLOUR),         # Sink countertop
    (r"sink_area_sink", SILVER_COLOUR),            # Sink itself
    (r"sink_area.*dish_washer.*door", YELLOW_COLOUR),  # Dishwasher door
    (r"sink_area.*dish_washer.*handle", SILVER_COLOUR),  # Dishwasher handle
    (r"sink_area.*drawer.*main", YELLOW_COLOUR),   # Sink drawers are yellow
    (r"sink_area.*panel", SILVER_COLOUR),          # Panels in sink area are silver

    # Oven area
    (r"oven_area_area$", SILVER_COLOUR),           # Oven area base
    (r"oven_area.*oven_door", GREEN_COLOUR),       # Oven door
    (r"oven_area.*oven_panel", BLUE_COLOUR),       # Oven panel
    (r"oven_area.*oven_knob", SILVER_COLOUR),      # Oven knobs
    (r"oven_area.*oven.*handle", SILVER_COLOUR),   # Oven handle
    (r"oven_area.*middle.*drawer.*main", GREEN_COLOUR),  # Middle drawers in oven area are green
    
    # Fridge area
    (r"fridge_area$", SILVER_COLOUR),              # Fridge area base
    (r".*fridge_door$", GREEN_COLOUR),             # Fridge door
    (r".*fridge_door_handle", SILVER_COLOUR),      # Fridge handle
    
    # Table
    (r"table_area_main", WOOD_COLOUR),             # Table
    
    # Walls
    (r".*wall.*", GRAY_COLOUR),                    # Walls are gray
    
    # Generic rules (apply last)
    (r".*handle", SILVER_COLOUR),                  # All other handles are silver 
    (r".*footprint", GRAY_COLOUR),                 # Footprints are light gray
    (r".*panel", SILVER_COLOUR),                   # Panels are silver
    (r"room_link", GRAY_COLOUR),                   # Room link is gray
    (r"world", GRAY_COLOUR),                       # World is gray
]

class RobotColorHandler:
    """Handler for coloring robot parts."""
    
    @staticmethod
    def get_robot_colors():
        """Get color mapping for robot parts."""
        return {
            "base_link": BLACK_COLOUR,
            "head_tilt_link": BLACK_COLOUR,
            "r_forearm_link": BLACK_COLOUR,
            "l_forearm_link": BLACK_COLOUR,
            "torso_lift_link": GREEN_COLOUR,
            "r_gripper_palm_link": GREEN_COLOUR,
            "l_gripper_palm_link": GREEN_COLOUR,
        }

def get_kitchen_colors_from_links(link_names):
    """
    Generate a color mapping based on link names using pattern matching rules.
    
    Args:
        link_names (list): List of link names to color
        
    Returns:
        dict: Mapping of link names to colors
    """
    color_mapping = {}
    
    # Apply rules to each link
    for link_name in link_names:
        for pattern, color in KITCHEN_COLOR_RULES:
            if re.match(pattern, link_name):
                color_mapping[link_name] = color
                break
    
    return color_mapping

def debug_colorable_parts(obj):
    """
    Get a list of parts that can be colored for an object.
    
    Args:
        obj: The object to check
    
    Returns:
        list: List of colorable part names, or None if not supported
    """
    if not hasattr(obj, 'links') or not hasattr(obj, 'links'):
        print(f"Object {obj.name if hasattr(obj, 'name') else 'unknown'} does not have links attribute")
        return None
    
    try:
        # Get available links that might be colorable
        link_names = []
        for link_key in obj.links:
            link = obj.links[link_key]
            link_name = link.name if hasattr(link, 'name') else str(link_key)
            link_names.append(link_name)
        
        print(f"Available links for {obj.name if hasattr(obj, 'name') else 'object'}: {link_names}")
        return link_names
    except Exception as e:
        print(f"Error checking colorable parts: {str(e)}")
        return None

def apply_colors(obj, colors_dict, debug=False):
    """
    Apply colors to an object safely.
    
    Args:
        obj: The object to apply colors to
        colors_dict: Dictionary mapping part names to colors
        debug (bool): Enable debug output
        
    Returns:
        bool: True if coloring was successful, False otherwise
    """
    if not hasattr(obj, 'set_color'):
        print(f"Object {obj.name if hasattr(obj, 'name') else 'unknown'} does not have set_color method")
        return False
    
    if debug:
        print(f"Applying {len(colors_dict)} colors to {obj.name if hasattr(obj, 'name') else 'object'}")
        
    try:
        # Convert all color strings to ColorWrapper objects
        wrapped_colors = {}
        for part, color in colors_dict.items():
            wrapped_colors[part] = ColorWrapper(color)
        
        # Apply colors
        obj.set_color(wrapped_colors)
        print(f"Successfully applied {len(colors_dict)} colors to {obj.name if hasattr(obj, 'name') else 'object'}")
        return True
    except Exception as e:
        print(f"Warning: Could not apply colors to {obj.name if hasattr(obj, 'name') else 'object'}: {str(e)}")
        if debug:
            traceback.print_exc()
        return False

def apply_kitchen_colors(kitchen_obj, debug=False):
    """
    Apply rule-based colors to a kitchen object using available links.
    
    Args:
        kitchen_obj: The kitchen object to color
        debug (bool): Enable debug output
        
    Returns:
        bool: True if coloring was successful, False otherwise
    """
    # Get the available links
    link_names = debug_colorable_parts(kitchen_obj)
    
    if not link_names:
        print("No links found for coloring")
        return False
    
    # Generate color mapping from links using rules
    color_mapping = get_kitchen_colors_from_links(link_names)
    
    if debug:
        print(f"Generated {len(color_mapping)} color mappings from rules")
        # Print first 10 mappings as a sample
        sample_mappings = list(color_mapping.items())[:10]
        print(f"Sample mappings: {sample_mappings}")
    
    # Apply the colors
    return apply_colors(kitchen_obj, color_mapping, debug)
    
def apply_robot_colors(robot_obj, debug=False):
    """
    Apply standard colors to a robot object.
    
    Args:
        robot_obj: The robot object to color
        debug (bool): Enable debug output
        
    Returns:
        bool: True if coloring was successful, False otherwise
    """
    return apply_colors(robot_obj, RobotColorHandler.get_robot_colors(), debug)