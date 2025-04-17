import requests
from utils.rotation import euler_to_quaternion

url = "http://localhost:8001/execute"

# orientation = euler_to_quaternion(0, 0, 120)


# def test camera
# def test_camera():
#     payload = {
#         "command": "get_camera_images",
#         "params": {
#             "target_distance": 2.0
#         }
#     }
#     response = requests.post(url, json=payload)
#     print(response.json())
# ... existing code ...

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

# def test move robot
def test_move_robot():
    payload = {
        "command": "move_robot",
        "params": {"coordinates": [0, 0, 0]}
    }
    response = requests.post(url, json=payload) 
    print(response.json())

# test pickup and place
def test_pickup_and_place():
    payload = {
        "command": "pickup_and_place",
        "params": {"object_name": "cereal", "target_location": [1.4, 0.2, 0.95], "arm": "left"}
    }
    response = requests.post(url, json=payload)
    print(response.json())

# test robot perceive
def test_robot_perceive():
    payload = {
        "command": "robot_perceive",
        "params": {"perception_area": "sink"}
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
            "coordinates": [1.4, 0.4, 0.95],
        }
    }
    response = requests.post(url, json=payload)
    print(response.json())

test_move = False
test_camera_function = False
test_pickup_and_place_function = False
test_robot_perceive_function = True
test_transport_object_function = False
test_calculate_object_distances_function = False
test_look_at_object_function = False
test_detect_object_function = False
test_move_and_rotate_function = False
test_move_torso_function = False
test_park_arms_function = False
test_enhanced_camera_function = False
test_spawn_objects_function = False

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

if __name__ == "__main__":
    main()
