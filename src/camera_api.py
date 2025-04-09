#!/usr/bin/env python3

import base64
import os
import signal
import sys
from io import BytesIO
from typing import Any, Dict, List, Optional

# Import the interactive_sim module itself, not just its functions
import interactive_sim
import matplotlib.pyplot as plt
import numpy as np

# Import PR2 camera utilities
import pr2_camera_utils
import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# We'll also import the individual functions for clarity
from interactive_sim import (
    add_objects,
    capture_camera_image,
    create_objects,
    demo_advanced_camera_functions,
    demo_camera,
    demo_object_distances,
    exit_world,
    initialize_world,
    run_robot_actions,
    spawn_objects,
)
from pydantic import BaseModel

# Try to import robot movement function
try:
    from robot_actions.api import move_robot_to_location

    has_robot_movement = True
except ImportError:
    print(
        "Warning: robot_actions.api module not found. Robot movement functionality will be disabled."
    )
    has_robot_movement = False

    # Define a placeholder function for move_robot_to_location
    def move_robot_to_location(*args, **kwargs):
        raise NotImplementedError("Robot movement functionality is not available.")


# Create FastAPI application
app = FastAPI(
    title="PyCRAM Camera API",
    description="API for interacting with PyCRAM camera and robot functions",
)

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory for HTML rendering
templates = Jinja2Templates(directory=".")

# Initialize in-memory image storage
images_store = {}


# Pydantic models for request validation
class SpawnObjectRequest(BaseModel):
    object_choice: str
    coordinates: List[float]
    color: Optional[str] = None
    name: Optional[str] = None


class CameraImageRequest(BaseModel):
    display: bool = True
    save_path: Optional[str] = None
    target_distance: float = 2.0


class ObjectVisibilityRequest(BaseModel):
    object_name: str
    threshold: float = 0.6


class LookAtObjectRequest(BaseModel):
    object_name: str
    distance: float = 1.5
    elevation_angle: float = 30
    azimuth_angle: float = 45


class ScanEnvironmentRequest(BaseModel):
    angles: int = 4


class DistanceRequest(BaseModel):
    source_object: Optional[str] = None
    destination_objects: Optional[List[str]] = None
    exclude_types: List[str] = ["floor", "wall", "kitchen", "ground"]
    top_n: int = 10


class Visualization3DRequest(BaseModel):
    source_object: Optional[str] = None
    max_objects: int = 8


# Robot movement model
class RobotMoveRequest(BaseModel):
    x: float
    y: float
    z: Optional[float] = 0.0
    orientation: Optional[List[float]] = None


# Track object counts for auto-naming
object_counters = {}


# Setup events
@app.on_event("startup")
async def startup_event():
    """Initialize resources when the application starts up"""
    # Copy static files
    setup_static_files()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when the application shuts down"""
    if interactive_sim.world is not None:
        print("Shutting down the world...")
        exit_world()
    print("Application shutdown complete.")


# Helper function to convert matplotlib figure to base64 image
def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    return img_str


# Save image and return URL for web display
def save_image_for_web(fig, name="image"):
    img_id = f"{name}_{len(images_store)}"
    img_str = fig_to_base64(fig)
    images_store[img_id] = img_str
    return {"image_id": img_id, "data": img_str}


# Copy the JavaScript file to the static directory on startup
def setup_static_files():
    try:
        # Create a copy of the JS file in the static directory
        js_content = ""
        with open("camera_view.js", "r") as js_file:
            js_content = js_file.read()

        with open("static/camera_view.js", "w") as static_js:
            static_js.write(js_content)

        print("Static files copied successfully.")
    except Exception as e:
        print(f"Warning: Failed to copy static files: {str(e)}")
        print("You may need to manually copy camera_view.js to the static directory.")


# Helper function to check if world is initialized
def ensure_world_initialized():
    """Ensure the world is initialized, raise an exception if not"""
    # Access the world variable directly from the interactive_sim module
    if interactive_sim.world is None:
        raise ValueError("World is not initialized. Please initialize the world first.")
    return interactive_sim.world


# API Routes
@app.get("/", response_class=HTMLResponse)
async def get_html(request: Request):
    return templates.TemplateResponse("camera_view.html", {"request": request})


# Serve the JavaScript file directly if needed
@app.get("/camera_view.js")
async def get_js():
    try:
        with open("camera_view.js", "r") as js_file:
            js_content = js_file.read()
        return HTMLResponse(content=js_content, media_type="application/javascript")
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"JavaScript file not found: {str(e)}"
        )


@app.post("/initialize_world")
async def api_initialize_world():
    try:
        if interactive_sim.world is not None:
            print("World is already initialized")
            return {"status": "success", "message": "World is already initialized"}

        print("Initializing world...")
        # Call the initialize_world function
        initialize_world()

        # Verify that the world was properly initialized
        if interactive_sim.world is None:
            return {
                "status": "error",
                "message": "Failed to initialize world. The world variable is still None.",
            }

        print(f"World initialized: {interactive_sim.world}")
        return {"status": "success", "message": "World initialized successfully"}
    except Exception as e:
        print(f"Error initializing world: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/create_objects")
async def api_create_objects():
    try:
        world = ensure_world_initialized()
        create_objects()

        # Get list of all objects in the world, including kitchen and PR2
        objects_info = []
        for obj in world.objects:
            if hasattr(obj, "name"):
                position = obj.get_position()
                # Create an object info dictionary
                obj_info = {
                    "name": obj.name,
                    "type": str(type(obj).__name__),
                    "position": (
                        [position.x, position.y, position.z] if position else "unknown"
                    ),
                }
                objects_info.append(obj_info)

        # Create a detailed message listing all objects
        message = "Objects created successfully:\n"
        for obj in objects_info:
            pos_str = f"at {obj['position']}" if obj["position"] != "unknown" else ""
            message += f"- {obj['name']} ({obj['type']}) {pos_str}\n"

        return {"status": "success", "message": message, "objects": objects_info}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/add_objects")
async def api_add_objects():
    try:
        world = ensure_world_initialized()
        add_objects()
        return {"status": "success", "message": "Additional objects added successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/spawn_object")
async def api_spawn_object(request: SpawnObjectRequest):
    try:
        world = ensure_world_initialized()

        # Import required modules
        from pr2_camera_utils import spawn_object

        # Extract data from request
        object_choice = request.object_choice
        coordinates = request.coordinates
        color = request.color
        name = request.name

        # Spawn the object with optional custom name
        obj = spawn_object(object_choice, coordinates, color, name)

        if obj is None:
            return {"status": "error", "message": "Failed to spawn object"}

        return {
            "status": "success",
            "message": f"Object {obj.name} of type {object_choice} created at {coordinates}",
            "name": obj.name,
            "type": object_choice,
            "coordinates": coordinates,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/run_robot_actions")
async def api_run_robot_actions():
    try:
        world = ensure_world_initialized()
        run_robot_actions()
        return {"status": "success", "message": "Robot actions completed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/capture_camera_image")
async def api_capture_camera_image(request: CameraImageRequest):
    try:
        world = ensure_world_initialized()
        # Create a plotting figure for the image
        plt.figure(figsize=(10, 8))

        save_result = None
        saved_path = None

        # Capture the image but don't display it (we'll handle display via the API)
        try:
            rgb_image, depth_image, segmentation_mask = capture_camera_image(
                display=False,
                save_path=request.save_path if request.save_path else None,
                target_distance=request.target_distance,
            )

            # If a save path was requested, verify the save
            if request.save_path:
                try:
                    saved_path = os.path.abspath(request.save_path)
                    if os.path.exists(saved_path):
                        save_result = f"Image saved to: {saved_path}"
                    else:
                        save_result = (
                            f"Warning: Unable to verify saved file at {saved_path}"
                        )
                except Exception as save_err:
                    save_result = (
                        f"Warning: Error verifying saved file: {str(save_err)}"
                    )
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to capture camera image: {str(e)}",
            }

        # Plot the image
        plt.imshow(rgb_image)
        plt.axis("off")
        plt.title("Robot Camera View")
        plt.tight_layout()

        # Convert the figure to base64 for web display
        image_data = save_image_for_web(plt.gcf(), "camera")
        plt.close()

        message = "Camera image captured successfully"
        if save_result:
            message += f". {save_result}"

        response_data = {"status": "success", "message": message, "image": image_data}

        if saved_path:
            response_data["saved_to"] = saved_path

        return response_data
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/demo_camera")
async def api_demo_camera():
    try:
        world = ensure_world_initialized()

        # Use PR2 camera utilities for the demo
        pr2_camera_utils.initialize(world)

        # Capture image and save for web
        plt.figure(figsize=(10, 8))
        rgb_image, depth_image, segmentation_mask = capture_camera_image(display=False)
        plt.imshow(rgb_image)
        plt.axis("off")
        plt.title("Robot Camera Demo View")
        plt.tight_layout()

        image_data = save_image_for_web(plt.gcf(), "demo_camera")
        plt.close()

        return {
            "status": "success",
            "message": "Camera demo completed successfully",
            "image": image_data,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/visualize_depth_map")
async def api_visualize_depth_map(colormap: str = "plasma"):
    try:
        world = ensure_world_initialized()

        # Initialize camera utilities
        try:
            pr2_camera_utils.initialize(world)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize camera utilities: {str(e)}",
            }

        # Capture the raw depth image first
        try:
            _, depth_image, _ = capture_camera_image(display=False)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to capture camera image: {str(e)}",
            }

        # Create a new figure for depth visualization
        fig = plt.figure(figsize=(10, 8))
        try:
            # Use plt's imshow directly instead of pr2_camera_utils visualization which might show locally
            plt.imshow(depth_image, cmap=colormap)
            plt.colorbar(label="Depth")
            plt.title("Depth Map")
            plt.axis("off")
            plt.tight_layout()
        except Exception as e:
            plt.close()
            return {
                "status": "error",
                "message": f"Failed to visualize depth map: {str(e)}",
            }

        # Save for web display
        image_data = save_image_for_web(plt.gcf(), "depth_map")
        plt.close()

        return {
            "status": "success",
            "message": "Depth map visualization completed",
            "image": image_data,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/identify_objects")
async def api_identify_objects():
    try:
        world = ensure_world_initialized()

        # Initialize camera utilities
        try:
            pr2_camera_utils.initialize(world)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize camera utilities: {str(e)}",
            }

        # Identify objects
        try:
            visible_objects = pr2_camera_utils.identify_objects_in_view(
                display_segmentation=False
            )
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to identify objects: {str(e)}",
            }

        # Get the camera image for visualization
        rgb_image, _, _ = capture_camera_image(display=False)

        # Process object information for response
        object_list = []
        if visible_objects:
            for obj_id, data in visible_objects.items():
                object_list.append(
                    {
                        "name": data.get("name", "unknown"),
                        "pixel_count": data.get("pixel_count", 0),
                        "id": str(obj_id),
                    }
                )

        # Format a message with identified objects
        if object_list:
            message = f"Identified {len(object_list)} objects:\n"
            for obj in object_list:
                message += (
                    f"- {obj['name']} (ID: {obj['id']}, Pixels: {obj['pixel_count']})\n"
                )
        else:
            message = "No objects identified in the camera view."

        # Create visualization
        fig = plt.figure(figsize=(10, 8))
        try:
            # Create a custom visualization
            plt.imshow(rgb_image)
            plt.title("Object Identification")
            plt.axis("off")

            # Add object labels if available
            for obj_data in object_list:
                name = obj_data["name"]
                px_count = obj_data["pixel_count"]
                plt.annotate(
                    f"{name} ({px_count} px)",
                    xy=(10, 20 + 20 * object_list.index(obj_data)),
                    color="red",
                    fontsize=12,
                    bbox=dict(facecolor="white", alpha=0.7),
                )

            plt.tight_layout()
        except Exception as e:
            plt.close()
            return {
                "status": "error",
                "message": f"Failed to visualize object identification: {str(e)}",
            }

        # Save for web display
        image_data = save_image_for_web(plt.gcf(), "object_identification")
        plt.close()

        return {
            "status": "success",
            "message": message,
            "objects": object_list,
            "image": image_data,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/check_object_visibility")
async def api_check_object_visibility(request: ObjectVisibilityRequest):
    try:
        world = ensure_world_initialized()

        # Initialize camera utilities
        try:
            pr2_camera_utils.initialize(world)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize camera utilities: {str(e)}",
            }

        # Check visibility
        try:
            visibility_result = pr2_camera_utils.check_object_visibility(
                request.object_name, threshold=request.threshold, display=False
            )
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to check object visibility: {str(e)}",
            }

        # Create visualization
        fig = plt.figure(figsize=(10, 8))
        try:
            visibility_image = pr2_camera_utils.visualize_object_visibility(
                request.object_name, display=False
            )
        except Exception as e:
            plt.close()
            return {
                "status": "error",
                "message": f"Failed to visualize object visibility: {str(e)}",
            }

        # Save for web display
        image_data = save_image_for_web(plt.gcf(), "visibility")
        plt.close()

        return {
            "status": "success",
            "message": f"Visibility of {request.object_name}: {visibility_result}",
            "visibility": visibility_result,
            "image": image_data,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/find_occluding_objects")
async def api_find_occluding_objects(object_name: str):
    try:
        world = ensure_world_initialized()

        # Initialize camera utilities
        try:
            pr2_camera_utils.initialize(world)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize camera utilities: {str(e)}",
            }

        # Find occluding objects
        try:
            occluding_objects = pr2_camera_utils.find_occluding_objects(
                object_name, display=False
            )
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to find occluding objects: {str(e)}",
            }

        # Create visualization
        fig = plt.figure(figsize=(10, 8))
        try:
            occlusion_image = pr2_camera_utils.visualize_occlusions(
                object_name, display=False
            )
        except Exception as e:
            plt.close()
            return {
                "status": "error",
                "message": f"Failed to visualize occlusions: {str(e)}",
            }

        # Save for web display
        image_data = save_image_for_web(plt.gcf(), "occlusions")
        plt.close()

        return {
            "status": "success",
            "message": f"Found {len(occluding_objects) if occluding_objects else 0} occluding objects",
            "occluding_objects": occluding_objects,
            "image": image_data,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/estimate_distances")
async def api_estimate_distances():
    try:
        world = ensure_world_initialized()

        # Initialize camera utilities
        try:
            pr2_camera_utils.initialize(world)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize camera utilities: {str(e)}",
            }

        # Estimate distances
        try:
            distances = pr2_camera_utils.estimate_distances_to_objects(display=False)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to estimate distances: {str(e)}",
            }

        # Create visualization
        fig = plt.figure(figsize=(10, 8))
        try:
            distance_image = pr2_camera_utils.visualize_distances(display=False)
        except Exception as e:
            plt.close()
            return {
                "status": "error",
                "message": f"Failed to visualize distances: {str(e)}",
            }

        # Save for web display
        image_data = save_image_for_web(plt.gcf(), "distances")
        plt.close()

        return {
            "status": "success",
            "message": "Distance estimation completed",
            "distances": distances,
            "image": image_data,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/look_at_object")
async def api_look_at_object(request: LookAtObjectRequest):
    try:
        world = ensure_world_initialized()

        # Initialize camera utilities
        try:
            pr2_camera_utils.initialize(world)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize camera utilities: {str(e)}",
            }

        # Look at object
        try:
            pr2_camera_utils.look_at_object(
                request.object_name,
                distance=request.distance,
                elevation_angle=request.elevation_angle,
                azimuth_angle=request.azimuth_angle,
            )
        except Exception as e:
            return {"status": "error", "message": f"Failed to look at object: {str(e)}"}

        # Capture the view after looking at the object
        fig = plt.figure(figsize=(10, 8))
        try:
            rgb_image, _, _ = capture_camera_image(display=False)
            plt.imshow(rgb_image)
            plt.axis("off")
            plt.title(f"View of {request.object_name}")
            plt.tight_layout()
        except Exception as e:
            plt.close()
            return {
                "status": "error",
                "message": f"Failed to capture view after looking at object: {str(e)}",
            }

        # Save for web display
        image_data = save_image_for_web(plt.gcf(), "look_at")
        plt.close()

        return {
            "status": "success",
            "message": f"Looking at {request.object_name} completed",
            "image": image_data,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/scan_environment")
async def api_scan_environment(request: ScanEnvironmentRequest):
    try:
        world = ensure_world_initialized()

        # Initialize camera utilities
        try:
            pr2_camera_utils.initialize(world)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize camera utilities: {str(e)}",
            }

        # Scan environment
        try:
            scan_images = pr2_camera_utils.scan_environment(
                angles=request.angles, display=False
            )
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to scan environment: {str(e)}",
            }

        # Process all scan images for web display
        image_data_list = []
        for i, img in enumerate(scan_images):
            try:
                fig = plt.figure(figsize=(10, 8))
                plt.imshow(img)
                plt.axis("off")
                plt.title(f"Scan View {i+1}")
                plt.tight_layout()

                image_data = save_image_for_web(plt.gcf(), f"scan_{i}")
                image_data_list.append(image_data)
                plt.close()
            except Exception as e:
                plt.close()
                return {
                    "status": "error",
                    "message": f"Failed to process scan image {i+1}: {str(e)}",
                }

        return {
            "status": "success",
            "message": f"Environment scan completed with {request.angles} angles",
            "images": image_data_list,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/object_distances")
async def api_object_distances(request: DistanceRequest):
    try:
        world = ensure_world_initialized()

        # Initialize camera utilities
        try:
            pr2_camera_utils.initialize(world)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize camera utilities: {str(e)}",
            }

        # Calculate distances
        try:
            # The function expects target_objects not destination_objects
            distances = pr2_camera_utils.calculate_object_distances(
                source_object=request.source_object,
                target_objects=request.destination_objects,
                exclude_types=request.exclude_types,
            )

            if not distances:
                return {
                    "status": "success",
                    "message": "No distances found between objects",
                    "distances": [],
                }

            # Format distances for the response
            formatted_distances = []
            for key, distance in distances.items():
                if "-to-" in key:
                    obj1, obj2 = key.split("-to-")
                    formatted_distances.append(
                        {"object1": obj1, "object2": obj2, "distance": float(distance)}
                    )
                else:
                    # Single source to one target case
                    formatted_distances.append(
                        {
                            "object1": request.source_object,
                            "object2": key,
                            "distance": float(distance),
                        }
                    )

            # Sort by distance
            formatted_distances.sort(key=lambda x: x["distance"])

            # Limit to top_n if specified
            if request.top_n > 0 and len(formatted_distances) > request.top_n:
                formatted_distances = formatted_distances[: request.top_n]

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to calculate object distances: {str(e)}",
            }

        # Create a visualization of the distances
        fig = plt.figure(figsize=(10, 8))
        try:
            # Create a table visualization
            plt.axis("off")
            plt.title("Object Distances")

            # Create a table with the distances
            table_data = []
            table_data.append(["Object 1", "Object 2", "Distance (m)"])

            for item in formatted_distances:
                table_data.append(
                    [item["object1"], item["object2"], f"{item['distance']:.3f}"]
                )

            table = plt.table(
                cellText=table_data,
                cellLoc="center",
                loc="center",
                colWidths=[0.3, 0.3, 0.2],
            )
            table.auto_set_font_size(False)
            table.set_fontsize(12)
            table.scale(1.2, 1.5)

            plt.tight_layout()
        except Exception as e:
            plt.close()
            return {
                "status": "error",
                "message": f"Failed to display object distances: {str(e)}",
            }

        # Save for web display
        image_data = save_image_for_web(plt.gcf(), "distance_table")
        plt.close()

        return {
            "status": "success",
            "message": f"Found {len(formatted_distances)} distance measurements",
            "distances": formatted_distances,
            "image": image_data,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/visualize_3d_distances")
async def api_visualize_3d_distances(request: Visualization3DRequest):
    try:
        world = ensure_world_initialized()

        # Initialize camera utilities
        try:
            pr2_camera_utils.initialize(world)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize camera utilities: {str(e)}",
            }

        # Create 3D visualization
        fig = plt.figure(figsize=(10, 8))
        try:
            pr2_camera_utils.visualize_object_distances_3d(
                source_object=request.source_object,
                max_objects=request.max_objects,
                display=False,
            )
        except Exception as e:
            plt.close()
            return {
                "status": "error",
                "message": f"Failed to visualize 3D distances: {str(e)}",
            }

        # Save for web display
        image_data = save_image_for_web(plt.gcf(), "3d_viz")
        plt.close()

        return {
            "status": "success",
            "message": "3D visualization completed",
            "image": image_data,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/advanced_camera_demo")
async def api_advanced_camera_demo():
    try:
        world = ensure_world_initialized()

        # Create a list to hold all the images generated
        image_list = []

        # Initialize camera utilities
        try:
            pr2_camera_utils.initialize(world)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize camera utilities: {str(e)}",
            }

        # 1. Depth map
        try:
            fig = plt.figure(figsize=(10, 8))
            pr2_camera_utils.visualize_depth_map(colormap="plasma", display=False)
            image_list.append(save_image_for_web(plt.gcf(), "demo_depth"))
            plt.close()
        except Exception as e:
            plt.close()
            return {
                "status": "error",
                "message": f"Failed to visualize depth map: {str(e)}",
            }

        # 2. Object identification
        try:
            fig = plt.figure(figsize=(10, 8))
            pr2_camera_utils.visualize_object_identification(display=False)
            image_list.append(save_image_for_web(plt.gcf(), "demo_objects"))
            plt.close()
        except Exception as e:
            plt.close()
            return {
                "status": "error",
                "message": f"Failed to visualize object identification: {str(e)}",
            }

        # 3. Distance estimation
        try:
            fig = plt.figure(figsize=(10, 8))
            pr2_camera_utils.visualize_distances(display=False)
            image_list.append(save_image_for_web(plt.gcf(), "demo_distances"))
            plt.close()
        except Exception as e:
            plt.close()
            return {
                "status": "error",
                "message": f"Failed to visualize distances: {str(e)}",
            }

        return {
            "status": "success",
            "message": "Advanced camera demo completed",
            "images": image_list,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/exit_world")
async def api_exit_world():
    try:
        if interactive_sim.world is None:
            return {"status": "success", "message": "World is already exited"}

        exit_world()
        return {"status": "success", "message": "World exited successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/images/{image_id}")
async def get_image(image_id: str):
    if image_id in images_store:
        return {"data": images_store[image_id]}
    raise HTTPException(status_code=404, detail="Image not found")


@app.get("/get_available_objects")
async def get_available_objects():
    try:
        world = ensure_world_initialized()

        objects = world.objects
        object_names = [obj.name for obj in objects if hasattr(obj, "name")]
        return {"status": "success", "objects": object_names}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/move_robot")
async def api_move_robot(request: RobotMoveRequest):
    try:
        world = ensure_world_initialized()

        if not has_robot_movement:
            return {
                "status": "error",
                "message": "Robot movement functionality is not available.",
            }

        # Create the target location
        target_location = [request.x, request.y, request.z]

        # Add optional orientation if provided
        if request.orientation:
            target_location.extend(request.orientation)

        print(f"Moving robot to location: {target_location}")

        # Call the move_robot_to_location function
        try:
            result = move_robot_to_location(target_location)
            return {
                "status": "success",
                "message": f"Robot moved to location {target_location}",
                "result": result,
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to move robot: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Setup signal handlers for graceful shutdown
def signal_handler(sig, frame):
    print("Shutdown signal received, exiting gracefully...")
    if interactive_sim.world is not None:
        exit_world()
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Print initial state for debugging
print(f"Initial world state: {interactive_sim.world}")

# Run the server if this script is executed directly
if __name__ == "__main__":
    print("Starting PyCRAM Camera API server...")
    print("Open http://127.0.0.1:8000 in your browser to access the interface")

    # Setup static files before starting the server
    setup_static_files()

    # Start the server
    uvicorn.run(app, host="127.0.0.1", port=8000)
