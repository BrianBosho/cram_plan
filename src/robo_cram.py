import itertools
from enum import Enum
from typing import Any, Iterable, Optional, Tuple, TypedDict

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
from pycram.datastructures.grasp import GraspDescription
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
)
from pycram.designators.location_designator import (
    CostmapLocation,
    SemanticCostmapLocation,
)
from pycram.designators.object_designator import BelieveObject
from pycram.failures import (
    IKError,
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


class ObjectType(Enum):
    CEREAL, MILK, SPOON, BOWL = range(4)


class Colour(Enum):
    RED, GREEN, BLUE, YELLOW, WHITE, BLACK, DEFAULT = range(7)


class Location(Enum):
    KITCHEN_ISLAND, SINK_AREA = range(2)


ROBOT_NAME = "pr2"
ROBOT_HOME_POSE = Pose([0, 0, 0], [0, 0, 0, 1])
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
OBJECTS_TYPES = {
    ObjectType.CEREAL: (Cereal, "breakfast_cereal.stl"),
    ObjectType.MILK: (Milk, "milk.stl"),
    ObjectType.SPOON: (Spoon, "spoon.stl"),
    ObjectType.BOWL: (Bowl, "bowl.stl"),
}
LOCATIONS = {
    Location.KITCHEN_ISLAND: "kitchen_island_surface",
    Location.SINK_AREA: "sink_area_surface",
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


def park_arms() -> Response:
    with simulated_robot:
        ParkArmsActionDescription([Arms.BOTH]).resolve().perform()
    return Response(status="success", message="Robot arms park successful")


def adjust_torso(high: bool) -> Response:
    with simulated_robot:
        MoveTorsoActionDescription(
            [TorsoState.HIGH if high else TorsoState.LOW]
        ).resolve().perform()
    return Response(
        status="success",
        message=f"Robot torso move to {'high' if high else 'low'} successful",
    )


def get_robot_pose() -> Response:
    with simulated_robot:
        try:
            robot = BelieveObject(names=[ROBOT_NAME]).resolve()
        except StopIteration:
            robot = None

    return Response(
        status="success" if robot is not None else "error",
        message=f"Robot pose resolve{'' if robot is not None else ' not'} successful",
        payload={
            "position": (
                [robot.pose.position.x, robot.pose.position.y, robot.pose.position.z]
                if robot is not None
                else "error"
            ),
            "orientation": (
                [
                    robot.pose.orientation.x,
                    robot.pose.orientation.y,
                    robot.pose.orientation.z,
                    robot.pose.orientation.w,
                ]
                if robot is not None
                else "error"
            ),
        },
    )


def spawn_object(
    obj_type: ObjectType,
    obj_name: str,
    coordinates: Tuple[float, float, float] = (1.4, 1.0, 0.95),
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
    object_type, obj_file = OBJECTS_TYPES[obj_type]
    Object(
        obj_name,
        object_type,
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


def move_robot(
    coordinates: Tuple[float, float, float] = (0, 0, 0),
    orientation: Tuple[float, float, float, float] = (0, 0, 0, 1),
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

    try:
        rotation = [float(i) for i in orientation]
    except ValueError:
        return Response(
            status="error",
            message="Orientation must have exactly 4 real numbers (x,y,z,w)",
        )

    if len(rotation) != 4:
        return Response(
            status="error",
            message="Orientation must have exactly 4 real numbers (x,y,z,w)",
        )

    with simulated_robot:
        ParkArmsActionDescription([Arms.BOTH]).resolve().perform()
        NavigateActionDescription(
            target_location=[Pose(position, rotation)]
        ).resolve().perform()

    return Response(
        status="success",
        message=f"Robot moved to coordinates {position} and orientation {rotation}",
        payload={"coordinates": position, "orientation": rotation},
    )


def is_object_type_in_environment(obj_type: ObjectType) -> Response:
    object_type = OBJECTS_TYPES[obj_type][0]
    objects = BelieveObject(types=[object_type])
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

    return Response(
        status="success" if obj is not None else "error",
        message=f"Object '{obj_name}' is{'' if obj is None else ' not'} in the environment",
    )


def is_object_type_in_location(location: Location, obj_type: ObjectType) -> Response:
    object_type = OBJECTS_TYPES[obj_type][0]
    object_desig = BelieveObject(types=[object_type])

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


def pick_and_place_coordinates(
    obj_name: str, destination: Tuple[float, float, float]
) -> Response:
    obj_name = obj_name.lower()

    try:
        position = [float(i) for i in destination]
    except ValueError:
        return Response(
            status="error",
            message="Destination coordinates must have exactly 3 real numbers (x,y,z)",
        )

    with simulated_robot:
        try:
            obj = BelieveObject(names=[obj_name]).resolve()
            obj_pose_initial = obj.pose
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
        NavigateActionDescription(target_location=pickup_pose).resolve().perform()

        grasped = False
        for approach_direction in [
            Grasp.FRONT,
            Grasp.BACK,
            Grasp.RIGHT,
            Grasp.LEFT,
        ]:
            grasp = GraspDescription(
                approach_direction,
                vertical_alignment=(
                    Grasp.TOP if issubclass(obj.obj_type, Spoon) else None
                ),
                rotate_gripper=False,
            )
            try:
                PickUpActionDescription(
                    object_designator=obj, arm=pickup_arm, grasp_description=grasp
                ).resolve().perform()
                grasped = True
            except (ObjectNotGraspedError, IKError):
                pass

    if not grasped:
        with simulated_robot:
            ParkArmsActionDescription([Arms.BOTH]).resolve().perform()
            NavigateActionDescription(
                target_location=ROBOT_HOME_POSE
            ).resolve().perform()
            MoveTorsoActionDescription([TorsoState.LOW]).resolve().perform()

        return Response(
            status="error", message=f"The object '{obj_name}' could not be grasped"
        )

    with simulated_robot:
        try:
            place_location = CostmapLocation(
                target=Pose(position),
                reachable_for=robot,
                reachable_arm=pickup_arm,
                object_in_hand=obj,
            ).resolve()
        except StopIteration:
            place_location = None

    if place_location is None:
        with simulated_robot:
            PlaceActionDescription(
                obj, target_location=obj_pose_initial, arm=pickup_arm
            ).resolve().perform()
            ParkArmsActionDescription([Arms.BOTH]).resolve().perform()
            NavigateActionDescription(
                target_location=ROBOT_HOME_POSE
            ).resolve().perform()
            MoveTorsoActionDescription([TorsoState.LOW]).resolve().perform()

        return Response(
            status="error",
            message="The location to place the object cannot be resolved",
        )

    with simulated_robot:
        ParkArmsActionDescription([Arms.BOTH]).resolve().perform()
        NavigateActionDescription(target_location=place_location).resolve().perform()
        PlaceActionDescription(
            obj, target_location=Pose(position), arm=pickup_arm
        ).resolve().perform()
        ParkArmsActionDescription([Arms.BOTH]).resolve().perform()
        NavigateActionDescription(target_location=ROBOT_HOME_POSE).resolve().perform()
        MoveTorsoActionDescription([TorsoState.LOW]).resolve().perform()

    return Response(
        status="success",
        message=f"Object '{obj_name}' successfully moved to '{position}'",
    )


def pick_and_place_location(obj_name: str, destination: Location) -> Response:
    obj_name = obj_name.lower()

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
        destination_location = SemanticCostmapLocation(
            link_name=LOCATIONS[destination], part_of=env, for_object=obj
        ).resolve()

    return pick_and_place_coordinates(
        obj_name,
        [
            destination_location.pose.position.x,
            destination_location.pose.position.y,
            destination_location.pose.position.z,
        ],
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

        try:
            obj = world.get_object_by_id(idx)
        except IndexError:
            obj = None

        if obj is not None:
            visible_objects[int(idx)] = {
                "name": obj.name,
                "type": str(type(obj).__name__),
                "pixel_count": int(pixel_count),
            }

    return Response(
        status="success",
        message="Getting objects in robot view successful",
        payload=visible_objects,
    )


def get_distance_between_objects(
    source_object_name: Optional[str] = None,
    target_object_names: Optional[Iterable[str]] = None,
    exclude_object_names: Iterable[str] = ("floor", "kitchen"),
) -> Response:
    source_name = source_object_name.lower() if source_object_name is not None else None
    target_names = (
        [i.lower() for i in target_object_names]
        if target_object_names is not None
        else None
    )
    exclude_names = [i.lower() for i in exclude_object_names]
    filtered_objects = [i for i in world.objects if i.name not in exclude_names]

    if target_names is not None:
        filtered_objects = [i for i in filtered_objects if i.name in target_names]

    if source_name is not None:
        with simulated_robot:
            try:
                source = BelieveObject(names=[source_name]).resolve()
            except StopIteration:
                source = None
        if source is None:
            response = Response(
                status="error", message=f"Object {source_name} not in environment"
            )
        else:
            distances = {}
            source_pos = source.get_position()
            for obj in filtered_objects:
                if obj.name == source_name:
                    continue
                obj_pos = obj.get_position()
                distances[obj.name] = np.sqrt(
                    (source_pos.x - obj_pos.x) ** 2
                    + (source_pos.y - obj_pos.y) ** 2
                    + (source_pos.z - obj_pos.z) ** 2
                )
            response = Response(
                status="success",
                message="Distance calculation is successful",
                payload=distances,
            )
    else:
        distances = {}
        for obj1, obj2 in itertools.combinations(filtered_objects, 2):
            pos1 = obj1.get_position()
            pos2 = obj2.get_position()
            if obj1.name not in distances:
                distances[obj1.name] = {}
            distances[obj1.name][obj2.name] = np.sqrt(
                (pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2 + (pos1.z - pos2.z) ** 2
            )
        response = Response(
            status="success",
            message="Distance calculation is successful",
            payload=distances,
        )

    return response


def exit_simulation() -> Response:
    if world is not None:
        world.exit()
    return Response(status="success", message="Simulation exit successful")
