# PyCRAM API User Guide

This guide explains how to use the PyCRAM API to control the simulated robot through both a web interface and programmatic API calls.

## Introduction

The PyCRAM API provides HTTP endpoints for controlling a simulated robot. You can interact with it through:
- A web browser interface
- Direct API calls using tools like curl
- Python scripts

## Setup and Installation

### Prerequisites
- Python 3.6+
- PyCRAM simulation environment
- FastAPI and Uvicorn
- A modern web browser

### Installation

1. Install required Python packages:
   ```bash
   pip install fastapi uvicorn requests
   ```

2. Ensure PyCRAM is properly installed and configured.

## Starting the API Server

1. Run the API server:
   ```bash
   python api.py
   ```

2. You should see output similar to:
   ```
   Robot spawned as 'pr2'.
   Environment initialized successfully.
   Starting PyCRAM API server on port 8001...
   INFO:     Started server process [40354]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
   ```

## Using the Web Interface

1. Open the `robot_control.html` file in your web browser, or serve it with a simple HTTP server:
   ```bash
   # Start a simple HTTP server
   python -m http.server 8080
   ```
   
   Then visit: http://localhost:8080/robot_control.html

2. The web interface is divided into command panels:
   - Move Robot
   - Spawn Objects
   - Pickup and Place
   - Robot Perceive
   - Look for Object
   - Unpack Arms
   - Detect Object
   - Transport Object

3. For each command:
   - Fill in the required parameters
   - Click the associated button
   - View results at the top of the page

### Example: Moving the Robot

1. In the "Move Robot" panel:
   - Enter X, Y, Z coordinates (e.g., 1.0, 1.0, 0.0)
   - Click "Move Robot"
   - The results will appear in the results area

### Example: Spawning Objects

1. In the "Spawn Objects" panel:
   - Select an object type (cereal, milk, spoon, or bowl)
   - Enter coordinates
   - Choose a color (or leave as default)
   - Click "Spawn Object"

## Using the API Directly

You can interact with the API using HTTP requests.

### Checking Available Commands 