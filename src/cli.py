from pycram.datastructures.enums import Arms

import robo_cram


def init_simulation():
    env_options = {
        1: robo_cram.Env.KITCHEN,
        2: robo_cram.Env.APARTMENT
    }

    print(
        """
        \rSelect environment to create:
        \r1) Kitchen
        \r2) Apartment
        """
    )
    choice = int(input("Enter your choice: ").strip())
    while choice not in env_options:
        choice = int(input("Invalid choice, enter your choice: ").strip())

    robo_cram.init_simulation(env_options[choice])


def exit_simulation():
    robo_cram.exit_simulation()


def spawn_object():
    obj_types = {
        1: robo_cram.Obj.CEREAL,
        2: robo_cram.Obj.MILK,
        3: robo_cram.Obj.SPOON,
        4: robo_cram.Obj.BOWL
    }
    colours = {
        1: robo_cram.Colour.RED,
        2: robo_cram.Colour.GREEN,
        3: robo_cram.Colour.BLUE,
        4: robo_cram.Colour.YELLOW,
        5: robo_cram.Colour.WHITE,
        6: robo_cram.Colour.BLACK,
        7: robo_cram.Colour.DEFAULT
    }

    print(
        """
        \nSelect an object to create:
        \n1) Cereal
        \n2) Milk
        \n3) Spoon
        \n4) Bowl
        """
    )
    obj_type = int(input("Enter your choice: ").strip())
    while obj_type not in obj_types:
        obj_type = int(input("Invalid choice, enter your choice: ").strip())

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
    colour = int(input("Enter your choice: ").strip())
    while colour not in colours:
        colour = int(input("Invalid choice, enter your choice: ").strip())
    
    robo_cram.spawn_object(obj_types[obj_type], coordinates, colour)


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
            pass

    robo_cram.move_robot(coordinates)


def pickup_and_place():
    obj_types = {
        1: robo_cram.Obj.CEREAL,
        2: robo_cram.Obj.MILK,
        3: robo_cram.Obj.SPOON,
        4: robo_cram.Obj.BOWL
    }
    arms = {
        1: Arms.RIGHT,
        2: Arms.LEFT
    }

    print(
        """
        \nSelect an object to pick and place somewhere else:
        \n1) Cereal
        \n2) Milk
        \n3) Spoon
        \n4) Bowl
        """
    )
    obj = int(input("Enter your choice: ").strip())
    if obj not in obj_types:
        obj = int(input("Invalid choice, enter your choice: ").strip())

    coordinates_str = input("Enter the coordinates to place the object at using the format x,y,z: ").strip()
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
        \nSelect an arm to use:
        \n1) Right
        \n2) Left
        """
    )
    arm = int(input("Enter your choice: ").strip())
    if arm not in arms:
        arm = int(input("Invalid choice, enter your choice: ").strip())

    robo_cram.pickup_and_place(obj_types[obj], coordinates, arms[arm])


def robot_perceive():
    perception_area = input("Where do you want the robot to perceive: ").strip()
    robo_cram.robot_perceive(perception_area)


def look_for_object():
    obj_types = {
        1: robo_cram.Obj.CEREAL,
        2: robo_cram.Obj.MILK,
        3: robo_cram.Obj.SPOON,
        4: robo_cram.Obj.BOWL
    }

    print(
        """
        \nSelect an object to look for:
        \n1) Cereal
        \n2) Milk
        \n3) Spoon
        \n4) Bowl
        """
    )
    obj = int(input("Enter your choice: ").strip())
    if obj not in obj_types:
        obj = int(input("Invalid choice, enter your choice: ").strip())

    robo_cram.look_for_object(obj_types[obj])


def unpack_arms():
    robo_cram.unpack_arms()


def detect_object():
    obj_types = {
        1: robo_cram.Obj.CEREAL,
        2: robo_cram.Obj.MILK,
        3: robo_cram.Obj.SPOON,
        4: robo_cram.Obj.BOWL
    }

    print(
        """
        \nSelect an object detect:
        \n1) Cereal
        \n2) Milk
        \n3) Spoon
        \n4) Bowl
        """
    )
    obj = int(input("Enter your choice: ").strip())
    if obj not in obj_types:
        obj = int(input("Invalid choice, enter your choice: ").strip())

    robo_cram.detect_object(obj_types[obj])


def transport_object():
    obj_types = {
        1: robo_cram.Obj.CEREAL,
        2: robo_cram.Obj.MILK,
        3: robo_cram.Obj.SPOON,
        4: robo_cram.Obj.BOWL
    }
    arms = {
        1: Arms.RIGHT,
        2: Arms.LEFT
    }

    print(
        """
        \nSelect an object to transport:
        \n1) Cereal
        \n2) Milk
        \n3) Spoon
        \n4) Bowl
        """
    )
    obj = int(input("Enter your choice: ").strip())
    if obj not in obj_types:
        obj = int(input("Invalid choice, enter your choice: ").strip())

    coordinates_str = input("Enter the coordinates to transport the object to using the format x,y,z: ").strip()
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
        \nSelect an arm to use:
        \n1) Right
        \n2) Left
        """
    )
    arm = int(input("Enter your choice: ").strip())
    if arm not in arms:
        arm = int(input("Invalid choice, enter your choice: ").strip())

    robo_cram.transport_object(obj_types[obj], coordinates, arms[arm])


def run():
    choice_to_command = {
        1: spawn_object,
        2: move_robot,
        3: pickup_and_place,
        4: robot_perceive,
        5: look_for_object,
        6: unpack_arms,
        7: detect_object,
        8: transport_object,
        9: exit_simulation,
    }

    print("--- Interactive RoboCRAM Demo ---")
    init_simulation()

    while True:
        print(
            """
            \r--- Main Menu ---
            \r1) Add Objects
            \r2) Move Robot
            \r3) Pickup and Place Item
            \r4) Robot Perception
            \r5) Look for Object
            \r6) Unpack Arms
            \r7) Detect Object
            \r8) Transport Object
            \r9) Exit Simulation
            """
        )

        choice = int(input("Enter your choice: ").strip())
        if choice not in choice_to_command:
            print("Invalid choice. Please try again.")
            continue

        choice_to_command[choice]()

        if choice == 9:
            break


if __name__ == "__main__":
    run()
