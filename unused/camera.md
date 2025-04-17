# PyCRAM Camera Utilities Documentation

This document provides an overview of the camera utilities available in PyCRAM for the PR2 robot. It covers the core functionality provided by the `pr2_camera_utils.py` module, as well as the API endpoints from `camera_api.py` for interacting with these utilities through a web interface.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Camera Utilities](#core-camera-utilities)
3. [Object Visualization and Analysis](#object-visualization-and-analysis)
4. [Camera Positioning and Views](#camera-positioning-and-views)
5. [API Endpoints](#api-endpoints)
6. [Examples](#examples)

## Getting Started

Before using any camera utilities, you need to initialize the world and the camera utilities:

```python
from pr2_camera_utils import initialize
from interactive_sim import initialize_world

# First initialize the world
world = initialize_world()

# Then initialize camera utilities with the world instance
initialize(world)
```

## Core Camera Utilities

### `initialize(world_instance)`

Initializes the camera utilities with a world instance.

**Parameters:**
- `world_instance`: The world instance to use for camera operations

**Returns:** None

**Example:**
```python
from pr2_camera_utils import initialize
initialize(world)
```

### `capture_camera_image(display=True, save_path=None, target_distance=2.0)`

Captures an image from the robot's camera.

**Parameters:**
- `display` (bool): Whether to display the image (default: True)
- `save_path` (str, optional): Path to save the image, if None the image is not saved
- `target_distance` (float): Distance to the target point (default: 2.0)

**Returns:** 
- Tuple of (rgb_image, depth_image, segmentation_mask)

**Example:**
```python
rgb, depth, segmentation = capture_camera_image(save_path="robot_view.png")
```

### `visualize_depth_map(display=True, save_path=None, colormap='viridis', normalize=True)`

Visualizes the depth map from the robot's camera with color mapping.

**Parameters:**
- `display` (bool): Whether to display the depth map (default: True)
- `save_path` (str, optional): Path to save the depth map
- `colormap` (str): Matplotlib colormap to use for visualization (default: 'viridis')
- `normalize` (bool): Whether to normalize depth values for better visualization (default: True)

**Returns:** 
- numpy.ndarray: The depth image data

**Example:**
```python
depth_data = visualize_depth_map(colormap='plasma')
```

## Object Visualization and Analysis

### `identify_objects_in_view(min_pixel_count=50)`

Identifies and lists all objects visible in the camera view.

**Parameters:**
- `min_pixel_count` (int): Minimum number of pixels required to consider an object visible (default: 50)

**Returns:** 
- dict: Dictionary mapping object IDs to visible objects, with pixel counts

**Example:**
```python
visible_objects = identify_objects_in_view()
for obj_id, data in visible_objects.items():
    print(f"Object: {data['name']}, Pixels: {data['pixel_count']}")
```

### `check_object_visibility(object_name, threshold=0.8, plot_result=True)`

Checks if a specific object is visible from the current camera position.

**Parameters:**
- `object_name` (str): Name of the object to check visibility for
- `threshold` (float): Minimum percentage of the object that must be visible (0.0-1.0, default: 0.8)
- `plot_result` (bool): Whether to plot the segmentation mask (default: True)

**Returns:** 
- bool: True if the object is visible according to the threshold, False otherwise

**Example:**
```python
is_visible = check_object_visibility("cup", threshold=0.6)
```

### `find_occluding_objects(object_name, plot_result=True)`

Finds all objects that are occluding the specified object.

**Parameters:**
- `object_name` (str): Name of the object to check for occlusion
- `plot_result` (bool): Whether to plot the segmentation mask (default: True)

**Returns:** 
- list: List of objects that are occluding the target object

**Example:**
```python
occluding_objs = find_occluding_objects("bowl")
for obj in occluding_objs:
    print(f"Occluding object: {obj.name}")
```

### `calculate_object_distances(source_object=None, target_objects=None, exclude_types=None)`

Calculates distances between objects in the world.

**Parameters:**
- `source_object` (str, optional): Name of source object. If None, will calculate distances between all pairs.
- `target_objects` (list, optional): List of target object names. If None, will use all objects.
- `exclude_types` (list, optional): List of object types to exclude (like 'floor', 'wall', etc.)

**Returns:** 
- dict: Dictionary of distances between objects

**Example:**
```python
distances = calculate_object_distances(source_object="cup")
for obj_name, distance in distances.items():
    print(f"Distance from cup to {obj_name}: {distance:.2f}m")
```

### `display_object_distances(distances, top_n=None, sort=True)`

Displays the calculated distances in a formatted table.

**Parameters:**
- `distances` (dict): Dictionary of distances between objects
- `top_n` (int, optional): Number of closest distances to display. If None, displays all.
- `sort` (bool): Whether to sort distances by value (default: True)

**Returns:** None

**Example:**
```python
distances = calculate_object_distances()
display_object_distances(distances, top_n=5)
```

### `visualize_object_distances_3d(source_object=None, exclude_types=None, max_objects=10, show_labels=True, show_distances=True)`

Creates a 3D visualization of objects in the world with distances.

**Parameters:**
- `source_object` (str, optional): Name of source object to calculate distances from
- `exclude_types` (list, optional): List of object types to exclude
- `max_objects` (int): Maximum number of objects to include in visualization (default: 10)
- `show_labels` (bool): Whether to show object labels (default: True)
- `show_distances` (bool): Whether to show distance labels on lines (default: True)

**Returns:** None

**Example:**
```python
visualize_object_distances_3d(source_object="bowl", max_objects=5)
```

### `estimate_distances_to_objects(max_objects=5)`

Estimates distances to the visible objects using depth information.

**Parameters:**
- `max_objects` (int): Maximum number of objects to report distances for (default: 5)

**Returns:** 
- dict: Dictionary mapping object names to their estimated distances

**Example:**
```python
distances = estimate_distances_to_objects(max_objects=10)
```

## Camera Positioning and Views

### `look_at_object(object_name, distance=2.0, elevation_angle=0.0, azimuth_angle=0.0, display_result=True)`

Simulates moving the camera to look at a specific object from a given viewpoint.

**Parameters:**
- `object_name` (str): Name of the object to look at
- `distance` (float): Distance from the object in meters (default: 2.0)
- `elevation_angle` (float): Vertical angle in degrees (0=level, 90=above, -90=below) (default: 0.0)
- `azimuth_angle` (float): Horizontal angle in degrees (0=front, 90=right, 180=behind) (default: 0.0)
- `display_result` (bool): Whether to display the resulting camera view (default: True)

**Returns:** 
- tuple: (rgb_image, depth_image, segmentation_mask) - The images from the new viewpoint

**Example:**
```python
rgb, depth, seg = look_at_object("cup", distance=1.5, elevation_angle=30, azimuth_angle=45)
```

### `scan_environment(center_point=None, radius=3.0, angles=8, display_result=True)`

Performs a 360-degree scan of the environment from multiple camera angles.

**Parameters:**
- `center_point` (list, optional): Center point to scan around [x,y,z] (uses robot position if None)
- `radius` (float): Radius of the scanning circle in meters (default: 3.0)
- `angles` (int): Number of different angles to capture (default: 8)
- `display_result` (bool): Whether to display the resulting camera views (default: True)

**Returns:** 
- list: List of tuples (angle, rgb_image, depth_image, segmentation_mask)

**Example:**
```python
scan_results = scan_environment(angles=4, radius=2.0)
```

### `spawn_multiple_objects(objects_to_spawn=None)`

Spawns multiple objects in the world for testing.

**Parameters:**
- `objects_to_spawn` (list, optional): List of dictionaries with object specifications

**Returns:** 
- list: List of spawned objects

**Example:**
```python
objects = [
    {
        'name': 'test_bowl',
        'type': 'bowl',
        'coordinates': [1.3, 0.8, 0.95],
        'color': 'blue'
    },
    {
        'name': 'test_cup',
        'type': 'cup',
        'coordinates': [1.5, 0.9, 0.95],
        'color': 'red'
    }
]
spawned_objects = spawn_multiple_objects(objects)
```

## API Endpoints

The `camera_api.py` file provides a FastAPI-based web API for interacting with the camera utilities. Here are the main endpoints:

### World Management

- `POST /initialize_world`: Initializes the world
- `POST /create_objects`: Creates default objects in the world
- `POST /add_objects`: Adds additional objects to the world
- `POST /spawn_object`: Spawns a single object with specified parameters
- `POST /exit_world`: Exits the world

### Camera and Visualization

- `POST /capture_camera_image`: Captures an image from the robot's camera
- `POST /visualize_depth_map`: Visualizes the depth map
- `POST /identify_objects`: Identifies objects in the camera view
- `POST /check_object_visibility`: Checks if a specific object is visible
- `POST /find_occluding_objects`: Finds objects occluding a specific object
- `POST /estimate_distances`: Estimates distances to visible objects
- `POST /look_at_object`: Simulates moving the camera to look at a specific object
- `POST /scan_environment`: Performs a 360-degree scan of the environment
- `POST /object_distances`: Calculates distances between objects
- `POST /visualize_3d_distances`: Creates a 3D visualization of object distances

### Demo Functions

- `POST /demo_camera`: Demonstrates basic camera functionality
- `POST /advanced_camera_demo`: Demonstrates advanced camera functions

### Utility Endpoints

- `GET /images/{image_id}`: Retrieves a stored image by ID
- `GET /get_available_objects`: Lists all available objects in the world

## Examples

### Basic Usage

```python
# Initialize world and camera
from interactive_sim import initialize_world
from pr2_camera_utils import initialize, capture_camera_image

world = initialize_world()
initialize(world)

# Capture an image
rgb, depth, segmentation = capture_camera_image()

# Identify objects in view
objects = identify_objects_in_view()
print(f"Found {len(objects)} objects in view")

# Check if a specific object is visible
is_visible = check_object_visibility("cup")
print(f"Cup is visible: {is_visible}")
```

### Object Distance Analysis

```python
# Calculate distances between all objects
distances = calculate_object_distances()
display_object_distances(distances, top_n=5)

# Create a 3D visualization of distances from a specific object
visualize_object_distances_3d(source_object="bowl")
```

### Camera Manipulation

```python
# Look at a specific object from different angles
look_at_object("cup", distance=1.5, elevation_angle=30, azimuth_angle=45)

# Perform a 360-degree scan of the environment
scan_results = scan_environment(angles=8)
```

### Using the API

To use the web API, first start the server:

```bash
python camera_api.py
```

Then, access the web interface at http://127.0.0.1:8000 or make API calls to the various endpoints.

Example using Python requests:

```python
import requests

# Initialize the world
response = requests.post("http://127.0.0.1:8000/initialize_world")
print(response.json())

# Create objects
response = requests.post("http://127.0.0.1:8000/create_objects")
print(response.json())

# Capture a camera image
response = requests.post("http://127.0.0.1:8000/capture_camera_image", 
                         json={"display": True, "save_path": "my_image.png"})
print(response.json())
``` 