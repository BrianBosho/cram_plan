#!/usr/bin/env python3
import time
from pycram.process_module import simulated_robot
from pycram.designators.motion_designator import *
from pycram.designators.location_designator import *
from pycram.designators.action_designator import *
from pycram.designators.object_designator import *
from pycram.datastructures.enums import Arms, Grasp, TorsoState, DetectionTechnique
from pycram.datastructures.pose import Pose

# Import the world reference from environment.py
#from environment import world
from environment import get_world


def move_robot():
    """
    Prompt for destination coordinates and move the robot.
    
    Returns:
        Pose or None: The destination pose if movement was successful
    """
    try:
        print("\n--- Move the Robot ---")
        dest_input = input("Enter destination coordinates as x,y,z: ").strip()
        try:
            dest_vals = [float(val.strip()) for val in dest_input.split(",")]
            if len(dest_vals) != 3:
                print("Invalid coordinates. Aborting robot movement.")
                return None
        except Exception as e:
            print("CRAM error parsing coordinates:", e)
            return None

        with simulated_robot:
            robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()
            nav_pose = Pose(dest_vals)
            navigate_action = NavigateAction(target_locations=[nav_pose]).resolve()
            print("Navigating to", nav_pose)
            navigate_action.perform()
            print("Robot has moved to destination.")
        return nav_pose
    except Exception as e:
        print("CRAM error in move_robot:", e)
        return None

def pickup_and_place():
    """
    Pickup an object and place it at a destination.
    """
    try:
        print("\n--- Pickup and Place ---")
        obj_to_pick = input("Enter the name of the object to pick up: ").strip()
        place_input = input("Enter DESTINATION placement coordinates as x,y,z: ").strip()
        try:
            place_vals = [float(val.strip()) for val in place_input.split(",")]
            if len(place_vals) != 3:
                print("Invalid placement coordinates. Aborting pickup/place.")
                return
        except Exception as e:
            print("CRAM error parsing placement coordinates:", e)
            return

        with simulated_robot:
            object_desig = ObjectDesignatorDescription(names=[obj_to_pick])
            robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()
            
            print("Parking arms and moving torso for pickup...")
            ParkArmsAction([Arms.BOTH]).resolve().perform()
            MoveTorsoAction([TorsoState.HIGH]).resolve().perform()

            print("Resolving pickup location...")
            pickup_pose = CostmapLocation(
                target=object_desig.resolve(),
                reachable_for=robot_desig
            ).resolve()
            if not pickup_pose.reachable_arms:
                print("CRAM error: No reachable arms for object", obj_to_pick)
                return
            pickup_arm = pickup_pose.reachable_arms[0]

            print("Navigating to pickup location at", pickup_pose.pose)
            NavigateAction(target_locations=[pickup_pose.pose]).resolve().perform()
            print("Executing pickup action...")
            PickUpAction(
                object_designator_description=object_desig,
                arms=[pickup_arm],
                grasps=[Grasp.FRONT]
            ).resolve().perform()
            ParkArmsAction([Arms.BOTH]).resolve().perform()
            print("Pickup action performed.")
            
            time.sleep(0.5)  # Allow simulation state to update

            destination_pose = Pose(place_vals)
            print("Destination pose for placement:", destination_pose)
            try:
                print("Resolving placement location...")
                place_stand = CostmapLocation(
                    destination_pose,
                    reachable_for=robot_desig,
                    reachable_arm=pickup_arm
                ).resolve()
                if not hasattr(place_stand, 'pose'):
                    print("CRAM error: Placement location resolution returned no valid pose.")
                    return
                print("Resolved placement stand pose:", place_stand.pose)
            except Exception as e:
                print("CRAM error resolving placement location:", e)
                print("The provided placement coordinates might be unreachable. Please try different coordinates.")
                return

            try:
                print("Navigating to placement location...")
                NavigateAction(target_locations=[place_stand.pose]).resolve().perform()
            except Exception as e:
                print("CRAM error during navigation to placement location:", e)
                return

            try:
                print("Executing place action...")
                PlaceAction(
                    object_designator_description=object_desig,
                    target_locations=[destination_pose],
                    arms=[pickup_arm]
                ).resolve().perform()
                ParkArmsAction([Arms.BOTH]).resolve().perform()
                print("Place action performed.")
            except Exception as e:
                print("CRAM error during place action:", e)
                return
    except Exception as e:
        print("CRAM error in pickup_and_place:", e)

def robot_perceive():
    """
    Report the objects visible to the robot.
    """
    try:
        print("\n--- Robot Perception ---")
        if world:
            visible_objects = world.get_visible_objects() if hasattr(world, "get_visible_objects") else []
            if visible_objects:
                print("The robot sees the following objects:")
                for obj in visible_objects:
                    print(f" - {obj.name}")
            else:
                print("No objects detected by the robot.")
                all_objects = world.objects if hasattr(world, "objects") else []
                if all_objects:
                    print("All objects in the world:")
                    for obj in all_objects:
                        print(f" - {obj.name}")
                else:
                    print("World has no objects.")
        else:
            print("World is not initialized.")
    except Exception as e:
        print("CRAM error in robot_perceive:", e)

def look_for_object():
    """
    Navigate to a computed viewpoint near an object and then perform perception.
    """
    try:
        print("\n--- Look For Object ---")
        obj_name = input("Enter the name of the object to look for: ").strip()
        object_desig = ObjectDesignatorDescription(names=[obj_name])
        try:
            obj_pose = object_desig.resolve().pose
            x = obj_pose.position.x
            y = obj_pose.position.y
            z = obj_pose.position.z
            print(f"Object '{obj_name}' resolved at pose: x={x}, y={y}, z={z}")
        except Exception as e:
            print("CRAM error resolving object pose:", e)
            return
        
        # Compute a viewpoint by offsetting the x-coordinate by 0.5m.
        offset = 0.5
        viewpoint = Pose([x - offset, y, z])
        print(f"Computed viewpoint for perception: {viewpoint}")
        
        with simulated_robot:
            robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()
            navigate_action = NavigateAction(target_locations=[viewpoint]).resolve()
            print("Navigating to viewpoint for perception...")
            navigate_action.perform()
            print("Robot reached viewpoint.")
        
        robot_perceive()
    except Exception as e:
        print("CRAM error in look_for_object:", e)

def unpack_arms():
    """
    Unpack (open) the robot's arms.
    """
    try:
        print("\n--- Unpack Arms ---")
        with simulated_robot:
            # Add proper arm unpacking code based on PyCRAM API
            # This is a placeholder for now
            print("Unpacking arms...")
            time.sleep(0.5)
            print("Arms are now unpacked.")
    except Exception as e:
        print("CRAM error in unpack_arms:", e)

def detect_object():
    """
    Use DetectAction to search for an object by type.
    """
    try:
        print("\n--- Detect Object ---")
        obj_type = input("Enter object type to detect (e.g., Milk, Cereal, Spoon, Bowl): ").strip()
        with simulated_robot:
            believe_desig = BelieveObject(types=[obj_type])
            detected = DetectAction(technique=DetectionTechnique.TYPES,
                                   object_designator_description=believe_desig).resolve().perform()
        if detected:
            print("Detected the following objects:")
            for obj in detected:
                print(f" - {obj.name}")
        else:
            print("No objects of type", obj_type, "were detected.")
    except Exception as e:
        print("CRAM error in detect_object:", e)

def transport_object():
    """
    Transport an object to a destination using TransportAction.
    """
    try:
        print("\n--- Transport Object ---")
        obj_name = input("Enter the name of the object to transport: ").strip()
        dest_input = input("Enter destination coordinates as x,y,z: ").strip()
        try:
            dest_vals = [float(val.strip()) for val in dest_input.split(",")]
            if len(dest_vals) != 3:
                print("Invalid destination coordinates.")
                return
        except Exception as e:
            print("CRAM error parsing destination coordinates:", e)
            return
        
        arm_input = input("Enter which arm to use (left/right): ").strip().lower()
        if arm_input == "left":
            arm = Arms.LEFT
        elif arm_input == "right":
            arm = Arms.RIGHT
        else:
            print("Invalid arm selection.")
            return

        with simulated_robot:
            object_desig = BelieveObject(names=[obj_name])
            destination_pose = Pose(dest_vals)
            print("Transporting object...")
            TransportAction(object_desig, [destination_pose], [arm]).resolve().perform()
            print("Transport action performed.")
    except Exception as e:
        print("CRAM error in transport_object:", e)
