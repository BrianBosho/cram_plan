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

def get_kitchen_info():
    """
    Get detailed information about the kitchen environment including dimensions of furniture
    and locations of objects.
    
    Returns:
        dict: Information about the kitchen environment including furniture dimensions and objects
    """
    try:
        # Get world reference
        world = get_world_safely()
        if world is None:
            return {
                "status": "error",
                "message": "World is not initialized."
            }
        
        kitchen_info = {
            "furniture": [],
            "objects": [],
            "dimensions": {}
        }
        
        # Check if kitchen model is available in the world
        kitchen_object = None
        if hasattr(world, "objects"):
            for obj in world.objects:
                if obj.name.lower() in ["kitchen", "kitchen_model"]:
                    kitchen_object = obj
                    break
        
        # If we found kitchen model, extract information
        if kitchen_object:
            # Try to get kitchen dimensions if the world has the capability
            if hasattr(kitchen_object, "dimensions"):
                kitchen_info["dimensions"]["kitchen"] = {
                    "width": kitchen_object.dimensions[0] if len(kitchen_object.dimensions) > 0 else "unknown",
                    "length": kitchen_object.dimensions[1] if len(kitchen_object.dimensions) > 1 else "unknown",
                    "height": kitchen_object.dimensions[2] if len(kitchen_object.dimensions) > 2 else "unknown"
                }
            elif hasattr(kitchen_object, "bbox"):
                # Some worlds use bounding boxes instead
                kitchen_info["dimensions"]["kitchen"] = {
                    "width": kitchen_object.bbox[0] if len(kitchen_object.bbox) > 0 else "unknown",
                    "length": kitchen_object.bbox[1] if len(kitchen_object.bbox) > 1 else "unknown",
                    "height": kitchen_object.bbox[2] if len(kitchen_object.bbox) > 2 else "unknown"
                }
        
        # Identify common kitchen furniture
        furniture_types = ["table", "counter", "cabinet", "sink", "stove", "refrigerator"]
        
        with simulated_robot:
            # Look around to get a better view of the environment
            try:
                # Use a look-around sequence to get better perception
                central_positions = [
                    [1.0, 0.0, 1.2],  # Center
                    [1.0, 1.0, 1.2],  # Right
                    [1.0, -1.0, 1.2],  # Left
                    [2.0, 0.0, 1.2]    # Forward
                ]
                
                for pos in central_positions:
                    # Look at different points in the kitchen
                    LookAtAction(targets=[Pose(pos)]).resolve().perform()
                    
                    # Try to perceive furniture
                    for furniture_type in furniture_types:
                        try:
                            # First try to detect by type
                            furniture_items = DetectAction(
                                technique=DetectionTechnique.TYPES,
                                object_designator_description=BelieveObject(types=[furniture_type])
                            ).resolve().perform()
                            
                            if furniture_items:
                                for furniture in furniture_items:
                                    furniture_info = {
                                        "name": furniture.name,
                                        "type": furniture_type,
                                        "pose": str(furniture.pose) if hasattr(furniture, "pose") else "unknown"
                                    }
                                    
                                    # Try to get dimensions
                                    if hasattr(furniture, "dimensions"):
                                        furniture_info["dimensions"] = {
                                            "width": furniture.dimensions[0] if len(furniture.dimensions) > 0 else "unknown",
                                            "length": furniture.dimensions[1] if len(furniture.dimensions) > 1 else "unknown",
                                            "height": furniture.dimensions[2] if len(furniture.dimensions) > 2 else "unknown"
                                        }
                                    elif hasattr(furniture, "bbox"):
                                        furniture_info["dimensions"] = {
                                            "width": furniture.bbox[0] if len(furniture.bbox) > 0 else "unknown",
                                            "length": furniture.bbox[1] if len(furniture.bbox) > 1 else "unknown",
                                            "height": furniture.bbox[2] if len(furniture.bbox) > 2 else "unknown"
                                        }
                                    
                                    kitchen_info["furniture"].append(furniture_info)
                        except Exception as furniture_error:
                            print(f"Error detecting furniture {furniture_type}: {furniture_error}")
                    
                    # Now try to detect by name as fallback
                    for furniture_type in furniture_types:
                        try:
                            furniture_items = DetectAction(
                                technique=DetectionTechnique.NAMES,
                                object_designator_description=BelieveObject(names=[furniture_type])
                            ).resolve().perform()
                            
                            if furniture_items:
                                for furniture in furniture_items:
                                    furniture_info = {
                                        "name": furniture.name,
                                        "type": furniture_type,
                                        "pose": str(furniture.pose) if hasattr(furniture, "pose") else "unknown"
                                    }
                                    
                                    # Try to get dimensions
                                    if hasattr(furniture, "dimensions"):
                                        furniture_info["dimensions"] = {
                                            "width": furniture.dimensions[0] if len(furniture.dimensions) > 0 else "unknown",
                                            "length": furniture.dimensions[1] if len(furniture.dimensions) > 1 else "unknown",
                                            "height": furniture.dimensions[2] if len(furniture.dimensions) > 2 else "unknown"
                                        }
                                    elif hasattr(furniture, "bbox"):
                                        furniture_info["dimensions"] = {
                                            "width": furniture.bbox[0] if len(furniture.bbox) > 0 else "unknown",
                                            "length": furniture.bbox[1] if len(furniture.bbox) > 1 else "unknown",
                                            "height": furniture.bbox[2] if len(furniture.bbox) > 2 else "unknown"
                                        }
                                    
                                    # Only add if not already in the list
                                    if not any(f["name"] == furniture.name for f in kitchen_info["furniture"]):
                                        kitchen_info["furniture"].append(furniture_info)
                        except Exception as furniture_error:
                            print(f"Error detecting furniture {furniture_type} by name: {furniture_error}")
            except Exception as perception_error:
                print(f"Error during furniture perception: {perception_error}")
            
            # Fallback to direct access if perception failed
            if not kitchen_info["furniture"] and hasattr(world, "objects"):
                for obj in world.objects:
                    if obj.name.lower() in furniture_types or any(furniture_type in obj.name.lower() for furniture_type in furniture_types):
                        furniture_info = {
                            "name": obj.name,
                            "type": str(type(obj)),
                            "pose": str(obj.pose) if hasattr(obj, "pose") else "unknown"
                        }
                        
                        # Try to get dimensions
                        if hasattr(obj, "dimensions"):
                            furniture_info["dimensions"] = {
                                "width": obj.dimensions[0] if len(obj.dimensions) > 0 else "unknown",
                                "length": obj.dimensions[1] if len(obj.dimensions) > 1 else "unknown",
                                "height": obj.dimensions[2] if len(obj.dimensions) > 2 else "unknown"
                            }
                        elif hasattr(obj, "bbox"):
                            furniture_info["dimensions"] = {
                                "width": obj.bbox[0] if len(obj.bbox) > 0 else "unknown",
                                "length": obj.bbox[1] if len(obj.bbox) > 1 else "unknown",
                                "height": obj.bbox[2] if len(obj.bbox) > 2 else "unknown"
                            }
                            
                        kitchen_info["furniture"].append(furniture_info)
            
            # Get objects on tables or counters (common kitchen items)
            # First try perception
            try:
                common_types = ["Milk", "Cereal", "Spoon", "Bowl", "Cup", "Plate", "Fork", "Knife"]
                for obj_type in common_types:
                    try:
                        detected = DetectAction(
                            technique=DetectionTechnique.TYPES,
                            object_designator_description=BelieveObject(types=[obj_type])
                        ).resolve().perform()
                        
                        if detected:
                            for obj in detected:
                                kitchen_info["objects"].append({
                                    "name": obj.name if hasattr(obj, "name") else "unknown",
                                    "type": obj_type,
                                    "pose": str(obj.pose) if hasattr(obj, "pose") else "unknown"
                                })
                    except Exception as detect_error:
                        print(f"Detection error for type {obj_type}: {detect_error}")
            except Exception as object_error:
                print(f"Error during object perception: {object_error}")
                
            # Fallback to direct world access for objects
            if not kitchen_info["objects"] and hasattr(world, "objects"):
                for obj in world.objects:
                    if (obj.name != "pr2" and 
                        obj.name.lower() not in ["kitchen", "apartment"] and
                        not any(f["name"] == obj.name for f in kitchen_info["furniture"])):
                        kitchen_info["objects"].append({
                            "name": obj.name,
                            "type": str(type(obj)),
                            "pose": str(obj.pose) if hasattr(obj, "pose") else "unknown"
                        })
        
        return {
            "status": "success",
            "message": "Successfully retrieved kitchen information",
            "kitchen_info": kitchen_info
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
    

def get_camera_info(camera_name=None):
    """
    Get information from the PR2 robot's camera with improved reliability.
    
    Args:
        camera_name (str): Name of the camera to use ('head_camera', 'kinect', 'wide_stereo')
        
    Returns:
        dict: Camera information including resolution, field of view, and other properties
    """
    try:
        # Default to head camera if not specified
        if camera_name is None:
            camera_name = "head_camera"
            
        # Standardized camera specifications for PR2
        camera_specs = {
            "head_camera": {
                "resolution": [640, 480],
                "field_of_view": 58.0,
                "frame_rate": 30.0,
                "frame_id": "head_camera_rgb_optical_frame",
                "description": "High-resolution head-mounted camera"
            },
            "kinect": {
                "resolution": [640, 480],
                "field_of_view": 57.0,
                "frame_rate": 30.0,
                "frame_id": "kinect_rgb_optical_frame",
                "depth_sensing": True,
                "description": "Depth-sensing camera with RGB capabilities"
            },
            "wide_stereo": {
                "resolution": [640, 480],
                "field_of_view": 90.0,
                "frame_rate": 15.0,
                "frame_id": "wide_stereo_optical_frame",
                "stereo": True,
                "description": "Wide-angle stereo camera pair"
            }
        }
        
        # Validate camera name
        if camera_name not in camera_specs:
            return {
                "status": "error",
                "message": f"Unknown camera: {camera_name}. Choose from {list(camera_specs.keys())}"
            }
        
        with simulated_robot:
            # Initialize camera information with standard specs
            camera_info = {
                "name": camera_name,
                "status": "simulated",
                "properties": camera_specs[camera_name]
            }
            
            # Attempt to get current view information
            try:
                # Use LookAtAction to simulate camera orientation
                # Choose a default look position based on camera type
                look_positions = {
                    "head_camera": [1.0, 0.0, 1.2],
                    "kinect": [1.5, 0.0, 1.0],
                    "wide_stereo": [2.0, 0.0, 1.2]
                }
                
                look_pose = Pose(look_positions.get(camera_name, [1.0, 0.0, 1.2]))
                
                # Look at the specified position
                LookAtAction(targets=[look_pose]).resolve().perform()
                
                # Try to detect objects in view
                try:
                    detected_objects = DetectAction(
                        technique=DetectionTechnique.TYPES,
                        object_designator_description=BelieveObject()
                    ).resolve().perform()
                    
                    # Process detected objects
                    visible_objects = []
                    if detected_objects:
                        for obj in detected_objects:
                            if obj.name != "pr2":
                                visible_objects.append({
                                    "name": obj.name,
                                    "type": str(type(obj).__name__),
                                    "pose": str(obj.pose) if hasattr(obj, "pose") else "unknown"
                                })
                    
                    camera_info["current_view"] = {
                        "look_position": str(look_pose),
                        "visible_objects": visible_objects
                    }
                except Exception as detect_error:
                    camera_info["current_view"] = {
                        "look_position": str(look_pose),
                        "visible_objects": [],
                        "detection_error": str(detect_error)
                    }
                
            except Exception as look_error:
                camera_info["current_view"] = {
                    "error": f"Could not simulate camera view: {str(look_error)}"
                }
            
            return {
                "status": "success",
                "message": f"Camera information for {camera_name}",
                "camera_info": camera_info
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def get_robot_camera_images(target_distance=None):
    """
    Get images from the robot's camera.
    
    Args:
        target_distance (float): How far in front of the camera to look (in meters)
        
    Returns:
        dict: Result containing encoded camera images
    """
    try:
        # Import the camera_utils function
        from camera_utils import get_camera_images
        import cv2
        import base64
        import numpy as np
        
        # Get the world reference
        world = get_world_safely()
        if not world:
            return {"status": "error", "message": "World is not initialized."}
            
        # Find the robot in the world
        robot = None
        for obj in world.objects:
            if obj.name == "pr2":
                robot = obj
                break
                
        if not robot:
            return {"status": "error", "message": "Robot (PR2) not found in the world."}
        
        # Convert target_distance to float if provided
        if target_distance is not None:
            try:
                target_distance = float(target_distance)
            except ValueError:
                return {"status": "error", "message": "Invalid target_distance value. Must be a number."}
        else:
            target_distance = 2.0  # Default distance
            
        # Get camera images
        images = get_camera_images(world, robot, target_distance)
        
        # Encode images for web display
        encoded_images = {}
        
        # Process color image (convert to PNG base64)
        if images["color_image"] is not None:
            color_img = images["color_image"]
            # Convert the color image to BGR format for OpenCV
            if len(color_img.shape) == 3 and color_img.shape[2] == 3:
                color_img = cv2.cvtColor(color_img, cv2.COLOR_RGB2BGR)
            # Encode to PNG
            _, buffer = cv2.imencode('.png', color_img)
            encoded_images["color_image"] = base64.b64encode(buffer).decode('utf-8')
        else:
            encoded_images["color_image"] = None
            
        # Process depth image (normalize and convert to heatmap)
        if images["depth_image"] is not None:
            depth_img = images["depth_image"]
            # Normalize depth map to 0-255 range for visualization
            if np.max(depth_img) > 0:
                normalized_depth = (depth_img / np.max(depth_img) * 255).astype(np.uint8)
            else:
                normalized_depth = np.zeros_like(depth_img, dtype=np.uint8)
            # Apply colormap for better visualization
            depth_colormap = cv2.applyColorMap(normalized_depth, cv2.COLORMAP_JET)
            # Encode to PNG
            _, buffer = cv2.imencode('.png', depth_colormap)
            encoded_images["depth_image"] = base64.b64encode(buffer).decode('utf-8')
        else:
            encoded_images["depth_image"] = None
            
        # Process segmentation mask (convert to colored visualization)
        if images["segmentation_mask"] is not None:
            seg_mask = images["segmentation_mask"]
            # If seg_mask is not uint8, convert it
            if seg_mask.dtype != np.uint8:
                # If it's an integer mask with different values per object
                if np.max(seg_mask) > 0:
                    # Normalize to 0-255 and apply colormap
                    normalized_seg = (seg_mask % 255).astype(np.uint8)
                    seg_colormap = cv2.applyColorMap(normalized_seg, cv2.COLORMAP_RAINBOW)
                else:
                    seg_colormap = np.zeros((*seg_mask.shape, 3), dtype=np.uint8)
            else:
                # If it's already a color image
                seg_colormap = seg_mask
                
            # Encode to PNG
            _, buffer = cv2.imencode('.png', seg_colormap)
            encoded_images["segmentation_mask"] = base64.b64encode(buffer).decode('utf-8')
        else:
            encoded_images["segmentation_mask"] = None
            
        return {
            "status": "success",
            "message": "Camera images retrieved successfully",
            "images": encoded_images
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

def get_kitchen_table_height():
    """
    Comprehensive method to find kitchen table height.
    """
    try:
        # Try direct object inspection first
        world = get_world()
        if world:
            for obj in world.objects:
                if 'table' in obj.name.lower():
                    return obj.pose.position.z

        # Try perception-based detection
        from pycram.designators.action_designator import DetectAction
        from pycram.designators.object_designator import BelieveObject
        from pycram.datastructures.enums import DetectionTechnique

        with simulated_robot:
            table_objects = DetectAction(
                technique=DetectionTechnique.TYPES,
                object_designator_description=BelieveObject(types=['Table'])
            ).resolve().perform()

            if table_objects:
                return table_objects[0].pose.position.z

        # Fall back to predefined height
        return 0.95  # Standard kitchen table height in meters
    
    except Exception as e:
        print(f"Error detecting table height: {e}")
        return None

# Add this to the list of available commands in get_commands()
def get_commands():
    commands = {
        # ... existing commands ...
        "get_table_height": {
            "description": "Get the height of the kitchen table",
            "parameters": {}
        }
    }
    return commands

# Add this to the execute_command function
def execute_command(command, params=None):
    if command == "get_table_height":
        height = get_kitchen_table_height()
        return {
            "status": "success" if height is not None else "error",
            "message": f"Kitchen table height: {height} meters" if height is not None else "Could not detect table height",
            "height": height
        }
    
    # ... existing command handling ... 