#!/usr/bin/env python3
"""
Reset functionality for the robot and simulation environment.
This module provides functions to reset the robot state and the world environment.
"""

import time
import traceback
import numpy as np
import random
from pycram.process_module import simulated_robot
from pycram.designators.motion_designator import *
from pycram.designators.location_designator import *
from pycram.designators.action_designator import *
from pycram.designators.object_designator import *
from pycram.datastructures.enums import Arms, Grasp, TorsoState, DetectionTechnique
from pycram.datastructures.pose import Pose
from pycram.world_concepts.world_object import Object
from pycram.datastructures.enums import ObjectType
from pycrap.ontologies import Milk, Cereal, Spoon, Bowl, Robot, Kitchen, Apartment
from utils.color_wrapper import ColorWrapper

# Try to import environment color utilities, but don't fail if not available
try:
    from utils.environment_colors import apply_kitchen_colors, apply_robot_colors
    HAS_COLOR_UTILS = True
except ImportError:
    HAS_COLOR_UTILS = False

def reset_robot_state():
    """
    Reset the robot to a safe state by parking arms, adjusting torso, and releasing any held objects.
    
    This function is useful when the robot gets stuck or is in an unknown state.
    
    Returns:
        dict: Result of the operation
    """
    try:
        with simulated_robot:
            print("API: Resetting robot state...")
            
            # First try to force release any held objects
            try:
                release_result = force_release_object()
                if release_result["status"] == "error":
                    print(f"Warning: Object release failed: {release_result['message']}")
            except Exception as e:
                print(f"Warning: Error during object release: {str(e)}")
            
            # Make sure the torso is in a good position
            try:
                MoveTorsoAction([TorsoState.HIGH]).resolve().perform()
                print("API: Torso moved to high position")
            except Exception as e:
                print(f"Warning: Failed to move torso: {str(e)}")
            
            # Park the arms
            try:
                ParkArmsAction([Arms.BOTH]).resolve().perform()
                print("API: Arms parked")
            except Exception as e:
                print(f"Warning: Failed to park arms: {str(e)}")
            
            # Move robot to a neutral position if possible
            try:
                neutral_position = [0, 0, 0]  # Center of the world
                navigate_action = NavigateAction(
                    target_locations=[Pose(neutral_position)]
                ).resolve()
                navigate_action.perform()
                print("API: Robot moved to neutral position")
            except Exception as e:
                print(f"Warning: Failed to move robot: {str(e)}")
            
            return {
                "status": "success",
                "message": "Robot state has been reset"
            }
            
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": f"Error during robot reset: {str(e)}"}


def force_release_object(arm=None):
    """
    Force the robot to release any object it's currently holding.
    
    This function performs several emergency release actions to ensure
    the robot lets go of anything it might be gripping.
    
    Args:
        arm (str): Which arm to release. Options: "left", "right", or None for both.
                  Default is None (both arms).
        
    Returns:
        dict: Result of the operation
    """
    try:
        # Map string arm to Arms enum
        arm_enum = None
        if arm == "left":
            arms_to_release = [Arms.LEFT]
        elif arm == "right":
            arms_to_release = [Arms.RIGHT]
        else:
            # Default to both arms
            arms_to_release = [Arms.LEFT, Arms.RIGHT]
            
        with simulated_robot:
            print(f"API: Performing emergency release for {arm if arm else 'both'} arm(s)")
            
            success = False
            errors = []
            
            # Try several methods to ensure release
            for arm_to_release in arms_to_release:
                # Method 1: Try using PlaceAction with a downward pose
                try:
                    print(f"API: Attempting direct place action on {arm_to_release}")
                    # Create a simple release pose directly below the current gripper position
                    drop_pose = Pose([0, 0, -0.3], [0, 0, 0, 1], frame='gripper')
                    
                    # For this emergency release, we don't care if it fails due to no object being held
                    try:
                        PlaceAction(
                            arms=[arm_to_release],
                            target_locations=[drop_pose]
                        ).resolve().perform()
                        success = True
                        print(f"API: Successfully released object from {arm_to_release} using place action")
                    except Exception as e:
                        errors.append(f"Place action failed: {str(e)}")
                except Exception as e:
                    errors.append(f"Method 1 failed for {arm_to_release}: {str(e)}")
                
                # Method 2: Update transforms and try again with ParkArms
                try:
                    print(f"API: Attempting to park {arm_to_release} arm")
                    ParkArmsAction([arm_to_release]).resolve().perform()
                    success = True
                    print(f"API: Successfully parked {arm_to_release} arm")
                except Exception as e:
                    errors.append(f"Method 2 failed for {arm_to_release}: {str(e)}")
            
            # Always move torso to a safe position
            try:
                MoveTorsoAction([TorsoState.HIGH]).resolve().perform()
                print("API: Torso moved to high position")
            except Exception as e:
                errors.append(f"Failed to move torso: {str(e)}")
            
            if success:
                return {
                    "status": "success",
                    "message": f"Successfully released objects from {arm if arm else 'both'} arm(s)"
                }
            else:
                return {
                    "status": "error",
                    "message": f"All release methods failed: {'; '.join(errors)}"
                }
                
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": f"Error during force release: {str(e)}"}


def reset_world(spawn_default_objects=True):
    """
    Reset the world to its initial state, removing all objects except the 
    robot and environment, and optionally spawn default objects.
    
    Args:
        spawn_default_objects (bool): Whether to spawn the default objects after reset
    
    Returns:
        dict: Result of the operation
    """
    try:
        from environment import get_world
        
        # Get the current world
        world = get_world()
        if not world:
            return {"status": "error", "message": "No world to reset. You may need to initialize it first."}
        
        print("API: Resetting world state...")
        
        # First, reset the robot to a safe state
        reset_robot_result = reset_robot_state()
        if reset_robot_result["status"] == "error":
            print(f"Warning: Robot reset had issues: {reset_robot_result['message']}")
        
        # Objects that should never be removed (core environment)
        core_objects = ["pr2", "kitchen", "apartment"]
        
        # Delete all objects except the core ones
        print("API: Removing non-core objects from world...")
        objects_removed = 0
        
        for obj in list(world.objects):  # Copy list to avoid modification during iteration
            if hasattr(obj, 'name') and obj.name not in core_objects:
                try:
                    world.remove_object(obj)
                    objects_removed += 1
                    print(f"API: Removed object '{obj.name}'")
                except Exception as e:
                    print(f"API: Warning: Could not remove object '{obj.name}': {str(e)}")
        
        # Optionally spawn default objects
        if spawn_default_objects:
            print("API: Spawning default objects...")
            default_objects = [
                {"name": "spoon", "ontology": Spoon, "file": "spoon.stl", "pose": [1.4, 1, 0.95], "color": "blue"},
                {"name": "cereal", "ontology": Cereal, "file": "breakfast_cereal.stl", "pose": [1.4, 0.8, 0.95], "color": "red"},
                {"name": "milk", "ontology": Milk, "file": "milk.stl", "pose": [1.4, 0.6, 0.95], "color": "green"}
            ]
            
            objects_created = 0
            for obj_data in default_objects:
                try:
                    color_wrapper = ColorWrapper(obj_data['color']) if obj_data['color'] else None
                    Object(
                        obj_data['name'], 
                        obj_data['ontology'], 
                        obj_data['file'], 
                        pose=Pose(obj_data['pose']), 
                        color=color_wrapper
                    )
                    objects_created += 1
                    print(f"API: Spawned {obj_data['color']} {obj_data['name']}")
                except Exception as e:
                    print(f"API: Warning: Could not create object '{obj_data['name']}': {str(e)}")
        
        # A short pause to allow physics to stabilize
        time.sleep(0.5)
        
        return {
            "status": "success",
            "message": f"World reset successfully. Removed {objects_removed} objects and created {objects_created if spawn_default_objects else 0} default objects."
        }
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": f"Error resetting world: {str(e)}"}


def reset_all(spawn_default_objects=True):
    """
    Reset both the robot and the world to their initial states.
    This is a combined function that performs a complete reset of the simulation.
    
    Args:
        spawn_default_objects (bool): Whether to spawn default objects after reset
        
    Returns:
        dict: Result of the operation
    """
    try:
        print("API: Performing complete simulation reset...")
        
        # Step 1: Reset robot state
        robot_result = reset_robot_state()
        if robot_result["status"] == "error":
            print(f"Warning: Robot reset issues: {robot_result['message']}")
        
        # Step 2: Reset world
        world_result = reset_world(spawn_default_objects)
        if world_result["status"] == "error":
            print(f"Warning: World reset issues: {world_result['message']}")
            return world_result  # Return the error if world reset failed
        
        return {
            "status": "success",
            "message": "Complete simulation reset successful",
            "robot_reset": robot_result["status"] == "success",
            "world_reset": world_result["status"] == "success",
            "details": {
                "robot": robot_result["message"],
                "world": world_result["message"]
            }
        }
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": f"Error during complete reset: {str(e)}"}