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
3. Spawn objects in the environment
4. Move the robot within its environment
5. Find if an object of some type is in the environment
6. Find if an object with some name is in the environment
7. Find if an object of some type is in some location of the environment
8. Find if an object with some name is in some location of the environment
9. Look at an object
10. Pick an object and place it elsewhere
11. Capture an image using the robot's camera
12. Get a list of objects in the robot's field of view
13. Exit the simulation

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
2. Access the web page to control the robot on `http://hostname:port`
3. Access the REST API endoints (further details on the API are listed in later sections of this document):
    - List all supported commands: `http://hostname:port/commands`
    - Execute a specific command: `http://hostname:port/execute`

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
| Table            | 2    |

### List all supported API endpoints

```bash
$ http GET http://hostname:port/commands
[
  "park_arms",
  "adjust_torso",
  "spawn_object",
  "move_robot",
  "is_object_type_in_environment",
  "is_object_in_environment",
  "is_object_type_in_location",
  "is_object_in_location",
  "look_at_object",
  "pick_and_place",
  "capture_image",
  "get_objects_in_robot_view"
]
```

### Park the robot's arms

```bash
$ http POST http://hostname:port/execute \
    command=park_arms
{
  "status": "success",
  "message": "Robot arms park successful"
}
```

### Adjust the robot's torso

```bash
$ http POST http://hostname:port/execute \
    command=adjust_torso \
    params:='{"high": true}'
{
  "status": "success",
  "message": "Robot torso move to high successful"
}
```

### Spawn objects in the environment

```bash
$ http POST http://hostname:port/execute \
    command=spawn_object \
    params:='{"obj": 0, "obj_name": "cereal1", "coordinates": [1.4, 1.0, 0.9], "colour": 0}'
{
  "status": "success",
  "message": "Object 'cereal1' created successfully",
  "payload": {
    "object": {
      "name": "cereal1",
      "type": "Cereal",
      "file": "breakfast_cereal.stl",
      "position": [1.4, 1.0, 0.9],
      "colour": [1.0, 0.0, 0.0, 1.0]
    }
  }
}
```

### Move the robot within its environment

```bash
$ http POST http://hostname:port/execute \
    command=move_robot \
    params:='{"coordinates": [0.75, 1, 0]}'
{
  "status": "success",
  "message": "Robot moved to coordinates [0.75, 1.0, 0.0]",
  "payload": {
    "coordinates": [0.75, 1.0, 0.0]
  }
}
```

### Find if an object of some type is in the environment

```bash
$ http POST http://hostname:port/execute \
    command=is_object_type_in_environment \
    params:='{"obj": 0}'
{
  "status": "success",
  "message": "1 object of type 'Cereal' is in the environment",
  "payload": {
    "objects": [
      {
        "name": "cereal1",
        "type": "Cereal"
      }
    ]
  }
}
```

### Find if an object with some name is in the environment

```bash
$ http POST http://hostname:port/execute \
    command=is_object_in_environment \
    params:='{"obj_name": "cereal1"}'
{
  "status": "success", "message":
  "Object 'cereal1' is in the environment"
}
```

### Find if an object of some type is in some location of the environment

```bash
$ http POST http://hostname:port/execute \
    command=is_object_type_in_location \
    params:='{"obj": 0, "location": 0}'
TODO: command has a bug that needs to be rectified
```

### Find if an object with some name is in some location of the environment

```bash
$ http POST http://hostname:port/execute \
    command=is_object_in_location \
    params:='{"obj_name": "cereal1", "location": 0}'
TODO: command has a bug that needs to be rectified
```

### Look at an object

```bash
$ http POST http://hostname:port/execute \
    command=look_at_object \
    params:='{"obj_name": "cereal1"}'
{
  "status": "success",
  "message": "Robot is now looking at 'cereal1'"
}
```

### Pick an object and place it elsewhere

```bash
$ http POST http://hostname:port/execute \
    command=pick_and_place \
    params:='{"obj_name": "cereal1", "destination": 0}'
TODO: command has a bug that needs to be rectified
```

### Capture an image using the robot's camera

```bash
$ http POST http://hostname:port/execute \
    command=capture_image \
    params:='{"target_distance": 2.0}'
{
  "status": "success",
  "message": "Image capture successful",
  "payload": {
    "rgb_image": "base64 encoded image",
    "depth_image": "base64 encoded image",
    "segmentation_mask": "base64 encoded image"
  }
}
```

### Get a list of objects in the robot's field of view

```bash
$ http POST http://hostname:port/execute \
    command=get_objects_in_robot_view \
    params:='{"target_distance": 2.0, "min_pixel_count": 50}'
TODO: command has a bug that needs to be rectified
```

### Exit the simulation

This command is disabled from being accessed remotely, and therefore it has no API endpoint
