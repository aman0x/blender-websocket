from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/create_cube', methods=['GET'])
def create_cube():
    # Get color from the URL query parameter
    color = request.args.get('color', 'FFFFFF')  # Default to white if no color is provided

    # Convert the color from HEX to RGB
    r = int(color[0:2], 16) / 255.0
    g = int(color[2:4], 16) / 255.0
    b = int(color[4:6], 16) / 255.0

    # Create a temporary script to pass data to Blender
    with open('temp_script.py', 'w') as f:
        f.write(f"""
import bpy

# Create cube
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 1))

# Set cube color
mat = bpy.data.materials.new(name="Cube_Material")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = ({r}, {g}, {b}, 1)
bpy.context.object.data.materials.append(mat)

# Render and save
bpy.context.scene.render.filepath = '/home/mac/Work/important/self/nodejs-server-boilerplate/blender-3d/output.png'
bpy.ops.render.render(write_still=True)
        """)

    # Run Blender with the temporary script
    command = "blender --background --python temp_script.py"
    process = subprocess.Popen(command, shell=True)
    process.communicate()

    return jsonify({"message": "Cube created and rendered!", "color": color})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
