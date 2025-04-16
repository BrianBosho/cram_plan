import os
import uuid

import matplotlib.pyplot as plt

import robo_cram

IMAGES_DIR = "images"
ENV_OPTIONS = {1: robo_cram.Env.KITCHEN, 2: robo_cram.Env.APARTMENT}
OBJ_TYPES = {
    1: robo_cram.ObjectType.CEREAL,
    2: robo_cram.ObjectType.MILK,
    3: robo_cram.ObjectType.SPOON,
    4: robo_cram.ObjectType.BOWL,
}
COLOURS = {
    1: robo_cram.Colour.RED,
    2: robo_cram.Colour.GREEN,
    3: robo_cram.Colour.BLUE,
    4: robo_cram.Colour.YELLOW,
    5: robo_cram.Colour.WHITE,
    6: robo_cram.Colour.BLACK,
    7: robo_cram.Colour.DEFAULT,
}
LOCATIONS = {
    1: robo_cram.Location.KITCHEN_ISLAND,
    2: robo_cram.Location.SINK_AREA,
    3: robo_cram.Location.TABLE,
}


def init_simulation():
    print(
        """
        \rSelect environment to create:
        \r1) Kitchen
        \r2) Apartment
        """
    )
    choice = input("Enter your choice: ").strip()
    while len(choice) == 0 or int(choice) not in ENV_OPTIONS:
        choice = input("Invalid choice, enter your choice: ").strip()

    response = robo_cram.init_simulation(ENV_OPTIONS[int(choice)])
    print(f"{response['status'].upper()}: {response['message']}")


def park_arms():
    response = robo_cram.park_arms()
    print(f"{response['status'].upper()}: {response['message']}")


def adjust_torso():
    print(
        """
        \nSet the torso high?
        \n1) True
        \n2) False
        """
    )
    high = input("Enter your choice: ").strip()
    if len(high) == 0 or int(high) not in [1, 2]:
        high = input("Invalid choice, enter your choice: ").strip()

    response = robo_cram.adjust_torso(int(high) == 1)
    print(f"{response['status'].upper()}: {response['message']}")


def get_robot_pose():
    response = robo_cram.get_robot_pose()
    print(
        f"{response['status'].upper()}: {response['message']} ({response['payload']})"
    )


def spawn_object():
    print(
        """
        \nSelect an object to spawn:
        \n1) Cereal
        \n2) Milk
        \n3) Spoon
        \n4) Bowl
        """
    )
    obj_type = input("Enter your choice: ").strip()
    while len(obj_type) == 0 or int(obj_type) not in OBJ_TYPES:
        obj_type = input("Invalid choice, enter your choice: ").strip()

    obj_name = input("What name do you give the object: ").strip()
    while len(obj_name) == 0:
        obj_name = input("You must give the object a name: ").strip()

    coordinates_str = input(
        "Enter the coordinates to spawn the object using the format x,y,z: "
    ).strip()
    coordinates = coordinates_str.split(",")

    while True:
        while len(coordinates) != 3:
            coordinates_str = input("Invalid entry, re-try again: ").strip()
            coordinates = coordinates_str.split(",")
        try:
            coordinates = [float(i) for i in coordinates]
            break
        except ValueError:
            pass

    print(
        """
        \nSelect a colour for the object:
        \n1) Red
        \n2) Green
        \n3) Blue
        \n4) Yellow
        \n5) White
        \n6) Black
        \n7) Default colour
        """
    )
    colour = input("Enter your choice: ").strip()
    while len(colour) == 0 or int(colour) not in COLOURS:
        colour = input("Invalid choice, enter your choice: ").strip()

    response = robo_cram.spawn_object(
        OBJ_TYPES[int(obj_type)], obj_name, coordinates, COLOURS[int(colour)]
    )
    print(f"{response['status'].upper()}: {response['message']}")


def move_robot():
    coordinates_str = input(
        "Enter the coordinates to move the robot to using the format x,y,z: "
    ).strip()
    coordinates = coordinates_str.split(",")

    while True:
        while len(coordinates) != 3:
            coordinates_str = input("Invalid entry, re-try again: ").strip()
            coordinates = coordinates_str.split(",")
        try:
            coordinates = [float(i) for i in coordinates]
            break
        except ValueError:
            coordinates = []

    orientation_str = input(
        "Enter the orientation (as quaternions) to move the robot to using the format x,y,z,w: "
    ).strip()
    orientation = orientation_str.split(",")

    while True:
        while len(orientation) != 4:
            orientation_str = input("Invalid entry, re-try again: ").strip()
            orientation = orientation_str.split(",")
        try:
            orientation = [float(i) for i in orientation]
            break
        except ValueError:
            orientation = []

    response = robo_cram.move_robot(coordinates, orientation)
    print(f"{response['status'].upper()}: {response['message']}")


def is_object_type_in_environment():
    print(
        """
        \nSelect an object type to search for:
        \n1) Cereal
        \n2) Milk
        \n3) Spoon
        \n4) Bowl
        """
    )
    obj_type = input("Enter your choice: ").strip()
    if len(obj_type) == 0 or int(obj_type) not in OBJ_TYPES:
        obj_type = input("Invalid choice, enter your choice: ").strip()

    response = robo_cram.is_object_type_in_environment(OBJ_TYPES[int(obj_type)])
    print(f"{response['status'].upper()}: {response['message']}")


def is_object_in_environment():
    obj_name = input("Enter the name of the object to search for: ").strip()
    while len(obj_name) == 0:
        obj_name = input("You must enter a name: ").strip()

    response = robo_cram.is_object_in_environment(obj_name)
    print(f"{response['status'].upper()}: {response['message']}")


def is_object_type_in_location():
    print(
        """
        \nSelect an object type to search for:
        \n1) Cereal
        \n2) Milk
        \n3) Spoon
        \n4) Bowl
        """
    )
    obj_type = input("Enter your choice: ").strip()
    if len(obj_type) == 0 or int(obj_type) not in OBJ_TYPES:
        obj_type = input("Invalid choice, enter your choice: ").strip()

    print(
        """
        \nSelect a location to search for the object in:
        \n1) Kitchen island
        \n2) Sink area
        \n3) Table
        """
    )
    perception_location = input("Enter your choice: ").strip()
    if len(perception_location) == 0 or int(perception_location) not in LOCATIONS:
        perception_location = input("Invalid choice, enter your choice: ").strip()

    response = robo_cram.is_object_type_in_location(
        LOCATIONS[int(perception_location)], OBJ_TYPES[int(obj_type)]
    )
    print(f"{response['status'].upper()}: {response['message']}")


def is_object_in_location():
    obj_name = input("Enter the name of the object to search for: ").strip()
    while len(obj_name) == 0:
        obj_name = input("You must enter a name: ").strip()

    print(
        """
        \nSelect a location to search for the object in:
        \n1) Kitchen island
        \n2) Sink area
        \n3) Table
        """
    )
    perception_location = input("Enter your choice: ").strip()
    if len(perception_location) == 0 or int(perception_location) not in LOCATIONS:
        perception_location = input("Invalid choice, enter your choice: ").strip()

    response = robo_cram.is_object_in_location(
        LOCATIONS[int(perception_location)], obj_name
    )
    print(f"{response['status'].upper()}: {response['message']}")


def look_at_object():
    obj_name = input("Enter the name of the object to look at: ").strip()
    while len(obj_name) == 0:
        obj_name = input("You must enter a name: ").strip()

    response = robo_cram.look_at_object(obj_name)
    print(f"{response['status'].upper()}: {response['message']}")


def pick_and_place():
    obj_name = input("Enter the name of the object to pick: ").strip()
    while len(obj_name) == 0:
        obj_name = input("You must enter a name: ").strip()

    print(
        """
        \nSelect a location to place the object:
        \n1) Kitchen island
        \n2) Sink area
        \n3) Table
        """
    )
    destination_location = input("Enter your choice: ").strip()
    if len(destination_location) == 0 or int(destination_location) not in LOCATIONS:
        destination_location = input("Invalid choice, enter your choice: ").strip()

    response = robo_cram.pick_and_place(obj_name, LOCATIONS[int(destination_location)])
    print(f"{response['status'].upper()}: {response['message']}")


def capture_image():
    target_distance = input("Enter the camera's target distance: ").strip()
    while len(target_distance) == 0:
        target_distance = input("You must enter a target distance: ").strip()

    response = robo_cram.capture_image(float(target_distance))

    if response["status"] == "success":
        image_name_prefix = uuid.uuid4().hex
        rgb_image = response["payload"]["rgb_image"]
        depth_image = response["payload"]["depth_image"]
        segmentation_mask = response["payload"]["segmentation_mask"]

        if not os.path.exists(IMAGES_DIR):
            os.mkdir(IMAGES_DIR)

        for k, v in [
            ("rgb_image", rgb_image),
            ("depth_image", depth_image),
            ("segmentation_mask", segmentation_mask),
        ]:
            save_path = os.path.join(IMAGES_DIR, f"{image_name_prefix}_{k}.png")
            plt.figure(figsize=(10, 8))
            (
                plt.imshow(depth_image, cmap="viridis")
                if k == "depth_image"
                else plt.imshow(v)
            )
            plt.colorbar(label="Depth") if k == "depth_image" else "pass"
            plt.axis("off")
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
            print(f"Image '{k}' saved to {save_path}")

    print(f"{response['status'].upper()}: {response['message']}")


def get_objects_in_robot_view():
    target_distance = input("Enter the camera's target distance: ").strip()
    while len(target_distance) == 0:
        target_distance = input("You must enter a target distance: ").strip()

    min_pixel_count = input(
        "Enter the minimum number of pixels an object has to have for it to be detected: "
    ).strip()
    while True:
        try:
            _ = int(min_pixel_count)
            break
        except ValueError:
            min_pixel_count = input("You must enter an integer: ").strip()

    response = robo_cram.get_objects_in_robot_view(
        float(target_distance), int(min_pixel_count)
    )
    [print(f"{k}: {v}") for k, v in response["payload"].items()]
    print(f"{response['status'].upper()}: {response['message']}")


def exit_simulation():
    response = robo_cram.exit_simulation()
    print(f"{response['status'].upper()}: {response['message']}")


def run():
    MENU = {
        1: park_arms,
        2: adjust_torso,
        3: get_robot_pose,
        4: spawn_object,
        5: move_robot,
        6: is_object_type_in_environment,
        7: is_object_in_environment,
        8: is_object_type_in_location,
        9: is_object_in_location,
        10: look_at_object,
        11: pick_and_place,
        12: capture_image,
        13: get_objects_in_robot_view,
        14: exit_simulation,
    }
    exit_choice = len(MENU)

    print("--- RoboCRAM Interactive ---")
    init_simulation()

    while True:
        print(
            """
            \r--- Main Menu ---
            \r1) Park robot arms
            \r2) Adjust robot torso
            \r3) Get robot pose
            \r4) Spawn objects in the environment
            \r5) Move robot
            \r6) Find if an object of some type is in the environment
            \r7) Find if an object with some name is in the environment
            \r8) Find if an object of some type is in some location
            \r9) Find if an object with some name is in some location
            \r10) Look at an object
            \r11) Pick an object and place it elsewhere
            \r12) Capture an image using robot's camera
            \r13) Get objects in robot's view
            \r14) Exit simulation
            """
        )

        choice = input("Enter your choice: ").strip()
        if len(choice) == 0 or int(choice) not in MENU:
            print("Invalid choice. Please try again.")
            continue

        MENU[int(choice)]()

        if int(choice) == exit_choice:
            break


if __name__ == "__main__":
    run()
