import pybullet as p
import numpy as np
from pycram.worlds.bullet_world import BulletWorld
from pycram.world_concepts.world_object import Object
from pycram.datastructures.pose import Pose

def setup_simulation():
    """Initialize a BulletWorld with a robot and an object."""
    # Create a BulletWorld in GUI mode for visualization
    world = BulletWorld("GUI")
    
    # Add a kitchen environment
    kitchen = Object("kitchen", "ENVIRONMENT", "kitchen.urdf")
    
    # Add a PR2 robot
    robot = Object("pr2", "ROBOT", "pr2.urdf", pose=Pose([0, 0, 0]))
    
    # Add a cereal box
    cereal = Object("cereal", "BREAKFAST_CEREAL", "breakfast_cereal.stl", pose=Pose([1.4, 1, 0.95]))
    
    return world

def get_camera_image(width=640, height=480, view_point=[2, 2, 2], target_point=[0, 0, 0], up_vector=[0, 0, 1]):
    """
    Capture and return an image from the simulation camera.
    
    Args:
        width (int): Image width in pixels
        height (int): Image height in pixels
        view_point (list): Camera position [x, y, z]
        target_point (list): Point the camera looks at [x, y, z]
        up_vector (list): Camera up direction [x, y, z]
    
    Returns:
        numpy.ndarray: RGB image as a 3D array (height, width, 3)
    """
    # Compute view and projection matrices using PyBullet
    view_matrix = p.computeViewMatrix(
        cameraEyePosition=view_point,
        cameraTargetPosition=target_point,
        cameraUpVector=up_vector
    )
    projection_matrix = p.computeProjectionMatrixFOV(
        fov=60,  # Field of view in degrees
        aspect=float(width) / height,
        nearVal=0.1,
        farVal=100.0
    )
    
    # Capture the image
    # Returns: [width, height, rgbPixels, depthPixels, segmentationMask]
    img_data = p.getCameraImage(
        width=width,
        height=height,
        viewMatrix=view_matrix,
        projectionMatrix=projection_matrix,
        renderer=p.ER_BULLET_HARDWARE_OPENGL  # Use OpenGL for better quality
    )
    
    # Extract RGB image (img_data[2] is the RGB pixel array)
    rgb_img = np.reshape(img_data[2], (height, width, 4))[:, :, :3]  # Drop alpha channel
    
    return rgb_img

def main():
    # Set up the simulation
    world = setup_simulation()
    
    # Capture an image
    image = get_camera_image(
        width=640,
        height=480,
        view_point=[2, 2, 2],  # Camera positioned above the scene
        target_point=[0, 0, 0],  # Looking at the origin
        up_vector=[0, 0, 1]    # Up is along Z-axis
    )
    
    # Optional: Save or display the image (requires additional libraries like PIL or OpenCV)
    from PIL import Image
    img = Image.fromarray(image, 'RGB')
    img.save("simulation_image.png")
    print("Image saved as simulation_image.png")
    
    # Keep the simulation running to view it
    input("Press Enter to exit...")
    
    # Close the world
    world.exit()

if __name__ == "__main__":
    main()