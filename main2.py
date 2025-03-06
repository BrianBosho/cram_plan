#!/usr/bin/env python3
"""
Main entry point for the PyCRAM interactive simulation with API interface.
"""
from environment import create_environment, get_world
from object_management import spawn_objects
from robot_actions import (
    move_robot, 
    pickup_and_place, 
    robot_perceive, 
    look_for_object, 
    unpack_arms, 
    detect_object, 
    transport_object
)
from ui.menu import display_menu, exit_simulation
import threading
from fastapi import FastAPI, Body
import uvicorn

# Create API app
app = FastAPI()

# Store environment and world globally
env_obj = None
world = None

# Function to execute commands (will be called by both API and interactive mode)
def execute_command(command_name, **kwargs):
    """Execute a PyCRAM command and return the result"""
    result = {"status": "error", "message": "Unknown command"}
    
    try:
        if command_name == "spawn_objects":
            result = spawn_objects(**kwargs)
            return {"status": "success", "message": "Objects spawned successfully"}
        elif command_name == "move_robot":
            result = move_robot(**kwargs)
            return {"status": "success", "message": "Robot moved successfully"}
        elif command_name == "pickup_and_place":
            result = pickup_and_place(**kwargs)
            return {"status": "success", "message": "Pickup and place executed successfully"}
        elif command_name == "robot_perceive":
            result = robot_perceive(**kwargs)
            return {"status": "success", "message": "Robot perception executed successfully"}
        elif command_name == "look_for_object":
            result = look_for_object(**kwargs)
            return {"status": "success", "message": "Look for object executed successfully"}
        elif command_name == "unpack_arms":
            result = unpack_arms(**kwargs)
            return {"status": "success", "message": "Arms unpacked successfully"}
        elif command_name == "detect_object":
            result = detect_object(**kwargs)
            return {"status": "success", "message": "Object detected successfully"}
        elif command_name == "transport_object":
            result = transport_object(**kwargs)
            return {"status": "success", "message": "Object transported successfully"}
        else:
            return {"status": "error", "message": f"Unknown command: {command_name}"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

# API endpoints
@app.post("/execute")
async def api_execute_command(data: dict = Body(...)):
    """API endpoint for executing commands"""
    command_name = data.get("command")
    kwargs = data.get("params", {})
    
    return execute_command(command_name, **kwargs)

@app.get("/available_commands")
async def get_available_commands():
    """Return list of available commands"""
    return {
        "commands": [
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

def main():
    """
    Main function to run the interactive simulation.
    It creates the environment (spawning both the environment and the robot)
    and then enters a menu loop for additional actions.
    """
    global env_obj, world
    
    try:
        print("\n--- Interactive PyCRAM Modular Demo ---\n")
        env_obj, world = create_environment()
        
        if world is None:
            print("Failed to initialize the world. Exiting...")
            return
            
    except Exception as e:
        print("CRAM error during environment creation in main:", e)
        return
    
    while True:
        try:
            choice = display_menu()
            if choice == "1":
                execute_command("spawn_objects")
            elif choice == "2":
                execute_command("move_robot")
            elif choice == "3":
                execute_command("pickup_and_place")
            elif choice == "4":
                execute_command("robot_perceive")
            elif choice == "5":
                execute_command("look_for_object")
            elif choice == "6":
                execute_command("unpack_arms")
            elif choice == "7":
                execute_command("detect_object")
            elif choice == "8":
                execute_command("transport_object")
            elif choice == "9":
                exit_simulation()
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print("CRAM error in main loop:", e)
            import traceback
            traceback.print_exc()

def run_api_server():
    """Run the API server"""
    global env_obj, world
    
    # Initialize environment if not already done
    if env_obj is None or world is None:
        print("Initializing environment for API mode...")
        env_obj, world = create_environment()
        
        if world is None:
            print("Failed to initialize the world. Exiting...")
            return
    
    # Start the API server
    print("Starting API server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        # Run in API mode for LangChain access
        run_api_server()
    else:
        # Run in interactive mode
        main()
