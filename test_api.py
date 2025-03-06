import requests
import json

# Base URL
BASE_URL = "http://localhost:8001"  # Updated port to match

# List available commands
def get_commands():
    response = requests.get(f"{BASE_URL}/commands")
    print("Available commands:", response.json())

# Execute a command
def execute_command(command, params=None):
    if params is None:
        params = {}
    
    data = {
        "command": command,
        "params": params
    }
    
    response = requests.post(f"{BASE_URL}/execute", json=data)
    return response.json()

# Example usage
if __name__ == "__main__":
    # List available commands
    get_commands()
    
    # Test move_robot with coordinates
    print("\nExecuting move_robot command with coordinates:")
    result = execute_command("move_robot", {"coordinates": [1.0, 2.0, 0.0]})
    print(json.dumps(result, indent=2))
    
    # Test pickup_and_place
    print("\nExecuting pickup_and_place command:")
    result = execute_command("pickup_and_place", {
        "object_name": "cup1",
        "target_location": [0.5, 0.5, 0.8]
    })
    print(json.dumps(result, indent=2))
    
    # Test robot_perceive
    print("\nExecuting robot_perceive command:")
    result = execute_command("robot_perceive", {"perception_area": "table"})
    print(json.dumps(result, indent=2)) 