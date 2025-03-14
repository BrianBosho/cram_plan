# PyCRAM API Server

A FastAPI-based REST API for controlling the PyCRAM robot simulation environment through HTTP requests.

## Overview

This project provides an HTTP API interface to control the PyCRAM robot simulation, allowing you to:

- Move the robot
- Manipulate objects (pickup, place, transport)
- Spawn new objects in the environment
- Perceive objects in the environment
- Execute other robot control commands

The system includes both a programmatic API and a web-based user interface.

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

### Endpoint: `/execute`

This is the main endpoint for all robot commands. It accepts POST requests with JSON payloads.

General request format:
```json
{
  "command": "command_name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

General response format:
```json
{
  "status": "success|error",
  "message": "Human-readable message",
  "additional_data": { ... }
}
```

### API Examples for All Commands

#### 1. Move Robot

Moves the robot to specific coordinates.

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "move_robot", "params": {"coordinates": [1.0, 1.0, 0.0]}}'
```

Postman:
- Method: POST
- URL: http://localhost:8001/execute
- Body (raw JSON):
```json
{
  "command": "move_robot", 
  "params": {
    "coordinates": [1.0, 1.0, 0.0]
  }
}
```

#### 2. Spawn Objects

Creates a new object in the environment.

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "spawn_objects", "params": {"object_choice": "cereal", "coordinates": [1.4, 1.0, 0.95], "color": "blue"}}'
```

Postman:
- Method: POST
- URL: http://localhost:8001/execute
- Body (raw JSON):
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

#### 3. Pickup and Place

Picks up an object and places it at the target location.

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "pickup_and_place", "params": {"object_name": "cereal", "target_location": [1.0, 1.0, 0.8], "arm": "right"}}'
```

Postman:
- Method: POST
- URL: http://localhost:8001/execute
- Body (raw JSON):
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

#### 4. Robot Perceive

Makes the robot perceive objects in a specified area.

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "robot_perceive", "params": {"perception_area": "table"}}'
```

Postman:
- Method: POST
- URL: http://localhost:8001/execute
- Body (raw JSON):
```json
{
  "command": "robot_perceive", 
  "params": {
    "perception_area": "table"
  }
}
```

#### 5. Look for Object

Makes the robot look for a specific object.

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "look_for_object", "params": {"object_name": "cereal"}}'
```

Postman:
- Method: POST
- URL: http://localhost:8001/execute
- Body (raw JSON):
```json
{
  "command": "look_for_object", 
  "params": {
    "object_name": "cereal"
  }
}
```

#### 6. Unpack Arms

Unpacks the robot's arms.

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "unpack_arms", "params": {}}'
```

Postman:
- Method: POST
- URL: http://localhost:8001/execute
- Body (raw JSON):
```json
{
  "command": "unpack_arms", 
  "params": {}
}
```

#### 7. Detect Object

Detects objects of a specific type.

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "detect_object", "params": {"object_type": "Cereal", "detection_area": "table"}}'
```

Postman:
- Method: POST
- URL: http://localhost:8001/execute
- Body (raw JSON):
```json
{
  "command": "detect_object", 
  "params": {
    "object_type": "Cereal", 
    "detection_area": "table"
  }
}
```

#### 8. Transport Object

Transports an object to a target location.

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "transport_object", "params": {"object_name": "cereal", "target_location": [0.5, 0.5, 0.8], "arm": "left"}}'
```

Postman:
- Method: POST
- URL: http://localhost:8001/execute
- Body (raw JSON):
```json
{
  "command": "transport_object", 
  "params": {
    "object_name": "cereal", 
    "target_location": [0.5, 0.5, 0.8], 
    "arm": "left"
  }
}
```

### List Available Commands

Get a list of all available commands with a GET request:

```bash
curl -X GET http://localhost:8001/commands
```

Postman:
- Method: GET
- URL: http://localhost:8001/commands

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