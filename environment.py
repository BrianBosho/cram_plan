#!/usr/bin/env python3
from pycram.worlds.bullet_world import BulletWorld
from pycram.world_concepts.world_object import Object
from pycram.datastructures.enums import WorldMode
from pycrap.ontologies import Robot, Kitchen, Apartment

# Global reference to the world - accessible by importing this module
world = None

def create_environment():
    """
    Create the simulation environment.
    The user chooses an environment type (Kitchen, Apartment, Office).
    This function spawns both the environment object and the robot.
    
    Returns:
        Object: The environment object
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
