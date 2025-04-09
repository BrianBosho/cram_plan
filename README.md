# PyCRAM API Server

[![CI workflow](https://github.com/BrianBosho/cram_plan/actions/workflows/CI.yml/badge.svg?branch=master)](https://github.com/BrianBosho/cram_plan/actions/workflows/CI.yml)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://github.com/pycqa/isort)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-red.svg)](https://github.com/pycqa/flake8)

A FastAPI-based REST API for controlling the PyCRAM robot simulation environment through HTTP requests.

## Overview

This project provides an HTTP API interface to control the PyCRAM robot simulation, allowing you to:

- Move the robot
- Manipulate objects (pickup, place, transport)
- Spawn new objects in the environment
- Perceive objects in the environment
- Execute other robot control commands

The system includes both a programmatic API and a web-based user interface.

## Development

### Linting

NOTE: This is a one-time step, and it is required if your code changes are to be pushed upstream to GitHub

Isort, black, and flake8 are used to check that code is well formatted and styled. Pre-commit hooks are used to automate
this process.

1. Install pre-commit package: `pip install pre-commit`
2. Install git hook scripts: `pre-commit install`
3. (optional) Run against all files: `pre-commit run --all-files`

## Components

- **API Server**: FastAPI-based server that handles requests
- **Non-Interactive Action Layer**: Parameter-driven versions of robot actions
- **Web Interface**: Browser-based UI for easy control
- **Test Client**: Python script for testing API functionality

## Installation

### Prerequisites

- Python 3.6+
- PyCRAM simulation environment
- FastAPI and Uvicorn

### Setup

1. Install required Python packages:

```bash
pip install fastapi uvicorn requests
```

2. Ensure PyCRAM is properly installed and configured.

3. Clone or download this repository to your local machine.

## Quick Start

### Starting the API Server

1. Run the API server:

```bash
python api.py
```

2. You should see output confirming the server is running, and a browser will automatically open with the web interface:

```
Robot spawned as 'pr2'.
Environment initialized successfully.
Starting PyCRAM API server on port 8001...
Web interface will be available at: http://localhost:8001
To access from other devices, use: http://YOUR_IP_ADDRESS:8001
Browser window opened. If no window appeared, navigate to: http://localhost:8001
INFO:     Started server process [40354]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Accessing the API and Web Interface Over a Network

The API server is configured to accept connections from all network interfaces (0.0.0.0), which means you can access it from other devices on your network:

1. Find your server's IP address by running one of these commands:
   ```bash
   # On Linux
   ip addr show
   
   # On macOS
   ifconfig | grep inet
   
   # On Windows
   ipconfig
   ```

2. Access the API and web interface from other devices:
   - Web interface URL: `http://YOUR_SERVER_IP:8001`
   - API endpoint: `http://YOUR_SERVER_IP:8001/execute`
   - OpenAPI docs: `http://YOUR_SERVER_IP:8001/docs`

### Using in a Virtual Machine

If you're running the server in a virtual machine (VM), you need to configure networking properly:

1. **VM IP Address**: Find the VM's IP address (not localhost):
   ```bash
   # Inside the VM
   ip addr show
   ```
   Look for an IP like 192.168.x.x (not 127.0.0.1)

2. **Network Mode**: Make sure your VM is using either:
   - **Bridged networking**: Your VM appears as a separate device on your network
   - **Port forwarding**: Forward port 8001 from host to VM

3. **Accessing from host machine**: Use the VM's IP address:
   ```
   http://VM_IP_ADDRESS:8001
   ```

4. **Troubleshooting VM connections**:
   - Make sure your VM firewall allows connections on port 8001
   - Try `ping VM_IP_ADDRESS` from host to check connectivity
   - Ensure port forwarding is set up if using NAT networking

### Mobile Device Access

To access the interface from a mobile device:

1. Make sure your phone/tablet is on the same WiFi network
2. Use your server's IP address in the browser: `http://YOUR_SERVER_IP:8001`
3. The interface will automatically adapt to mobile screen sizes

### Using the Web Interface

1. The web interface is now directly integrated with the server:
   - When you start the server, it's automatically available at http://localhost:8001
   - No need to run a separate server for the HTML file

2. The interface will automatically detect the server address when loaded

3. Use the form controls to interact with the robot simulation.

### Testing with the Python Client

Run the test script to verify API functionality:

```bash
python test_api.py
```

## Features

- **RESTful API Design**: Standard HTTP methods and JSON responses
- **Web Interface**: Easy-to-use browser control panel
- **Parameter-Based Control**: Non-interactive versions of all robot actions
- **Error Handling**: Structured error responses and logging
- **CORS Support**: Web interface works across different domains
- **Network Accessible**: Control the robot from any device on your network

## API Reference

This section details all available commands in the PyCRAM Robot API.

#### Available Commands

1. **move_robot**
   - Move the robot to specific coordinates
   - Parameters:
     - `coordinates` (list): [x, y, z] coordinates to move to
   - Example:
```json
{
  "command": "move_robot", 
       "params": {"coordinates": [1.0, 1.0, 0.0]}
     }
     ```

2. **spawn_objects**
   - Create new objects in the environment
   - Parameters:
     - `object_choice` (str): Object type (e.g., "cereal", "milk", "spoon", "bowl")
     - `coordinates` (list): [x, y, z] placement coordinates
     - `color` (str, optional): Color of the object
   - Example:
```json
{
  "command": "spawn_objects", 
  "params": {
    "object_choice": "cereal", 
    "coordinates": [1.4, 1.0, 0.95], 
    "color": "blue"
  }
}
```

3. **pickup_and_place**
   - Pick up an object and place it at a target location
   - Parameters:
     - `object_name` (str): Name of the object to pick up
     - `target_location` (list): [x, y, z] coordinates for placement
     - `arm` (str, optional): Arm to use ("left" or "right")
   - Example:
```json
{
  "command": "pickup_and_place", 
  "params": {
    "object_name": "cereal", 
    "target_location": [1.0, 1.0, 0.8], 
    "arm": "right"
  }
}
```

4. **robot_perceive**
   - Make the robot perceive objects in its environment
   - Parameters:
     - `perception_area` (str, optional): Area to perceive (e.g., "table", "room")
   - Example:
```json
{
  "command": "robot_perceive", 
       "params": {"perception_area": "table"}
     }
     ```

5. **get_kitchen_info**
   - Retrieve detailed information about the kitchen environment
   - No parameters required
   - Example:
     ```json
     {
       "command": "get_kitchen_info"
     }
     ```

6. **get_camera_info**
   - Get information from the robot's cameras
   - Parameters:
     - `camera_name` (str, optional): Camera to query ("head_camera", "kinect", "wide_stereo")
   - Example:
     ```json
     {
       "command": "get_camera_info",
       "params": {"camera_name": "head_camera"}
     }
     ```

7. **look_for_object**
   - Make the robot look for a specific object
   - Parameters:
     - `object_name` (str): Name of the object to find
   - Example:
```json
{
  "command": "look_for_object", 
       "params": {"object_name": "cup1"}
     }
     ```

8. **unpack_arms**
   - Unpack the robot's arms
   - No parameters required
   - Example:
```json
{
       "command": "unpack_arms"
     }
     ```

9. **detect_object**
   - Detect objects of a specific type
   - Parameters:
     - `object_type` (str): Type of object to detect (e.g., "Milk", "Cereal")
   - Example:
```json
{
  "command": "detect_object", 
       "params": {"object_type": "Cereal"}
     }
     ```

10. **transport_object**
    - Transport an object to a target location
    - Parameters:
      - `object_name` (str): Name of the object to transport
      - `target_location` (list): [x, y, z] coordinates for destination
      - `arm` (str, optional): Arm to use ("left" or "right")
    - Example:
```json
{
  "command": "transport_object", 
  "params": {
    "object_name": "cereal", 
          "target_location": [1.0, 1.0, 0.8], 
          "arm": "right"
  }
}
```

11. **get_table_height**
    - Get the height of the kitchen table
    - No parameters required
    - Example:
      ```json
      {
        "command": "get_table_height"
      }
      ```

### Response Format

All commands return a JSON response with the following structure:
```json
{
  "status": "success|error|not_found",
  "message": "Descriptive message about the operation",
  "additional_data": { ... }  // Optional additional information
}
```

- `status`: Indicates the result of the operation
  - `"success"`: Operation completed successfully
  - `"error"`: An error occurred
  - `"not_found"`: Requested object or action could not be completed

### Error Handling

- If a command fails, the response will include an error message
- Check the `status` field to determine the outcome of the operation
- Detailed error information is provided in the `message` field

## Troubleshooting Network Access

If you can't access the API from other devices:

1. **Firewall Issues**: Check if your firewall is blocking port 8001
   ```bash
   # Linux
   sudo ufw status
   # If needed, allow the port
   sudo ufw allow 8001
   ```

2. **Network Isolation**: Ensure both devices are on the same network

3. **Correct IP**: Make sure you're using the correct server IP address

4. **CORS Issues**: If experiencing CORS problems in the browser, the API already has CORS middleware enabled

## Available Commands

- `spawn_objects` - Create new objects in the environment
- `move_robot` - Navigate the robot to coordinates
- `pickup_and_place` - Pick up an object and place it somewhere
- `robot_perceive` - Report objects visible to the robot
- `look_for_object` - Find and focus on a specific object
- `unpack_arms` - Prepare robot arms
- `detect_object` - Detect objects of a specific type
- `transport_object` - Move an object to a destination

## Documentation

For more detailed information:

- [User Guide](user_guide.md) - Explains basic usage for end users
- [Technical Guide](technical_guide.md) - Provides technical details for developers

## Integration with External Systems

The API can be easily integrated with:

- Custom UI applications
- Python scripts
- LangChain or other LLM frameworks
- Any system capable of making HTTP requests

## License

MIT License

## Credits

Developed for the PyCRAM robot simulation framework. Special thanks to the PyCRAM development team. 