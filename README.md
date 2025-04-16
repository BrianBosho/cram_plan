# PyCRAM API Server

[![CI workflow](https://github.com/BrianBosho/cram_plan/actions/workflows/CI.yml/badge.svg?branch=master)](https://github.com/BrianBosho/cram_plan/actions/workflows/CI.yml)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://github.com/pycqa/isort)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-red.svg)](https://github.com/pycqa/flake8)

A command-line application and a FastAPI-based REST API for controlling a PR2 robot in a BulletWorld simulation
environment via [PyCRAM](https://pycram.readthedocs.io/en/latest/index.html)

## Overview

This software provides the following functions for controlling a PR2 robot and the simulated environment in which it
resides:

1. Park the robot's arms
2. Adjust the robot's torso
3. Get the robot's pose
4. Spawn objects in the environment
5. Move the robot within its environment
6. Find if an object of some type is in the environment
7. Find if an object with some name is in the environment
8. Find if an object of some type is in some location of the environment
9. Find if an object with some name is in some location of the environment
10. Look at an object
11. Pick an object and place it at a specific coordinate
12. Pick an object and place it at a specific location
13. Capture an image using the robot's camera
14. Get a list of objects in the robot's field of view
15. Get distances between objects in the environment
16. Exit the simulation

## Components

- CLI application: command-line application to interact with the system from the terminal
- REST API application: FastAPI-based API to interact with the system remotely using other tools that can call the API
- Web Interface: web page to remotely interact with the system on a web browser

## Installation and Development

### Prerequisites

A machine with the following tools installed is required:

- Python 3.9+
- PyCRAM (and its dependencies such as ROS Noetic and PyBullet)
- FastAPI (and other packages listed in `requirements.txt`)

### Linting

NOTE: This is a one-time step, and it is required if your code changes are to be pushed upstream to GitHub

Isort, black, and flake8 are used to check that code is well formatted and styled. Pre-commit hooks are used to automate
this process.

1. Install pre-commit package: `pip install pre-commit`
2. Install git hook scripts: `pre-commit install`
3. (optional) Run against all files: `pre-commit run --all-files`

## Quick Start

### Using the CLI application

1. Run the CLI application: `./python3 src/cli.py`
2. Follow the prompts from the application

### Using the REST API application and web interface

Update required environment variables by editing the `.env` file (create it if it doesn't exist, using the format laid
out in `.env.sample`)

| Env variable key  | Env variable value  | Description                                       |
| ----------------- | ------------------- | ------------------------------------------------- |
| HOST              | 0.0.0.0             | Hostname to access the API endpoints from         |
| PORT              | 8001                | Port that the API endpoints are to be exposed on  |
| ALLOW_HEADERS     | *                   | Headers to allow as a comma separated list        |
| ALLOW_METHODS     | *                   | Methods to allow as a comma separated list        |
| ALLOW_ORIGINS     | *                   | Origina to allow as a comma separated list        |
| SIM_ENV           | kitchen             | Simulation environment (kitchen or apartment)     |

1. Run the REST API application: `./python3 src/http_api.py`
2. Access the web page to control the robot on `http://127.0.0.1:8001`
3. Access the REST API endoints (further details on the API are listed in later sections of this document):
    - List all supported commands: `http://127.0.0.1:8001/commands`
    - Execute a specific command: `http://127.0.0.1:8001/execute`

## API Reference

This API reference uses [HTTPie](https://httpie.io/), and the listed commands can be run after installing HTTPie

Some parameters needed by different API endpoints use numeric codes, and these numeric codes are listed below:

Objects and their numeric codes:

| Object  | Code  |
| ------- | ----- |
| Cereal  | 0     |
| Milk    | 1     |
| Spoon   | 2     |
| Bowl    | 3     |

Colours and their numeric codes:

| Colour          | Code  |
| --------------- | ----- |
| Red             | 0     |
| Green           | 1     |
| Blue            | 2     |
| Yellow          | 3     |
| White           | 4     |
| Black           | 5     |
| Default colour  | 6     |

Location areas and their numeric codes:

| Location        | Code  |
| --------------- | ----- |
| Kitchen island  | 0     |
| Sink area       | 1     |

### List all supported API endpoints

```bash
$ http GET http://127.0.0.1:8001/commands
[
    "park_arms",
    "adjust_torso",
    "get_robot_pose",
    "spawn_object",
    "move_robot",
    "is_object_type_in_environment",
    "is_object_in_environment",
    "is_object_type_in_location",
    "is_object_in_location",
    "look_at_object",
    "pick_and_place_coordinates",
    "pick_and_place_location",
    "capture_image",
    "get_objects_in_robot_view"
]
```

### Park the robot's arms

```bash
$ http POST http://127.0.0.1:8001/execute command=park_arms
{
    "message": "Robot arms park successful",
    "status": "success"
}
```

### Adjust the robot's torso

```bash
$ http POST http://127.0.0.1:8001/execute command=adjust_torso params:='{"high": true}'
{
    "message": "Robot torso move to high successful",
    "status": "success"
}
```

### Get the robot's pose

```bash
$ http POST http://127.0.0.1:8001/execute command=get_robot_pose
{
    "message": "Robot pose resolve successful",
    "payload": {
        "orientation": [
            0.0,
            0.0,
            0.0,
            1.0
        ],
        "position": [
            0.0,
            0.0,
            0.0
        ]
    },
    "status": "success"
}
```

### Spawn objects in the environment

```bash
$ http POST http://127.0.0.1:8001/execute command=spawn_object params:='{"obj_type": 0, "obj_name": "cereal1", "coordinates": [1.4, 1.0, 0.95], "colour": 0}'
{
{
    "message": "Object 'cereal1' created successfully",
    "payload": {
        "object": {
            "colour": [
                1.0,
                0.0,
                0.0,
                1.0
            ],
            "file": "breakfast_cereal.stl",
            "name": "cereal1",
            "position": [
                1.4,
                1.0,
                0.95
            ],
            "type": "CEREAL"
        }
    },
    "status": "success"
}
```

### Move the robot within its environment

```bash
$ http POST http://127.0.0.1:8001/execute command=move_robot params:='{"coordinates": [0.5, 0.5, 0], "orientation": [0, 0, 0.7071, 0.7071]}'
{
    "message": "Robot moved to coordinates [0.5, 0.5, 0.0] and orientation [0.0, 0.0, 0.7071, 0.7071]",
    "payload": {
        "coordinates": [
            0.5,
            0.5,
            0.0
        ],
        "orientation": [
            0.0,
            0.0,
            0.7071,
            0.7071
        ]
    },
    "status": "success"
}
```

### Find if an object of some type is in the environment

```bash
$ http POST http://127.0.0.1:8001/execute command=is_object_type_in_environment params:='{"obj_type": 0}'
{
    "message": "1 object of type 'CEREAL' is in the environment",
    "payload": {
        "objects": [
            {
                "name": "cereal1",
                "type": "CEREAL"
            }
        ]
    },
    "status": "success"
}
```

### Find if an object with some name is in the environment

```bash
$ http POST http://127.0.0.1:8001/execute command=is_object_in_environment params:='{"obj_name": "cereal1"}'
{
    "message": "Object 'cereal1' is not in the environment",
    "status": "success"
}
```

### Find if an object of some type is in some location of the environment

```bash
$ http POST http://127.0.0.1:8001/execute command=is_object_type_in_location params:='{"obj_type": 0, "location": 0}'
TODO: command has a bug that needs to be rectified
```

### Find if an object with some name is in some location of the environment

```bash
$ http POST http://127.0.0.1:8001/execute command=is_object_in_location params:='{"obj_name": "cereal1", "location": 0}'
TODO: command has a bug that needs to be rectified
```

### Look at an object

At times the returned result may have a status of `error` even though the robot may have turned its head to look at the
object. It's advisable to retry running one more time, as the chances of returning a status of `success` greatly improve
on the second attempt.

```bash
$ http POST http://127.0.0.1:8001/execute command=look_at_object params:='{"obj_name": "cereal1"}'
{
    "message": "Robot is now looking at 'cereal1'",
    "status": "success"
}
```

### Pick an object and place it at a specific coordinate

```bash
$ http POST http://127.0.0.1:8001/execute command=pick_and_place_coordinates params:='{"obj_name": "cereal1", "destination": [1.4, 0.5, 0.95]}'
{
    "message": "Object 'cereal1' successfully moved to '[1.4, 0.5, 0.95]'",
    "status": "success"
}
```

### Pick an object and place it at a specific location

```bash
$ http POST http://127.0.0.1:8001/execute command=pick_and_place_location params:='{"obj_name": "cereal1", "destination": 0}'
{
    "message": "Object 'cereal1' successfully moved to '[-1.2274999952316283, 2.099200015068054, 0.9547865257474011]'",
    "status": "success"
}
```

### Capture an image using the robot's camera

```bash
$ http POST http://127.0.0.1:8001/execute command=capture_image params:='{"target_distance": 2.0}'
{
    "message": "Image capture successful",
    "payload": {
        "depth_image": <base64-encoded-image>,
        "rgb_image": <base64-encoded-image>,
        "segmentation_mask": <base64-encoded-image>
    },
    "status": "success"
}
```

### Get a list of objects in the robot's field of view

```bash
$ http POST http://127.0.0.1:8001/execute command=get_objects_in_robot_view params:='{"target_distance": 2.0, "min_pixel_count": 50}'
{
    "message": "Getting objects in robot view successful",
    "payload": {
        "1": {
            "name": "floor",
            "pixel_count": 11401,
            "type": "Object"
        },
        "2": {
            "name": "kitchen",
            "pixel_count": 47615,
            "type": "Object"
        },
        "3": {
            "name": "pr2",
            "pixel_count": 3666,
            "type": "Object"
        },
        "4": {
            "name": "cereal1",
            "pixel_count": 141,
            "type": "Object"
        }
    },
    "status": "success"
}
```

### Get distances between objects in the environment

The parameter `source_object_name` takes an empty string when not passing any object name to it, and both
`target_object_names` and `exclude_object_names` take an empty list when not passing any object names to them.

```bash
$ http POST http://127.0.0.1:8001/execute command=get_distance_between_objects params:='{"source_object_name": "", "target_object_names": [], "exclude_object_names": []}'
{
    "message": "Distance calculation is successful",
    "payload": {
        "pr2": {
            "cereal1": 1.9653244007033546
        }
    },
    "status": "success"
}
```

### Exit the simulation

This command is disabled from being accessed remotely, and therefore it has no API endpoint
