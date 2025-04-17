import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from pycram.robot_description import RobotDescription
from pycram.datastructures.enums import Frame
from pycram.datastructures.pose import Pose
from pycram.world_concepts.world_object import Object
from pycram.world_reasoning import visible, occluding, get_visible_objects

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import itertools
from pycram.world_concepts.world_object import Object
from pycram.datastructures.pose import Pose

from pycram.process_module import simulated_robot
from pycram.designators.motion_designator import *
# Add a global world variable and initialization function
world = None

def calculate_object_distances(source_object=None, target_objects=None, exclude_types=None):
    """
    Calculate distances between objects in the world.
    
    Parameters:
    -----------
    source_object : str or None
        Name of source object. If None, will calculate distances between all pairs.
    target_objects : list or None
        List of target object names. If None, will use all objects.
    exclude_types : list or None
        List of object types to exclude (like 'floor', 'wall', etc.)
        
    Returns:
    --------
    dict
        Dictionary of distances between objects
    """
    global world
    if world is None:
        print("Cannot calculate distances because the world is not initialized.")
        return {}
    
    # Default exclusion list if not provided
    if exclude_types is None:
        exclude_types = ['floor', 'wall', 'ceiling', 'ground']
    
    # Get all objects or filter by provided names
    all_objects = world.objects
    filtered_objects = []
    
    for obj in all_objects:
        # Skip excluded types
        if any(exclude_type in obj.name.lower() for exclude_type in exclude_types):
            continue
        filtered_objects.append(obj)
    
    # If target objects specified, filter to only those
    if target_objects:
        filtered_objects = [obj for obj in filtered_objects if obj.name in target_objects]
    
    # If source object specified, only measure from that object
    if source_object:
        source = world.get_object_by_name(source_object)
        if source is None:
            print(f"Source object '{source_object}' not found.")
            return {}
        
        distances = {}
        source_pos = source.get_position()
        
        for obj in filtered_objects:
            if obj.name == source_object:
                continue
                
            obj_pos = obj.get_position()
            dist = np.sqrt((source_pos.x - obj_pos.x)**2 + 
                          (source_pos.y - obj_pos.y)**2 + 
                          (source_pos.z - obj_pos.z)**2)
            
            distances[obj.name] = dist
        
        return distances
    
    # Otherwise calculate all pairwise distances
    else:
        distances = {}
        
        # Get all unique pairs of objects
        for obj1, obj2 in itertools.combinations(filtered_objects, 2):
            pos1 = obj1.get_position()
            pos2 = obj2.get_position()
            
            dist = np.sqrt((pos1.x - pos2.x)**2 + 
                          (pos1.y - pos2.y)**2 + 
                          (pos1.z - pos2.z)**2)
            
            key = f"{obj1.name}-to-{obj2.name}"
            distances[key] = dist
        
        return distances


def display_object_distances(distances, top_n=None, sort=True):
    """
    Display the calculated distances in a formatted table.
    
    Parameters:
    -----------
    distances : dict
        Dictionary of distances between objects
    top_n : int or None
        Number of closest distances to display. If None, displays all.
    sort : bool
        Whether to sort distances by value (default: True)
    """
    if not distances:
        print("No distances to display.")
        return
    
    if sort:
        # Sort distances by value (closest first)
        sorted_distances = sorted(distances.items(), key=lambda x: x[1])
    else:
        sorted_distances = list(distances.items())
    
    # Limit to top_n if specified
    if top_n is not None and top_n > 0:
        sorted_distances = sorted_distances[:top_n]
    
    # Print header
    print("\n----- Object Distances -----")
    print(f"{'Objects':<30} {'Distance (m)':<15}")
    print("-" * 45)
    
    # Print distances
    for key, dist in sorted_distances:
        print(f"{key:<30} {dist:<15.3f}")


def visualize_object_distances_3d(source_object=None, exclude_types=None, max_objects=10, 
                                  show_labels=True, show_distances=True):
    """
    Create a 3D visualization of objects in the world with distances.
    
    Parameters:
    -----------
    source_object : str or None
        Name of source object to calculate distances from. If None, just shows all objects.
    exclude_types : list or None
        List of object types to exclude
    max_objects : int
        Maximum number of objects to include in visualization
    show_labels : bool
        Whether to show object labels
    show_distances : bool
        Whether to show distance labels on lines
    """
    global world
    if world is None:
        print("Cannot visualize because the world is not initialized.")
        return
    
    # Default exclusion list if not provided
    if exclude_types is None:
        exclude_types = ['floor', 'wall', 'ceiling', 'ground']
    
    # Get all objects excluding certain types
    all_objects = world.objects
    filtered_objects = []
    
    for obj in all_objects:
        # Skip excluded types
        if any(exclude_type in obj.name.lower() for exclude_type in exclude_types):
            continue
        filtered_objects.append(obj)
    
    # Limit to max_objects (excluding source if specified)
    if source_object:
        source = world.get_object_by_name(source_object)
        if source is None:
            print(f"Source object '{source_object}' not found.")
            return
        
        # Ensure source object is included
        if source not in filtered_objects:
            filtered_objects.append(source)
        
        # Limit other objects if needed
        other_objects = [obj for obj in filtered_objects if obj != source]
        if len(other_objects) > max_objects-1:
            other_objects = other_objects[:max_objects-1]
        
        filtered_objects = [source] + other_objects
    
    elif len(filtered_objects) > max_objects:
        filtered_objects = filtered_objects[:max_objects]
    
    # Create 3D plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Collect positions
    positions = []
    labels = []
    
    for obj in filtered_objects:
        pos = obj.get_position()
        positions.append([pos.x, pos.y, pos.z])
        labels.append(obj.name)
    
    # Convert to numpy array for easier manipulation
    positions = np.array(positions)
    
    # Plot objects as points
    ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], s=100, c='blue', marker='o')
    
    # Add labels if requested
    if show_labels:
        for i, label in enumerate(labels):
            ax.text(positions[i, 0], positions[i, 1], positions[i, 2], label, size=10, color='black')
    
    # Draw lines and distances if source_object is specified
    if source_object and show_distances and source in filtered_objects:
        source_idx = filtered_objects.index(source)
        source_pos = positions[source_idx]
        
        for i, obj in enumerate(filtered_objects):
            if i == source_idx:
                continue
            
            # Draw line from source to this object
            obj_pos = positions[i]
            ax.plot([source_pos[0], obj_pos[0]], 
                    [source_pos[1], obj_pos[1]], 
                    [source_pos[2], obj_pos[2]], 'r--', alpha=0.7)
            
            # Calculate and show distance
            dist = np.sqrt(sum((source_pos - obj_pos)**2))
            
            # Find midpoint for distance label
            mid_point = (source_pos + obj_pos) / 2
            ax.text(mid_point[0], mid_point[1], mid_point[2], f"{dist:.2f}m", size=8, color='red')
    
    # Set axis labels and title
    ax.set_xlabel('X (meters)')
    ax.set_ylabel('Y (meters)')
    ax.set_zlabel('Z (meters)')
    
    if source_object:
        ax.set_title(f"Object Distances from {source_object}")
    else:
        ax.set_title("3D Object Positions")
    
    # Set equal aspect ratio
    max_range = np.array([positions[:, 0].max() - positions[:, 0].min(),
                          positions[:, 1].max() - positions[:, 1].min(),
                          positions[:, 2].max() - positions[:, 2].min()]).max() / 2.0
    
    mid_x = (positions[:, 0].max() + positions[:, 0].min()) * 0.5
    mid_y = (positions[:, 1].max() + positions[:, 1].min()) * 0.5
    mid_z = (positions[:, 2].max() + positions[:, 2].min()) * 0.5
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    plt.tight_layout()
    plt.show()


def spawn_multiple_objects(objects_to_spawn=None):
    """
    Spawn multiple objects in the world for distance testing.
    
    Parameters:
    -----------
    objects_to_spawn : list or None
        List of dictionaries with object specifications.
        Each dict should have keys: 'name', 'type', 'pose', and optionally 'color'
        If None, will spawn a default set of objects.
    
    Returns:
    --------
    list
        List of spawned objects
    """
    global world
    if world is None:
        print("Cannot spawn objects because the world is not initialized.")
        return []
    
    # Default set of objects if none provided
    if objects_to_spawn is None:
        objects_to_spawn = [
            {
                'name': 'bowl',
                'type': 'bowl',
                'coordinates': [1.3, 0.8, 0.95],
                'color': 'blue'
            },
            {
                'name': 'cup',
                'type': 'cup',
                'coordinates': [1.5, 0.9, 0.95],
                'color': 'red'
            },
            {
                'name': 'apple',
                'type': 'apple',
                'coordinates': [1.2, 1.2, 0.95],
                'color': 'green'
            },
            {
                'name': 'banana',
                'type': 'banana',
                'coordinates': [1.0, 0.7, 0.95],
                'color': 'yellow'
            }
        ]
    
    spawned_objects = []
    
    # Import required modules
    from pycram.datastructures.enums import ObjectType, Frame
    from pycram.datastructures.pose import Pose
    
    # Spawn each object using the world's create_object method
    for obj_spec in objects_to_spawn:
        try:
            # Get object parameters
            obj_name = obj_spec.get('name', obj_spec.get('type', 'object'))
            obj_type = obj_spec.get('type', 'generic').lower()
            coordinates = obj_spec.get('coordinates', [1.0, 1.0, 1.0])
            color = obj_spec.get('color', None)
            
            # Parse coordinates
            try:
                pose_vals = [float(val) for val in coordinates]
                if len(pose_vals) != 3:
                    print(f"Error spawning {obj_name}: Coordinates must have exactly 3 values (x,y,z)")
                    continue
            except Exception as e:
                print(f"Error spawning {obj_name}: Error parsing coordinates: {str(e)}")
                continue
            
            # Create a pose object
            pose = Pose(pose_vals, frame=Frame.Map.value)
            
            # Map object type string to ObjectType enum (similar to add_objects in interactive_sim)
            obj_type_enum = None
            for type_enum in ObjectType:
                if obj_type in type_enum.name.lower():
                    obj_type_enum = type_enum
                    break
            
            if obj_type_enum is None:
                obj_type_enum = ObjectType.GENERIC
            
            # Create the object using world's create_object method
            obj = world.create_object(
                obj_type_enum, 
                name=obj_name,
                pose=pose,
                color=color
            )
            
            print(f"Spawned {obj_name} at position {pose_vals} with color {color if color else 'default'}")
            spawned_objects.append(obj)
            
        except Exception as e:
            print(f"Error spawning {obj_spec.get('name', 'object')}: {str(e)}")
    
    return spawned_objects


def initialize(world_instance):
    """
    Initialize the camera utilities with a world instance.
    
    Parameters:
    -----------
    world_instance : World
        The world instance to use for camera operations
    """
    global world
    world = world_instance
    print("Camera utilities initialized with world instance.")

# 1. DEPTH MAP VISUALIZATION
def visualize_depth_map(display=True, save_path=None, colormap='viridis', normalize=True):
    """
    Visualize the depth map from the robot's camera with color mapping.
    
    Based on world.get_images_for_target() which returns depth information at index 1.
    
    Parameters:
    -----------
    display : bool
        Whether to display the depth map (default: True)
    save_path : str or None
        Path to save the depth map, if None the image is not saved (default: None)
    colormap : str
        Matplotlib colormap to use for visualization (default: 'viridis')
    normalize : bool
        Whether to normalize depth values for better visualization (default: True)
        
    Returns:
    --------
    numpy.ndarray
        The depth image data
    """
    global world
    if world is None:
        print("Cannot visualize depth map because the world is not initialized.")
        return None
    
    # Get the camera configuration - same setup as in capture_camera_image
    robot = world.robot
    camera_link_name = RobotDescription.current_robot_description.get_camera_link()
    camera_link = robot.get_link(camera_link_name)
    camera_pose = camera_link.pose
    camera_axis = RobotDescription.current_robot_description.get_default_camera().front_facing_axis
    
    # Create a target point
    target = np.array(camera_axis) * 2.0
    target_pose = Pose(target, frame=camera_link.tf_frame)
    target_pose = robot.local_transformer.transform_pose(target_pose, Frame.Map.value)
    
    # Get the depth image (index 1 from get_images_for_target)
    images = world.get_images_for_target(target_pose, camera_pose)
    depth_image = images[1]
    
    # Visualize
    if display or save_path:
        plt.figure(figsize=(10, 8))
        
        # For better visualization, we can normalize and use a colormap
        if normalize:
            # Handle potential division by zero
            depth_min = np.min(depth_image) if np.min(depth_image) != np.max(depth_image) else 0
            depth_max = np.max(depth_image) if np.min(depth_image) != np.max(depth_image) else 1
            normalized_depth = (depth_image - depth_min) / (depth_max - depth_min)
            plt.imshow(normalized_depth, cmap=colormap)
        else:
            plt.imshow(depth_image, cmap=colormap)
            
        plt.colorbar(label='Depth')
        plt.title('Depth Map from Robot Camera')
        plt.axis('off')
        
        if save_path:
            plt.savefig(save_path)
        
        if display:
            plt.show()
        else:
            plt.close()
    
    return depth_image


# 2. OBJECT IDENTIFICATION IN SCENE
def identify_objects_in_view(display_segmentation=True, min_pixel_count=50):
    """
    Identify and list all objects visible in the camera view.
    
    Uses the segmentation mask from get_images_for_target() and references 
    world_reasoning.py's functions for object identification.
    
    Parameters:
    -----------
    display_segmentation : bool
        Whether to display the segmentation mask with labels (default: True)
    min_pixel_count : int
        Minimum number of pixels required to consider an object visible (default: 50)
        
    Returns:
    --------
    dict
        Dictionary mapping object IDs to visible objects, with pixel counts
    """
    global world
    if world is None:
        print("Cannot identify objects because the world is not initialized.")
        return None
    
    # Get the camera configuration
    robot = world.robot
    camera_link_name = RobotDescription.current_robot_description.get_camera_link()
    camera_link = robot.get_link(camera_link_name)
    camera_pose = camera_link.pose
    camera_axis = RobotDescription.current_robot_description.get_default_camera().front_facing_axis
    
    # Create a target point
    target = np.array(camera_axis) * 2.0
    target_pose = Pose(target, frame=camera_link.tf_frame)
    target_pose = robot.local_transformer.transform_pose(target_pose, Frame.Map.value)
    
    # Get the segmentation mask (index 2)
    images = world.get_images_for_target(target_pose, camera_pose)
    segmentation_mask = images[2]
    rgb_image = images[0]
    
    # Find unique object IDs in the segmentation mask
    unique_ids = np.unique(segmentation_mask)
    
    # Map IDs to objects and count pixels
    visible_objects = {}
    
    # Create colormap for visualization
    colors = cm.get_cmap('tab10', len(unique_ids))
    
    for idx, obj_id in enumerate(unique_ids):
        if obj_id == 0:  # Usually 0 is background
            continue
            
        # Count pixels for this object
        pixel_count = np.sum(segmentation_mask == obj_id)
        
        if pixel_count >= min_pixel_count:
            # Get the actual object from its ID
            try:
                obj = world.get_object_by_id(obj_id)
                visible_objects[obj_id] = {
                    'object': obj,
                    'name': obj.name,
                    'pixel_count': pixel_count
                }
            except (IndexError, Exception) as e:
                # Object with this ID doesn't exist in the world
                print(f"Object ID {obj_id} found in segmentation mask but not in world objects.")
                continue
    
    # Display segmentation mask with labels if requested
    if display_segmentation and visible_objects:
        plt.figure(figsize=(15, 10))
        
        # Create a subplot layout: RGB image on left, segmentation on right
        plt.subplot(1, 2, 1)
        plt.imshow(rgb_image)
        plt.title('RGB Camera View')
        plt.axis('off')
        
        plt.subplot(1, 2, 2)
        # Create a colored segmentation mask for visualization
        colored_mask = np.zeros((*segmentation_mask.shape, 3))
        
        for i, obj_id in enumerate(visible_objects.keys()):
            # Set pixels for this object to its assigned color
            mask = segmentation_mask == obj_id
            colored_mask[mask] = colors(i % 10)[:3]  # Use modulo to cycle through colors
        
        plt.imshow(colored_mask)
        plt.title('Object Segmentation')
        plt.axis('off')
        
        # Add legend
        legend_elements = []
        for i, (obj_id, data) in enumerate(visible_objects.items()):
            from matplotlib.patches import Patch
            legend_elements.append(
                Patch(facecolor=colors(i % 10)[:3], 
                      label=f"{data['name']} ({data['pixel_count']} px)")
            )
        
        plt.figlegend(handles=legend_elements, 
                     title="Visible Objects", 
                     loc="center right")
        
        plt.tight_layout()
        plt.show()
    
    return visible_objects


# 3. CHECKING OBJECT VISIBILITY
def check_object_visibility(object_name, threshold=0.8, plot_result=True):
    """
    Check if a specific object is visible from the current camera position.
    
    Uses the visible() function from world_reasoning.py to determine visibility.
    
    Parameters:
    -----------
    object_name : str
        Name of the object to check visibility for
    threshold : float
        Minimum percentage of the object that must be visible (0.0-1.0, default: 0.8)
    plot_result : bool
        Whether to plot the segmentation mask (default: True)
        
    Returns:
    --------
    bool
        True if the object is visible according to the threshold, False otherwise
    """
    global world
    if world is None:
        print("Cannot check visibility because the world is not initialized.")
        return False
    
    # Find the object
    obj = world.get_object_by_name(object_name)
    if obj is None:
        print(f"Object '{object_name}' not found in the world.")
        return False
    
    # Get the camera configuration
    robot = world.robot
    camera_link_name = RobotDescription.current_robot_description.get_camera_link()
    camera_link = robot.get_link(camera_link_name)
    camera_pose = camera_link.pose
    
    # Get the camera's front facing axis
    camera_axis = RobotDescription.current_robot_description.get_default_camera().front_facing_axis
    
    # Check if object is visible using the world_reasoning.visible function
    # Reference: visible() function around line 409 in your provided code
    is_visible = visible(obj, camera_pose, front_facing_axis=camera_axis, 
                         threshold=threshold, plot_segmentation_mask=plot_result)
    
    if is_visible:
        print(f"Object '{object_name}' is visible from the current camera position.")
    else:
        print(f"Object '{object_name}' is NOT visible (or below threshold) from the current camera position.")
    
    return is_visible


# 4. FINDING OCCLUDED OBJECTS
def find_occluding_objects(object_name, plot_result=True):
    """
    Find all objects that are occluding the specified object.
    
    Uses the occluding() function from world_reasoning.py.
    
    Parameters:
    -----------
    object_name : str
        Name of the object to check for occlusion
    plot_result : bool
        Whether to plot the segmentation mask (default: True)
        
    Returns:
    --------
    list
        List of objects that are occluding the target object
    """
    global world
    if world is None:
        print("Cannot check occlusions because the world is not initialized.")
        return []
    
    # Find the object
    obj = world.get_object_by_name(object_name)
    if obj is None:
        print(f"Object '{object_name}' not found in the world.")
        return []
    
    # Get the camera configuration
    robot = world.robot
    camera_link_name = RobotDescription.current_robot_description.get_camera_link()
    camera_link = robot.get_link(camera_link_name)
    camera_pose = camera_link.pose
    
    # Get the camera's front facing axis
    camera_axis = RobotDescription.current_robot_description.get_default_camera().front_facing_axis
    
    # Find occluding objects using the occluding() function
    # Reference: occluding() function around line 456 in your provided code
    occluding_objects = occluding(obj, camera_pose, front_facing_axis=camera_axis, 
                                 plot_segmentation_mask=plot_result)
    
    if occluding_objects:
        print(f"Object '{object_name}' is occluded by: {[o.name for o in occluding_objects]}")
    else:
        print(f"Object '{object_name}' is not occluded by any objects.")
    
    return occluding_objects


# 5. DISTANCE ESTIMATION FROM DEPTH IMAGE
def estimate_distances_to_objects(max_objects=5):
    """
    Estimate distances to the visible objects using depth information.
    
    Combines segmentation mask with depth image to calculate average distances.
    
    Parameters:
    -----------
    max_objects : int
        Maximum number of objects to report distances for (default: 5)
        
    Returns:
    --------
    dict
        Dictionary mapping object names to their estimated distances
    """
    global world
    if world is None:
        print("Cannot estimate distances because the world is not initialized.")
        return {}
    
    # Get the camera configuration
    robot = world.robot
    camera_link_name = RobotDescription.current_robot_description.get_camera_link()
    camera_link = robot.get_link(camera_link_name)
    camera_pose = camera_link.pose
    camera_axis = RobotDescription.current_robot_description.get_default_camera().front_facing_axis
    
    # Create a target point
    target = np.array(camera_axis) * 2.0
    target_pose = Pose(target, frame=camera_link.tf_frame)
    target_pose = robot.local_transformer.transform_pose(target_pose, Frame.Map.value)
    
    # Get the depth image and segmentation mask
    images = world.get_images_for_target(target_pose, camera_pose)
    depth_image = images[1]
    segmentation_mask = images[2]
    
    # Find unique object IDs in the segmentation mask
    unique_ids = np.unique(segmentation_mask)
    
    # Calculate average depth for each object
    distances = {}
    
    for obj_id in unique_ids:
        if obj_id == 0:  # Skip background
            continue
            
        # Create a mask for this object
        mask = segmentation_mask == obj_id
        
        # If the object has enough pixels visible
        if np.sum(mask) > 50:
            # Get the object
            obj = world.get_object_by_id(obj_id)
            if obj is not None:
                # Calculate average depth for this object's pixels
                obj_depth = depth_image[mask]
                avg_distance = np.mean(obj_depth)
                
                distances[obj.name] = avg_distance
    
    # Sort by distance and limit to max_objects
    sorted_distances = dict(sorted(distances.items(), key=lambda x: x[1])[:max_objects])
    
    # Print the distances
    print("Estimated distances to objects:")
    for name, dist in sorted_distances.items():
        print(f"  {name}: {dist:.2f} units")
    
    return sorted_distances


# 6. CAMERA POSITION MANIPULATION
def look_at_object(object_name, distance=2.0, elevation_angle=0.0, azimuth_angle=0.0, display_result=True):
    """
    Simulate moving the camera to look at a specific object from a given viewpoint.
    
    Parameters:
    -----------
    object_name : str
        Name of the object to look at
    distance : float
        Distance from the object in meters (default: 2.0)
    elevation_angle : float
        Vertical angle in degrees (0=level, 90=above, -90=below) (default: 0.0)
    azimuth_angle : float
        Horizontal angle in degrees (0=front, 90=right, 180=behind) (default: 0.0)
    display_result : bool
        Whether to display the resulting camera view (default: True)
        
    Returns:
    --------
    tuple
        (rgb_image, depth_image, segmentation_mask) - The images from the new viewpoint
    """
    global world
    if world is None:
        print("Cannot look at object because the world is not initialized.")
        return None
    
    # Find the object
    obj = world.get_object_by_name(object_name)
    if obj is None:
        print(f"Object '{object_name}' not found in the world.")
        return None
    
    # Get object position
    obj_position = obj.get_position()
    
    # Convert angles to radians
    elev_rad = np.radians(elevation_angle)
    azim_rad = np.radians(azimuth_angle)
    
    # Calculate camera position in spherical coordinates relative to the object
    x = obj_position.x + distance * np.cos(elev_rad) * np.cos(azim_rad)
    y = obj_position.y + distance * np.cos(elev_rad) * np.sin(azim_rad)
    z = obj_position.z + distance * np.sin(elev_rad)
    
    # Create camera pose looking at the object
    camera_position = [x, y, z]
    
    # Compute direction vector from camera to object
    direction = [
        obj_position.x - x,
        obj_position.y - y,
        obj_position.z - z
    ]
    
    # Normalize the direction vector
    direction_length = np.sqrt(sum(d*d for d in direction))
    if direction_length > 0:
        direction = [d / direction_length for d in direction]
    
    # Create camera pose
    camera_pose = Pose(camera_position)
    
    # Create a target pose based on the object position
    target_pose = Pose([obj_position.x, obj_position.y, obj_position.z])
    
    # Get images from this viewpoint
    images = world.get_images_for_target(target_pose, camera_pose)
    rgb_image, depth_image, segmentation_mask = images[:3]
    
    if display_result:
        plt.figure(figsize=(12, 8))
        plt.subplot(1, 2, 1)
        plt.imshow(rgb_image)
        plt.title(f'View of {object_name} from custom position')
        plt.axis('off')
        
        # Display depth as well
        plt.subplot(1, 2, 2)
        depth_min = np.min(depth_image) if np.min(depth_image) != np.max(depth_image) else 0
        depth_max = np.max(depth_image) if np.min(depth_image) != np.max(depth_image) else 1
        normalized_depth = (depth_image - depth_min) / (depth_max - depth_min)
        plt.imshow(normalized_depth, cmap='viridis')
        plt.title('Depth Map')
        plt.axis('off')
        
        plt.tight_layout()
        plt.suptitle(f'Camera: Distance={distance}m, Elevation={elevation_angle}°, Azimuth={azimuth_angle}°')
        plt.subplots_adjust(top=0.9)
        plt.show()
    
    return rgb_image, depth_image, segmentation_mask


# 7. ENVIRONMENTAL SCANNING
def scan_environment(center_point=None, radius=3.0, angles=8, display_result=True):

    """
    Perform a 360-degree scan of the environment from multiple camera angles.
    
    Parameters:
    -----------
    center_point : list or None
        Center point to scan around [x,y,z] (default: None, uses robot position)
    radius : float
        Radius of the scanning circle in meters (default: 3.0)
    angles : int
        Number of different angles to capture (default: 8)
    display_result : bool
        Whether to display the resulting camera views (default: True)
        
    Returns:
    --------
    list
        List of tuples (angle, rgb_image, depth_image, segmentation_mask)
    """
    global world
    if world is None:
        print("Cannot scan environment because the world is not initialized.")
        return None
    
    # Determine center point
    if center_point is None:
        robot_position = world.robot.get_position()
        center_point = [robot_position.x, robot_position.y, robot_position.z]
    
    # Calculate camera height (typical eye height)
    camera_height = center_point[2] + 0.5  # 0.5m above center point
    
    # Prepare for scanning
    scan_results = []
    
    # Create figure for visualization
    if display_result:
        fig = plt.figure(figsize=(15, 12))
        fig.suptitle('360° Environmental Scan', fontsize=16)
    
    # Perform scan in a circle around the center point
    for i in range(angles):
        # Calculate angle in radians
        angle_rad = 2 * np.pi * i / angles
        angle_deg = 360 * i / angles
        
        # Calculate camera position
        camera_x = center_point[0] + radius * np.cos(angle_rad)
        camera_y = center_point[1] + radius * np.sin(angle_rad)
        camera_z = camera_height
        
        # Create camera pose looking at the center
        camera_position = [camera_x, camera_y, camera_z]
        camera_pose = Pose(camera_position)
        
        # Create a target pose at the center point
        target_pose = Pose(center_point)
        
        # Get images from this viewpoint
        images = world.get_images_for_target(target_pose, camera_pose)
        rgb_image, depth_image, segmentation_mask = images[:3]
        
        # Add to results
        scan_results.append((angle_deg, rgb_image, depth_image, segmentation_mask))
        
        # Display this view
        if display_result:
            rows = int(np.ceil(angles / 2))
            plt.subplot(rows, 2, i+1)
            plt.imshow(rgb_image)
            plt.title(f'View from {angle_deg:.0f}°')
            plt.axis('off')
    
    if display_result:
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust for suptitle
        plt.show()
    
    return scan_results


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
        else:
            print("Failed to capture image.")
