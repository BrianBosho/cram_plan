#!/usr/bin/env python3
from pycram.worlds.bullet_world import BulletWorld
from pycram.world_concepts.world_object import Object
from pycram.datastructures.enums import WorldMode
from pycrap.ontologies import Robot, Kitchen, Apartment
from pycram.datastructures.pose import Pose
from pycram.datastructures.enums import ObjectType
from utils.color_wrapper import ColorWrapper

# Try to import environment color utilities, but don't fail if not available
try:
    from utils.environment_colors import apply_kitchen_colors, apply_robot_colors
    HAS_COLOR_UTILS = True
except ImportError:
    HAS_COLOR_UTILS = False

# Global reference to the world - accessible by importing this module
world = None

def create_environment(spawn_default_objects=True):
    """
    Create the simulation environment.
    The user chooses an environment type (Kitchen, Apartment, Office).
    This function spawns both the environment object and the robot.
    
    Args:
        spawn_default_objects (bool): Whether to spawn default objects in the environment
    
    Returns:
        tuple: The environment object and the world
    """
    try:
        print("Select environment to create:")
        print("1) Kitchen")
        print("2) Apartment")
        
        choice = input("Enter the number of your choice: ").strip()
        
        environment_options = {
            "1": ("kitchen", Kitchen, "kitchen.urdf"),
            "2": ("apartment", Apartment, "apartment.urdf")
        }
        
        if choice not in environment_options:
            print("Invalid choice, defaulting to kitchen.")
            choice = "1"
            
        env_name, env_ontology, env_file = environment_options[choice]
        
        global world
        world = BulletWorld(WorldMode.GUI)
        print(f"World created in GUI mode with environment: {env_name}")
        
        env_obj = Object(env_name, env_ontology, env_file)
        print(f"Environment object '{env_name}' created.")
        
        # Spawn the robot
        robot_obj = Object("pr2", Robot, "pr2.urdf")
        print("Robot spawned as 'pr2'.")

        # Try to apply colors, but continue even if it fails
        if HAS_COLOR_UTILS and env_name == 'kitchen':
            try:
                print("Applying colors to kitchen environment...")
                # Enable debug mode to see what's happening with kitchen coloring
                apply_kitchen_colors(env_obj, debug=True)
                print("Applying colors to robot...")
                apply_robot_colors(robot_obj)
            except Exception as color_error:
                print(f"Warning: Could not apply colors: {str(color_error)}")
                print("Continuing without custom colors...")

        # Optional: Spawn default objects in the kitchen
        if spawn_default_objects and env_name == 'kitchen':
            default_objects = [
                {"name": "spoon", "ontology": ObjectType.GENERIC, "file": "spoon.stl", "pose": [1.4, 1, 0.95], "color": "blue"},
                {"name": "cereal", "ontology": ObjectType.GENERIC, "file": "breakfast_cereal.stl", "pose": [1.4, 0.8, 0.95], "color": "red"},
                {"name": "milk", "ontology": ObjectType.GENERIC, "file": "milk.stl", "pose": [1.4, 0.6, 0.95], "color": "green"}
            ]
            
            for obj_data in default_objects:
                color_wrapper = ColorWrapper(obj_data['color']) if obj_data['color'] else None
                Object(
                    obj_data['name'], 
                    obj_data['ontology'], 
                    obj_data['file'], 
                    pose=Pose(obj_data['pose']), 
                    color=color_wrapper
                )
                print(f"Spawned {obj_data['color']} {obj_data['name']}")
        
        return env_obj, world  # Return both the environment object and the world
    except Exception as e:
        print("CRAM error during environment creation:", e)
        return None, None

def get_world():
    """
    Get the current world instance.
    
    Returns:
        BulletWorld: The current world instance or None if not initialized
    """
    global world
    return world

def get_environment_name(env_obj):
    """
    Get the name of the environment.
    
    Args:
        env_obj (Object): The environment object
    
    Returns:
        str: The name of the environment
    """
    if env_obj is None:
        return None
    
    # Assuming the environment name is the first argument used in Object creation
    return env_obj.name if hasattr(env_obj, 'name') else None

def reset_world():
    """
    Reset the world to its initial state.
    
    This function:
    1. Clears all objects from the world
    2. Resets the robot to its default position
    3. Recreates the basic environment (kitchen, tables, etc.)
    
    Returns:
        dict: Result of the reset operation
    """
    try:
        from pycram.bullet_world import BulletWorld
        from pycram.process_module import with_simulated_robot, simulated_robot
        import time
        
        # Get the current world
        world = get_world()
        if not world:
            return {"status": "error", "message": "No world to reset. You may need to initialize it first."}
        
        # Get the robot reference before clearing
        robot = None
        for obj in world.objects:
            if hasattr(obj, 'name') and obj.name == "pr2":
                robot = obj
                break
        
        print("Clearing all objects from the world...")
        
        # Store kitchen for later (if present)
        kitchen = None
        for obj in world.objects:
            if hasattr(obj, 'name') and obj.name == "kitchen":
                kitchen = obj
                break
        
        # Clear all objects except robot and room
        objects_to_keep = ["pr2", "room_link"]
        for obj in list(world.objects):  # Create a copy of the list to avoid modification during iteration
            if not hasattr(obj, 'name') or obj.name not in objects_to_keep:
                try:
                    world.remove_object(obj)
                except Exception as e:
                    print(f"Could not remove object {obj}: {str(e)}")
        
        # Reset robot position and orientation
        if robot:
            with simulated_robot:
                from pycram.designators.motion_designator import NavigateAction
                from pycram.designators.motion_designator import ParkArmsAction, MoveTorsoAction
                from pycram.designators.motion_designator_enums import Arms, TorsoState
                from pycram.enums import GazeModes
                from pycram.pose import Pose
                
                # Move to default position
                print("Resetting robot position...")
                # Default starting position
                default_pose = Pose([0, 0, 0])
                NavigateAction(target_locations=[default_pose]).resolve().perform()
                
                # Reset torso and arms
                print("Resetting robot configuration...")
                MoveTorsoAction([TorsoState.LOW]).resolve().perform()
                ParkArmsAction([Arms.BOTH]).resolve().perform()
                
                # Reset gaze
                robot.gaze_mode = GazeModes.HEAD_LOOKING_AT
        
        # Recreate kitchen environment
        print("Recreating kitchen environment...")
        initialize_kitchen(world)
        
        # A short pause to allow physics to stabilize
        time.sleep(1.0)
        
        return {
            "status": "success",
            "message": "World reset successfully to initial state"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Error resetting world: {str(e)}"}