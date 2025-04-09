import numpy as np
from pycram.worlds.bullet_world import BulletWorld
from pycram.world_concepts.world_object import Object
from pycram.datastructures.enums import ObjectType, WorldMode
from pycram.datastructures.pose import Pose
from pycram.robot_description import RobotDescription

def get_camera_images(world, robot, target_distance=2.0):
    """
    Retrieve camera images from the robot's perspective.
    
    Args:
        world (BulletWorld): The simulation world
        robot (Object): The robot object
        target_distance (float, optional): Distance in front of the camera to look. Defaults to 2.0 meters.
    
    Returns:
        dict: A dictionary containing color image, depth image, and segmentation mask
    """
    # Get camera link name from robot description
    camera_link_name = RobotDescription.current_robot_description.get_camera_link()
    
    # Get camera pose from robot
    camera_pose = robot.get_link_pose(camera_link_name)
    
    # Get camera front-facing axis
    camera_axis = RobotDescription.current_robot_description.get_default_camera().front_facing_axis
    
    # Define target point (2 meters in front of the camera)
    target_point = Pose(list(np.array(camera_pose.position_as_list()) + np.array(camera_axis) * target_distance))
    
    # Get images
    # Returns a list with [color_image, depth_image, segmentation_mask]
    images = world.get_images_for_target(target_point, camera_pose)
    
    return {
        "color_image": images[0],
        "depth_image": images[1],
        "segmentation_mask": images[2]
    } 