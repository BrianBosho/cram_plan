"""
Utility module for handling kitchen surfaces and placement locations in PyCRAM.
"""
from pycram.datastructures.pose import Pose
from pycram.world_concepts.world_object import Object
from pycram.datastructures.enums import ObjectType
from utils.color_wrapper import ColorWrapper
import numpy as np

# Key surfaces where objects can be placed
PLACEMENT_SURFACES = {
    # Primary surfaces
    "sink_area_surface": {
        "description": "Countertop around the sink",
        "height": 0.95,
        "recommended_for": ["utensils", "dishes", "cleaning_supplies"],
        "position": [2.115, 2.35, 0.95]  # From URDF: sink_area_footprint (1.825, 1.32) + sink_area (0.29, 1.03) + height
    },
    "kitchen_island_surface": {
        "description": "Kitchen island's main countertop",
        "height": 0.95,
        "recommended_for": ["food", "dishes", "utensils", "cooking_supplies"],
        "position": [-1.0675, 1.7192, 0.95]  # From URDF: kitchen_island_footprint (-1.365, 0.59) + kitchen_island (0.2975, 1.1292) + height
    },
    "kitchen_island_stove": {
        "description": "Cooking surface on the island",
        "height": 0.97,
        "recommended_for": ["pots", "pans", "cooking_utensils"],
        "position": [-1.0675, 2.485, 0.97]  # From URDF: kitchen_island position + (0, 0.7658) + height
    },
    "table_area_main": {
        "description": "Dining table surface",
        "height": 0.74,
        "recommended_for": ["dishes", "food", "utensils"],
        "position": [-1.4, -1.05, 0.74]  # From URDF: direct position
    },
    "oven_area_area": {
        "description": "Countertop in the oven area",
        "height": 0.95,
        "recommended_for": ["baking_supplies", "hot_food"],
        "position": [2.095, 3.12, 0.95]  # From URDF: oven_area_footprint (1.805, 2.52) + oven_area (0.29, 0.6) + height
    },
    
    # Secondary surfaces
    "sink_area_sink": {
        "description": "Inside the sink",
        "height": 0.90,
        "recommended_for": ["dirty_dishes", "washing_items"],
        "position": [2.12, 2.82, 0.90]  # From URDF: sink_area_surface + (0.005, 0.47) + adjusted height
    },
    "oven_area_oven_door": {
        "description": "Top of the closed oven door",
        "height": 0.85,
        "recommended_for": ["hot_dishes", "mitts"],
        "position": [2.3687, 3.12, 0.85]  # From URDF: oven_area + (0.2737, 0) + adjusted height
    },
    "fridge_area": {
        "description": "Top of the refrigerator",
        "height": 1.75,
        "recommended_for": ["lightweight_items", "cereal_boxes"],
        "position": [2.115, -0.44, 1.75]  # From URDF: fridge_area_footprint (1.825, -0.74) + fridge_area (0.29, 0.3) + height
    }
}

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
    if not world:
        print("World not initialized")
        # Return fallback position if available
        if surface_name in PLACEMENT_SURFACES and "position" in PLACEMENT_SURFACES[surface_name]:
            return PLACEMENT_SURFACES[surface_name]["position"]
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
            if hasattr(surface, 'get_position'):
                pos = surface.get_position()
                if hasattr(pos, 'x') and hasattr(pos, 'y') and hasattr(pos, 'z'):
                    return [pos.x, pos.y, pos.z]
                else:
                    return list(pos)
            else:
                print(f"Warning: {surface_name} doesn't have get_position method")
                # Return fallback position if available
                if surface_name in PLACEMENT_SURFACES and "position" in PLACEMENT_SURFACES[surface_name]:
                    print(f"Using fallback position for {surface_name}: {PLACEMENT_SURFACES[surface_name]['position']}")
                    return PLACEMENT_SURFACES[surface_name]["position"]
                return None
        
        print(f"Surface {surface_name} not found in world")
        # Return fallback position if available
        if surface_name in PLACEMENT_SURFACES and "position" in PLACEMENT_SURFACES[surface_name]:
            print(f"Using fallback position for {surface_name}: {PLACEMENT_SURFACES[surface_name]['position']}")
            return PLACEMENT_SURFACES[surface_name]["position"]
        return None
        
    except Exception as e:
        print(f"Error getting position for {surface_name}: {str(e)}")
        # Return fallback position if available
        if surface_name in PLACEMENT_SURFACES and "position" in PLACEMENT_SURFACES[surface_name]:
            print(f"Using fallback position for {surface_name}: {PLACEMENT_SURFACES[surface_name]['position']}")
            return PLACEMENT_SURFACES[surface_name]["position"]
        return None

def place_on_surface(world, item_name, surface_name, offset_x=0, offset_y=0):
    """
    Place an existing item on a specified surface.
    
    Args:
        world: The BulletWorld instance
        item_name (str): Name of the item to place
        surface_name (str): Name of the surface
        offset_x (float): X offset from center of surface
        offset_y (float): Y offset from center of surface
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not world:
        print("World not initialized")
        return False
        
    try:
        # Get the item and surface
        item = next((obj for obj in world.objects if hasattr(obj, 'name') and obj.name == item_name), None)
        
        if not item:
            print(f"Item {item_name} not found in world")
            return False
            
        # Get surface dimensions and position
        dims, bbox = get_surface_dimensions(world, surface_name)
        surface_pos = get_surface_position(world, surface_name)
        
        if not surface_pos:
            print(f"Surface {surface_name} position could not be determined")
            return False
            
        # Get item dimensions
        item_bbox = item.get_bounding_box() if hasattr(item, 'get_bounding_box') else None
        item_height = 0.05  # Default height if we can't get it
        
        if item_bbox:
            item_height = (item_bbox[5] - item_bbox[2]) / 2  # Half of the height
        
        # Calculate placement position
        surface_height = dims[2] if dims else PLACEMENT_SURFACES.get(surface_name, {}).get("height", 0.95)
        
        # New position: surface position + offsets + height adjustment
        new_pos = [
            surface_pos[0] + offset_x,
            surface_pos[1] + offset_y,
            surface_height + item_height
        ]
        
        # Place the item
        if hasattr(item, 'set_position'):
            item.set_position(new_pos)
            print(f"Placed {item_name} on {surface_name} at position {new_pos}")
            return True
        else:
            print(f"Item {item_name} doesn't have set_position method")
            return False
            
    except Exception as e:
        print(f"Error placing {item_name} on {surface_name}: {str(e)}")
        return False

def spawn_object_on_surface(world, obj_type, obj_name, surface_name, color="red", offset_x=0, offset_y=0):
    """
    Spawn a new object directly on a specific surface.
    
    Args:
        world: The BulletWorld instance
        obj_type: Object type or class
        obj_name (str): Name for the new object
        surface_name (str): Name of the surface to place on
        color (str): Color name for the object
        offset_x (float): X offset from center of surface
        offset_y (float): Y offset from center of surface
        
    Returns:
        dict: Result of the operation with status and object info
    """
    if not world:
        return {"status": "error", "message": "World not initialized"}
        
    try:
        # Get surface info
        surface_info = get_surface_info(surface_name)
        if not surface_info:
            return {"status": "error", "message": f"Surface '{surface_name}' not found"}
            
        # Get surface position
        surface_pos = get_surface_position(world, surface_name)
        if not surface_pos:
            return {"status": "error", "message": f"Surface '{surface_name}' position not found"}
            
        print(f"Surface {surface_name} position: {surface_pos}")
        
        # Import necessary classes
        from pycram.world_concepts.world_object import Object
        from pycram.datastructures.pose import Pose
        from pycram.datastructures.enums import ObjectType
        from utils.color_wrapper import ColorWrapper
        
        # Create color wrapper for the object
        color_wrapper = ColorWrapper(color) if color else None
        
        # Get object type enum and file name
        ont_type = None
        obj_file = None
        
        # Handle string type names
        if isinstance(obj_type, str):
            obj_type_lower = obj_type.lower()
            
            if obj_type_lower == "cereal":
                # Try both import approaches for cereal
                try:
                    from pycrap.ontologies import Cereal
                    ont_type = Cereal
                    obj_file = "breakfast_cereal.stl"
                except ImportError:
                    ont_type = ObjectType.CEREAL
                    obj_file = "breakfast_cereal.stl"
            elif obj_type_lower == "milk":
                try:
                    from pycrap.ontologies import Milk
                    ont_type = Milk
                    obj_file = "milk.stl"
                except ImportError:
                    ont_type = ObjectType.MILK
                    obj_file = "milk.stl"
            elif obj_type_lower == "spoon":
                try:
                    from pycrap.ontologies import Spoon
                    ont_type = Spoon
                    obj_file = "spoon.stl"
                except ImportError:
                    ont_type = ObjectType.SPOON
                    obj_file = "spoon.stl"
            elif obj_type_lower == "bowl":
                try:
                    from pycrap.ontologies import Bowl
                    ont_type = Bowl
                    obj_file = "bowl.stl"
                except ImportError:
                    ont_type = ObjectType.BOWL
                    obj_file = "bowl.stl"
            else:
                # Use generic type for unknown objects
                ont_type = ObjectType.GENERIC
                obj_file = f"{obj_type_lower}.stl"
        else:
            # If obj_type is already a class or enum
            ont_type = obj_type
            
            # Try to get the name for the file
            try:
                type_name = ont_type.__name__.lower()
                if type_name == "cereal":
                    obj_file = "breakfast_cereal.stl"
                else:
                    obj_file = f"{type_name}.stl"
            except:
                # Fallback to generic name
                obj_file = "generic.stl"
        
        # Calculate position with offset and height
        # Get the surface height from info or use position[2]
        surface_height = surface_info.get("height", surface_pos[2])
        
        # Calculate final position (add some height for the object)
        final_pos = [
            surface_pos[0] + offset_x, 
            surface_pos[1] + offset_y,
            surface_height + 0.1  # Add 10cm to place object on top of surface
        ]
        
        print(f"Creating {obj_name} of type {ont_type} at position {final_pos}")
        
        # Create the object
        pose = Pose(final_pos)
        obj = Object(obj_name, ont_type, obj_file, pose=pose, color=color_wrapper)
        
        return {
            "status": "success",
            "message": f"Object {obj_name} created on {surface_name}",
            "object": {
                "name": obj_name,
                "type": str(ont_type),
                "position": final_pos,
                "color": color if color else "default"
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Error spawning object on surface: {str(e)}"}

def detect_objects_on_surface(world, surface_name):
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