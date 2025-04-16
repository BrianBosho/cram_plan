#!/usr/bin/env python3

import sys

# --- PyCRAM/BulletWorld imports ---
from pycram.worlds.bullet_world import BulletWorld
from pycram.world_concepts.world_object import Object
from pycram.process_module import simulated_robot
from pycram.designators.motion_designator import *
from pycram.designators.location_designator import *
from pycram.designators.action_designator import *
from pycram.designators.object_designator import *
from pycram.datastructures.enums import ObjectType, Arms, Grasp, WorldMode, TorsoState
from pycram.datastructures.pose import Pose
from pycrap.ontologies import Milk, Cereal, Robot, Kitchen
from pycrap.ontologies import Milk, Cereal, Spoon, Bowl
from utils.color_wrapper import ColorWrapper


import matplotlib.pyplot as plt
import numpy as np
from pycram.robot_description import RobotDescription
from pycram.datastructures.enums import Frame
from pycram.datastructures.pose import Pose


import pr2_camera_utils

def capture_camera_image(display=True, save_path=None, target_distance=2.0):
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
    global world
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

def spawn_objects(object_choice=None, coordinates=None, color=None, name=None):
    """
    Non-interactive version of spawn_objects that creates objects based on parameters.
    
    Args:
        object_choice (str): "cereal", "milk", "spoon", "bowl", or a custom name
        coordinates (list): [x, y, z] coordinates for object placement
        color (str): Color name (e.g., "red", "blue") or None for default
        name (str): Optional custom name for the object. If None, object_choice will be used
        
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
        
        # Handle object name and type
        if object_choice in object_types:
            obj_ontology, obj_file = object_types[object_choice]
            obj_name = name if name else object_choice  # Use custom name if provided
        else:
            # Custom/generic object
            obj_name = name if name else object_choice
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

def add_objects():
    
    objects_to_spawn = [
        {"object_choice": "spoon", "coordinates": [1.4, 1, 0.95], "color": "blue"},
        {"object_choice": "cereal", "coordinates": [1.4, 0.8, 0.95], "color": "red"},
        {"object_choice": "milk", "coordinates": [1.4, 0.6, 0.95], "color": "green"}
    ]
    
    for obj in objects_to_spawn:
        spawn_result = spawn_objects(
            obj['object_choice'], 
            obj['coordinates'], 
            obj['color']
        )
        print(f"Spawned {obj['color']} {obj['object_choice']}: {spawn_result}")
    
    print("Objects added successfully.")

# We keep a global reference to the world so all functions can access it.
world = None

def initialize_world():
    """
    Create the BulletWorld in GUI mode so we can visualize it.
    """
    global world
    if world is not None:
        print("World is already initialized!")
        return

    world = BulletWorld(WorldMode.GUI)
    print("World created (GUI mode).")


def create_objects():
    """
    Create objects in the BulletWorld (kitchen, robot, cereal, etc.).
    """
    global world
    if world is None:
        print("Cannot create objects because the world is not initialized.")
        return

    # Create objects in the simulation
    # kitchen = Object("kitchen", ObjectType.ENVIRONMENT, "kitchen.urdf")
    kitchen = Object("kitchen", Kitchen, "kitchen.urdf")
    print("Kitchen created.")

    # robot = Object("pr2", ObjectType.ROBOT, "pr2.urdf")
    robot = Object("pr2", Robot, "pr2.urdf")
    print("Robot created.")
    
    cereal = Object("cereal", Cereal, "breakfast_cereal.stl", pose=Pose([1.4, 1, 0.95]))

    # cereal = Object("cereal", ObjectType.BREAKFAST_CEREAL, "breakfast_cereal.stl", pose=Pose([1.4, 1, 0.95]))
    print("Cereal created.")

    # Optionally, store references or designators if needed for later
    # but for demonstration, let's just print that it was done.
    print("Objects spawned in the world.")


def run_robot_actions():
    """
    Demonstrate some simple PyCRAM actions: parking arms, moving torso,
    navigating, picking up an object, etc.
    """
    global world
    if world is None:
        print("Cannot run actions because the world is not initialized.")
        return

    # Create or re-create designators as needed
    cereal_desig = ObjectDesignatorDescription(names=["cereal"])
    kitchen_desig = ObjectDesignatorDescription(names=["kitchen"])
    robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()
    

    with simulated_robot:
        print("Entered simulated_robot context.")

        # Park the robot's arms
        park_action = ParkArmsAction([Arms.BOTH]).resolve()
        print("ParkArmsAction resolved:", park_action)
        park_action.perform()
        print("ParkArmsAction performed.")

        # Move the torso up
        move_torso = MoveTorsoAction([TorsoState.HIGH]).resolve()
        print("MoveTorsoAction resolved:", move_torso)
        move_torso.perform()
        print("MoveTorsoAction performed.")

        # Attempt to pick up cereal (just an example)
        pickup_pose = CostmapLocation(
            target=cereal_desig.resolve(), 
            reachable_for=robot_desig
        ).resolve()
        print("Pickup pose resolved:", pickup_pose.pose)
        
        if pickup_pose.reachable_arms:
            pickup_arm = pickup_pose.reachable_arms[0]
            print("Pickup arm selected:", pickup_arm)

            navigate_to_pickup = NavigateAction(target_locations=[pickup_pose.pose]).resolve()
            print("NavigateAction resolved (to pickup):", navigate_to_pickup)
            navigate_to_pickup.perform()
            print("NavigateAction performed (to pickup).")

            pickup_action = PickUpAction(
                object_designator_description=cereal_desig,
                arms=[pickup_arm],
                grasps=[Grasp.FRONT]
            ).resolve()
            print("PickUpAction resolved:", pickup_action)
            pickup_action.perform()
            print("PickUpAction performed.")

            park_after_pickup = ParkArmsAction([Arms.BOTH]).resolve()
            park_after_pickup.perform()
            print("Arms parked again.")
        else:
            print("No reachable arms found for picking up cereal!")

        print("Robot actions complete.")


def exit_world():
    """
    Close the BulletWorld, ending the simulation.
    """
    global world
    if world is None:
        print("World is not running or already exited.")
        return

    world.exit()
    print("World exited.")
    world = None


def ask_to_proceed(prompt):
    """
    Helper function to ask user if they want to proceed with a step.
    Returns True if 'y' or 'Y' is typed, otherwise False.
    """
    answer = input(f"{prompt} (y/n): ").strip().lower()
    return answer == 'y'

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

            

def demo_advanced_camera_functions():
    """
    Demonstrate the advanced camera functions with error handling.
    """
    global world
    if world is None:
        print("Cannot demonstrate advanced camera functions because the world is not initialized.")
        return
    
    # Position robot for good views
    with simulated_robot:
        try:
            # Park arms and raise torso
            park_action = ParkArmsAction([Arms.BOTH]).resolve()
            park_action.perform()
            move_torso = MoveTorsoAction([TorsoState.HIGH]).resolve()
            move_torso.perform()
            
            # Initialize the camera utils with your world instance
            pr2_camera_utils.initialize(world)
            print("Camera utilities initialized successfully.")
        except Exception as e:
            print(f"Error during robot positioning: {str(e)}")
            print("Continuing with camera demos anyway...")

        # Example 1: Visualize depth map
        try:
            print("\n--- Visualizing Depth Map ---")
            pr2_camera_utils.visualize_depth_map(colormap='plasma')
            print("Depth map visualization completed successfully.")
        except Exception as e:
            print(f"Error visualizing depth map: {str(e)}")
        
        # Example 2: Identify objects in view
        try:
            print("\n--- Identifying Objects in View ---")
            visible_objects = pr2_camera_utils.identify_objects_in_view()
            print(f"Object identification completed. Found {len(visible_objects) if visible_objects else 0} objects.")
        except Exception as e:
            print(f"Error identifying objects in view: {str(e)}")
        
        # Example 3: Check visibility of a specific object
        try:
            if world.get_object_by_name("cereal"):
                print("\n--- Checking Visibility of Cereal ---")
                pr2_camera_utils.check_object_visibility("cereal", threshold=0.6)
                print("Visibility check completed successfully.")
            else:
                print("\nSkipping cereal visibility check - cereal object not found.")
        except Exception as e:
            print(f"Error checking object visibility: {str(e)}")
        
        # Example 4: Find occluding objects
        try:
            if world.get_object_by_name("cereal"):
                print("\n--- Finding Objects Occluding Cereal ---")
                pr2_camera_utils.find_occluding_objects("cereal")
                print("Occlusion detection completed successfully.")
            else:
                print("\nSkipping occlusion detection - cereal object not found.")
        except Exception as e:
            print(f"Error finding occluding objects: {str(e)}")
        
        # Example 5: Estimate distances to objects
        try:
            print("\n--- Estimating Distances to Objects ---")
            pr2_camera_utils.estimate_distances_to_objects()
            print("Distance estimation completed successfully.")
        except Exception as e:
            print(f"Error estimating distances to objects: {str(e)}")
        
        # Example 6: Look at an object from different angles
        try:
            if world.get_object_by_name("cereal"):
                print("\n--- Looking at Cereal from Different Angles ---")
                pr2_camera_utils.look_at_object("cereal", distance=1.5, elevation_angle=30, azimuth_angle=45)
                print("Look-at-object function completed successfully.")
            else:
                print("\nSkipping look-at function - cereal object not found.")
        except Exception as e:
            print(f"Error looking at object from different angles: {str(e)}")
        
        # Example 7: Scan the environment (this is more computationally intensive)
        try:
            if ask_to_proceed("Perform a 360° environmental scan? (this may take some time)"):
                print("\n--- Scanning Environment ---")
                pr2_camera_utils.scan_environment(angles=4)  # Use fewer angles for quicker demonstration
                print("Environment scan completed successfully.")
        except Exception as e:
            print(f"Error during environment scan: {str(e)}")
        
        print("\nAdvanced camera functions demo completed.")

def demo_object_distances():
    """
    Demonstrate measuring distances between objects.
    """
    global world
    if world is None:
        print("Cannot demonstrate object distances because the world is not initialized.")
        return
    
    # Spawn additional objects if wanted
    try:
        if ask_to_proceed("Spawn additional objects for distance measurement?"):
            spawned_objects = pr2_camera_utils.spawn_multiple_objects()
            print(f"Spawned {len(spawned_objects)} additional objects.")
    except Exception as e:
        print(f"Error spawning additional objects: {str(e)}")
    
    # Get all distances
    try:
        print("\n--- Calculating All Pairwise Distances ---")
        all_distances = pr2_camera_utils.calculate_object_distances(exclude_types=['floor', 'wall', 'kitchen', 'ground'])
        pr2_camera_utils.display_object_distances(all_distances, top_n=10)
    except Exception as e:
        print(f"Error calculating all pairwise distances: {str(e)}")
    
    # Get distances from a specific object
    try:
        if world.get_object_by_name("cereal"):
            print("\n--- Distances from Cereal Box ---")
            cereal_distances = pr2_camera_utils.calculate_object_distances(
                source_object="cereal", 
                exclude_types=['floor', 'wall', 'kitchen', 'ground']
            )
            pr2_camera_utils.display_object_distances(cereal_distances)
        else:
            print("\nSkipping cereal distances - cereal object not found.")
    except Exception as e:
        print(f"Error calculating distances from cereal box: {str(e)}")
    
    # Visualize in 3D
    try:
        if ask_to_proceed("Display 3D visualization of object positions and distances?"):
            pr2_camera_utils.visualize_object_distances_3d(
                source_object="cereal" if world.get_object_by_name("cereal") else None,
                max_objects=8
            )
    except Exception as e:
        print(f"Error visualizing object distances in 3D: {str(e)}")
    
    print("\nObject distances demo completed.")

def main():
    print("\n--- Welcome to the Interactive PyCRAM Demo ---\n")

    # Step 1: Initialize World
    if ask_to_proceed("Initialize the simulation world?"):
        initialize_world()

    # Step 2: Create Objects
    if ask_to_proceed("Create objects in the simulation world?"):
        create_objects()

    # Step 3: Add Objects
    if ask_to_proceed("Add objects to the simulation world?"):        
        add_objects()

    # Step 4: Run Robot Actions
    if ask_to_proceed("Run robot actions?"):
        run_robot_actions()

    # Step 5: Test Camera
    if ask_to_proceed("Test robot camera?"):
        demo_camera()

    # Step 6: Test Advanced Camera Functions
    if ask_to_proceed("Test advanced camera functions?"):
        demo_advanced_camera_functions()

    # Step 7: Test Object Distances
    if ask_to_proceed("Test object distances?"):
        demo_object_distances()

    # Step 6: Exit World
    if ask_to_proceed("Exit the simulation world now?"):
        exit_world()
    else:
        print("Leaving the world running. Press Ctrl+C to exit manually, or call exit_world() in code.")


if __name__ == "__main__":
    main()

