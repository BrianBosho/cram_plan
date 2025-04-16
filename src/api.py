#!/usr/bin/env python3
"""
API interface for PyCRAM simulation functions.
"""
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import sys
import os
import webbrowser
import threading
import time

# Create the API app
app = FastAPI(title="PyCRAM API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Store environment objects globally
env_obj = None
world = None

# Initialize environment - we'll do this before starting the server
def init_environment():
    global env_obj, world
    # Import these here to prevent auto-execution of interactive code
    from environment import create_environment, get_world, get_environment_name
    from robot_actions_api import spawn_objects
    
    print("Initializing environment for API mode...")
    env_obj, world = create_environment(spawn_default_objects=False)
    if world is None:
        print("Failed to initialize the world. Exiting...")
        return False
    
    # Check if the environment is a kitchen or user chose to initialize with objects
    # Use the new get_environment_name function
    env_name = get_environment_name(env_obj)
    if env_name == 'kitchen':
        # Spawn initial objects at specified locations
        objects_to_spawn = [
            {"object_choice": "spoon", "coordinates": [1.4, 1, 0.95], "color": "blue"},
            {"object_choice": "cereal", "coordinates": [1.4, 0.8, 0.95], "color": "red"},
            {"object_choice": "milk", "coordinates": [1.4, 0.6, 0.95], "color": "green"}
        ]
        
        for obj in objects_to_spawn:
            spawn_result = spawn_objects(
                obj['object_choice'], 
                obj['coordinates'], 
                obj['color']
            )
            print(f"Spawned {obj['color']} {obj['object_choice']}: {spawn_result}")
    
    print("Environment initialized successfully.")
    return True

# Import the non-interactive functions
from robot_actions_api import (
    move_robot,
    pickup_and_place,
    robot_perceive,
    transport_object,
    demo_camera,
    get_robot_camera_images,
    calculate_object_distances,
    look_at_object,
    detect_object,
    move_and_rotate
)

# from camera import get_camera_images    

# Static files mounting - if we have a 'static' directory
if os.path.exists('static'):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the robot_control.html file directly
@app.get("/", response_class=HTMLResponse)
async def get_robot_control():
    """Serve the robot control interface"""
    try:
        with open("robot_control.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Robot control interface not found.</h1>")

# API endpoints
@app.post("/execute")
async def execute_command(data: dict = Body(...)):
    """Execute a PyCRAM command"""
    command = data.get("command")
    params = data.get("params", {})
    
    try:
        if command == "spawn_objects":
            # Extract the correct parameters for spawn_objects
            object_choice = params.get("object_choice")
            coordinates = params.get("coordinates")
            color = params.get("color")
            
            # Call our non-interactive spawn_objects
            from robot_actions_api import spawn_objects
            result = spawn_objects(object_choice, coordinates, color)
            return result
        elif command == "move_robot":
            result = move_robot(**params)
            return result
        elif command == "pickup_and_place":
            result = pickup_and_place(**params)
            return result
        elif command == "robot_perceive":
            result = robot_perceive(**params)
            return result
        elif command == "transport_object":
            result = transport_object(**params)
            return result
        elif command == "get_camera_images":
            target_distance = params.get("target_distance", 2.0)
            result = get_robot_camera_images(target_distance, world)
            return result
        elif command == "calculate_object_distances":
            result = calculate_object_distances(**params, world=world)
            return result
        elif command == "look_at_object":
            result = look_at_object(**params)
            return result
        elif command == "detect_object":
            result = detect_object(**params)
            return result
        elif command == "move_and_rotate":
            result = move_and_rotate(**params)
            return result
        else:
            return {"status": "error", "message": f"Unknown command: {command}"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/commands")
async def list_commands():
    """List available commands"""
    return {
        "available_commands": [
            "spawn_objects",
            "move_robot",
            "pickup_and_place",
            "robot_perceive",
            "transport_object",
            "get_camera_images"
        ]
    }

def open_browser():
    """Open browser after a short delay to ensure server is up"""
    time.sleep(2)  # Wait for server to start
    webbrowser.open('http://localhost:8001')
    print("Browser window opened. If no window appeared, navigate to: http://localhost:8001")

# Run the server when this file is executed directly
if __name__ == "__main__":
    # Initialize the environment first
    if init_environment():
        print("Starting PyCRAM API server on port 8001...")
        print("Web interface will be available at: http://localhost:8001")
        print("To access from other devices, use: http://YOUR_IP_ADDRESS:8001")
        
        # Open browser automatically in a separate thread
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Start the server
        uvicorn.run(app, host="0.0.0.0", port=8001) 