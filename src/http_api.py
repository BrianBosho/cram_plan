import uvicorn
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

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

    try:
        result = getattr(robo_cram, command)(**params)
    except AttributeError:
        result = {"status": "error", "message": f"Unknown command: {command}"}

    return result


@app.get("/commands")
async def list_commands():
    return {
        "available_commands": [
            "spawn_objects",
            "move_robot",
            "pickup_and_place",
            "robot_perceive",
            "look_for_object",
            "unpack_arms", 
            "detect_object",
            "transport_object"
        ]
    }


if __name__ == "__main__":
    robo_cram.init_simulation()
    uvicorn.run(app, host="0.0.0.0", port=8001)
