#!/usr/bin/env python3
"""
Non-interactive versions of robot actions for API usage.
"""
import time
import threading
from pycram.process_module import simulated_robot
from pycram.designators.motion_designator import *
from pycram.designators.location_designator import *
from pycram.designators.action_designator import *
from pycram.designators.object_designator import *
from pycram.datastructures.enums import Arms, Grasp, TorsoState, DetectionTechnique
from pycram.datastructures.pose import Pose
from pycram.world_concepts.world_object import Object
from pycram.datastructures.enums import ObjectType
from pycrap.ontologies import Milk, Cereal, Spoon, Bowl
from utils.color_wrapper import ColorWrapper
import numpy as np
import base64
import io
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from pycram.robot_description import RobotDescription
from pycram.datastructures.enums import Frame
from io import BytesIO
from typing import TypedDict, Any
from utils.rotation import euler_to_quaternion

from pycram.failures import (
    LookAtGoalNotReached,
    
)




class Response(TypedDict):
    status: str
    message: str
    payload: Any = None


def detect_object(object_name=None, location=None):
    """
    Detect an object in the robot's environment and return information about it.
    
    Parameters:
        object_name (str): Name of the object to detect. If None, will detect any visible object.
        location (dict or Pose): Location to search for objects. Can be a dictionary with 'position' 
                                and optional 'orientation' keys, or a Pose object.
    
    Returns:
        dict: A response object with the following fields:
            - status (str): 'success' if object was detected, 'error' otherwise
            - message (str): A description of the operation result
            - payload (dict): Information about the detected object(s) if successful
    """
    try:
        from pycram.datastructures.enums import DetectionTechnique, DetectionState
        from pycram.designators.location_designator import Location
        from pycram.datastructures.pose import Pose
        
        with simulated_robot:
            # First, try to look in the general direction where objects might be
            try:
                # Get the world
                world = get_world_safely()
                if world is None:
                    return {"status": "error", "message": "World is not initialized"}
                
                # Find a central pose to look at (any object that's not the robot)
                central_pose = None
                for obj in world.objects:
                    if obj.name != "pr2" and obj.name not in ["kitchen", "apartment", "floor", "wall"]:
                        central_pose = obj.pose
                        break
                
                if central_pose:
                    # Look at the object to orient the robot's camera
                    LookAtAction(targets=[central_pose]).resolve().perform()
            except Exception as e:
                print(f"Warning: Could not orient robot camera: {str(e)}")
            
            # If object_name is provided, try to find it directly in the world
            if object_name:
                print(f"API: Looking for object with name: {object_name}")
                matching_objects = []
                
                for obj in world.objects:
                    if obj.name.lower() == object_name.lower():
                        matching_objects.append(obj)
                
                if matching_objects:
                    # Extract information about detected objects
                    objects_info = []
                    for obj in matching_objects:
                        obj_info = {
                            "name": obj.name,
                            "type": str(obj.type if hasattr(obj, "type") else type(obj).__name__)
                        }
                        
                        # Get object position
                        try:
                            pose = obj.pose
                            if pose:
                                position = pose.position
                                obj_info["position"] = {
                                    "x": float(position[0]),
                                    "y": float(position[1]),
                                    "z": float(position[2])
                                }
                                
                                # Get dimensions if available
                                if hasattr(obj, "dimensions"):
                                    dims = obj.dimensions
                                    obj_info["dimensions"] = {
                                        "x": float(dims[0]),
                                        "y": float(dims[1]),
                                        "z": float(dims[2])
                                    }
                        except Exception as pos_error:
                            print(f"Warning: Could not get position for {obj.name}: {str(pos_error)}")
                        
                        # Get color if available
                        if hasattr(obj, "color"):
                            obj_info["color"] = str(obj.color)
                        
                        objects_info.append(obj_info)
                    
                    return {
                        "status": "success",
                        "message": f"Successfully found object: {object_name}",
                        "object": objects_info[0] if len(objects_info) == 1 else None,
                        "objects": objects_info
                    }
            
            # If we get here, either no object_name was provided or the object wasn't found directly
            # So we'll use the DetectAction to find objects
            
            # Prepare object designator based on input
            object_designator = None
            if object_name:
                object_designator = BelieveObject(names=[object_name])
            
            # Prepare location if provided (location and region are the same parameter in PyCRAM)
            location_designator = None
            if location:
                try:
                    # If location is already a Pose object, use it directly
                    if isinstance(location, Pose):
                        location_pose = location
                    # If location is a dictionary, create a Pose from it
                    elif isinstance(location, dict):
                        position = location.get('position', [0, 0, 0])
                        orientation = location.get('orientation', [0, 0, 0, 1])
                        location_pose = Pose(position, orientation)
                    else:
                        # Try to convert to a Pose if it's something else
                        location_pose = Pose(location)
                    
                    # Create a Location designator with the pose
                    location_designator = Location(poses=[location_pose])
                except Exception as loc_error:
                    print(f"Warning: Could not create location designator: {str(loc_error)}")
            
            # Perform detection
            print(f"API: Detecting objects using DetectAction")
            try:
                detected_objects = DetectAction(
                    technique=DetectionTechnique.ALL,
                    state=DetectionState.START,
                    object_designator_description=object_designator,
                    region=location_designator
                ).resolve().perform()
                
                # Process detection results
                if not detected_objects:
                    return {
                        "status": "error", 
                        "message": f"No objects detected{' matching ' + object_name if object_name else ''}"
                    }
                
                # Filter objects by name if specified
                if object_name:
                    detected_objects = [obj for obj in detected_objects if obj.name.lower() == object_name.lower()]
                    if not detected_objects:
                        return {
                            "status": "error",
                            "message": f"No objects detected matching '{object_name}'"
                        }
                
                # Extract information about detected objects
                objects_info = []
                for obj in detected_objects:
                    obj_info = {
                        "name": obj.name,
                        "type": str(obj.type if hasattr(obj, "type") else type(obj).__name__)
                    }
                    
                    # Get object position
                    try:
                        if hasattr(obj, "get_pose"):
                            pose = obj.get_pose()
                            position = pose.position
                            obj_info["position"] = {
                                "x": float(position[0]),
                                "y": float(position[1]),
                                "z": float(position[2])
                            }
                    except Exception as pos_error:
                        print(f"Warning: Could not get position for {obj.name}: {str(pos_error)}")
                    
                    # Get color if available
                    if hasattr(obj, "color"):
                        obj_info["color"] = str(obj.color)
                    
                    objects_info.append(obj_info)
                
                # Return success response with object information
                if object_name and len(objects_info) == 1:
                    return {
                        "status": "success",
                        "message": f"Successfully detected object: {object_name}",
                        "object": objects_info[0]
                    }
                else:
                    return {
                        "status": "success",
                        "message": f"Successfully detected {len(objects_info)} object(s)",
                        "objects": objects_info
                    }
                
            except Exception as detect_error:
                return {
                    "status": "error",
                    "message": f"Detection failed: {str(detect_error)}"
                }
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error", 
            "message": f"Error during object detection: {str(e)}"
        }

def look_at_object(obj_name: str) -> Response:
    """
    Make the robot look at the specified object.
    
    Parameters:
        obj_name (str): The name of the object to look at. Required parameter.
    
    Returns:
        Response: A response object with the following fields:
            - status (str): 'success' if robot successfully looks at object, 'error' otherwise
            - message (str): A description of the operation result
    
    Errors:
        - Returns error response if no object with the specified name is in the environment
        - Returns error response if the robot cannot successfully look at the object
        - obj_name parameter must be provided, otherwise will raise TypeError
        
    Notes:
        - Implicitly relies on the simulation being initialized
        - Object name is converted to lowercase for case-insensitive comparison
        - The function first checks if the object exists in the environment
        - Then attempts to make the robot look at the object
    """
    obj_name = obj_name.lower()

    with simulated_robot:
        try:
            obj = BelieveObject(names=[obj_name]).resolve()
        except StopIteration:
            obj = None

    if obj is None:
        return Response(
            status="error", message=f"Object '{obj_name}' is not in the environment"
        )

    with simulated_robot:
        try:
            LookAtAction(targets=[obj.pose]).resolve().perform()
            looking_at_object = True
        except LookAtGoalNotReached:
            looking_at_object = False

    if not looking_at_object:
        return Response(
            status="error", message=f"Robot vision failed to reach '{obj_name}'"
        )

    return Response(status="success", message=f"Robot is now looking at '{obj_name}'")
# Import from environment but avoid initialization side effects
def get_world_safely():
    from environment import get_world
    return get_world()

def calculate_object_distances(source_object=None, target_objects=None, exclude_types=None, world=None):
    """
    Calculate distances between objects in the world.
    
    Parameters:
    -----------
    source_object : str or None
        Name of source object. If None, will calculate distances between all pairs.
    target_objects : list or None
        List of target object names. If None, will use all objects.
    exclude_types : list or None
        List of object types to exclude (like 'floor', 'wall', etc.)
        
    Returns:
    --------
    dict
        Dictionary of distances between objects
    """
    # global world
    if world is None:
        print("Cannot calculate distances because the world is not initialized.")
        return {}
    
    # Default exclusion list if not provided
    if exclude_types is None:
        exclude_types = ['floor', 'wall', 'ceiling', 'ground']
    
    # Get all objects or filter by provided names
    all_objects = world.objects
    filtered_objects = []
    
    for obj in all_objects:
        # Skip excluded types
        if any(exclude_type in obj.name.lower() for exclude_type in exclude_types):
            continue
        filtered_objects.append(obj)
    
    # If target objects specified, filter to only those
    if target_objects:
        filtered_objects = [obj for obj in filtered_objects if obj.name in target_objects]
    
    # If source object specified, only measure from that object
    if source_object:
        source = world.get_object_by_name(source_object)
        if source is None:
            print(f"Source object '{source_object}' not found.")
            return {}
        
        distances = {}
        source_pos = source.get_position()
        
        for obj in filtered_objects:
            if obj.name == source_object:
                continue
                
            obj_pos = obj.get_position()
            dist = np.sqrt((source_pos.x - obj_pos.x)**2 + 
                          (source_pos.y - obj_pos.y)**2 + 
                          (source_pos.z - obj_pos.z)**2)
            
            distances[obj.name] = dist
        
        return distances
    
    # Otherwise calculate all pairwise distances
    else:
        distances = {}
        
        # Get all unique pairs of objects
        for obj1, obj2 in itertools.combinations(filtered_objects, 2):
            pos1 = obj1.get_position()
            pos2 = obj2.get_position()
            
            dist = np.sqrt((pos1.x - pos2.x)**2 + 
                          (pos1.y - pos2.y)**2 + 
                          (pos1.z - pos2.z)**2)
            
            key = f"{obj1.name}-to-{obj2.name}"
            distances[key] = dist
        
        return distances

def move_robot(coordinates=None):
    """
    Move robot to specified coordinates without interactive prompts.
    
    Args:
        coordinates (list): [x, y, z] coordinates to move to
        
    Returns:
        dict: Result of the operation
    """
    try:
        # Use provided coordinates or defaults
        if coordinates is None or len(coordinates) != 3:
            coordinates = [0, 0, 0]  # Default position
            
        dest_vals = [float(val) for val in coordinates]
        
        with simulated_robot:
            robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()
            nav_pose = Pose(dest_vals)
            navigate_action = NavigateAction(target_locations=[nav_pose]).resolve()
            print(f"API: Navigating to {nav_pose}")
            navigate_action.perform()
            print("API: Robot has moved to destination.")
        
        return {
            "status": "success", 
            "message": f"Robot moved to coordinates {dest_vals}",
            "coordinates": dest_vals
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def pickup_and_place(object_name=None, target_location=None, arm=None):
    """
    Pick up an object and place it at a target location without interactive prompts.
    
    Args:
        object_name (str): Name of the object to pick up
        target_location (list): [x, y, z] coordinates for placement
        arm (str): Which arm to use ('left', 'right', or None for automatic)
        
    Returns:
        dict: Result of the operation
    """
    try:
        # Default values
        if object_name is None:
            object_name = "cereal"  # Default object to pick up
            
        if target_location is None:
            target_location = [1.4, 1.0, 0.95]  # Default placement location
            
        # Convert arm string to enum
        arm_enum = None
        if arm == "left":
            arm_enum = Arms.LEFT
        elif arm == "right":
            arm_enum = Arms.RIGHT
        
        # Perform pickup and place action
        with simulated_robot:
            # Get the world
            world = get_world_safely()
            
            # Make object name lookup case-insensitive
            # First, try the exact name as provided
            object_desig = BelieveObject(names=[object_name])
            
            # If that fails, try a case-insensitive search
            robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()
            
            print(f"API: Preparing to pick up {object_name}...")
            # print the target location
            print(f"API: Target location: {target_location}")
            
            
            # Park arms and adjust torso for pickup
            ParkArmsAction([Arms.BOTH]).resolve().perform()
            MoveTorsoAction([TorsoState.HIGH]).resolve().perform()
            
            # Resolve pickup location
            print("API: Resolving pickup location...")
            try:
                # Try to resolve with the original name case
                try:
                    object_resolved = object_desig.resolve()
                except StopIteration:
                    # If that fails, try some case variations
                    print(f"API: Could not find '{object_name}', trying case variations...")
                    variants = [
                        object_name.lower(),
                        object_name.upper(),
                        object_name.capitalize()
                    ]
                    
                    # Try each case variant
                    object_resolved = None
                    for variant in variants:
                        if variant != object_name:  # Skip if same as original
                            try:
                                variant_desig = BelieveObject(names=[variant])
                                object_resolved = variant_desig.resolve()
                                if object_resolved:
                                    print(f"API: Found object with name '{variant}'")
                                    object_desig = variant_desig  # Use the successful designator
                                    object_name = variant  # Update name for messages
                                    break
                            except StopIteration:
                                continue
                    
                    if not object_resolved:
                        return {"status": "error", "message": f"Object '{object_name}' not found in the world. You may need to spawn it first."}
                
                if not object_resolved:
                    return {"status": "error", "message": f"Object '{object_name}' not found in the world. You may need to spawn it first."}
                
                pickup_pose = CostmapLocation(
                    target=object_resolved,
                    reachable_for=robot_desig
                ).resolve()
            except StopIteration:
                return {"status": "error", "message": f"Object '{object_name}' not found in the world. You may need to spawn it first."}
            except Exception as e:
                return {"status": "error", "message": f"Error finding object location: {str(e)}"}
            
            if not pickup_pose.reachable_arms:
                return {"status": "error", "message": f"No reachable arms for object {object_name}"}
            
            # Use specified arm or the first available one
            pickup_arm = arm_enum if arm_enum else pickup_pose.reachable_arms[0]
            
            # Navigate to pickup location
            print(f"API: Navigating to pickup location at {pickup_pose.pose}")
            NavigateAction(target_locations=[pickup_pose.pose]).resolve().perform()
            
            # Execute pickup
            print("API: Executing pickup action...")
            PickUpAction(
                object_designator_description=object_desig,
                arms=[pickup_arm],
                grasps=[Grasp.FRONT]
            ).resolve().perform()
            
            ParkArmsAction([Arms.BOTH]).resolve().perform()
            print("API: Pickup action performed.")
            
            # Allow simulation state to update
            time.sleep(0.5)
            
            # Prepare for placement
            destination_pose = Pose(target_location)
            print(f"API: Destination pose for placement: {destination_pose}")
            
            # Resolve placement location
            print("API: Resolving placement location...")
            
            # Simple timeout implementation for placement resolution
           
            
            place_stand = None
            resolution_timeout = 5  # seconds
            resolution_complete = False
            resolution_error = None
            
            def resolve_placement():
                nonlocal place_stand, resolution_complete, resolution_error
                try:
                    place_stand = CostmapLocation(
                        destination_pose,
                        reachable_for=robot_desig,
                        reachable_arm=pickup_arm
                    ).resolve()
                    resolution_complete = True
                except Exception as e:
                    resolution_error = str(e)
                    resolution_complete = True
            
            # Start resolution in thread
            resolution_thread = threading.Thread(target=resolve_placement)
            resolution_thread.daemon = True
            resolution_thread.start()
            
            # Wait for resolution with timeout
            start_time = time.time()
            while not resolution_complete and time.time() - start_time < resolution_timeout:
                time.sleep(0.1)
            
            # Check resolution status
            if not resolution_complete:
                print("API: Placement location resolution timed out")
                # Fallback to direct placement at the current location
                place_stand = None
                
            if resolution_error:
                print(f"API: Error in placement resolution: {resolution_error}")
                place_stand = None
                
            # If resolution failed, use a direct approach
            if place_stand is None or not hasattr(place_stand, 'pose'):
                print("API: Using fallback placement approach")
                # Try a direct placement without costmap resolution
                print("API: Executing place action with direct pose...")
                try:
                    PlaceAction(
                        object_designator_description=object_desig,
                        target_locations=[destination_pose],
                        arms=[pickup_arm]
                    ).resolve().perform()
                    
                    ParkArmsAction([Arms.BOTH]).resolve().perform()
                    print("API: Place action completed with fallback method.")
                    
                    return {
                        "status": "success",
                        "message": f"Successfully picked up {object_name} and placed at {target_location} (using fallback)",
                        "object": object_name,
                        "target_location": target_location,
                        "arm_used": str(pickup_arm)
                    }
                except Exception as place_error:
                    return {"status": "error", "message": f"Failed to place object using fallback method: {str(place_error)}"}
            
            # Regular placement execution if resolution succeeded
            # Navigate to placement location
            print(f"API: Navigating to placement location at {place_stand.pose}")
            NavigateAction(target_locations=[place_stand.pose]).resolve().perform()
            
            # Execute place action
            print("API: Executing place action...")
            PlaceAction(
                object_designator_description=object_desig,
                target_locations=[destination_pose],
                arms=[pickup_arm]
            ).resolve().perform()
            
            ParkArmsAction([Arms.BOTH]).resolve().perform()
            print("API: Place action completed successfully.")
            
            return {
                "status": "success",
                "message": f"Successfully picked up {object_name} and placed at {target_location}",
                "object": object_name,
                "target_location": target_location,
                "arm_used": str(pickup_arm)
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def robot_perceive(perception_area=None):
    """
    Make the robot perceive its environment without interactive prompts.
    
    Args:
        perception_area (str): Area to perceive ('table', 'room', etc.)
        
    Returns:
        dict: Result of the operation with perceived objects
    """
    try:
        # Get the world reference 
        world = get_world_safely()
        if world is None:
            return {
                "status": "error", 
                "message": "World is not initialized."
            }
        
        with simulated_robot:
            # Use a proper perception action based on reference code
            perceived_objects = []
            
            if perception_area is None:
                perception_area = "table"  # Default area
            
            # Try to use a proper detection action
            try:
                # First, try to use LookAtAction to orient the robot
                # Find a central pose to look at
                central_pose = None
                
                # If the world has objects, look at the first one
                if hasattr(world, "objects") and world.objects:
                    for obj in world.objects:
                        if obj.name != "pr2" and obj.name not in ["kitchen", "apartment"]:
                            central_pose = obj.pose
                            break
                
                if central_pose:
                    # Look at the object
                    LookAtAction(targets=[central_pose]).resolve().perform()
                
                # Now perform actual perception
                if perception_area.lower() in ["table", "counter", "surface"]:
                    # Try to detect common objects on surfaces
                    common_types = ["Milk", "Cereal", "Spoon", "Bowl"]
                    for obj_type in common_types:
                        try:
                            detected = DetectAction(
                                technique=DetectionTechnique.TYPES,
                                object_designator_description=BelieveObject(types=[obj_type])
                            ).resolve().perform()
                            
                            if detected:
                                for obj in detected:
                                    perceived_objects.append({
                                        "name": obj.name if hasattr(obj, "name") else "unknown",
                                        "type": obj_type,
                                        "pose": str(obj.pose) if hasattr(obj, "pose") else "unknown"
                                    })
                        except Exception as detect_error:
                            print(f"Detection error for type {obj_type}: {detect_error}")
                else:
                    # Fallback to a general perception
                    if hasattr(world, "objects"):
                        for obj in world.objects:
                            if obj.name != "pr2" and obj.name not in ["kitchen", "apartment"]:
                                perceived_objects.append({
                                    "name": obj.name,
                                    "type": str(type(obj)),
                                    "pose": str(obj.pose) if hasattr(obj, "pose") else "unknown"
                                })
            except Exception as perception_error:
                print(f"Error during perception: {perception_error}")
                
                # Fallback to direct world object access
                if hasattr(world, "objects"):
                    for obj in world.objects:
                        if obj.name != "pr2" and obj.name not in ["kitchen", "apartment"]:
                            perceived_objects.append({
                                "name": obj.name,
                                "type": str(type(obj)),
                                "pose": str(obj.pose) if hasattr(obj, "pose") else "unknown"
                            })
                
        return {
            "status": "success",
            "message": f"Robot perceived {len(perceived_objects)} objects in {perception_area}",
            "perceived_objects": perceived_objects
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


def transport_object(object_name=None, target_location=None, arm=None):
    """
    Transport an object to a target location without interactive prompts.
    
    Args:
        object_name (str): Name of the object to transport
        target_location (list): [x, y, z] coordinates for the target location
        arm (str): Which arm to use ('left', 'right')
        
    Returns:
        dict: Result of the operation
    """
    try:
        if object_name is None:
            object_name = "cereal"  # Default object
            
        if target_location is None:
            target_location = [1.0, 1.0, 0.8]  # Default target location
            
        # Convert arm string to enum
        arm_enum = None
        if arm == "left":
            arm_enum = Arms.LEFT
        elif arm == "right":
            arm_enum = Arms.RIGHT
        else:
            # Default to right arm if not specified
            arm_enum = Arms.RIGHT
            
        with simulated_robot:
            # Create object designator
            object_desig = BelieveObject(names=[object_name])
            destination_pose = Pose(target_location)
            
            print(f"API: Transporting {object_name} to {target_location} using {arm_enum}...")
            
            # Execute transport action with the correct parameter names
            TransportAction(
                object_desig, 
                [destination_pose],
                [arm_enum]
            ).resolve().perform()
            
            print(f"API: Transport action completed for {object_name}")
            
        return {
            "status": "success",
            "message": f"Successfully transported {object_name} to {target_location}",
            "object": object_name,
            "target_location": target_location,
            "arm_used": str(arm_enum)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def spawn_objects(object_choice=None, coordinates=None, color=None):
    """
    Non-interactive version of spawn_objects that creates objects based on parameters.
    
    Args:
        object_choice (str): "cereal", "milk", "spoon", "bowl", or a custom name
        coordinates (list): [x, y, z] coordinates for object placement
        color (str): Color name (e.g., "red", "blue") or None for default
        
    Returns:
        dict: Information about the created object
    """
    try:
        # Define available object types
        object_types = {
            "cereal": (Cereal, "breakfast_cereal.stl"),
            "milk": (Milk, "milk.stl"),
            "spoon": (Spoon, "spoon.stl"),
            "bowl": (Bowl, "bowl.stl")
        }
        
        # Default values
        if object_choice is None:
            object_choice = "bowl"
            
        if coordinates is None:
            coordinates = [1.4, 1.0, 0.95]  # Default position
            
        # Parse coordinates
        try:
            pose_vals = [float(val) for val in coordinates]
            if len(pose_vals) != 3:
                return {"status": "error", "message": "Coordinates must have exactly 3 values (x,y,z)"}
        except Exception as e:
            return {"status": "error", "message": f"Error parsing coordinates: {str(e)}"}
            
        # Handle color
        color_wrapper = ColorWrapper(color) if color else None
        
        # Create the object
        if object_choice in object_types:
            obj_ontology, obj_file = object_types[object_choice]
            obj_name = object_choice  # Use the choice as the name
        else:
            # Custom/generic object
            obj_name = object_choice
            obj_ontology = ObjectType.GENERIC
            obj_file = f"{object_choice}.stl"  # Assume filename matches object name
            
        # Create the object
        try:
            obj = Object(
                obj_name, 
                obj_ontology, 
                obj_file, 
                pose=Pose(pose_vals), 
                color=color_wrapper
            )
            
            print(f"API: Object '{obj_name}' created at pose {pose_vals} with color {color if color else 'default'}.")
            
            return {
                "status": "success",
                "message": f"Object '{obj_name}' created successfully",
                "object": {
                    "name": obj_name,
                    "type": str(obj_ontology),
                    "file": obj_file,
                    "pose": pose_vals,
                    "color": color if color else "default"
                }
            }
        except FileNotFoundError as e:
            return {"status": "error", "message": f"File not found: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Error creating object: {str(e)}"}
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


def capture_camera_image(world, display=False, save_path=None, target_distance=2.0):
    """
    Capture an image from the robot's camera.
    
    Parameters:
    -----------
    display : bool
        Whether to display the image (default: True)
    save_path : str or None
        Path to save the image, if None the image is not saved (default: None)
    target_distance : float
        Distance in meters to the target point (default: 2.0)
        
    Returns:
    --------
    tuple
        (rgb_image, depth_image, segmentation_mask) - The RGB, depth, and segmentation images
    """
    
    if world is None:
        print("Cannot capture image because the world is not initialized.")
        return None
    
    # Get the camera configuration
    robot = world.robot
    camera_link_name = RobotDescription.current_robot_description.get_camera_link()
    camera_link = robot.get_link(camera_link_name)
    camera_pose = camera_link.pose
    camera_axis = RobotDescription.current_robot_description.get_default_camera().front_facing_axis
    
    # Create a target point in front of the camera
    target = np.array(camera_axis) * target_distance
    target_pose = Pose(target, frame=camera_link.tf_frame)
    target_pose = robot.local_transformer.transform_pose(target_pose, Frame.Map.value)
    
    # Get the images (RGB, depth, segmentation)
    images = world.get_images_for_target(target_pose, camera_pose)
    rgb_image = images[0]  # RGB image is typically the first returned image
    depth_image = images[1]  # Depth image is typically the second returned image
    segmentation_mask = images[2]  # Segmentation mask is at index 2
    
    # Display the RGB image if requested
    if display:
        plt.figure(figsize=(10, 8))
        plt.imshow(rgb_image)
        plt.axis('off')
        plt.title('Robot Camera View')
        plt.tight_layout()
        
        # Save the image if a path is provided
        if save_path:
            plt.savefig(save_path)
        
        plt.show()
    
    # Save without displaying if needed
    elif save_path:
        plt.figure(figsize=(10, 8))
        plt.imshow(rgb_image)
        plt.axis('off')
        plt.title('Robot Camera View')
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
    
    return rgb_image, depth_image, segmentation_mask

def demo_camera():
    """
    Demonstrate camera functionality by capturing and displaying an image from the robot's camera.
    """
    global world
    if world is None:
        print("Cannot demonstrate camera because the world is not initialized.")
        return

    print("Moving robot to position with good view...")
    with simulated_robot:
        # Position robot for a good view
        park_action = ParkArmsAction([Arms.BOTH]).resolve()
        park_action.perform()
        
        move_torso = MoveTorsoAction([TorsoState.HIGH]).resolve()
        move_torso.perform()
        
        # You can add navigation here if needed to get a better view
        
        print("Capturing camera image...")
        images = capture_camera_image(display=True, save_path="robot_view.png")
        if images:
            print("Image captured successfully!")
            return images
        else:
            print("Failed to capture image.")
            return None

def get_robot_camera_images(target_distance=2.0, world=None):
    """
    Capture images from the robot's camera and return them as base64-encoded strings.
    
    Args:
        target_distance (float): Distance in meters to the target point
        
    Returns:
        dict: Result with encoded images
    """
    try:
        # Convert target_distance to float if provided
        if target_distance is not None:
            target_distance = float(target_distance)
        else:
            target_distance = 2.0  # Default value
            
        # Import the capture function
        from robot_actions_api import capture_camera_image
        
        # Capture images without displaying them
        rgb_image, depth_image, segmentation_mask = capture_camera_image(
            display=False, 
            save_path=None,
            target_distance=target_distance,
            world=world
        )
        
        if rgb_image is None:
            return {"status": "error", "message": "Failed to capture camera images"}
        
        # Convert images to base64 strings
        def encode_image(img):
            if img is None:
                return None
                
            # For depth images, normalize and colormap for better visualization
            if len(img.shape) == 2:  # It's a depth image
                plt.figure(figsize=(10, 8))
                plt.imshow(img, cmap='viridis')
                plt.axis('off')
                plt.tight_layout()
                
                buf = BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                return img_str
            
            # For RGB or segmentation images
            buf = BytesIO()
            plt.figure(figsize=(10, 8))
            plt.imshow(img)
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            return img_str
        
        # Encode all three images
        color_b64 = encode_image(rgb_image)
        depth_b64 = encode_image(depth_image)
        segmentation_b64 = encode_image(segmentation_mask)
        
        return {
            "status": "success",
            "message": "Camera images captured successfully",
            "images": {
                "color_image": color_b64,
                "depth_image": depth_b64,
                "segmentation_mask": segmentation_b64
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def move_and_rotate(location=None,angle=None):
    """
    Move robot to specified location and/or rotate to specified orientation.
    
    Args:
        location (list): [x, y, z] coordinates to move to. If None, robot will only rotate.
        orientation (list): [x, y, z, w] quaternion for rotation. If None, robot will maintain current orientation.
        
    Returns:
        dict: Result of the operation
    """
    try:
        # Get the world to access current robot state
        world = get_world_safely()
        if world is None:
            return {"status": "error", "message": "World is not initialized"}
            
        # Get current robot pose
        robot = None
        for obj in world.objects:
            if obj.name == "pr2":
                robot = obj
                break
                
        if not robot:
            return {"status": "error", "message": "Robot not found in world"}
            
        current_pose = robot.pose
        current_position = current_pose.position
        current_orientation = current_pose.orientation
        
        # Use provided values or defaults from current pose
        if location is None:
            location = current_position
        else:
            # Ensure location is a list of 3 floats
            if len(location) != 3:
                return {"status": "error", "message": "Location must be a list of 3 values [x, y, z]"}
            location = [float(val) for val in location]

        if angle is None:
            orientation = current_orientation
        else:
            orientation = euler_to_quaternion(0, 0, angle)
            
        if orientation is None:
            orientation = current_orientation
        else:
            # Ensure orientation is a list of 4 floats
            if len(orientation) != 4:
                return {"status": "error", "message": "Orientation must be a list of 4 values [x, y, z, w]"}
            orientation = [float(val) for val in orientation]
        
        # Create the target pose
        target_pose = Pose(location, orientation)
        
        with simulated_robot:
            robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()
            navigate_action = NavigateAction(target_locations=[target_pose]).resolve()
            
            print(f"API: Navigating to position {location} with orientation {orientation}")
            navigate_action.perform()
            print("API: Robot has moved and/or rotated to target pose.")
        
        return {
            "status": "success", 
            "message": f"Robot moved to coordinates {location} with orientation {orientation}",
            "position": location,
            "orientation": orientation
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def move_torso(position="high"):
    """
    Move the robot's torso to a specified position.
    
    Args:
        position (str): Position to move the torso to. Options: "low", "high".
                       Default is "high".
        
    Returns:
        dict: Result of the operation
    """
    try:
        # Map string position to TorsoState enum
        position_map = {
            "low": TorsoState.LOW,
            "high": TorsoState.HIGH
        }
        
        # Validate input
        position = position.lower() if isinstance(position, str) else "high"
        if position not in position_map:
            return {
                "status": "error", 
                "message": f"Invalid torso position: {position}. Valid options are: low, high."
            }
            
        torso_state = position_map[position]
        
        with simulated_robot:
            print(f"API: Moving torso to {position} position")
            move_torso_action = MoveTorsoAction([torso_state]).resolve()
            move_torso_action.perform()
            print(f"API: Torso moved to {position} position")
        
        return {
            "status": "success",
            "message": f"Torso moved to {position} position",
            "position": position
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def park_arms(arm=None):
    """
    Move the robot's arm(s) to the pre-defined parking position.
    
    Args:
        arm (str): Arm to park. Options: "left", "right", or None for both arms.
                  Default is None (both arms).
        
    Returns:
        dict: Result of the operation
    """
    try:
        # Map string arm to Arms enum
        arm_map = {
            "left": Arms.LEFT,
            "right": Arms.RIGHT,
            "both": [Arms.LEFT, Arms.RIGHT]
        }
        
        # Determine which arms to park
        arms_to_park = []
        if arm is None or arm.lower() == "both":
            arms_to_park = [Arms.LEFT, Arms.RIGHT]
        elif arm.lower() in arm_map:
            arms_to_park = [arm_map[arm.lower()]]
        else:
            return {
                "status": "error", 
                "message": f"Invalid arm: {arm}. Valid options are: left, right, both."
            }
        
        with simulated_robot:
            print(f"API: Parking arm(s): {arm if arm else 'both'}")
            
            # Park each arm
            for arm_to_park in arms_to_park:
                park_action = ParkArmsAction([arm_to_park]).resolve()
                park_action.perform()
                
            print(f"API: Arm(s) parked successfully")
        
        return {
            "status": "success",
            "message": f"Successfully parked arm(s): {arm if arm else 'both'}",
            "arm": arm if arm else "both"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
