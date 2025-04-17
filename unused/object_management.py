#!/usr/bin/env python3
from pycram.world_concepts.world_object import Object
from pycram.datastructures.pose import Pose
from pycram.datastructures.enums import ObjectType
from pycrap.ontologies import Milk, Cereal, Spoon, Bowl

from utils.color_wrapper import ColorWrapper

def spawn_objects():
    """
    Interactively spawn objects in the environment.
    
    Returns:
        list: List of created Object instances
    """
    try:
        objects = []
        print("\n--- Add Objects ---")
        
        object_types = {
            "1": ("cereal", Cereal, "breakfast_cereal.stl"),
            "2": ("milk", Milk, "milk.stl"),
            "3": ("spoon", Spoon, "spoon.stl"),
            "4": ("bowl", Bowl, "bowl.stl")
        }
        
        while True:
            add_more = input("Do you want to add an object? (y/n): ").strip().lower()
            if add_more != "y":
                break
                
            print("Select object type:")
            print("1) Cereal")
            print("2) Milk")
            print("3) Spoon")
            print("4) Bowl")
            print("5) Other (custom)")
            
            obj_choice = input("Enter your choice: ").strip()
            
            if obj_choice in object_types:
                obj_name, obj_ontology, obj_file = object_types[obj_choice]
            elif obj_choice == "5":
                obj_name = input("Enter object name: ").strip()
                obj_ontology = ObjectType.GENERIC
                obj_file = input("Enter model file for the object: ").strip()
            else:
                print("Invalid choice. Skipping object creation.")
                continue
            
            # Get pose information
            pose_input = input("Enter spawn pose as x,y,z (e.g. 1.4,1.0,0.95): ").strip()
            try:
                pose_vals = [float(val.strip()) for val in pose_input.split(",")]
                if len(pose_vals) != 3:
                    print("Invalid pose input. Skipping object.")
                    continue
            except Exception as e:
                print("CRAM error parsing pose:", e)
                continue
            
            # Get color information
            color_input = input("Enter object color (e.g. red, blue) or press Enter for default: ").strip()
            color = ColorWrapper(color_input) if color_input else None

            try:
                obj = Object(obj_name, obj_ontology, obj_file, pose=Pose(pose_vals), color=color)
                print(f"Object '{obj_name}' created at pose {pose_vals} with color {color_input if color else 'default'}.")
                objects.append(obj)
            except FileNotFoundError as e:
                print("CRAM error spawning object:", e)
                
        return objects
    except Exception as e:
        print("CRAM error in spawn_objects:", e)
        return []
