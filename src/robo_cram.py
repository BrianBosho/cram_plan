import threading
import time
from enum import Enum
from typing import AnyStr, Dict, Tuple

from pycram.datastructures.dataclasses import Color
from pycram.datastructures.enums import Arms, WorldMode
from pycram.datastructures.pose import Pose
from pycram.designators.action_designator import NavigateActionDescription, ParkArmsActionDescription
from pycram.designators.location_designator import SemanticCostmapLocation
from pycram.designators.object_designator import BelieveObject
from pycram.process_module import simulated_robot
from pycram.worlds.bullet_world import BulletWorld
from pycram.world_concepts.world_object import Object
from pycrap.ontologies import Apartment, Bowl, Cereal, Kitchen, Milk, Spoon, Robot


class Env(Enum):
    KITCHEN, APARTMENT = range(2)


class Obj(Enum):
    CEREAL, MILK, SPOON, BOWL = range(4)


class Colour(Enum):
    RED, GREEN, BLUE, YELLOW, WHITE, BLACK, DEFAULT = range(7)


class Area(Enum):
    SINK = range(1)


ROBOT_NAME = "pr2"
COLOURS = {
    Colour.RED: (1.0, 0.0, 0.0, 1.0),
    Colour.GREEN: (0.0, 1.0, 0.0, 1.0),
    Colour.BLUE: (0.0, 0.0, 1.0, 1.0),
    Colour.YELLOW: (1.0, 1.0, 0.0, 1.0),
    Colour.WHITE: (1.0, 1.0, 1.0, 1.0),
    Colour.BLACK: (0.0, 0.0, 0.0, 1.0),
    Colour.DEFAULT: (0.5, 0.0, 0.0, 1.0)
}
ENVIRONMENTS = {
    Env.KITCHEN: ("kitchen", Kitchen, "kitchen.urdf"),
    Env.APARTMENT: ("apartment", Apartment, "apartment.urdf")
}
OBJECTS = {
    Obj.CEREAL: (Cereal, "breakfast_cereal.stl"),
    Obj.MILK: (Milk, "milk.stl"),
    Obj.SPOON: (Spoon, "spoon.stl"),
    Obj.BOWL: (Bowl, "bowl.stl")
}
AREAS = {
    Area.SINK: "sink"
}
world = None
environment = None


def init_simulation(env: Env = Env.KITCHEN) -> None:
    global world, environment

    environment = env
    world = BulletWorld(WorldMode.GUI)
    environment = Object(*ENVIRONMENTS[env])
    robot = Object(ROBOT_NAME, Robot, "pr2.urdf")

    if env == Env.KITCHEN:
        environment.set_link_color("iai_fridge_door", [0.0, 0.0, 0.5])
        environment.set_link_color("sink_area_sink", [0.75, 0.75, 0.75])
        environment.set_link_color("sink_area_dish_washer_door", [0.0, 0.25, 0.0])
        environment.set_link_color("oven_area_oven_panel", [0.0, 0.0, 0.5])
        environment.set_link_color("oven_area_oven_door", [0.0, 0.25, 0.0])

    robot.set_link_color("base_link", [0.0, 0.0, 0.0])
    robot.set_link_color("head_tilt_link", [0.0, 0.0, 0.0])
    robot.set_link_color("r_forearm_link", [0.0, 0.0, 0.0])
    robot.set_link_color("l_forearm_link", [0.0, 0.0, 0.0])
    robot.set_link_color("torso_lift_link", [0, 0.2, 0.5])
    robot.set_link_color("r_gripper_palm_link", [0, 0.2, 0.5])
    robot.set_link_color("l_gripper_palm_link", [0, 0.2, 0.5])


def robot_pack_arms() -> None:
    with simulated_robot:
        ParkArmsActionDescription([Arms.BOTH]).resolve().perform()


def spawn_object(
        obj: Obj = Obj.CEREAL, obj_name: AnyStr = "object", coordinates: Tuple[float, float, float] = (1.4, 1.0, 0.875),
        colour: Colour = Colour.DEFAULT
    ) -> Dict:
    try:
        position = [float(i) for i in coordinates]
    except ValueError:
        return {"status": "error", "message": "Coordinates must have exactly 3 real numbers (x,y,z)"}

    if len(position) != 3:
        return {"status": "error", "message": "Coordinates must have exactly 3 real numbers (x,y,z)"}

    obj_type, obj_file = OBJECTS[obj]
    Object(obj_name, obj_type, obj_file, pose=Pose(position), color=Color.from_list(COLOURS[colour]))

    return {
        "status": "success",
        "message": f"Object '{obj_name}' created successfully",
        "object": {
            "name": obj_name,
            "type": str(obj_type).split(".")[1],
            "file": obj_file,
            "position": position,
            "colour": COLOURS[colour]
        }
    }


def move_robot(coordinates: Tuple[float, float, float] = (0, 0, 0)) -> Dict:
    try:
        position = [float(i) for i in coordinates]
    except ValueError:
        return {"status": "error", "message": "Coordinates must have exactly 3 real numbers (x,y,z)"}

    if len(position) != 3:
        return {"status": "error", "message": "Coordinates must have exactly 3 real numbers (x,y,z)"}

    with simulated_robot:
        ParkArmsActionDescription([Arms.BOTH]).resolve().perform()
        NavigateActionDescription(target_location=[Pose(position)]).resolve().perform()

    return {
        "status": "success", 
        "message": f"Robot moved to coordinates {position}",
        "coordinates": position
    }


def is_object_type_in_environment(obj: Obj) -> Dict:
    obj_type = OBJECTS[obj][0]

    with simulated_robot:
        try:
            objects = BelieveObject(types=[obj_type])
        except StopIteration:
            objects = []

    objs_in_environment = [{"name": i.name, "type": str(obj_type).split(".")[1]} for i in objects]

    return {
        "status": "success" if len(objs_in_environment) > 0 else "error",
        "message": f"{len(objs_in_environment)} object{'s' if len(objs_in_environment) != 1 else ''} of type "
            f"'{str(obj_type).split('.')[1]}' {'are' if len(objs_in_environment) != 1 else 'is'} in the environment",
        "objects": objs_in_environment
    }


def is_object_in_environment(obj_name: AnyStr) -> Dict:
    with simulated_robot:
        try:
            object = BelieveObject(names=[obj_name]).resolve()
        except StopIteration:
            object = None

    if object is None:
        return {
            "status": "error",
            "message": f"Object '{obj_name}' is not in the environment"
        }

    return {
        "status": "success",
        "message": f"Object '{obj_name}' is in the environment"
    }


def is_object_type_in_area(area: Area, obj: Obj) -> Dict:
    with simulated_robot:
        env = BelieveObject(names=[ENVIRONMENTS[environment][0]]).resolve()
        location_description = SemanticCostmapLocation(link_name=AREAS[area], part_of=env)

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


def is_object_in_area(area: Area, obj_name: AnyStr) -> Dict:
    with simulated_robot:
        env = BelieveObject(names=[ENVIRONMENTS[environment][0]]).resolve()
        location_description = SemanticCostmapLocation(link_name=AREAS[area], part_of=env)

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


def exit_simulation() -> None:
    if world is not None:
        world.exit()
