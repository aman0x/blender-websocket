import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/render', methods=['POST'])
def render_scene():
    data = request.json

    # Convert camera data to string arguments for the subprocess command
    camera_position_arg = "{X},{Y},{Z}".format(
        **data['cameraData']['position'])
    camera_target_arg = "{X},{Y},{Z}".format(**data['cameraData']['target'])
    camera_rotation_arg = "{X},{Y},{Z}".format(**data['cameraData'].get(
        'rotation', {'X': 0, 'Y': 0, 'Z': 0}))  # Default to 0 rotation if not provided

    glb_file_path = "./r4.glb"  # Ensure this path is correct
    blender_path = "/snap/bin/blender"  # Adjust to your Blender installation path
    script_file = "./blender_script.py"

    # Construct the command with dynamic values
    command = [
        blender_path,
        "--background",
        "--python", script_file,
        "--", glb_file_path,
        str(data.get('material_id', '')),  # Convert to string
        str(data.get('product_id', '')),   # Convert to string
        str(data.get('scene_id', '')),     # Convert to string
        camera_position_arg, camera_target_arg, camera_rotation_arg  # Include rotation
    ]

    print("Executing command:", " ".join(command))
    subprocess.run(command)

    return jsonify({"message": "Rendering started", "status": "success"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
