#!/usr/bin/env python3
from pycram.worlds.bullet_world import BulletWorld
from pycram.world_concepts.world_object import Object
from pycram.datastructures.enums import WorldMode
from pycrap.ontologies import Robot, Kitchen, Apartment
from pycram.datastructures.pose import Pose
from pycram.datastructures.enums import ObjectType
from utils.color_wrapper import ColorWrapper

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
