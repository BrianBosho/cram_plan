"""
PR2 Camera Utilities for Kitchen Environment (Minimal Version)

This module provides basic functions to access PR2 robot camera information
and generate simulated camera images.

References:
- pycram/robot_description.py: Contains CameraDescription class implementation
- pycram/utils.py: Contains camera utility functions
"""

import numpy as np
from typing import List, Dict, Tuple, Union
from pycram.robot_description import RobotDescriptionManager, CameraDescription
from pycram.datastructures.pose import Pose
import pycram.utils as utils
import matplotlib.pyplot as plt


def list_pr2_cameras() -> Dict[str, Dict[str, Union[str, float]]]:
    """
    List all cameras available on the PR2 robot with their properties.
    
    Returns:
        Dict: Dictionary of camera information with camera names as keys and properties as values.
    
    Example:
        >>> cameras = list_pr2_cameras()
        >>> for name, props in cameras.items():
        ...     print(f"Camera: {name}, Link: {props['link_name']}")
    """
    rdm = RobotDescriptionManager()
    pr2 = rdm.get_active_description()  # Should be PR2
    
    camera_info = {}
    for camera_name, camera in pr2.camera_descriptions.items():
        camera_info[camera_name] = {
            'link_name': camera.link_name,
            'horizontal_fov': camera.horizontal_angle,
            'vertical_fov': camera.vertical_angle,
            'min_height': camera.minimal_height,
            'max_height': camera.maximal_height,
            'front_facing_axis': camera.front_facing_axis
        }
    
    return camera_info


def generate_simulated_camera_image(camera_name: str = None, 
                                   resolution: int = 128, 
                                   min_distance: float = 0.1,
                                   max_distance: float = 3.0,
                                   visualize: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate a simulated camera image. This function doesn't use actual camera data
    but creates placeholder images that match the expected format.
    
    Args:
        camera_name: Name of the camera to use (optional)
        resolution: Image resolution in pixels (square image)
        min_distance: Minimum viewing distance in meters
        max_distance: Maximum viewing distance in meters
        visualize: Whether to display the images immediately
    
    Returns:
        Tuple containing:
            - color_depth_image: RGB visualization of depth (np.ndarray, uint8)
            - depth_image: Raw depth values in meters (np.ndarray, float)
            - segmentation_mask: Object IDs for each pixel (np.ndarray, int)
    """
    rdm = RobotDescriptionManager()
    pr2 = rdm.get_active_description()
    
    # Use the first available camera if none specified
    if camera_name is None:
        camera_name = next(iter(pr2.camera_descriptions.keys()))
    elif camera_name not in pr2.camera_descriptions:
        print(f"Warning: Camera '{camera_name}' not found. Using {next(iter(pr2.camera_descriptions.keys()))} instead.")
        camera_name = next(iter(pr2.camera_descriptions.keys()))
    
    # For demonstration purposes, creating dummy data:
    distances = np.random.uniform(min_distance, max_distance, resolution * resolution)
    object_ids = np.random.randint(-1, 10, resolution * resolution)
    
    # Construct images from simulated data
    # These functions we know exist from the search results
    segmentation_mask = utils.construct_segmentation_mask_from_ray_test_object_ids(object_ids, resolution)
    depth_image = utils.construct_depth_image_from_ray_test_distances(distances, resolution) + min_distance
    color_depth_image = utils.construct_color_image_from_depth_image(depth_image)
    
    # Add some interesting patterns to make the images look more realistic
    # Create a simple scene with a few objects
    for i in range(3):  # Add a few "objects"
        center_x = np.random.randint(int(resolution*0.2), int(resolution*0.8))
        center_y = np.random.randint(int(resolution*0.2), int(resolution*0.8))
        radius = np.random.randint(10, 30)
        object_id = i + 1
        object_distance = np.random.uniform(min_distance + 0.1, max_distance - 0.1)
        
        # Create a circular object
        for x in range(max(0, center_x - radius), min(resolution, center_x + radius)):
            for y in range(max(0, center_y - radius), min(resolution, center_y + radius)):
                if (x - center_x)**2 + (y - center_y)**2 <= radius**2:
                    segmentation_mask[y, x] = object_id
                    depth_image[y, x] = object_distance
    
    # Regenerate the color image with the updated depth
    color_depth_image = utils.construct_color_image_from_depth_image(depth_image)
    
    # Visualize if requested
    if visualize:
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 3, 1)
        plt.imshow(color_depth_image)
        plt.title("Color Depth Image")
        plt.axis('off')
        
        plt.subplot(1, 3, 2)
        plt.imshow(depth_image, cmap='viridis')
        plt.title("Depth Image")
        plt.colorbar(label='Distance (m)')
        plt.axis('off')
        
        plt.subplot(1, 3, 3)
        plt.imshow(segmentation_mask, cmap='tab20')
        plt.title("Segmentation Mask")
        plt.colorbar(label='Object ID')
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
    
    return color_depth_image, depth_image, segmentation_mask


def find_objects_in_image(depth_image: np.ndarray, 
                         segmentation_mask: np.ndarray,
                         min_object_size: int = 50) -> List[Dict]:
    """
    Identify and analyze objects in the depth image and segmentation mask.
    
    Args:
        depth_image: Raw depth values (np.ndarray)
        segmentation_mask: Object IDs for each pixel (np.ndarray)
        min_object_size: Minimum pixel size to consider an object valid
    
    Returns:
        List of dictionaries, each containing information about one object
    """
    objects_info = []
    unique_ids = np.unique(segmentation_mask)
    
    for obj_id in unique_ids:
        if obj_id <= 0:  # Skip background (-1) or empty space (0)
            continue
            
        # Create mask for this object
        obj_mask = segmentation_mask == obj_id
        obj_size = np.sum(obj_mask)
        
        # Skip if object is too small
        if obj_size < min_object_size:
            continue
            
        # Extract depth values for this object
        obj_depth = depth_image[obj_mask]
        
        # Get row, col coordinates of all pixels belonging to object
        obj_rows, obj_cols = np.where(obj_mask)
        
        # Calculate center as mean position
        center_row = np.mean(obj_rows)
        center_col = np.mean(obj_cols)
        
        # Create object information dictionary
        object_info = {
            'id': int(obj_id),
            'center': [float(center_row), float(center_col)],
            'min_depth': float(np.min(obj_depth)),
            'mean_depth': float(np.mean(obj_depth)),
            'size': int(obj_size)
        }
        
        objects_info.append(object_info)
    
    # Sort objects by minimum depth (closest first)
    objects_info.sort(key=lambda x: x['min_depth'])
    
    return objects_info


def get_closest_object(visualize: bool = False) -> Dict:
    """
    Get information about the closest object in a simulated camera image.
    
    Args:
        visualize: Whether to visualize the camera image with the closest object highlighted
    
    Returns:
        Dictionary containing information about the closest object
    
    Raises:
        ValueError: If no objects are detected in the camera view
    """
    # Get camera image (simulated)
    color_img, depth_img, seg_mask = generate_simulated_camera_image(visualize=False)
    
    # Find all objects in the image
    objects = find_objects_in_image(depth_img, seg_mask)
    
    if not objects:
        raise ValueError("No objects detected in camera view")
    
    # Objects are already sorted by distance (closest first)
    closest_object = objects[0]
    
    # Create result dictionary with simplified information
    result = {
        'id': closest_object['id'],
        'distance': closest_object['min_depth'],
        'center': closest_object['center'],
        'size': closest_object['size']
    }
    
    # Visualize if requested
    if visualize:
        plt.figure(figsize=(10, 5))
        
        # Show color image with object marked
        plt.subplot(1, 2, 1)
        plt.imshow(color_img)
        row, col = closest_object['center']
        plt.plot(col, row, 'ro', markersize=10)  # Mark center with red circle
        plt.title(f"Closest Object (ID: {result['id']})")
        
        # Show depth image with object marked
        plt.subplot(1, 2, 2)
        plt.imshow(depth_img, cmap='viridis')
        plt.colorbar(label='Distance (m)')
        plt.plot(col, row, 'ro', markersize=10)
        plt.title(f"Distance: {result['distance']:.2f}m")
        
        plt.tight_layout()
        plt.show()
    
    return result