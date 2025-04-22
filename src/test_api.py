import requests
from utils.rotation import euler_to_quaternion
import random

url = "http://localhost:8001/execute"

def get_random_surface_position(surface_name):
    """
    Helper function to get a random position within the allowed displacement
    bounds for a specific surface.
    
    Args:
        surface_name (str): Name of the surface
        
    Returns:
        tuple: (offset_x, offset_y) - Random offsets within allowed bounds
    """
    # Get placement surfaces to check max offsets
    payload = {
        "command": "get_placement_surfaces",
        "params": {}
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    # Default offsets
    max_dx, max_dy = 0.5, 0.5
    
    # Get the max offset values from the surface if available
    if (result["status"] == "success" and 
        surface_name in result["surfaces"]):
        
        # Try to fetch max_dx and max_dy directly from API response
        surface_info = result["surfaces"][surface_name]
        if "max_dx" in surface_info and "max_dy" in surface_info:
            max_dx = surface_info["max_dx"]
            max_dy = surface_info["max_dy"]
    
    # Generate random offsets within the allowed bounds
    offset_x = random.uniform(-max_dx, max_dx)
    offset_y = random.uniform(-max_dy, max_dy)
    
    # Round to 3 decimal places
    offset_x = round(offset_x, 3)
    offset_y = round(offset_y, 3)
    
    return (offset_x, offset_y)

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
    result = response.json()
    
    print("Perceived objects:")
    for obj in result.get("perceived_objects", []):
        name = obj.get("name", "Unknown")
        obj_type = obj.get("type", "Unknown")
        print(f" - Name: {name}, Type: {obj_type}")
    
    return result

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
        "params": {"source_object": "cereal1"}
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
    """Test the spawn_in_area API endpoint with random offsets."""
    print("\nTesting spawn_in_area with random offsets...")
    
    # Choose a reliable surface to test with
    surface_name = "kitchen_island_surface"
    import random
    random_number = random.randint(1, 100)
    
    # Test with None values for offsets to trigger random placement
    payload = {
        "command": "spawn_in_area",
        "params": {
            "object_choice": "cereal",
            "surface_name": surface_name,
            "color": "green",
            "name": f"test_spoon_{random_number}",
            "offset_x": None,  # Use None to get random offset
            "offset_y": None   # Use None to get random offset
        }
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["status"] == "success":
        print(f"Successfully spawned object: {result['message']}")
        print(f"Object details: {result['object']['name']} of type {result['object']['type']}")
        print(f"Position: {result['object']['pose']}")
        print(f"Random offsets used: x={result['offsets'][0]}, y={result['offsets'][1]}")
    else:
        print(f"Error: {result['message']}")
    
    return result   

def test_pick_and_place_on_surface():
    """Test the pick_and_place_on_surface API endpoint with random offsets."""
    print("\nTesting pick_and_place_on_surface with random offsets...")
   
    object_name = "cereal1"  # Use the name of an existing object
    
    surface_name = "sink_area_surface"
    payload = {
        "command": "pick_and_place_on_surface",
        "params": {
            "object_name": object_name,
            "surface_name": surface_name,
            "offset_x": None,  # Use None to get random offset
            "offset_y": None,  # Use None to get random offset
            "arm": "right"
        }
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["status"] == "success":
        print(f"Successfully picked up {object_name} and placed on {surface_name}")
        print(f"Random offsets used: x={result['offsets'][0]}, y={result['offsets'][1]}")
        print(f"Message: {result['message']}")
    else:
        print(f"Error: {result['message']}")
    
    return result 

def test_get_world_objects():
    """
    Test the get_world_objects API endpoint that retrieves all objects in the world
    and their positions. Demonstrates filtering by area and object type.
    
    Returns:
        dict: The JSON result from the server containing all objects in the world and their positions.
    """
    # Test 1: Get all objects (excluding environment elements)
    print("\nTest 1: Getting all objects in the world...")
    payload = {
        "command": "get_world_objects",
        "params": {
            "exclude_types": ["floor", "wall", "ceiling", "ground", "kitchen", "apartment", "pr2"]
        }
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["status"] == "success":
        print(f"Found {len(result['objects'])} objects in the world:")
        for obj_name, obj_info in result["objects"].items():
            position = obj_info.get("position", {})
            position_str = f"x: {position.get('x', 'N/A')}, y: {position.get('y', 'N/A')}, z: {position.get('z', 'N/A')}"
            obj_type = obj_info.get("type", "Unknown")
            color = obj_info.get("color", "N/A")
            area = obj_info.get("area", "N/A")
            print(f"- {obj_name} (Type: {obj_type}, Color: {color}, Area: {area})")
            print(f"  Position: {position_str}")
    else:
        print(f"Error: {result['message']}")
    
    # Test 2: Filter objects by type
    print("\nTest 2: Filtering objects by type (cereal)...")
    payload = {
        "command": "get_world_objects",
        "params": {
            "exclude_types": ["floor", "wall", "ceiling", "ground", "kitchen", "apartment", "pr2"],
            "obj_type": "cereal"
        }
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["status"] == "success":
        print(f"Found {len(result['objects'])} milk objects:")
        for obj_name, obj_info in result["objects"].items():
            position = obj_info.get("position", {})
            position_str = f"x: {position.get('x', 'N/A')}, y: {position.get('y', 'N/A')}, z: {position.get('z', 'N/A')}"
            obj_type = obj_info.get("type", "Unknown")
            color = obj_info.get("color", "N/A")
            area = obj_info.get("area", "N/A")
            print(f"- {obj_name} (Type: {obj_type}, Color: {color}, Area: {area})")
            print(f"  Position: {position_str}")
    else:
        print(f"Error: {result['message']}")
    
    # Test 3: Filter objects by area
    print("\nTest 3: Filtering objects by area (kitchen_island_surface)...")
    payload = {
        "command": "get_world_objects",
        "params": {
            "exclude_types": ["floor", "wall", "ceiling", "ground", "kitchen", "apartment", "pr2"],
            "area": "kitchen_island_surface"
        }
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["status"] == "success":
        print(f"Found {len(result['objects'])} objects in sink_area_surface:")
        for obj_name, obj_info in result["objects"].items():
            position = obj_info.get("position", {})
            position_str = f"x: {position.get('x', 'N/A')}, y: {position.get('y', 'N/A')}, z: {position.get('z', 'N/A')}"
            obj_type = obj_info.get("type", "Unknown")
            color = obj_info.get("color", "N/A")
            print(f"- {obj_name} (Type: {obj_type}, Color: {color})")
            print(f"  Position: {position_str}")
    else:
        print(f"Error: {result['message']}")
    
    # Test 4: Filter objects by both type and area
    print("\nTest 4: Filtering objects by type and area (cereal in kitchen_island_surface)...")
    payload = {
        "command": "get_world_objects",
        "params": {
            "exclude_types": ["floor", "wall", "ceiling", "ground", "kitchen", "apartment", "pr2"],
            "obj_type": "cereal",
            "area": "kitchen_island_surface"
        }
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["status"] == "success":
        print(f"Found {len(result['objects'])} cereal objects in kitchen_island_surface:")
        for obj_name, obj_info in result["objects"].items():
            position = obj_info.get("position", {})
            position_str = f"x: {position.get('x', 'N/A')}, y: {position.get('y', 'N/A')}, z: {position.get('z', 'N/A')}"
            obj_type = obj_info.get("type", "Unknown")
            color = obj_info.get("color", "N/A")
            print(f"- {obj_name} (Type: {obj_type}, Color: {color})")
            print(f"  Position: {position_str}")
    else:
        print(f"Error: {result['message']}")
    
    # Return the last result
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
test_pick_and_place_on_surface_function = False
test_get_world_objects_function = True

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
    if test_get_world_objects_function == True:
        test_get_world_objects()


if __name__ == "__main__":
    main()
