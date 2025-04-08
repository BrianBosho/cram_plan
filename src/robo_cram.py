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
BLACK_COLOUR = Color(0.0, 0.0, 0.0, 1.0)
GREEN_COLOUR = Color(0.0, 0.25, 0.0, 1.0)
BLUE_COLOUR = Color(0.0, 0.0, 0.5, 1.0)
YELLOW_COLOUR = Color(0.5, 0.5, 0.0, 1.0)
SILVER_COLOUR = Color(0.75, 0.75, 0.75, 1.0)
WOOD_COLOUR = Color(0.8, 0.7, 0.5, 1.0)
world = None
environment = None


def init_simulation(env: Env = Env.KITCHEN) -> None:
    global world, environment

    environment = env
    world = BulletWorld(WorldMode.GUI)
    env_obj = Object(*ENVIRONMENTS[env])
    robot_obj = Object(ROBOT_NAME, Robot, "pr2.urdf")

    if env == Env.KITCHEN:
        env_obj.set_color({
            "drawer_oven_right_front_link": WOOD_COLOUR,

            "fridge_area": SILVER_COLOUR,
            "iai_fridge_door": GREEN_COLOUR,
            "iai_fridge_door_handle": SILVER_COLOUR,
            "fridge_area_lower_drawer_main": WOOD_COLOUR,
            "fridge_area_lower_drawer_handle": SILVER_COLOUR,

            "kitchen_island": WOOD_COLOUR,
            "kitchen_island_right_upper_drawer_main": WOOD_COLOUR,
            "kitchen_island_right_upper_drawer_handle": SILVER_COLOUR,
            "kitchen_island_right_lower_drawer_main": WOOD_COLOUR,
            "kitchen_island_right_lower_drawer_handle": SILVER_COLOUR,
            "kitchen_island_middle_upper_drawer_main": WOOD_COLOUR,
            "kitchen_island_middle_upper_drawer_handle": SILVER_COLOUR,
            "kitchen_island_middle_lower_drawer_main": WOOD_COLOUR,
            "kitchen_island_middle_lower_drawer_handle": SILVER_COLOUR,
            "kitchen_island_left_upper_drawer_main": WOOD_COLOUR,
            "kitchen_island_left_upper_drawer_handle": SILVER_COLOUR,
            "kitchen_island_left_lower_drawer_main": WOOD_COLOUR,
            "kitchen_island_left_lower_drawer_handle": SILVER_COLOUR,

            "oven_area_area": SILVER_COLOUR,
            "oven_area_oven_panel": BLUE_COLOUR,
            "oven_area_oven_door": GREEN_COLOUR,
            "oven_area_oven_door_handle": SILVER_COLOUR,
            "oven_area_area_right_drawer_handle": SILVER_COLOUR,
            "oven_area_area_left_drawer_main": WOOD_COLOUR,
            "oven_area_area_left_drawer_handle": SILVER_COLOUR,
            "oven_area_area_middle_lower_drawer_main": GREEN_COLOUR,
            "oven_area_area_middle_lower_drawer_handle": SILVER_COLOUR,
            "oven_area_area_middle_upper_drawer_main": GREEN_COLOUR,
            "oven_area_area_middle_upper_drawer_handle": SILVER_COLOUR,
            "oven_area_oven_knob_oven": SILVER_COLOUR,
            "oven_area_oven_knob_stove_1": SILVER_COLOUR,
            "oven_area_oven_knob_stove_2": SILVER_COLOUR,
            "oven_area_oven_knob_stove_3": SILVER_COLOUR,
            "oven_area_oven_knob_stove_4": SILVER_COLOUR,

            "sink_area": WOOD_COLOUR,
            "sink_area_surface": SILVER_COLOUR,
            "sink_area_sink": SILVER_COLOUR,
            "sink_area_dish_washer_door": YELLOW_COLOUR,
            "sink_area_dish_washer_door_handle": SILVER_COLOUR,
            "sink_area_left_upper_drawer_main": YELLOW_COLOUR,
            "sink_area_left_upper_drawer_handle": SILVER_COLOUR,
            "sink_area_left_middle_drawer_main": YELLOW_COLOUR,
            "sink_area_left_middle_drawer_handle": SILVER_COLOUR,
            "sink_area_left_bottom_drawer_main": YELLOW_COLOUR,
            "sink_area_left_bottom_drawer_handle": SILVER_COLOUR,
            "sink_area_trash_drawer_main": YELLOW_COLOUR,
            "sink_area_trash_drawer_handle": SILVER_COLOUR,
            "sink_area_right_panel": SILVER_COLOUR,

            "table_area_main": WOOD_COLOUR
        })

    robot_obj.set_color({
        "base_link": BLACK_COLOUR,
        "head_tilt_link": BLACK_COLOUR,
        "r_forearm_link": BLACK_COLOUR,
        "l_forearm_link": BLACK_COLOUR,
        "torso_lift_link": GREEN_COLOUR,
        "r_gripper_palm_link": GREEN_COLOUR,
        "l_gripper_palm_link": GREEN_COLOUR,
    })


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


def pick_and_place():
    pass


def exit_simulation() -> None:
    if world is not None:
        world.exit()
