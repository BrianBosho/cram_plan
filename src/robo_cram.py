from enum import Enum
from typing import Any, Tuple, TypedDict

import numpy as np
from pycram.datastructures.dataclasses import Color
from pycram.datastructures.enums import (
    Arms,
    DetectionTechnique,
    Frame,
    Grasp,
    TorsoState,
    WorldMode,
)
from pycram.datastructures.pose import Pose
from pycram.designators.action_designator import (
    DetectActionDescription,
    LookAtActionDescription,
    MoveTorsoActionDescription,
    NavigateActionDescription,
    ObjectDesignatorDescription,
    ParkArmsActionDescription,
    PickUpActionDescription,
    PlaceActionDescription,
    ReachToPickUpActionDescription,
)
from pycram.designators.location_designator import (
    CostmapLocation,
    SemanticCostmapLocation,
)
from pycram.designators.object_designator import BelieveObject
from pycram.failures import (
    LookAtGoalNotReached,
    ObjectNotGraspedError,
    PerceptionObjectNotFound,
)
from pycram.process_module import simulated_robot
from pycram.robot_description import RobotDescription
from pycram.world_concepts.world_object import Object
from pycram.worlds.bullet_world import BulletWorld
from pycrap.ontologies import Apartment, Bowl, Cereal, Kitchen, Milk, Robot, Spoon


class Env(Enum):
    KITCHEN, APARTMENT = range(2)


class Obj(Enum):
    CEREAL, MILK, SPOON, BOWL = range(4)


class Colour(Enum):
    RED, GREEN, BLUE, YELLOW, WHITE, BLACK, DEFAULT = range(7)


class Location(Enum):
    KITCHEN_ISLAND, SINK_AREA, TABLE = range(3)


ROBOT_NAME = "pr2"
COLOURS = {
    Colour.RED: (1.0, 0.0, 0.0, 1.0),
    Colour.GREEN: (0.0, 1.0, 0.0, 1.0),
    Colour.BLUE: (0.0, 0.0, 1.0, 1.0),
    Colour.YELLOW: (1.0, 1.0, 0.0, 1.0),
    Colour.WHITE: (1.0, 1.0, 1.0, 1.0),
    Colour.BLACK: (0.0, 0.0, 0.0, 1.0),
    Colour.DEFAULT: (0.5, 0.3, 0.1, 1.0),
}
ENVIRONMENTS = {
    Env.KITCHEN: ("kitchen", Kitchen, "kitchen.urdf"),
    Env.APARTMENT: ("apartment", Apartment, "apartment.urdf"),
}
OBJECTS = {
    Obj.CEREAL: (Cereal, "breakfast_cereal.stl"),
    Obj.MILK: (Milk, "milk.stl"),
    Obj.SPOON: (Spoon, "spoon.stl"),
    Obj.BOWL: (Bowl, "bowl.stl"),
}
LOCATIONS = {
    Location.KITCHEN_ISLAND: "kitchen_island_surface",
    Location.SINK_AREA: "sink_area_surface",
    Location.TABLE: "table_area_main",
}
BLACK_COLOUR = Color(0.0, 0.0, 0.0, 1.0)
GREEN_COLOUR = Color(0.0, 0.25, 0.0, 1.0)
BLUE_COLOUR = Color(0.0, 0.0, 0.5, 1.0)
YELLOW_COLOUR = Color(0.5, 0.5, 0.0, 1.0)
SILVER_COLOUR = Color(0.75, 0.75, 0.75, 1.0)
WOOD_COLOUR = Color(0.8, 0.7, 0.5, 1.0)
world: BulletWorld = None
environment: Env = None


class Response(TypedDict):
    status: str
    message: str
    payload: Any = None


def init_simulation(env: Env = Env.KITCHEN) -> Response:
    global world, environment

    environment = env
    world = BulletWorld(WorldMode.GUI)
    env_obj = Object(*ENVIRONMENTS[env])
    robot_obj = Object(ROBOT_NAME, Robot, "pr2.urdf")

    if env == Env.KITCHEN:
        env_obj.set_color(
            {
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
                "drawer_oven_right_front_link": WOOD_COLOUR,
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
                "table_area_main": WOOD_COLOUR,
            }
        )

    robot_obj.set_color(
        {
            "base_link": BLACK_COLOUR,
            "head_tilt_link": BLACK_COLOUR,
            "r_forearm_link": BLACK_COLOUR,
            "l_forearm_link": BLACK_COLOUR,
            "torso_lift_link": GREEN_COLOUR,
            "r_gripper_palm_link": GREEN_COLOUR,
            "l_gripper_palm_link": GREEN_COLOUR,
        }
    )

    return Response(status="success", message="Simulation initialisation successful")


def pack_arms() -> Response:
    with simulated_robot:
        ParkArmsActionDescription([Arms.BOTH]).resolve().perform()
    return Response(status="success", message="Robot arms pack successful")


def adjust_torso(high: bool) -> Response:
    with simulated_robot:
        MoveTorsoActionDescription(
            [TorsoState.HIGH if high else TorsoState.LOW]
        ).resolve().perform()
    return Response(
        status="success",
        message=f"Robot torso move to {'high' if high else 'low'} successful",
    )


def spawn_object(
    obj: Obj,
    obj_name: str,
    coordinates: Tuple[float, float, float] = (1.4, 1.0, 0.9),
    colour: Colour = Colour.DEFAULT,
) -> Response:
    try:
        position = [float(i) for i in coordinates]
    except ValueError:
        return Response(
            status="error",
            message="Coordinates must have exactly 3 real numbers (x,y,z)",
        )

    if len(position) != 3:
        return Response(
            status="error",
            message="Coordinates must have exactly 3 real numbers (x,y,z)",
        )

    obj_name = obj_name.lower()
    obj_type, obj_file = OBJECTS[obj]
    Object(
        obj_name,
        obj_type,
        obj_file,
        pose=Pose(position),
        color=Color.from_list(COLOURS[colour]),
    )

    return Response(
        status="success",
        message=f"Object '{obj_name}' created successfully",
        payload={
            "object": {
                "name": obj_name,
                "type": str(obj_type).split(".")[1],
                "file": obj_file,
                "position": position,
                "colour": COLOURS[colour],
            }
        },
    )


def move_robot(coordinates: Tuple[float, float, float] = (0, 0, 0)) -> Response:
    try:
        position = [float(i) for i in coordinates]
    except ValueError:
        return Response(
            status="error",
            message="Coordinates must have exactly 3 real numbers (x,y,z)",
        )

    if len(position) != 3:
        return Response(
            status="error",
            message="Coordinates must have exactly 3 real numbers (x,y,z)",
        )

    with simulated_robot:
        ParkArmsActionDescription([Arms.BOTH]).resolve().perform()
        NavigateActionDescription(target_location=[Pose(position)]).resolve().perform()

    return Response(
        status="success",
        message=f"Robot moved to coordinates {position}",
        payload={"coordinates": position},
    )


def is_object_type_in_environment(obj: Obj) -> Response:
    obj_type = OBJECTS[obj][0]
    objects = BelieveObject(types=[obj_type])
    objs_in_environment = [
        {"name": i.name, "type": str(obj_type).split(".")[1]} for i in objects
    ]

    return Response(
        status="success" if len(objs_in_environment) > 0 else "error",
        message=f"{len(objs_in_environment)} object{'s' if len(objs_in_environment) != 1 else ''} of type "
        f"'{str(obj_type).split('.')[1]}' {'are' if len(objs_in_environment) != 1 else 'is'} in the environment",
        payload={"objects": objs_in_environment},
    )


def is_object_in_environment(obj_name: str) -> Response:
    obj_name = obj_name.lower()

    with simulated_robot:
        try:
            obj = BelieveObject(names=[obj_name]).resolve()
        except StopIteration:
            obj = None

    if obj is None:
        return Response(
            status="error", message=f"Object '{obj_name}' is not in the environment"
        )

    return Response(
        status="success", message=f"Object '{obj_name}' is in the environment"
    )


def is_object_type_in_location(location: Location, obj: Obj) -> Response:
    obj_type = OBJECTS[obj][0]
    object_desig = BelieveObject(types=[obj_type])

    if len([_ for _ in object_desig]) == 0:
        return Response(
            status="error",
            message=f"Objects of type '{str(obj_type).split('.')[1]}' are not in the environment",
        )

    with simulated_robot:
        try:
            DetectActionDescription(
                DetectionTechnique.TYPES,
                object_designator_description=object_desig,
                region=LOCATIONS[location],
            ).resolve().perform()
            object_found = True
        except PerceptionObjectNotFound:
            object_found = False

    return Response(
        status="success" if object_found else "error",
        message=f"Objects of type '{str(obj_type).split('.')[1]}' are{'' if object_found else ' not'} in the location",
    )


def is_object_in_location(location: Location, obj_name: str) -> Response:
    obj_name = obj_name.lower()
    object_desig = BelieveObject(names=[obj_name])

    if len([_ for _ in object_desig]) == 0:
        return Response(
            status="error", message=f"Object '{obj_name}' is not in the environment"
        )

    with simulated_robot:
        try:
            DetectActionDescription(
                DetectionTechnique.TYPES,
                object_designator_description=object_desig,
                region=LOCATIONS[location],
            ).resolve().perform()
            object_found = True
        except PerceptionObjectNotFound:
            object_found = False

    return Response(
        status="success" if object_found else "error",
        message=f"Object '{obj_name}' is{'' if object_found else ' not'} in the location",
    )


def look_at_object(obj_name: str) -> Response:
    obj_name = obj_name.lower()

    with simulated_robot:
        try:
            obj = BelieveObject(names=[obj_name]).resolve()
        except StopIteration:
            obj = None

    if obj is None:
        return Response(
            status="error", message=f"Object '{obj_name}' is not in the environment"
        )

    with simulated_robot:
        try:
            LookAtActionDescription(target=[obj.pose]).resolve().perform()
            looking_at_object = True
        except LookAtGoalNotReached:
            looking_at_object = False

    if not looking_at_object:
        return Response(
            status="error", message=f"Robot vision failed to reach '{obj_name}'"
        )

    return Response(status="success", message=f"Robot is now looking at '{obj_name}'")


def pick_and_place(obj_name: str, destination: Location) -> Response:
    obj_name = obj_name.lower()
    robot_home_pose = Pose([0, 0, 0])

    with simulated_robot:
        env = BelieveObject(names=[ENVIRONMENTS[environment][0]]).resolve()
        try:
            obj = BelieveObject(names=[obj_name]).resolve()
        except StopIteration:
            obj = None

    if obj is None:
        return Response(
            status="error", message=f"Object '{obj_name}' is not in the environment"
        )

    with simulated_robot:
        ParkArmsActionDescription([Arms.BOTH]).resolve().perform()
        MoveTorsoActionDescription([TorsoState.HIGH]).resolve().perform()

        robot = ObjectDesignatorDescription(names=[ROBOT_NAME]).resolve()
        pickup_arm = None

        try:
            pickup_pose = CostmapLocation(target=obj, reachable_for=robot).resolve()
            pickup_arm = pickup_pose.arm
        except StopIteration:
            pass

    if pickup_arm is None:
        with simulated_robot:
            MoveTorsoActionDescription([TorsoState.LOW]).resolve().perform()

        return Response(
            status="error", message=f"No reachable arms to pick up object '{obj_name}'"
        )

    with simulated_robot:
        NavigateActionDescription(
            target_location=Pose(
                pickup_pose.pose.position, pickup_pose.pose.orientation
            )
        ).resolve().perform()

        grasped = False
        for grasp in [
            Grasp.FRONT,
            Grasp.BACK,
            Grasp.RIGHT,
            Grasp.LEFT,
            Grasp.TOP,
            Grasp.BOTTOM,
        ]:
            try:
                PickUpActionDescription(
                    object_designator=obj, arm=pickup_arm, grasp_description=grasp
                ).resolve().perform()
                grasped = True
            except ObjectNotGraspedError:
                pass

        ParkArmsActionDescription([Arms.BOTH]).resolve().perform()

    if not grasped:
        with simulated_robot:
            NavigateActionDescription(
                target_location=robot_home_pose
            ).resolve().perform()
            MoveTorsoActionDescription([TorsoState.LOW]).resolve().perform()

        return Response(
            status="error", message=f"The object '{obj_name}' could not be grasped"
        )

    with simulated_robot:
        obj_dest_location = SemanticCostmapLocation(
            link_name=LOCATIONS[destination], part_of=env, for_object=obj
        ).resolve()
        place_location = CostmapLocation(
            target=obj_dest_location.pose, reachable_for=robot, reachable_arm=pickup_arm
        ).resolve()

        NavigateActionDescription(
            target_location=place_location.pose
        ).resolve().perform()
        PlaceActionDescription(
            obj, target_location=obj_dest_location.pose, arm=pickup_arm
        ).resolve().perform()
        ParkArmsActionDescription([Arms.BOTH]).resolve().perform()
        MoveTorsoActionDescription([TorsoState.LOW]).resolve().perform()

    return Response(
        status="success",
        message=f"Object '{obj_name}' successfully moved to '{LOCATIONS[destination]}'",
    )


def capture_image(target_distance: float = 2.0) -> Response:
    robot = BelieveObject(names=[ROBOT_NAME]).resolve()
    camera_link_name = RobotDescription.current_robot_description.get_camera_link()
    camera_link = robot.get_link(camera_link_name)
    camera_pose = camera_link.pose
    camera_axis = (
        RobotDescription.current_robot_description.get_default_camera().front_facing_axis
    )

    target = np.array(camera_axis) * target_distance
    target_pose = Pose(target, frame=camera_link.tf_frame)
    target_pose = robot.local_transformer.transform_pose(target_pose, Frame.Map.value)

    rgb_image, depth_image, segmentation_mask = world.get_images_for_target(
        target_pose, camera_pose
    )

    return Response(
        status="success",
        message="Image capture successful",
        payload={
            "rgb_image": rgb_image,
            "depth_image": depth_image,
            "segmentation_mask": segmentation_mask,
        },
    )


def get_objects_in_robot_view(
    target_distance: float = 2.0, min_pixel_count=50
) -> Response:
    robot = BelieveObject(names=[ROBOT_NAME]).resolve()
    camera_link_name = RobotDescription.current_robot_description.get_camera_link()
    camera_link = robot.get_link(camera_link_name)
    camera_pose = camera_link.pose
    camera_axis = (
        RobotDescription.current_robot_description.get_default_camera().front_facing_axis
    )

    target = np.array(camera_axis) * target_distance
    target_pose = Pose(target, frame=camera_link.tf_frame)
    target_pose = robot.local_transformer.transform_pose(target_pose, Frame.Map.value)

    _, __, segmentation_mask = world.get_images_for_target(target_pose, camera_pose)
    unique_ids = np.unique(segmentation_mask)
    visible_objects = {}

    for idx in unique_ids:
        pixel_count = np.sum(segmentation_mask == idx)
        if pixel_count < min_pixel_count:
            continue

        obj = world.get_object_by_id(idx)
        if obj is not None:
            visible_objects[idx] = {
                "name": obj.name,
                "type1": str(type(obj).__name__),
                "type2": str(type(obj)),
                "pixel_count": int(pixel_count),
            }

    return Response(
        status="success",
        message="Getting objects in robot view successful",
        payload=visible_objects,
    )


def exit_simulation() -> Response:
    if world is not None:
        world.exit()
    return Response(status="success", message="Simulation exit successful")
