#!/usr/bin/env python3
"""
API interface for PyCRAM simulation functions.
"""
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys

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
    from environment import create_environment, get_world
    
    print("Initializing environment for API mode...")
    env_obj, world = create_environment()
    if world is None:
        print("Failed to initialize the world. Exiting...")
        return False
    print("Environment initialized successfully.")
    return True

# Import the non-interactive functions
from robot_actions_api import (
    move_robot,
    pickup_and_place,
    robot_perceive,
    look_for_object,
    unpack_arms,
    detect_object,
    transport_object
)

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
        elif command == "look_for_object":
            result = look_for_object(**params)
            return result
        elif command == "unpack_arms":
            result = unpack_arms()
            return result
        elif command == "detect_object":
            result = detect_object(**params)
            return result
        elif command == "transport_object":
            result = transport_object(**params)
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
            "look_for_object",
            "unpack_arms", 
            "detect_object",
            "transport_object"
        ]
    }

# Run the server when this file is executed directly
if __name__ == "__main__":
    # Initialize the environment first
    if init_environment():
        print("Starting PyCRAM API server on port 8001...")
        uvicorn.run(app, host="0.0.0.0", port=8001) 