# PyCRAM Robot API

## Overview

This project provides an API interface for controlling and interacting with a PyCRAM robot simulation. PyCRAM is a toolbox for designing, implementing, and deploying software on autonomous robots. The API allows users to control robot movement, manipulate objects, perceive the environment, and capture camera data from the robot's sensors through a web interface or programmatic API calls.

The API server is built with FastAPI and provides a simple RESTful interface to the underlying PyCRAM simulation. A web-based control panel is also included for easy interaction without writing code.

## Key Components

The codebase is organized into several key components:

### 1. API Server (`api.py`)

- Creates the FastAPI application
- Handles HTTP requests and forwards them to the robot action functions
- Manages the simulation environment
- Serves the web control interface
- Provides API endpoints for robot control

### 2. Robot Actions (`robot_actions_api.py`)

Contains the implementation of various robot actions that can be performed in the simulation:
- Movement and navigation
- Object manipulation (pickup, place, transport)
- Environment perception
- Camera image capture
- Arm and torso positioning

### 3. Testing Module (`test_api.py`)

- Contains functions to test each API endpoint
- Demonstrates how to make API calls programmatically
- Can be used as example code for interacting with the API

### 4. Environment Setup (`environment.py`)

- Initializes the simulation environment
- Provides options for different environment types (kitchen, apartment)
- Creates the world and spawns default objects

### 5. Utility Functions (`utils/`)

- `color_wrapper.py`: Converts color strings to RGBA values for PyCRAM
- `rotation.py`: Provides functions to convert between Euler angles and quaternions

### 6. Web Interface (`robot_control.html`)

A browser-based user interface that allows users to:
- Connect to the API server
- Execute robot commands
- Visualize results
- Control all aspects of the robot without writing code

## Installation Requirements

### Prerequisites

- Python 3.8 or higher
- PyCRAM library (version compatible with this project)
- ROS (Robot Operating System) if running with real robots

### Dependencies

```
fastapi
uvicorn
numpy
scipy
matplotlib
opencv-python
requests
pillow
```

### PyCRAM Installation

This project uses a specific version of PyCRAM that can be found at: [https://github.com/BrianBosho/pycram_clone](https://github.com/BrianBosho/pycram_clone).

**Note:** The PyCRAM version used in this project is not the latest version. Some implementations and features may differ when using the latest version of PyCRAM. Please refer to the linked repository for the compatible version.

### Installation Steps

1. Clone the PyCRAM repository:
   ```bash
   git clone https://github.com/BrianBosho/pycram_clone.git
   ```

2. Install PyCRAM:
   ```bash
   cd pycram_clone
   pip install -e .
   ```

3. Clone this repository and install dependencies:
   ```bash
   git clone <this-repo-url>
   cd <repo-folder>
   pip install -r requirements.txt
   ```

## API Endpoints

The API exposes a single endpoint `/execute` which accepts POST requests with a JSON body containing the command to execute and its parameters.

### Available Commands

#### 1. spawn_objects

Spawns an object in the simulation environment.

**Parameters:**
- `object_choice` (string): Type of object to spawn ("cereal", "milk", "spoon", "bowl", or custom)
- `coordinates` (array): [x, y, z] coordinates for object placement
- `color` (string): Optional color for the object (e.g., "red", "blue", "green")

**Response:**
```json
{
  "status": "success",
  "message": "Object 'object_name' created successfully",
  "object": {
    "name": "object_name",
    "type": "object_type",
    "file": "file_name",
    "pose": [x, y, z],
    "color": "color_name"
  }
}
```

#### 2. move_robot

Moves the robot to specified coordinates.

**Parameters:**
- `coordinates` (array): [x, y, z] coordinates to move to

**Response:**
```json
{
  "status": "success",
  "message": "Robot moved to coordinates [x, y, z]",
  "coordinates": [x, y, z]
}
```

#### 3. pickup_and_place

Picks up an object and places it at a target location.

**Parameters:**
- `object_name` (string): Name of the object to pick up
- `target_location` (array): [x, y, z] coordinates for placement
- `arm` (string): Which arm to use ('left', 'right', or null for automatic)

**Response:**
```json
{
  "status": "success",
  "message": "Successfully picked up object_name and placed at [x, y, z]",
  "object": "object_name",
  "target_location": [x, y, z],
  "arm_used": "arm_used"
}
```

#### 4. robot_perceive

Makes the robot perceive its environment.

**Parameters:**
- `perception_area` (string): Area to perceive ('table', 'room', etc.)

**Response:**
```json
{
  "status": "success",
  "message": "Robot perceived N objects in perception_area",
  "perceived_objects": [
    {
      "name": "object_name",
      "type": "object_type",
      "pose": "object_pose"
    },
    // More objects...
  ]
}
```

#### 5. transport_object

Transports an object to a target location.

**Parameters:**
- `object_name` (string): Name of the object to transport
- `target_location` (array): [x, y, z] coordinates for the target location
- `arm` (string): Which arm to use ('left', 'right')

**Response:**
```json
{
  "status": "success",
  "message": "Successfully transported object_name to [x, y, z]",
  "object": "object_name",
  "target_location": [x, y, z],
  "arm_used": "arm_used"
}
```

#### 6. get_camera_images

Captures images from the robot's camera and returns them as base64-encoded strings.

**Parameters:**
- `target_distance` (float): Distance in meters to the target point (default: 2.0)

**Response:**
```json
{
  "status": "success",
  "message": "Camera images captured successfully",
  "images": {
    "color_image": "base64_encoded_string",
    "depth_image": "base64_encoded_string",
    "segmentation_mask": "base64_encoded_string"
  }
}
```

#### 7. get_enhanced_camera_images

Similar to get_camera_images but with improved visualization of depth and segmentation data.

**Parameters:**
- `target_distance` (float): Distance in meters to the target point (default: 2.0)

**Response:** Same as get_camera_images but with enhanced visualizations.

#### 8. calculate_object_distances

Calculates distances between objects in the world.

**Parameters:**
- `source_object` (string): Name of source object (if null, calculates distances between all pairs)
- `target_objects` (array): List of target object names (if null, uses all objects)
- `exclude_types` (array): List of object types to exclude

**Response:**
```json
{
  "status": "success",
  "message": "Distances calculated",
  "distances": {
    "object1-to-object2": distance,
    // More distance pairs...
  }
}
```

#### 9. look_at_object

Makes the robot look at the specified object.

**Parameters:**
- `obj_name` (string): The name of the object to look at

**Response:**
```json
{
  "status": "success",
  "message": "Robot is now looking at 'obj_name'"
}
```

#### 10. detect_object

Detects an object in the robot's environment and returns information about it.

**Parameters:**
- `object_name` (string): Name of the object to detect (if null, detects any visible object)
- `location` (object): Location to search for objects

**Response:**
```json
{
  "status": "success",
  "message": "Successfully detected object: object_name",
  "object": {
    "name": "object_name",
    "type": "object_type",
    "position": {
      "x": x,
      "y": y,
      "z": z
    },
    "color": "color"
  }
}
```

#### 11. move_and_rotate

Moves the robot to a specified location and/or rotates it to a specified orientation.

**Parameters:**
- `location` (array): [x, y, z] coordinates to move to (if null, robot will only rotate)
- `angle` (float): Angle in degrees to rotate around Z axis

**Response:**
```json
{
  "status": "success",
  "message": "Robot moved to coordinates [x, y, z] with orientation [x, y, z, w]",
  "position": [x, y, z],
  "orientation": [x, y, z, w]
}
```

#### 12. move_torso

Moves the robot's torso to a specified position.

**Parameters:**
- `position` (string): Position to move the torso to ("low", "high")

**Response:**
```json
{
  "status": "success",
  "message": "Torso moved to position position",
  "position": "position"
}
```

#### 13. park_arms

Moves the robot's arm(s) to the pre-defined parking position.

**Parameters:**
- `arm` (string): Arm to park ("left", "right", or null for both arms)

**Response:**
```json
{
  "status": "success",
  "message": "Successfully parked arm(s): arm",
  "arm": "arm"
}
```

#### 14. calculate_relative_distances

Calculates the difference in x, y, z coordinates and the Euclidean distance between two objects.

**Parameters:**
- `object_name_1` (string): Name of the first object
- `object_name_2` (string): Name of the second object

**Response:**
```json
{
  "status": "success",
  "object_1": "object_name_1",
  "object_2": "object_name_2",
  "dx": number,
  "dy": number,
  "dz": number,
  "euclidean": number
}
```

#### 15. get_robot_pose

Returns the current position and orientation of the robot in the simulation.

**Parameters:** None

**Response:**
```json
{
  "status": "success",
  "position": [x, y, z],
  "orientation": [qx, qy, qz, qw]
}
```

#### 16. get_placement_surfaces

Returns information about available surfaces in the environment where objects can be placed.

**Parameters:** None

**Response:**
```json
{
  "status": "success",
  "surfaces": {
    "surface_name": {
      "description": "string",
      "position": [x, y, z],
      "dimensions": [width, depth, height],
      "recommended_for": ["object_type1", ...]
    }
  }
}
```

#### 17. spawn_in_area

Spawns an object on a specific named surface with optional color, name, and offsets.

**Parameters:**
- `object_choice` (string): Type of object to spawn
- `surface_name` (string): Name of the surface
- `color` (string): Color for the object (optional)
- `name` (string): Custom name (optional)
- `offset_x` (number): X offset from surface center (optional)
- `offset_y` (number): Y offset from surface center (optional)

**Response:**
```json
{
  "status": "success",
  "object": {
    "name": "string",
    "type": "string",
    "pose": [x, y, z],
    "color": "string"
  }
}
```

#### 18. pick_and_place_on_surface

Picks up an object and places it on a specific named surface.

**Parameters:**
- `object_name` (string): Name of the object to pick up
- `surface_name` (string): Name of the surface
- `offset_x` (number): X offset from surface center (optional)
- `offset_y` (number): Y offset from surface center (optional)
- `arm` (string): Which arm to use (optional)

**Response:**
```json
{
  "status": "success",
  "message": "Successfully picked up {object_name} and placed on {surface_name}",
  "object": "string",
  "surface": "string",
  "position": [x, y, z],
  "arm_used": "string"
}
```

## Usage Examples

### Command-line (using curl)

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "move_robot", "params": {"coordinates": [1.0, 1.0, 0.0]}}'
```

### Python

```python
import requests

url = "http://localhost:8001/execute"
payload = {
    "command": "pickup_and_place",
    "params": {
        "object_name": "cereal",
        "target_location": [1.4, 0.5, 0.95],
        "arm": "left"
    }
}
response = requests.post(url, json=payload)
result = response.json()
print(result)
```

### Web Interface

Open your browser and navigate to `http://localhost:8001` to access the web control panel.

## Starting the Server

```bash
cd src
python api.py
```

The server will start at `http://localhost:8001` and automatically open a browser window with the control panel.