#!/usr/bin/env python3
"""
Non-interactive versions of robot actions for API usage.
"""
import time
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

# Import from environment but avoid initialization side effects
def get_world_safely():
    from environment import get_world
    return get_world()

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
            target_location = [1.0, 1.0, 0.8]  # Default placement location
            
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
            
            # Create object designator
            object_desig = ObjectDesignatorDescription(names=[object_name])
            robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()
            
            print(f"API: Preparing to pick up {object_name}...")
            
            # Park arms and adjust torso for pickup
            ParkArmsAction([Arms.BOTH]).resolve().perform()
            MoveTorsoAction([TorsoState.HIGH]).resolve().perform()
            
            # Resolve pickup location
            print("API: Resolving pickup location...")
            pickup_pose = CostmapLocation(
                target=object_desig.resolve(),
                reachable_for=robot_desig
            ).resolve()
            
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
            place_stand = CostmapLocation(
                destination_pose,
                reachable_for=robot_desig,
                reachable_arm=pickup_arm
            ).resolve()
            
            if not hasattr(place_stand, 'pose'):
                return {"status": "error", "message": "Placement location resolution returned no valid pose."}
            
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
        if perception_area is None:
            perception_area = "table"  # Default area
            
        with simulated_robot:
            # Create a perception action
            perceive_action = PerceiveAction(area=perception_area).resolve()
            
            print(f"API: Robot perceiving {perception_area}...")
            results = perceive_action.perform()
            
            # Extract object information from results
            perceived_objects = []
            for obj in results:
                perceived_objects.append({
                    "name": obj.name if hasattr(obj, "name") else "unknown",
                    "type": str(type(obj))
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

def look_for_object(object_name=None):
    """
    Make the robot look for a specific object without interactive prompts.
    
    Args:
        object_name (str): Name of the object to look for
        
    Returns:
        dict: Result of the operation
    """
    try:
        if object_name is None:
            object_name = "cup1"  # Default object to look for
            
        with simulated_robot:
            # Create an object designator for the search
            obj_desig = ObjectDesignatorDescription(names=[object_name]).resolve()
            
            # Create a look-for action
            look_action = LookForAction(object=obj_desig).resolve()
            
            print(f"API: Looking for {object_name}...")
            result = look_action.perform()
            
            if result:
                position = result.pose.position if hasattr(result, 'pose') else "unknown"
                return {
                    "status": "success",
                    "message": f"Found {object_name}",
                    "object": object_name,
                    "position": str(position)
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"Could not find {object_name}"
                }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def unpack_arms():
    """
    Unpack the robot's arms without interactive prompts.
    
    Returns:
        dict: Result of the operation
    """
    try:
        with simulated_robot:
            # Create unpacking action
            unpack_action = UnpackAction().resolve()
            
            print("API: Unpacking arms...")
            unpack_action.perform()
            
        return {
            "status": "success",
            "message": "Robot arms unpacked successfully"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def detect_object(object_type=None, detection_area=None):
    """
    Detect objects of a specific type without interactive prompts.
    
    Args:
        object_type (str): Type of object to detect ('Milk', 'Cereal', 'Spoon', 'Bowl')
        detection_area (str): Not used in this implementation
        
    Returns:
        dict: Result of the operation with detected objects
    """
    try:
        if object_type is None:
            object_type = "Cereal"  # Default object type
            
        with simulated_robot:
            # Create detection action with the correct parameter names
            believe_desig = BelieveObject(types=[object_type])
            
            print(f"API: Detecting objects of type {object_type}...")
            detected = DetectAction(
                technique=DetectionTechnique.TYPES,
                object_designator_description=believe_desig
            ).resolve().perform()
            
            detected_objects = []
            if detected:
                for obj in detected:
                    detected_objects.append({
                        "name": obj.name if hasattr(obj, "name") else "unknown",
                        "type": str(type(obj))
                    })
                
        return {
            "status": "success",
            "message": f"Detected {len(detected_objects)} objects of type {object_type}",
            "detected_objects": detected_objects
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