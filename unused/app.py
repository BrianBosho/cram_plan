from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import robot_actions_api as api

app = Flask(__name__, static_folder='static')

# Serve HTML files
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/robot-control')
def robot_control():
    return send_from_directory('.', 'robot_control.html')

# API endpoints
@app.route('/api/move-robot', methods=['POST'])
def move_robot_api():
    data = request.get_json()
    coordinates = data.get('coordinates')
    result = api.move_robot(coordinates)
    return jsonify(result)

@app.route('/api/pickup-place', methods=['POST'])
def pickup_place_api():
    data = request.get_json()
    object_name = data.get('object_name')
    target_location = data.get('target_location')
    arm = data.get('arm')
    result = api.pickup_and_place(object_name, target_location, arm)
    return jsonify(result)

@app.route('/api/perceive', methods=['GET'])
def perceive_api():
    perception_area = request.args.get('area')
    result = api.robot_perceive(perception_area)
    return jsonify(result)

@app.route('/api/camera-images', methods=['GET'])
def camera_images_api():
    target_distance = request.args.get('target_distance')
    result = api.get_robot_camera_images(target_distance)
    return jsonify(result)

@app.route('/api/kitchen-info', methods=['GET'])
def kitchen_info_api():
    result = api.get_kitchen_info()
    return jsonify(result)

@app.route('/api/spawn-object', methods=['POST'])
def spawn_object_api():
    data = request.get_json()
    object_choice = data.get('object_type')
    coordinates = data.get('coordinates')
    color = data.get('color')
    result = api.spawn_objects(object_choice, coordinates, color)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 