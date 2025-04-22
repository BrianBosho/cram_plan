# PyCRAM Robot API Technical Documentation

This document provides detailed technical specifications for the PyCRAM Robot API endpoints, including parameters, return values, data types, and default behaviors.

## API Overview

The PyCRAM Robot API exposes a single HTTP endpoint `/execute` that accepts POST requests. The request body must contain a JSON object with the following structure:

```json
{
  "command": "command_name",
  "params": {
    "param1": value1,
    "param2": value2,
    ...
  }
}
```

Where `command_name` is one of the available commands documented below, and the `params` object contains the parameters specific to that command.

All responses follow this general format:

```json
{
  "status": "success|error",
  "message": "Human-readable message",
  "payload": {
    // Command-specific response data
  }
}
```

## API Endpoints

### 1. spawn_objects

Creates an object in the simulation environment.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `object_choice` | string | No | "bowl" | Type of object to spawn ("cereal", "milk", "spoon", "bowl", or custom) |
| `coordinates` | array[number] | No | [1.4, 1.0, 0.95] | [x, y, z] coordinates for object placement |
| `color` | string | No | Random from ["red", "blue", "green", "yellow", "black"] | Color for the object |
| `name` | string | No | `object_choice` + random number (0-100) | Custom name for the object |

#### Return Value

**Success Response**: 
```json
{
  "status": "success",
  "message": "Object '{obj_name}' created successfully",
  "object": {
    "name": "string",
    "type": "string",
    "file": "string",
    "pose": [number, number, number],
    "color": "string"
  }
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

#### Error Conditions
- If coordinates don't have exactly 3 values
- If file for the specified object type is not found
- Any exception during object creation

### 2. move_robot

Moves the robot to specified coordinates.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `coordinates` | array[number] | No | [0, 0, 0] | [x, y, z] coordinates to move to |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Robot moved to coordinates [x, y, z]",
  "coordinates": [number, number, number]
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

### 3. pickup_and_place

Picks up an object and places it at a target location.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `object_name` | string | No | "cereal" | Name of the object to pick up |
| `target_location` | array[number] | No | [1.4, 1.0, 0.95] | [x, y, z] coordinates for placement |
| `arm` | string | No | Automatic selection | Which arm to use ('left', 'right', or null for automatic) |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Successfully picked up {object_name} and placed at {target_location}",
  "object": "string",
  "target_location": [number, number, number],
  "arm_used": "string"
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

#### Error Conditions
- If the object is not found in the world
- If no reachable arms are available for the object
- If placement location resolution fails
- Any exception during pickup or place operations

### 4. robot_perceive

Makes the robot perceive its environment.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `perception_area` | string | No | "table" | Area to perceive ('table', 'room', etc.) |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Robot perceived {n} objects in {perception_area}",
  "perceived_objects": [
    {
      "name": "string",
      "type": "string",
      "pose": "string"
    },
    ...
  ]
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

### 5. transport_object

Transports an object to a target location.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `object_name` | string | No | "cereal" | Name of the object to transport |
| `target_location` | array[number] | No | [1.0, 1.0, 0.8] | [x, y, z] coordinates for target location |
| `arm` | string | No | "right" | Which arm to use ('left', 'right') |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Successfully transported {object_name} to {target_location}",
  "object": "string",
  "target_location": [number, number, number],
  "arm_used": "string"
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

### 6. get_camera_images

Captures images from the robot's camera and returns them as base64-encoded strings.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target_distance` | number | No | 2.0 | Distance in meters to the target point |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Camera images captured successfully",
  "images": {
    "color_image": "string (base64)",
    "depth_image": "string (base64)",
    "segmentation_mask": "string (base64)"
  }
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

### 7. get_enhanced_camera_images

Captures enhanced visualization of images from the robot's camera. Similar to `get_camera_images` but with improved visualizations.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target_distance` | number | No | 2.0 | Distance in meters to the target point |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Enhanced camera images captured successfully",
  "images": {
    "color_image": "string (base64)",
    "depth_image": "string (base64)",
    "segmentation_mask": "string (base64)"
  }
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

### 8. calculate_object_distances

Calculates distances between objects in the world.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source_object` | string | No | null | Name of source object (if null, calculates distances between all pairs) |
| `target_objects` | array[string] | No | null | List of target object names (if null, uses all objects) |
| `exclude_types` | array[string] | No | ["floor", "wall", "ceiling", "ground"] | List of object types to exclude |

#### Return Value

When `source_object` is specified:
```json
{
  "status": "success",
  "message": "Distance calculation is successful",
  "payload": {
    "object_name1": distance1,
    "object_name2": distance2,
    ...
  }
}
```

When calculating all pairwise distances:
```json
{
  "status": "success",
  "message": "Distance calculation is successful",
  "payload": {
    "object1-to-object2": distance,
    "object1-to-object3": distance,
    ...
  }
}
```

### 9. look_at_object

Makes the robot look at the specified object.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `obj_name` | string | Yes | N/A | Name of the object to look at |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Robot is now looking at '{obj_name}'"
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Object '{obj_name}' is not in the environment"
}
```
or
```json
{
  "status": "error",
  "message": "Robot vision failed to reach '{obj_name}'"
}
```

#### Error Conditions
- If the object is not found in the environment
- If the robot cannot successfully look at the object (LookAtGoalNotReached)

### 10. detect_object

Detects an object in the robot's environment and returns information about it.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `object_name` | string | No | null | Name of the object to detect (if null, detects any visible object) |
| `location` | object or array | No | null | Location to search for objects (can be a Pose object or position array) |

#### Return Value

**Success Response (single object)**:
```json
{
  "status": "success",
  "message": "Successfully detected object: {object_name}",
  "object": {
    "name": "string",
    "type": "string",
    "position": {
      "x": number,
      "y": number,
      "z": number
    },
    "color": "string"
  }
}
```

**Success Response (multiple objects)**:
```json
{
  "status": "success",
  "message": "Successfully detected {n} object(s)",
  "objects": [
    {
      "name": "string",
      "type": "string",
      "position": {
        "x": number,
        "y": number,
        "z": number
      },
      "color": "string"
    },
    ...
  ]
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

#### Error Conditions
- If no objects matching the criteria are detected
- If the world is not initialized
- Any exception during detection

### 11. move_and_rotate

Moves the robot to a specified location and/or rotates it to a specified orientation.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `location` | array[number] | No | Current position | [x, y, z] coordinates to move to |
| `angle` | number | No | Current angle | Angle in degrees to rotate around Z axis |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Robot moved to coordinates {location} with orientation {orientation}",
  "position": [number, number, number],
  "orientation": [number, number, number, number]
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

#### Error Conditions
- If location is not a list of 3 values
- If world is not initialized
- If robot is not found in world
- Any exception during movement

### 12. move_torso

Moves the robot's torso to a specified position.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `position` | string | No | "high" | Position to move the torso to ("low", "high") |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Torso moved to {position} position",
  "position": "string"
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Invalid torso position: {position}. Valid options are: low, high."
}
```

#### Error Conditions
- If an invalid torso position is provided
- Any exception during torso movement

### 13. park_arms

Moves the robot's arm(s) to the pre-defined parking position.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `arm` | string | No | "both" | Arm to park ("left", "right", "both") |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Successfully parked arm(s): {arm}",
  "arm": "string"
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Invalid arm: {arm}. Valid options are: left, right, both."
}
```

#### Error Conditions
- If an invalid arm value is provided
- Any exception during arm movement

### 14. calculate_relative_distances

Calculates the relative distances between two objects in the world, returning the difference in x, y, z coordinates and the Euclidean distance.

#### Parameters

| Parameter        | Type   | Required | Description                                      |
|------------------|--------|----------|--------------------------------------------------|
| object_name_1    | string | Yes      | Name of the first object                         |
| object_name_2    | string | Yes      | Name of the second object                        |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "object_1": "object_name_1",
  "object_2": "object_name_2",
  "dx": number,
  "dy": number,
  "dz": number,
  "euclidean": number
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

#### Error Conditions

- If the world is not initialized
- If either object is not found

### 15. get_robot_pose

Gets the current pose (position and orientation) of the PR2 robot in the simulation.

#### Parameters

None

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "position": [x, y, z],
  "orientation": [qx, qy, qz, qw]
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

#### Error Conditions
- If the PR2 robot cannot be resolved in the simulation
- Any exception during pose retrieval

### 16. get_placement_surfaces

Returns information about available surfaces in the environment where objects can be placed.

#### Parameters

None

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Retrieved all available surfaces",
  "surfaces": {
    "surface_name1": {
      "description": "string",
      "position": [x, y, z],
      "dimensions": [width, depth, height],
      "max_dx": number,
      "max_dy": number,
      "recommended_for": ["object_type1", "object_type2", ...]
    },
    "surface_name2": {
      ...
    }
  }
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

#### Error Conditions
- If the environment is not initialized
- Any exception during surface data retrieval

### 17. spawn_in_area

Spawns an object on a specific named surface in the environment.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `object_choice` | string | No | "bowl" | Type of object to spawn |
| `surface_name` | string | Yes | N/A | Name of the surface to place the object on |
| `color` | string | No | Random | Color for the object |
| `name` | string | No | Auto-generated | Custom name for the object |
| `offset_x` | number or null | No | Random | X-axis offset from center of surface |
| `offset_y` | number or null | No | Random | Y-axis offset from center of surface |

#### Return Value

**Success Response**: 
```json
{
  "status": "success",
  "message": "Object '{obj_name}' created successfully on {surface_name}",
  "object": {
    "name": "string",
    "type": "string",
    "pose": [number, number, number],
    "color": "string"
  },
  "offsets": [number, number],
  "surface": "string"
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

#### Error Conditions
- If the specified surface name doesn't exist
- If the generated coordinates are invalid
- Any exception during the spawning process

### 18. pick_and_place_on_surface

Picks up an object and places it on a specific named surface.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `object_name` | string | Yes | N/A | Name of the object to pick up |
| `surface_name` | string | Yes | N/A | Name of the surface to place on |
| `offset_x` | number or null | No | Random | X-axis offset from center of surface |
| `offset_y` | number or null | No | Random | Y-axis offset from center of surface |
| `arm` | string | No | Auto-select | Which arm to use ('left', 'right', or null for automatic) |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Successfully picked up {object_name} and placed on {surface_name}",
  "object": "string",
  "surface": "string",
  "position": [number, number, number],
  "offsets": [number, number],
  "arm_used": "string"
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

#### Error Conditions
- If the object is not found in the world
- If the specified surface doesn't exist
- If the pickup or placement fails
- Any exception during the operation

### 19. get_world_objects

Retrieves all objects in the world and their positions with optional filtering by type, area, or excluded types.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `exclude_types` | array[string] | No | ["floor", "wall", "ceiling", "ground", "kitchen", "apartment", "pr2"] | Types of objects to exclude |
| `obj_type` | string | No | null | Type of object to filter by |
| `area` | string | No | null | Area name to filter objects by |

#### Return Value

**Success Response**:
```json
{
  "status": "success",
  "message": "Successfully retrieved objects from the world",
  "objects": {
    "object_name1": {
      "type": "string",
      "position": {
        "x": number,
        "y": number,
        "z": number
      },
      "color": "string",
      "area": "string"
    },
    "object_name2": {
      ...
    }
  }
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Error message"
}
```

#### Error Conditions
- If the world is not initialized
- Any exception during object retrieval

## Additional Notes

### Object Types
The API supports the following standard object types:
- "cereal"
- "milk"
- "spoon"
- "bowl"

### Color Support
The API supports the following colors:
- "red"
- "green"
- "blue"
- "yellow"
- "white"
- "black"

### Arm Options
When specifying an arm parameter, the following values are valid:
- "left"
- "right"
- "both" (only for park_arms)

### Torso Positions
When specifying a torso position, the following values are valid:
- "low"
- "high"

### Known Surface Areas
The API knows about the following surfaces by default:
- "kitchen_island_surface"
- "sink_area_surface"

## Error Handling

All API calls catch exceptions and return an error response with a descriptive message. Common error scenarios include:

1. Object not found in the environment
2. Invalid parameters (wrong types, missing required fields)
3. Robot cannot reach the specified location
4. Robot arm cannot reach the object
5. World initialization failure
6. Surface not found
7. Invalid coordinates or orientations

Error responses include the "status" field set to "error" and a "message" field with details.