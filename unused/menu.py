#!/usr/bin/env python3
"""
Main entry point for the PyCRAM interactive simulation.
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

def main():
    """
    Main function to run the interactive simulation.
    It creates the environment (spawning both the environment and the robot)
    and then enters a menu loop for additional actions.
    """
    try:
        print("\n--- Interactive PyCRAM Modular Demo ---\n")
        env_obj, world = create_environment()  # Now create_environment returns both env_obj and world
        
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
                spawn_objects()
            elif choice == "2":
                move_robot()
            elif choice == "3":
                pickup_and_place()
            elif choice == "4":
                robot_perceive()
            elif choice == "5":
                look_for_object()
            elif choice == "6":
                unpack_arms()
            elif choice == "7":
                detect_object()
            elif choice == "8":
                transport_object()
            elif choice == "9":
                exit_simulation()
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print("CRAM error in main loop:", e)
            import traceback
            traceback.print_exc()  # Print the full traceback for debugging
    
if __name__ == "__main__":
    main()
