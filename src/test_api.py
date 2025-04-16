import requests

url = "http://localhost:8001/execute"



# def test camera
def test_camera():
    payload = {
        "command": "get_camera_images",
        "params": {
            "target_distance": 2.0
        }
    }
    response = requests.post(url, json=payload)
    print(response.json())

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

test_move = False
test_camera_function = False
test_pickup_and_place_function = False
test_robot_perceive_function = False
test_transport_object_function = False
test_calculate_object_distances_function = False
test_look_at_object_function = True


def main():
    if test_move == True:
        test_move_robot()
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
    if test_look_at_object_function == True:
        test_look_at_object()

if __name__ == "__main__":
    main()
