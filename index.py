from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/create_cube', methods=['POST'])
def create_cube():
    # Extract data from the request (e.g., cube size)
    data = request.json
    cube_size = data.get('size', 2)

    # Create a temporary script to pass data to Blender
    with open('temp_script.py', 'w') as f:
        f.write(f"""
import bpy

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.mesh.primitive_cube_add(size={cube_size}, enter_editmode=False, align='WORLD', location=(0, 0, 1))
        """)

    # Run Blender with the temporary script
    command = "blender --background --python temp_script.py"
    process = subprocess.Popen(command, shell=True)
    process.communicate()

    return jsonify({"message": "Cube created!", "size": cube_size})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
