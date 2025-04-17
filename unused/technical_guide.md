# PyCRAM API Technical Documentation

This document provides detailed technical information about the PyCRAM API server implementation, its components, and how they work together.

## System Architecture

The PyCRAM API system consists of several components that work together:

1. **API Server** (`api.py`): A FastAPI-based server that exposes robot control functionality via REST endpoints.
2. **Non-Interactive Robot Actions** (`robot_actions_api.py`): Implementations of robot actions designed for API use.
3. **Web Interface** (`robot_control.html`): A browser-based UI for controlling the robot.
4. **Test Client** (`test_api.py`): A Python client for testing the API.

The system architecture follows these principles:
- Separation of interactive and non-interactive code
- Parameter-driven robot actions instead of user prompts
- RESTful API design with JSON responses
- Cross-Origin Resource Sharing (CORS) support for web access

## File Descriptions

### api.py

The core API server that:
- Initializes the PyCRAM environment
- Defines API endpoints using FastAPI
- Routes commands to appropriate handlers
- Provides CORS support for web access

Key components:
- `init_environment()`: Initializes the robot simulation environment
- `/execute` endpoint: Accepts command and parameters, routes to appropriate function
- `/commands` endpoint: Lists available commands
- Error handling for all API calls

### robot_actions_api.py

Provides non-interactive versions of all robot actions:
- Each function accepts parameters instead of prompting the user
- Functions return structured JSON responses
- Common error handling pattern for all functions
- Uses the underlying PyCRAM simulation framework

Contains implementations for:
- `move_robot()`: Navigate the robot to coordinates
- `pickup_and_place()`: Pick up an object and place it somewhere
- `robot_perceive()`: Report objects visible to the robot
- `look_for_object()`: Find and focus on a specific object
- `unpack_arms()`: Prepare robot arms
- `detect_object()`: Detect objects of a specific type
- `transport_object()`: Move an object to a destination
- `spawn_objects()`: Create new objects in the environment

### robot_control.html

A web-based user interface for the API with:
- Separate panels for each command
- Form inputs for parameters
- Result display area
- Asynchronous API calls

Technical features:
- Pure HTML/CSS/JavaScript with no dependencies
- Responsive design for different screen sizes
- Form validation and default values
- JSON pretty-printing for results

### test_api.py

A Python client for testing the API:
- Sends requests to API endpoints
- Formats and displays results
- Provides examples of API usage from Python

## API Endpoints

### POST /execute

Executes a command with parameters.

**Request format:**
```json
{
  "command": "command_name",
  "params": {
    "param1": value1,
    "param2": value2,
    ...
  }
}
```

**Response format:**
```json
{
  "status": "success|error",
  "message": "Human-readable message",
  "command_specific_data": "..."
}
```

### GET /commands

Lists available commands.

**Response format:**
```json
{
  "available_commands": [
    "spawn_objects",
    "move_robot",
    ...
  ]
}
```

## Command Implementation Details

### spawn_objects

Creates objects in the simulation environment.

**Parameters:**
- `object_choice`: Type of object ("cereal", "milk", "spoon", "bowl")
- `coordinates`: [x, y, z] position
- `color`: Optional color name

The implementation:
1. Maps object type to appropriate PyCRAM ontology class
2. Creates Pose object from coordinates
3. Handles color via ColorWrapper
4. Instantiates Object with appropriate parameters
5. Returns object details in response

### move_robot

Moves the robot to specified coordinates.

**Parameters:**
- `coordinates`: [x, y, z] position

The implementation:
1. Creates a Pose from coordinates
2. Constructs a NavigateAction using the pose
3. Executes the action in the simulated robot context
4. Returns status and coordinates in response

### pickup_and_place

Picks up an object and places it elsewhere.

**Parameters:**
- `object_name`: Name of object to pick up
- `target_location`: [x, y, z] destination
- `arm`: Optional arm specification ("left", "right")

The implementation is complex, involving:
1. Object resolution using designators
2. Arm preparation (parking and torso positioning)
3. Pickup location resolution using costmaps
4. Navigation to pickup location
5. Pickup action execution
6. Placement location resolution
7. Navigation to placement location
8. Place action execution

### Other Commands

Similar technical patterns apply to the other commands, with each having specific parameters and implementation details.

## Non-Interactive vs Interactive Mode

The original functions in the PyCRAM system are designed for interactive use with user prompts. The API versions differ in several ways:

1. **Parameter Handling**
   - Interactive: Uses `input()` calls to get parameters
   - API: Accepts parameters as function arguments with defaults

2. **Error Handling**
   - Interactive: Prints errors to console
   - API: Returns structured error responses

3. **Execution Flow**
   - Interactive: May have user decision points
   - API: Follows a predetermined flow with defaults

4. **Output**
   - Interactive: Prints status to console
   - API: Returns structured JSON data

## Exception Handling

All API functions follow a common pattern for exception handling:
```python
try:
    # Function implementation
    return {"status": "success", ...}
except Exception as e:
    import traceback
    traceback.print_exc()
    return {"status": "error", "message": str(e)}
```

This ensures that:
- Exceptions don't crash the server
- Detailed error information is available in logs
- Clients receive meaningful error messages

## Web Interface Implementation

The web interface uses standard web technologies:
- HTML for structure
- CSS for styling
- JavaScript for API interaction

Key JavaScript components:
- `callRobotApi()`: Generic function for API calls
- Event listeners for form submissions
- JSON parsing and formatting
- Error handling for failed API calls

## Advanced Topics

### CORS Support

The API includes CORS middleware to allow cross-origin requests, enabling the web interface to work even when served from a different domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Initialization

The API initializes the environment only once at startup, providing better performance than re-initializing for each request:

```python
if __name__ == "__main__":
    # Initialize the environment first
    if init_environment():
        print("Starting PyCRAM API server...")
        uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Lazy Imports

Some imports are done inside functions to prevent side effects during module loading:

```python
def get_world_safely():
    from environment import get_world
    return get_world()
```

This is important for avoiding interactive prompts that might occur during initialization.

## Dependencies and Requirements

The PyCRAM API relies on several Python packages to function correctly. Key dependencies include:

### Core Dependencies
- **FastAPI** (v0.115.11): Web framework for building the API endpoints
- **Uvicorn** (v0.33.0): ASGI server for running the FastAPI application
- **PyCRAM Bullet** (v3.2.8): Core PyCRAM simulation framework using Bullet physics
- **NumPy** (v1.24.4): Numerical computing library for mathematical operations
- **PyBullet**: 3D physics simulation (imported through PyCRAM Bullet)

### Web Interface
- **Flask** (v1.1.4): Used for serving the web interface
- **Flask-Cors** (v3.0.10): Handles Cross-Origin Resource Sharing for the web interface

### Robot Simulation
- **eigenpy** (v3.10.3): Python bindings for Eigen (linear algebra)
- **transforms3d** (v0.4.2): 3D transformations library
- **PyOpenGL** (v3.1.0): Python bindings for OpenGL

### ROS Integration
- **rospy** (v1.17.0): Python client library for ROS
- **tf** (v1.13.2): Transform library for ROS
- **actionlib** (v1.14.0): ROS action library

### Utils
- **Pillow** (v7.0.0): Image processing library
- **trimesh** (v4.6.3): Library for loading and manipulating triangular meshes
- **owlready2** (v0.47): Library for manipulating OWL ontologies in Python

For a complete list of dependencies with their versions, refer to the `requirements.txt` file in the project root.

To install all required dependencies, use:
```bash
pip install -r requirements.txt
```

## Running the API Server

To run the PyCRAM API server:

```bash
python api.py
```

This will:
1. Initialize the PyCRAM environment
2. Start the FastAPI server with Uvicorn
3. Listen for incoming requests on all interfaces (0.0.0.0) on port 8001

Alternatively, you can run the server using Uvicorn directly:

```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8001
```

### Accessing the API

Once the server is running, you can access:
- API endpoints at `http://localhost:8001/`
- API documentation at `http://localhost:8001/docs`
- The web interface by opening `robot_control.html` in your browser

### Running the Test Client

To test the API using the provided test client:

```bash
python test_api.py
```

This will send a series of test requests to the API server and display the results.