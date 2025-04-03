import threading
import time
from enum import Enum
from typing import AnyStr, Dict, Tuple

from pycram.datastructures.enums import Arms, DetectionTechnique, Grasp, ObjectType, TorsoState, WorldMode
from pycram.datastructures.pose import Pose
from pycram.designators.action_designator import *
from pycram.designators.location_designator import *
from pycram.designators.motion_designator import *
from pycram.designators.object_designator import *
from pycrap.ontologies import Apartment, Bowl, Cereal, Kitchen, Milk, Spoon, Robot
from pycram.process_module import simulated_robot
from pycram.worlds.bullet_world import BulletWorld
from pycram.world_concepts.world_object import Object


world = None


class Env(Enum):
    KITCHEN, APARTMENT = range(2)


class Obj(Enum):
    CEREAL, MILK, SPOON, BOWL = range(4)


class Colour(Enum):
    RED, GREEN, BLUE, YELLOW, WHITE, BLACK, DEFAULT = range(7)


def get_rgba(colour_string: AnyStr) -> Tuple[float, float, float, float]:
    colour_string_to_rgba = {
        "red": (1.0, 0.0, 0.0, 1.0),
        "green": (0.0, 1.0, 0.0, 1.0),
        "blue": (0.0, 0.0, 1.0, 1.0),
        "yellow": (1.0, 1.0, 0.0, 1.0),
        "white": (1.0, 1.0, 1.0, 1.0),
        "black": (0.0, 0.0, 0.0, 1.0)
    }
    return colour_string_to_rgba.get(colour_string.lower(), (0.5, 0.0, 0.0, 1.0))


def init_simulation(env: Env = Env.KITCHEN) -> None:
    global world

    env_name, env_ontology, env_file = {
        Env.KITCHEN: ("kitchen", Kitchen, "kitchen.urdf"),
        Env.APARTMENT: ("apartment", Apartment, "apartment.urdf")
    }[env]

    world = BulletWorld(WorldMode.GUI)
    Object(env_name, env_ontology, env_file)
    Object("pr2", Robot, "pr2.urdf")


def exit_simulation() -> None:
    if world is not None:
        world.exit()


def spawn_object(
        obj: Obj = Obj.CEREAL, coordinates: Tuple[float, float, float] = (1.4, 1.0, 0.95), colour: Colour = Colour.DEFAULT
    ) -> Dict:
    position = [float(i) for i in coordinates]
    if len(position) != 3:
        return {"status": "error", "message": "Coordinates must have exactly 3 values (x,y,z)"}

    obj_name, obj_ontology, obj_file = {
        Obj.CEREAL: ("cereal", Cereal, "breakfast_cereal.stl"),
        Obj.MILK: ("milk", Milk, "milk.stl"),
        Obj.SPOON: ("spoon", Spoon, "spoon.stl"),
        Obj.BOWL: ("bowl", Bowl, "bowl.stl")
    }[obj]
    obj_colour = get_rgba(colour) if colour else get_rgba("get_default_colour")
    obj = Object(obj_name, obj_ontology, obj_file, pose=Pose(position), colour=obj_colour)

    return {
        "status": "success",
        "message": f"Object '{obj_name}' created successfully",
        "object": {
            "name": obj_name,
            "type": str(obj_ontology),
            "file": obj_file,
            "position": position,
            "colour": colour if colour else "default"
        }
    }


def move_robot(coordinates: Tuple[float, float, float] = (0, 0, 0)) -> Dict:
    position = [float(i) for i in coordinates]
    if len(position) != 3:
        return {"status": "error", "message": "Coordinates must have exactly 3 values (x,y,z)"}

    nav_pose = Pose(position)

    with simulated_robot:
        ObjectDesignatorDescription(names=["pr2"]).resolve()
        NavigateAction(target_locations=[nav_pose]).resolve().perform()

    return {
        "status": "success", 
        "message": f"Robot moved to coordinates {position}",
        "coordinates": position
    }


def pickup_and_place(obj: Obj, target_coordinates: Tuple[float, float, float], arm: Arms) -> Dict:
    position = [float(i) for i in target_coordinates]
    if len(position) != 3:
        return {"status": "error", "message": "Coordinates must have exactly 3 values (x,y,z)"}

    obj_name = {
        Obj.CEREAL: "cereal",
        Obj.MILK: "milk",
        Obj.SPOON: "spoon",
        Obj.BOWL: "bowl"
    }[obj]

    with simulated_robot:
        object_desig = BelieveObject(names=[obj_name])
        robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()

        ParkArmsAction([Arms.BOTH]).resolve().perform()
        MoveTorsoAction([TorsoState.HIGH]).resolve().perform()

        try:
            try:
                object_resolved = object_desig.resolve()
            except StopIteration:
                variants = [
                    object_name.lower(),
                    object_name.upper(),
                    object_name.capitalize()
                ]

                object_resolved = None
                for variant in variants:
                    if variant != object_name:
                        try:
                            variant_desig = BelieveObject(names=[variant])
                            object_resolved = variant_desig.resolve()
                            if object_resolved:
                                print(f"API: Found object with name '{variant}'")
                                object_desig = variant_desig
                                object_name = variant
                                break
                        except StopIteration:
                            continue

                if not object_resolved:
                    return {"status": "error", "message": f"Object '{object_name}' not found in the world. You may need to spawn it first."}

            pickup_pose = CostmapLocation(target=object_resolved, reachable_for=robot_desig).resolve()

        except StopIteration:
            return {"status": "error", "message": f"Object '{object_name}' not found in the world. You may need to spawn it first."}

        if not pickup_pose.reachable_arms:
            return {"status": "error", "message": f"No reachable arms for object {object_name}"}

        if arm not in pickup_pose.reachable_arms:
            return {"status": "error", "message": f"Selected arm ({'right' if arm == Arms.RIGHT else 'left'}) can't reach object, use the other arm"}

        NavigateAction(target_locations=[pickup_pose.pose]).resolve().perform()
        PickUpAction(object_designator_description=object_desig, arms=[arm], grasps=[Grasp.FRONT]).resolve().perform()
        ParkArmsAction([Arms.BOTH]).resolve().perform()

        time.sleep(0.5)  # Allow simulation state to update

        destination_pose = Pose(position)
        place_stand = None
        resolution_timeout = 5  # seconds
        resolution_complete = False
        resolution_error = None

        def resolve_placement():
            nonlocal place_stand, resolution_complete, resolution_error
            try:
                place_stand = CostmapLocation(destination_pose, reachable_for=robot_desig, reachable_arm=arm).resolve()
                resolution_complete = True
            except Exception as e:
                resolution_error = str(e)
                resolution_complete = True

        resolution_thread = threading.Thread(target=resolve_placement)
        resolution_thread.daemon = True
        resolution_thread.start()

        start_time = time.time()
        while not resolution_complete and time.time() - start_time < resolution_timeout:
            time.sleep(0.1)

        if not resolution_complete:
            place_stand = None

        if resolution_error:
            place_stand = None

        if place_stand is None or not hasattr(place_stand, 'pose'):
            PlaceAction(object_designator_description=object_desig, target_locations=[destination_pose], arms=[arm]).resolve().perform()
            ParkArmsAction([Arms.BOTH]).resolve().perform()

            return {
                "status": "success",
                "message": f"Successfully picked up {object_name} and placed at {position} (using fallback)",
                "object": object_name,
                "target_location": position,
                "arm_used": str(arm)
            }

        NavigateAction(target_locations=[place_stand.pose]).resolve().perform()
        PlaceAction(object_designator_description=object_desig, target_locations=[destination_pose], arms=[arm]).resolve().perform()
        ParkArmsAction([Arms.BOTH]).resolve().perform()

        return {
            "status": "success",
            "message": f"Successfully picked up {object_name} and placed at {position}",
            "object": object_name,
            "target_location": position,
            "arm_used": str(arm)
        }


def robot_perceive(perception_area: AnyStr) -> Dict:
    with simulated_robot:
        results = PerceiveAction(area=perception_area).resolve().perform()

    perceived_objects = []

    for i in results:
        perceived_objects.append({
            "name": i.name if hasattr(i, "name") else "unknown",
            "type": str(type(i))
        })

    return {
        "status": "success",
        "message": f"Robot perceived {len(perceived_objects)} objects in {perception_area}",
        "perceived_objects": perceived_objects
    }


def look_for_object(obj: Obj) -> Dict:
    obj_name = {
        Obj.CEREAL: "cereal",
        Obj.MILK: "milk",
        Obj.SPOON: "spoon",
        Obj.BOWL: "bowl"
    }[obj]

    with simulated_robot:
        obj_desig = ObjectDesignatorDescription(names=[obj_name]).resolve()
        result = LookForAction(object=obj_desig).resolve().perform()

    if not result:
        return {
            "status": "error",
            "message": f"Could not find {obj_name}"
        }

    position = result.pose.position if hasattr(result, 'pose') else "unknown"

    return {
        "status": "success",
        "message": f"Found {obj_name}",
        "object": obj_name,
        "position": str(position)
    }


def unpack_arms() -> Dict:
    with simulated_robot:
        UnpackAction().resolve().perform()

    return {
        "status": "success",
        "message": "Robot arms unpacked successfully"
    }


def detect_object(obj: Obj) -> Dict:
    obj_name = {
        Obj.CEREAL: "cereal",
        Obj.MILK: "milk",
        Obj.SPOON: "spoon",
        Obj.BOWL: "bowl"
    }[obj]

    with simulated_robot:
        believe_desig = BelieveObject(types=[obj_name])
        detected = DetectAction(technique=DetectionTechnique.TYPES, object_designator_description=believe_desig).resolve().perform()

    detected_objects = []

    if detected:
        for i in detected:
            detected_objects.append({
                "name": i.name if hasattr(i, "name") else "unknown",
                "type": str(type(i))
            })

    return {
        "status": "success",
        "message": f"Detected {len(detected_objects)} objects of type {object_type}",
        "detected_objects": detected_objects
    }


def transport_object(obj: Obj, target_coordinates: Tuple[float, float, float], arm: Arms) -> Dict:
    position = [float(i) for i in target_coordinates]
    if len(position) != 3:
        return {"status": "error", "message": "Coordinates must have exactly 3 values (x,y,z)"}

    obj_name = {
        Obj.CEREAL: "cereal",
        Obj.MILK: "milk",
        Obj.SPOON: "spoon",
        Obj.BOWL: "bowl"
    }[obj]

    with simulated_robot:
        object_desig = BelieveObject(names=[obj_name])
        destination_position = Pose(position)
        TransportAction(object_desig, [destination_position], [arm]).resolve().perform()

    return {
        "status": "success",
        "message": f"Successfully transported {obj_name} to {position}",
        "object": obj_name,
        "target_location": position,
        "arm_used": str(arm)
    }
