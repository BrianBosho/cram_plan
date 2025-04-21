"""
Utility module for handling environment coloring in PyCRAM.
"""
from utils.color_wrapper import ColorWrapper
import traceback
import re

# Refined color palette as RGB tuples - for direct ColorWrapper use
PALETTE = {
    "wall":   (0.90, 0.90, 0.90, 1.0),   # light grey
    "floor":  (0.95, 0.95, 0.95, 1.0),   # very light grey
    "wood":   (0.82, 0.70, 0.55, 1.0),   # warm oak
    "stone":  (0.35, 0.35, 0.40, 1.0),   # dark countertop
    "metal":  (0.85, 0.85, 0.85, 1.0),   # stainless steel
    "black":  (0.10, 0.10, 0.10, 1.0),   # matte black handles
    "accent": (0.50, 0.60, 0.50, 1.0),   # sage green for island panels
    "accent2": (0.60, 0.50, 0.30, 1.0),  # warm amber for oven area drawers
    "white":  (1.00, 1.00, 1.00, 1.0),   # pure white for some appliances
    "gray":   (0.70, 0.70, 0.70, 1.0),   # medium gray for sink area drawers
    "wall2":   (0.60, 0.60, 0.60, 1.0), 
    "ocean_blue": (0.00, 0.50, 0.70, 1.0) 
}

# Pattern-based rules for coloring kitchen components (order matters for precedence)
KITCHEN_COLOR_RULES = [
    # Walls and floor
    (r".*wall.*",         "ocean_blue"),
    (r".*footprint",      "floor"),
    (r"room_link",        "floor"),
    (r"world",            "floor"),
    
    # Countertops & surfaces
    (r".*_surface$",      "stone"),
    (r"sink_area_sink",   "metal"),
    (r"kitchen_island_surface", "stone"),
    
    # Cabinetry base
    (r"sink_area$",       "wood"),
    (r"fridge_area$",     "wood"),
    (r"oven_area_area$",  "wood"),
    
    # Kitchen island with accent color
    (r"kitchen_island$",  "accent"),
    
    # Appliances & doors
    (r".*dish_washer.*door", "metal"),
    (r".*oven_door",      "metal"),
    (r".*fridge_door$",   "metal"),
    (r".*oven_panel",     "black"),
    # ADD kitchen_island_stove and make it metal
    (r".*stove.*",        "metal"),
    
    # Different drawer colors by area
    (r"sink_area.*drawer.*main", "gray"),
    (r"oven_area.*drawer.*main", "accent2"),
    (r"kitchen_island.*drawer.*main", "wood"),
    
    # Default for remaining drawers
    (r".*drawer.*main",   "wood"),
    
    # Handles & knobs (all black for consistency)
    (r".*handle",         "black"),
    (r".*knob",           "black"),
    
    # Other elements
    (r"table_area_main",  "wood"),
    (r".*panel",          "metal"),
]

class PaletteColorWrapper:
    """Wrapper that can handle both palette names and direct RGB tuples."""
    
    def __init__(self, color_key):
        """
        Initialize with a color key which can be a palette name or RGB tuple.
        
        Args:
            color_key: Either a string key to look up in PALETTE or an RGB tuple
        """
        if isinstance(color_key, str) and color_key in PALETTE:
            self.rgba = PALETTE[color_key]
        else:
            # If not in palette, pass to the standard ColorWrapper
            wrapper = ColorWrapper(color_key)
            self.rgba = wrapper.get_rgba()
    
    def get_rgba(self):
        """Return the RGBA tuple."""
        return self.rgba

class RobotColorHandler:
    """Handler for coloring robot parts."""
    
    @staticmethod
    def get_robot_colors():
        """Get color mapping for robot parts."""
        return {
            "base_link": "black",
            "head_tilt_link": "black",
            "r_forearm_link": "black",
            "l_forearm_link": "black",
            "torso_lift_link": "accent",
            "r_gripper_palm_link": "accent",
            "l_gripper_palm_link": "accent",
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
        # Convert all color strings to PaletteColorWrapper objects
        wrapped_colors = {}
        for part, color in colors_dict.items():
            wrapped_colors[part] = PaletteColorWrapper(color)
        
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