import uvicorn
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response

import robo_cram


app = FastAPI(title="RoboCRAM API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.post("/execute")
async def execute_command(data: dict = Body(...)):
    command = data.get("command")
    params = data.get("params", {})

    if command == "exit_simulation":
        return Response({"status": "error", "message": f"Forbidden command: {command}"}, 403)

    try:
        results = getattr(robo_cram, command)(**params)
        response = Response(results, 200 if results["status"] == "success" else 400)
    except AttributeError:
        response = Response({"status": "error", "message": f"Command not found: {command}"}, 404)

    return response


@app.get("/commands")
async def list_commands():
    return Response([
        "robot_pack_arms",
        "move_torso",
        "spawn_object",
        "move_robot",
        "is_object_type_in_environment",
        "is_object_in_environment",
        "is_object_type_in_location",
        "is_object_in_location",
        "is_object_visible_to_robot",
        "is_object_reachable_by_robot",
        "look_at_object",
        "pick_and_place"
    ], 200)


if __name__ == "__main__":
    robo_cram.init_simulation()
    uvicorn.run(app, host="0.0.0.0", port=8001)
