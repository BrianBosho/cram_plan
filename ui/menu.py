#!/usr/bin/env python3
from environment import world

def display_menu():
    """
    Display the interactive menu options.
    
    Returns:
        str: The user's menu choice
    """
    print("\n--- Main Menu ---")
    print("1) Add Objects")
    print("2) Move Robot")
    print("3) Pickup and Place Item")
    print("4) Robot Perception")
    print("5) Look for Object")
    print("6) Unpack Arms")
    print("7) Detect Object")
    print("8) Transport Object")
    print("9) Exit Simulation")
    return input("Enter your choice: ").strip()

def exit_simulation():
    """
    Clean up and exit the simulation.
    """
    try:
        if world is not None:
            world.exit()
        print("Simulation ended.")
        return True
    except Exception as e:
        print("CRAM error during simulation exit:", e)
        return False
