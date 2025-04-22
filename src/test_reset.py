#!/usr/bin/env python3
"""
Test script for reset functionality.
This script demonstrates how to use the reset functions in the PyCRAM API.
"""

import time
import requests
import json
import sys
import traceback

# Base URL for the API
API_URL = "http://localhost:8001/execute"

def call_api(command, params=None):
    """Call the API with the given command and parameters"""
    if params is None:
        params = {}
    
    data = {
        "command": command,
        "params": params
    }
    
    try:
        response = requests.post(API_URL, json=data)
        return response.json()
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": f"API call failed: {str(e)}"}

def print_result(result):
    """Print the result of an API call in a formatted way"""
    print("\nRESULT:")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Message: {result.get('message', 'No message')}")
    
    # Print any additional details
    for key, value in result.items():
        if key not in ["status", "message"]:
            print(f"{key}: {value}")
    
    print("-" * 50)

def test_reset_robot_state():
    """Test resetting the robot state"""
    print("\n=== Testing Reset Robot State ===")
    
    # First, move the robot to a non-default position to see the effect
    print("Moving robot to a different position...")
    result = call_api("move_robot", {"coordinates": [1.0, 1.0, 0.0]})
    print_result(result)
    
    # Move torso to a different position
    print("Moving torso to low position...")
    result = call_api("move_torso", {"position": "low"})
    print_result(result)
    
    # Now reset the robot state
    print("Resetting robot state...")
    result = call_api("reset_robot_state")
    print_result(result)
    
    # Verify robot position after reset
    print("Getting robot pose after reset...")
    result = call_api("get_robot_pose")
    print_result(result)
    
    print("Reset robot state test complete.\n")

def test_reset_world():
    """Test resetting the world state"""
    print("\n=== Testing Reset World ===")
    
    # First, spawn a few test objects
    print("Spawning test objects...")
    for i in range(3):
        result = call_api("spawn_objects", {
            "object_choice": "cereal",
            "coordinates": [1.0 + i*0.3, 0.8, 0.95],
            "color": "red",
            "name": f"test_cereal_{i}"
        })
        print(f"Spawned object {i+1}:")
        print_result(result)
    
    # Get all objects in the world
    print("Getting all objects before reset...")
    result = call_api("get_world_objects")
    print_result(result)
    
    # Reset the world with default objects
    print("Resetting world with default objects...")
    result = call_api("reset_world", {"spawn_default_objects": True})
    print_result(result)
    
    # Get all objects after reset
    print("Getting all objects after reset...")
    result = call_api("get_world_objects")
    print_result(result)
    
    # Reset again but without default objects
    print("Resetting world without default objects...")
    result = call_api("reset_world", {"spawn_default_objects": False})
    print_result(result)
    
    # Get all objects after reset without default objects
    print("Getting all objects after reset without default objects...")
    result = call_api("get_world_objects")
    print_result(result)
    
    print("Reset world test complete.\n")

def test_reset_all():
    """Test the combined reset_all function"""
    print("\n=== Testing Reset All ===")
    
    # First, move the robot and spawn objects
    print("Setting up test state (moving robot and spawning objects)...")
    call_api("move_robot", {"coordinates": [2.0, 2.0, 0.0]})
    
    for i in range(2):
        call_api("spawn_objects", {
            "object_choice": "bowl",
            "coordinates": [1.2 + i*0.3, 0.7, 0.95],
            "color": "blue",
            "name": f"test_bowl_{i}"
        })
    
    # Now perform the complete reset
    print("Performing complete reset...")
    result = call_api("reset_all", {"spawn_default_objects": True})
    print_result(result)
    
    # Verify the state after reset
    print("Getting robot pose after reset...")
    robot_result = call_api("get_robot_pose")
    print_result(robot_result)
    
    print("Getting world objects after reset...")
    objects_result = call_api("get_world_objects")
    print_result(objects_result)
    
    print("Reset all test complete.\n")

def test_force_release_object():
    """Test the force_release_object function"""
    print("\n=== Testing Force Release Object ===")
    
    # First try to pick up an object
    print("Setting up: Trying to pick up cereal...")
    pickup_result = call_api("pickup_and_place", {
        "object_name": "cereal",
        "target_location": [1.4, 1.0, 0.95],  # Just pick it up, not really moving it
        "arm": "right"
    })
    print_result(pickup_result)
    
    # Now force release it
    print("Forcing release of object from right arm...")
    result = call_api("force_release_object", {"arm": "right"})
    print_result(result)
    
    # Test releasing from both arms
    print("Forcing release from both arms...")
    result = call_api("force_release_object")
    print_result(result)
    
    print("Force release object test complete.\n")

def run_all_tests():
    """Run all the reset function tests"""
    print("\n=== Running All Reset Function Tests ===\n")
    
    try:
        test_reset_robot_state()
        time.sleep(5)  # Brief pause between tests
        
        test_reset_world()
        time.sleep(5)  # Brief pause between tests
        
        test_reset_all()
        time.sleep(5)  # Brief pause between tests
        
        test_force_release_object()
        
        print("\n=== All Reset Function Tests Completed ===")
    except Exception as e:
        traceback.print_exc()
        print(f"\nTest suite failed with error: {str(e)}")

if __name__ == "__main__":
    # Check if API is running
    try:
        requests.get("http://localhost:8001/commands")
        print("API is running. Starting tests...")
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("ERROR: API not running. Please start the API server first.")
        print("Run: python api.py")
        sys.exit(1)