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

2. You should see output confirming the server is running:

```
Robot spawned as 'pr2'.
Environment initialized successfully.
Starting PyCRAM API server on port 8001...
INFO:     Started server process [40354]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Using the Web Interface

1. Open the `robot_control.html` file in your browser or serve it with a simple HTTP server:

```bash
# Start a simple HTTP server
python -m http.server 8080
```

2. Visit: http://localhost:8080/robot_control.html

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

## Command Examples

### Moving the Robot

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "move_robot", "params": {"coordinates": [1.0, 1.0, 0.0]}}'
```

### Spawning Objects

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "spawn_objects", "params": {"object_choice": "cereal", "coordinates": [1.4, 1.0, 0.95], "color": "blue"}}'
```

### Picking and Placing Objects

```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "pickup_and_place", "params": {"object_name": "cereal", "target_location": [1.0, 1.0, 0.8], "arm": "right"}}'
```

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