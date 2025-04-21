import requests
from utils.rotation import euler_to_quaternion

url = "http://localhost:8001/execute"


def test_camera():
    import requests
    import base64
    import os
    from datetime import datetime
    import cv2
    import numpy as np
    
    # Create images directory if it doesn't exist
    image_dir = "images"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Make API request
    payload = {
        "command": "get_camera_images",
        "params": {
            "target_distance": 2.0
        }
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["status"] == "success":
        # Save each image type
        for img_type, img_data in result["images"].items():
            if img_data:
                # Decode base64 string
                img_bytes = base64.b64decode(img_data)
                
                # Convert to numpy array
                nparr = np.frombuffer(img_bytes, np.uint8)
                
                # Decode image
                img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
                
                # Save to file
                filename = f"{image_dir}/{timestamp}_{img_type}.png"
                cv2.imwrite(filename, img)
                print(f"Saved {img_type} to {filename}")
            else:
                print(f"No data for {img_type}")
    else:
        print(f"Error: {result['message']}")
    
    return result

# def test_robot pose
import requests

def test_robot_pose():
    """
    Test the get_robot_pose API endpoint.

    Args:
        url: Base URL of your robot API (e.g. "http://localhost:8001/execute")

    Returns:
        dict: The JSON result from the server.
    """
    payload = {
        "command": "get_robot_pose",
        "params": {}
    }

    # 1) Fire off the request
    resp = requests.post(url, json=payload)
    resp.raise_for_status()

    # 2) Parse JSON
    result = resp.json()

    # 3) Check status
    if result.get("status") != "success":
        print(f"Error from server: {result.get('message')}")
        return result

    # 4) Extract and validate pose fields
    pos = result.get("position")
    ori = result.get("orientation")

    # Basic sanity checks
    assert isinstance(pos, list) and len(pos) == 3, f"Position malformed: {pos}"
    assert isinstance(ori, list) and len(ori) == 4, f"Orientation malformed: {ori}"

    # 5) Print out for human inspection
    print(f"Robot position: {pos}")
    print(f"Robot orientation: {ori}")
    print("✅ get_robot_pose returned a valid 3‑vector position and 4‑vector orientation.")

    return result


# def test move robot
def test_move_robot():
    payload = {
        "command": "move_robot",
        "params": {"coordinates": [0, 1, 0]}
    }
    response = requests.post(url, json=payload) 
    print(response.json())

# test pickup and place
def test_pickup_and_place():
    payload = {
        "command": "pickup_and_place",
        "params": {"object_name": "cereal1", "target_location": [10, 10, 0.95]}
    }
    response = requests.post(url, json=payload)
    print(response.json())

# test robot perceive
def test_robot_perceive():
    payload = {
        "command": "robot_perceive",
        "params": {"perception_area": "table_area_main"}
    }
    response = requests.post(url, json=payload)
    print(response.json())

# test transport object
def test_transport_object():
    payload = {
        "command": "transport_object",
        "params": {"object_name": "cereal", "target_location": [1.4, 0.2, 0.95]}
    }
    response = requests.post(url, json=payload)
    print(response.json())

# test calculate object distances
def test_calculate_object_distances():
    payload = {
        "command": "calculate_object_distances",
        "params": {"source_object": "cereal"}
    }
    response = requests.post(url, json=payload)
    print(response.json())

# test look at object
def test_look_at_object():
    payload = {
        "command": "look_at_object",    
        "params": {"obj_name": "cereal"}
    }
    response = requests.post(url, json=payload)
    print(response.json())

# test detect object
def test_detect_object():
    payload = {
        "command": "detect_object",
        "params": {}
    }
    response = requests.post(url, json=payload)
    print(response.json())

# test move and rotate
def test_move_and_rotate():
    payload = {
        "command": "move_and_rotate",
        "params": {"location": [0, 0, 0], "angle": 60}
    }
    response = requests.post(url, json=payload)
    print(response.json())

# test move torso
def test_move_torso():
    payload = {
        "command": "move_torso",
        "params": {"position": "high"}    
    }
    response = requests.post(url, json=payload)
    print(response.json())  


# test park arms    
def test_park_arms():
    payload = {
        "command": "park_arms",
        "params": {}
    }
    response = requests.post(url, json=payload)
    print(response.json())

def test_enhanced_camera():
    import requests
    import base64
    import os
    from datetime import datetime
    
    # Create images directory if it doesn't exist
    image_dir = "enhanced_images"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Make API request
    payload = {
        "command": "get_enhanced_camera_images",
        "params": {
            "target_distance": 2.0
        }
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["status"] == "success":
        # Save each image type
        for img_type, img_data in result["images"].items():
            # Decode base64 string
            img_bytes = base64.b64decode(img_data)
            
            # Save to file
            filename = f"{image_dir}/{timestamp}_{img_type}.png"
            with open(filename, "wb") as f:
                f.write(img_bytes)
            print(f"Saved enhanced {img_type} to {filename}")
    else:
        print(f"Error: {result['message']}")
    
    return result

# test spawn objects
def test_spawn_objects():
    payload = {
        "command": "spawn_objects",
        "params": {
            "object_choice": "cereal",
            "coordinates": [1.825, -0.74, 1],
            "color": "red",
        }
    }
    response = requests.post(url, json=payload)
    print(response.json())


def test_calculate_relative_distances():
    """
    Test the calculate_relative_distances API endpoint.

    Returns:
        dict: The JSON result from the server.
    """
    payload = {
        "command": "calculate_relative_distances",
        "params": {
            "object_name_1": "cereal1",
            "object_name_2": "spoon1"
        }
    }
    response = requests.post(url, json=payload)
    result = response.json()
    print(result)
    return result

def test_get_placement_surfaces():
    """Test the get_placement_surfaces API endpoint."""
    print("\nTesting get_placement_surfaces...")
    
    payload = {
        "command": "get_placement_surfaces",
        "params": {}
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["status"] == "success":
        print(f"Found {len(result['surfaces'])} available surfaces:")
        for surface, info in result["surfaces"].items():
            position_str = str(info.get("position", "None"))
            dimensions_str = str(info.get("dimensions", "None"))
            print(f"- {surface}: {info.get('description', 'No description')}")
            print(f"  Position: {position_str}")
            print(f"  Dimensions: {dimensions_str}")
            if "recommended_for" in info:
                print(f"  Recommended for: {', '.join(info['recommended_for'])}")
    else:
        print(f"Error: {result['message']}")
    
    return result


def test_spawn_in_area():
    """Test the spawn_in_area API endpoint."""
    primary_surfaces_list = [
    "sink_area_surface",
    "kitchen_island_surface",
    "kitchen_island_stove",
    "table_area_main",
    "oven_area_area",
    ]

    secondary_surfaces_list = [
        "sink_area_sink",
        "oven_area_oven_door",
        "fridge_area",
    ]


    print("\nTesting spawn_in_area...")
    
    # Choose a reliable surface to test with
    surface_name = "sink_area_surface"
    # lets create a random number from 1 to 100
    import random
    random_number = random.randint(1, 100)
    
    payload = {
        "command": "spawn_in_area",
        "params": {
            "object_choice": "spoon",
            "surface_name": surface_name,
            "color": "red",
            "name": f"test_cereal_{random_number}",  # Unique name using timestamp
            "offset_x": 0.1,
            "offset_y": 0.1
        }
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["status"] == "success":
        print(f"Successfully spawned object: {result['message']}")
        print(f"Object details: {result['object']['name']} of type {result['object']['type']}")
        print(f"Position: {result['object']['pose']}")
    else:
        print(f"Error: {result['message']}")
    
    return result   
def test_pick_and_place_on_surface():
    """Test the pick_and_place_on_surface API endpoint."""
    print("\nTesting pick_and_place_on_surface...")
   
    object_name = "cereal1"  # Use the name of the object we just spawned
    # print(f"Created test object: {object_name}")
    
    surface_name = "sink_area_sink"
    payload = {
        "command": "pick_and_place_on_surface",
        "params": {
            "object_name": object_name,
            "surface_name": surface_name,
            "offset_x": 0.1,
            "offset_y": 0.1,
            "arm": "right"
        }
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["status"] == "success":
        print(f"Successfully picked up {object_name} and placed on {surface_name}")
        print(f"Message: {result['message']}")
    else:
        print(f"Error: {result['message']}")
    
    return result 


# call spawn objects multiple times

test_move = False
test_camera_function = False
test_pickup_and_place_function = False
test_robot_perceive_function = False
test_transport_object_function = False
test_calculate_object_distances_function = False
test_look_at_object_function = False
test_detect_object_function = False
test_move_and_rotate_function = False
test_move_torso_function = False
test_park_arms_function = False
test_enhanced_camera_function = False
test_spawn_objects_function = False
test_robot_pose_function = False
# To enable the test, set the flag to True:
test_calculate_relative_distances_function = False

# Test flags for kitchen surface functions
test_get_placement_surfaces_function = False
test_kitchen_surfaces_function = False  # Enable the combined kitchen surfaces test
test_spawn_in_area_function = False  # Enable the spawn_in_area test
test_pick_and_place_on_surface_function = True

def main():
    if test_move == True:
        test_move_robot()
    if test_park_arms_function == True:
        test_park_arms()
    if test_look_at_object_function == True:
        test_look_at_object()
    if test_camera_function == True:
        test_camera()
    if test_pickup_and_place_function == True:
        test_pickup_and_place()
    if test_robot_perceive_function == True:
        test_robot_perceive()
    if test_transport_object_function == True:
        test_transport_object()
    if test_calculate_object_distances_function == True:
        test_calculate_object_distances()    
    if test_detect_object_function == True:
        test_detect_object()
    if test_move_and_rotate_function == True:
        test_move_and_rotate()
    if test_move_torso_function == True:
        test_move_torso()
    if test_enhanced_camera_function == True:
        test_enhanced_camera()
    if test_spawn_objects_function == True:
        test_spawn_objects()
    if test_robot_pose_function == True:
        test_robot_pose()
    if test_calculate_relative_distances_function == True:
        test_calculate_relative_distances()    
    if test_get_placement_surfaces_function == True:
        test_get_placement_surfaces()    
    if test_spawn_in_area_function == True:
        test_spawn_in_area()
    if test_pick_and_place_on_surface_function == True:
        test_pick_and_place_on_surface()


if __name__ == "__main__":
    main()
