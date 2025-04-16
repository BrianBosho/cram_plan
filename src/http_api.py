import base64
import io
import os
import sys

import uvicorn
from dotenv import load_dotenv
from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from PIL import Image

import robo_cram

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
ALLOW_HEADERS = os.getenv("ALLOW_HEADERS")
ALLOW_METHODS = os.getenv("ALLOW_METHODS")
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS")
SIM_ENV = os.getenv("SIM_ENV").lower()

if SIM_ENV not in ["kitchen", "apartment"]:
    print(f"SIM_ENV should be one of 'kitchen' or 'apartment', not {SIM_ENV}")
    sys.exit(1)

SIM_ENV = robo_cram.Env.KITCHEN if SIM_ENV == "kitchen" else robo_cram.Env.APARTMENT

app = FastAPI(title="RoboCRAM API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=ALLOW_METHODS.split(","),
    allow_headers=ALLOW_HEADERS.split(","),
)


class RobotCommands:
    @staticmethod
    def park_arms():
        return robo_cram.park_arms()

    @staticmethod
    def adjust_torso(high):
        return robo_cram.adjust_torso(high)

    @staticmethod
    def get_robot_pose():
        return robo_cram.get_robot_pose()

    @staticmethod
    def spawn_object(obj_type, obj_name, coordinates, colour):
        return robo_cram.spawn_object(
            robo_cram.ObjectType(obj_type),
            obj_name,
            coordinates,
            robo_cram.Colour(colour),
        )

    @staticmethod
    def move_robot(coordinates, orientation):
        return robo_cram.move_robot(coordinates, orientation)

    @staticmethod
    def is_object_type_in_environment(obj_type):
        return robo_cram.is_object_type_in_environment(robo_cram.ObjectType(obj_type))

    @staticmethod
    def is_object_in_environment(obj_name):
        return robo_cram.is_object_in_environment(obj_name)

    @staticmethod
    def is_object_type_in_location(location, obj_type):
        return robo_cram.is_object_type_in_location(
            robo_cram.Location(location), robo_cram.ObjectType(obj_type)
        )

    @staticmethod
    def is_object_in_location(location, obj_name):
        return robo_cram.is_object_in_location(robo_cram.Location(location), obj_name)

    @staticmethod
    def look_at_object(obj_name):
        return robo_cram.look_at_object(obj_name)

    @staticmethod
    def pick_and_place_coordinates(obj_name, destination):
        return robo_cram.pick_and_place_coordinates(obj_name, destination)

    @staticmethod
    def pick_and_place_location(obj_name, destination):
        return robo_cram.pick_and_place_location(
            obj_name, robo_cram.Location(destination)
        )

    @staticmethod
    def capture_image(target_distance):
        response = robo_cram.capture_image(target_distance)

        rgb_image = Image.fromarray(response["payload"]["rgb_image"])
        rgb_image_buffer = io.BytesIO()
        rgb_image.save(rgb_image_buffer, format="PNG")
        rgb_image_buffer.seek(0)

        depth_image = Image.fromarray(response["payload"]["depth_image"]).convert("RGB")
        depth_image_buffer = io.BytesIO()
        depth_image.save(depth_image_buffer, format="PNG")
        depth_image_buffer.seek(0)

        segmentation_mask = Image.fromarray(response["payload"]["segmentation_mask"])
        segmentation_mask_buffer = io.BytesIO()
        segmentation_mask.save(segmentation_mask_buffer, format="PNG")
        segmentation_mask_buffer.seek(0)

        response["payload"]["rgb_image"] = base64.b64encode(
            rgb_image_buffer.read()
        ).decode("utf-8")
        response["payload"]["depth_image"] = base64.b64encode(
            depth_image_buffer.read()
        ).decode("utf-8")
        response["payload"]["segmentation_mask"] = base64.b64encode(
            segmentation_mask_buffer.read()
        ).decode("utf-8")

        return response

    @staticmethod
    def get_objects_in_robot_view(target_distance, min_pixel_count):
        return robo_cram.get_objects_in_robot_view(target_distance, min_pixel_count)


@app.get("/")
async def index():
    with open("./src/templates/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/commands")
async def list_commands():
    return JSONResponse(
        [k for k, v in RobotCommands.__dict__.items() if isinstance(v, staticmethod)],
        200,
    )


@app.post("/execute")
async def execute_command(data: dict = Body(...)):
    command = data.get("command")
    params = data.get("params", {})

    try:
        results = getattr(RobotCommands, command)(**params)
        response = JSONResponse(results, 200 if results["status"] == "success" else 400)
    except AttributeError:
        response = JSONResponse(
            {"status": "error", "message": f"Command not found: {command}"}, 404
        )

    return response


if __name__ == "__main__":
    robo_cram.init_simulation(SIM_ENV)
    uvicorn.run(app, host=HOST, port=PORT)
