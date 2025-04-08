from pycram.datastructures.enums import Arms

import robo_cram


ENV_OPTIONS = {
    1: robo_cram.Env.KITCHEN,
    2: robo_cram.Env.APARTMENT
}
OBJ_TYPES = {
    1: robo_cram.Obj.CEREAL,
    2: robo_cram.Obj.MILK,
    3: robo_cram.Obj.SPOON,
    4: robo_cram.Obj.BOWL
}
COLOURS = {
    1: robo_cram.Colour.RED,
    2: robo_cram.Colour.GREEN,
    3: robo_cram.Colour.BLUE,
    4: robo_cram.Colour.YELLOW,
    5: robo_cram.Colour.WHITE,
    6: robo_cram.Colour.BLACK,
    7: robo_cram.Colour.DEFAULT
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

    robo_cram.init_simulation(ENV_OPTIONS[int(choice)])


def robot_pack_arms():
    robo_cram.robot_pack_arms()


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

    coordinates_str = input("Enter the coordinates to spawn the object using the format x,y,z: ").strip()
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
    
    result = robo_cram.spawn_object(OBJ_TYPES[int(obj_type)], obj_name, coordinates, COLOURS[int(colour)])
    print(f"{result['status'].upper()}: {result['message']}")


def move_robot():
    coordinates_str = input("Enter the coordinates to move the robot to using the format x,y,z: ").strip()
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

    result = robo_cram.move_robot(coordinates)
    print(f"{result['status'].upper()}: {result['message']}")


def is_object_type_in_environment():
    print(
        """
        \nSelect an object type to detect:
        \n1) Cereal
        \n2) Milk
        \n3) Spoon
        \n4) Bowl
        """
    )
    obj_type = input("Enter your choice: ").strip()
    if len(obj_type) == 0 or int(obj_type) not in OBJ_TYPES:
        obj_type = input("Invalid choice, enter your choice: ").strip()

    result = robo_cram.is_object_type_in_environment(OBJ_TYPES[int(obj_type)])
    print(f"{result['status'].upper()}: {result['message']}")


def is_object_in_environment():
    obj_name = input("Enter the name of the object: ").strip()
    while len(obj_name) == 0:
        obj_name = input("You must enter a name: ").strip()

    result = robo_cram.is_object_in_environment(obj_name)
    print(f"{result['status'].upper()}: {result['message']}")


def is_object_type_in_area():
    perception_area = input("Where do you want to search for objects: ").strip()
    while len(perception_area) == 0:
        perception_area = input("You must enter an area to search for objects: ").strip()

    result = robo_cram.get_objects_in_an_area(perception_area)
    print(f"{result['status'].upper()}: {result['message']}")


def is_object_in_area():
    perception_area = input("Where do you want to search for objects: ").strip()
    while len(perception_area) == 0:
        perception_area = input("You must enter an area to search for objects: ").strip()

    result = robo_cram.get_objects_in_an_area(perception_area)
    print(f"{result['status'].upper()}: {result['message']}")


def pick_and_place():
    robo_cram.pick_and_place()


def exit_simulation():
    robo_cram.exit_simulation()


def run():
    MENU = {
        1: robot_pack_arms,
        2: spawn_object,
        3: move_robot,
        4: is_object_type_in_environment,
        5: is_object_in_environment,
        6: is_object_type_in_area,
        7: is_object_in_area,
        8: pick_and_place,
        9: exit_simulation,
    }
    print("--- RoboCRAM Interactive ---")
    init_simulation()

    while True:
        print(
            """
            \r--- Main Menu ---
            \r1) Pack robot arms
            \r2) Spawn objects in the environment
            \r3) Move robot
            \r4) Find if an object of some type is in the environment
            \r5) Find if an object with some name is in the environment
            \r6) Find if an object of some type is in some area
            \r7) Find if an object with some name is in some area
            \r8) Pick an object and place it elsewhere
            \r9) Exit simulation
            """
        )

        choice = input("Enter your choice: ").strip()
        if len(choice) == 0 or int(choice) not in MENU:
            print("Invalid choice. Please try again.")
            continue

        MENU[int(choice)]()

        if int(choice) == 9:
            break


if __name__ == "__main__":
    run()
