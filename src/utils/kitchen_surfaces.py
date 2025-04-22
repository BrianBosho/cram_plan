"""
Utility module for handling kitchen surfaces and placement locations in PyCRAM.
"""
from pycram.datastructures.pose import Pose
from pycram.world_concepts.world_object import Object
from pycram.datastructures.enums import ObjectType
from utils.color_wrapper import ColorWrapper
import numpy as np

primary_surfaces_list = [
    "sink_area_surface",
    "kitchen_island_surface",
    "kitchen_island_stove",
    "table_area_main",
    "oven_area_area",
    ]

secondary_surfaces_list = [
    "sink_area_sink",
    "oven_area_oven_door",
    "fridge_area",
]




# Key surfaces where objects can be placed
TESTED_PLACEMENT_SURFACES = {
    # Primary surfaces
    "sink_area_surface": {
        "description": "Countertop around the sink",
        "height": 0.95,
        "recommended_for": ["utensils", "dishes", "cleaning_supplies"],
        "position": [1.4, 0.6, 0.95],  # From URDF: sink_area_footprint (1.825, 1.32) + sink_area (0.29, 1.03) + height
        "max_dx": 0.2,  # Maximum displacement in x direction
        "max_dy": 0.5   # Maximum displacement in y direction
    },
    "kitchen_island_surface": {
        "description": "Kitchen island's main countertop",
        "height": 0.95,
        "recommended_for": ["food", "dishes", "utensils", "cooking_supplies"],
        "position": [-1.0675, 1.7192, 0.95],  # From URDF: kitchen_island_footprint (-1.365, 0.59) + kitchen_island (0.2975, 1.1292) + height
        "max_dx": 0.2,
        "max_dy": 0.5
    },
    "kitchen_island_stove": {
        "description": "Cooking surface on the island",
        "height": 0.97,
        "recommended_for": ["pots", "pans", "cooking_utensils"],
        "position": [-1.0675, 2.485, 0.97],  # From URDF: kitchen_island position + (0, 0.7658) + height
        "max_dx": 0.5,
        "max_dy": 0.5
    },
    "table_area_main": {
        "description": "Dining table surface",
        "height": 0.55,
        "recommended_for": ["dishes", "food", "utensils"],
        "position": [-1.4, -0.8, 0.55],  # From URDF: direct position
        "max_dx": 0.5,
        "max_dy": 0.1
    },   
    
    "sink_area_sink": {
        "description": "Inside the sink",
        "height": 0.90,
        "recommended_for": ["dirty_dishes", "washing_items"],
        "position": [1.4, 0, 0.90],  # From URDF: sink_area_surface + (0.005, 0.47) + adjusted height
        "max_dx": 0.2,
        "max_dy": 0.3
    }  
}

PLACEMENT_SURFACES = TESTED_PLACEMENT_SURFACES.copy()


def get_available_surfaces():
    """
    Get list of all available surfaces for object placement.
    
    Returns:
        list: Names of available placement surfaces
    """
    return list(PLACEMENT_SURFACES.keys())

def get_surface_info(surface_name):
    """
    Get information about a specific surface.
    
    Args:
        surface_name (str): Name of the surface
        
    Returns:
        dict: Surface information or None if not found
    """
    return PLACEMENT_SURFACES.get(surface_name)

def get_surface_dimensions(world, surface_name):
    """
    Get the dimensions of a named surface in the world.
    
    Args:
        world: The BulletWorld instance
        surface_name (str): Name of the surface
        
    Returns:
        tuple: (width, depth, height) or None if not found
        bbox: The full bounding box [min_x, min_y, min_z, max_x, max_y, max_z]
    """
    if not world:
        print("World not initialized")
        return None, None
        
    try:
        # First try to get the surface by exact name
        surface = next((obj for obj in world.objects if hasattr(obj, 'name') and obj.name == surface_name), None)
        
        # If not found, try getting the parent object and then finding the part
        if not surface:
            # For surfaces like sink_area_surface, the parent might be the kitchen
            kitchen = next((obj for obj in world.objects if hasattr(obj, 'name') and obj.name == "kitchen"), None)
            if kitchen and hasattr(kitchen, 'links'):
                for link_key in kitchen.links:
                    link = kitchen.links[link_key]
                    link_name = link.name if hasattr(link, 'name') else str(link_key)
                    if link_name == surface_name:
                        surface = link
                        break
        
        if surface:
            bbox = surface.get_bounding_box() if hasattr(surface, 'get_bounding_box') else None
            if bbox:
                # Calculate dimensions from bounding box [min_x, min_y, min_z, max_x, max_y, max_z]
                width = bbox[3] - bbox[0]
                depth = bbox[4] - bbox[1]
                height = bbox[5] - bbox[2]
                return (width, depth, height), bbox
            else:
                print(f"Warning: Couldn't get bounding box for {surface_name}")
                # Use default height from our database if available
                if surface_name in PLACEMENT_SURFACES:
                    return (0.5, 0.5, PLACEMENT_SURFACES[surface_name]["height"]), None
        
        print(f"Surface {surface_name} not found in world")
        return None, None
        
    except Exception as e:
        print(f"Error getting dimensions for {surface_name}: {str(e)}")
        return None, None

def get_surface_position(world, surface_name):
    """
    Get the position of a named surface in the world.
    
    Args:
        world: The BulletWorld instance
        surface_name (str): Name of the surface
        
    Returns:
        list: [x, y, z] position or None if not found
    """
    # Always check if we have a fallback position in our dictionary first
    if surface_name in PLACEMENT_SURFACES and "position" in PLACEMENT_SURFACES[surface_name]:
        fallback_position = PLACEMENT_SURFACES[surface_name]["position"]
    else:
        fallback_position = None
    
    # If no world is provided, use the fallback position
    if not world:
        print("World not initialized")
        if fallback_position:
            return fallback_position
        return None
        
    try:
        # First try to get the surface by exact name
        surface = next((obj for obj in world.objects if hasattr(obj, 'name') and obj.name == surface_name), None)
        
        # If not found, try getting the parent object and then finding the part
        if not surface:
            # For surfaces like sink_area_surface, the parent might be the kitchen
            kitchen = next((obj for obj in world.objects if hasattr(obj, 'name') and obj.name == "kitchen"), None)
            if kitchen and hasattr(kitchen, 'links'):
                for link_key in kitchen.links:
                    link = kitchen.links[link_key]
                    link_name = link.name if hasattr(link, 'name') else str(link_key)
                    if link_name == surface_name:
                        surface = link
                        break
        
        if surface:
            # Try multiple methods to get position in order of preference
            # Method 1: get_position method
            if hasattr(surface, 'get_position'):
                pos = surface.get_position()
                if hasattr(pos, 'x') and hasattr(pos, 'y') and hasattr(pos, 'z'):
                    return [pos.x, pos.y, pos.z]
                else:
                    return list(pos)
            
            # Method 2: 'position' attribute
            elif hasattr(surface, 'position'):
                pos = surface.position
                if hasattr(pos, 'x'):
                    return [pos.x, pos.y, pos.z]
                else:
                    return list(pos)
                
            # Method 3: 'pose' attribute
            elif hasattr(surface, 'pose') and hasattr(surface.pose, 'position'):
                pos = surface.pose.position
                if hasattr(pos, 'x'):
                    return [pos.x, pos.y, pos.z]
                else:
                    return list(pos)
            
            # If all else fails, use fallback position
            print(f"Warning: {surface_name} doesn't have position methods")
            if fallback_position:
                print(f"Using fallback position for {surface_name}: {fallback_position}")
                return fallback_position
            return None
        
        print(f"Surface {surface_name} not found in world")
        # Return fallback position if available
        if fallback_position:
            print(f"Using fallback position for {surface_name}: {fallback_position}")
            return fallback_position
        return None
        
    except Exception as e:
        print(f"Error getting position for {surface_name}: {str(e)}")
        # Return fallback position if available
        if fallback_position:
            print(f"Using fallback position for {surface_name}: {fallback_position}")
            return fallback_position
        return None

def get_surface_offsets(surface_name):
    """
    Get the maximum allowed displacement in x and y directions for a specific surface.
    
    Args:
        surface_name (str): Name of the surface
        
    Returns:
        tuple: (max_dx, max_dy) or (0.0, 0.0) if surface not found
    """
    if surface_name in PLACEMENT_SURFACES:
        surface = PLACEMENT_SURFACES[surface_name]
        return (surface.get("max_dx", 0.0), surface.get("max_dy", 0.0))
    else:
        print(f"Warning: Surface {surface_name} not found in placement surfaces")
        return (0.0, 0.0)

    """
    Detect objects that are on a specific surface.
    
    Args:
        world: The BulletWorld instance
        surface_name (str): Name of the surface
        
    Returns:
        list: Objects detected on the surface
    """
    if not world:
        print("World not initialized")
        return []
        
    try:
        # Get surface dimensions and position
        dims, bbox = get_surface_dimensions(world, surface_name)
        surface_pos = get_surface_position(world, surface_name)
        
        if not surface_pos or not bbox:
            print(f"Surface {surface_name} position or dimensions could not be determined")
            return []
            
        # Define the surface boundary with a small margin
        margin = 0.02  # 2cm margin
        surface_min_x = bbox[0] - margin
        surface_max_x = bbox[3] + margin
        surface_min_y = bbox[1] - margin
        surface_max_y = bbox[4] + margin
        surface_z = bbox[5]  # Top of surface
        
        objects_on_surface = []
        
        # Check all objects in the world
        for obj in world.objects:
            if not hasattr(obj, 'name') or not hasattr(obj, 'get_position'):
                continue
                
            # Skip surfaces and the kitchen itself
            if obj.name == "kitchen" or obj.name in PLACEMENT_SURFACES:
                continue
                
            obj_pos = obj.get_position()
            
            # Convert to list if it's not already
            if hasattr(obj_pos, 'x'):
                obj_pos = [obj_pos.x, obj_pos.y, obj_pos.z]
                
            # Check if object is on the surface (X/Y within bounds, Z close to surface)
            if (surface_min_x <= obj_pos[0] <= surface_max_x and
                surface_min_y <= obj_pos[1] <= surface_max_y and
                abs(obj_pos[2] - surface_z) < 0.2):  # Within 20cm above surface
                
                objects_on_surface.append({
                    "name": obj.name,
                    "position": obj_pos,
                    "type": obj.__class__.__name__ if hasattr(obj, '__class__') else "Object"
                })
        
        return objects_on_surface
            
    except Exception as e:
        print(f"Error detecting objects on {surface_name}: {str(e)}")
        return []