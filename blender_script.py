# blender --background --python blender_script.py -- room4.glb
import bpy
import mathutils
import sys
import math  # Needed for converting degrees to radians

# Function to make an object look at another location


def look_at(obj, target_pos):
    """
    Rotates 'obj' to look at 'target_pos' location.
    """
    if not isinstance(target_pos, mathutils.Vector):
        target_pos = mathutils.Vector(target_pos)

    direction = target_pos - obj.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    obj.rotation_euler = rot_quat.to_euler()


# Parse arguments from command line
args = sys.argv[sys.argv.index("--") + 1:]
glb_file_path, material_id, product_id, scene_id, camera_position_arg, camera_target_arg = args

# Convert string arguments to appropriate data types
camera_position = tuple(map(float, camera_position_arg.split(',')))
camera_target = tuple(map(float, camera_target_arg.split(',')))

# Ensure the GLB file path is correct and accessible
try:
    # Import GLB file
    bpy.ops.import_scene.gltf(filepath=glb_file_path)
except Exception as e:
    print(f"Failed to import {glb_file_path}: {e}")
    sys.exit(1)


# Create or get the camera
camera_data = bpy.data.cameras.new(
    name="FreeCameraData")  # Create new camera data
free_camera = bpy.data.objects.get("FreeCamera")
if not free_camera:
    free_camera = bpy.data.objects.new("FreeCamera", camera_data)
    # Adjusted for the correct scene collection
    bpy.context.collection.objects.link(free_camera)

# Adjusting World background to solid white
bpy.data.worlds['World'].use_nodes = True
bg = bpy.data.worlds['World'].node_tree.nodes['Background']
bg.inputs[0].default_value = (1, 1, 1, 1)  # Correct alpha value to 1
bg.inputs[1].default_value = 1.0  # Strength of the background color

# Lighting setup
sun = bpy.data.lights.new(name="Sun", type='SUN')
sun.use_shadow = True
sun.shadow_soft_size = 0.1
sun_obj = bpy.data.objects.new(name="Sun", object_data=sun)
bpy.context.collection.objects.link(sun_obj)
sun_obj.location = (10, 10, 10)

# Choose render engine: Cycles or Eevee
# Example: Switch to 'BLENDER_EEVEE' if preferred
bpy.context.scene.render.engine = 'CYCLES'

# Render settings for Cycles
bpy.context.scene.cycles.samples = 1

# Set the scene's active camera
bpy.context.scene.camera = free_camera

# Compositing for contrast enhancement
bpy.context.scene.use_nodes = True
nodes = bpy.context.scene.node_tree.nodes
links = bpy.context.scene.node_tree.links
nodes.clear()  # Clear existing nodes

rl_node = nodes.new('CompositorNodeRLayers')
bc_node = nodes.new('CompositorNodeBrightContrast')
comp_node = nodes.new('CompositorNodeComposite')

bc_node.inputs['Bright'].default_value = 0.0
bc_node.inputs['Contrast'].default_value = 0.5

links.new(rl_node.outputs[0], bc_node.inputs[0])
links.new(bc_node.outputs[0], comp_node.inputs[0])

free_camera = bpy.data.objects.get("FreeCamera")
if not free_camera:
    free_camera = bpy.data.objects.new("FreeCamera", camera_data)
    bpy.context.collection.objects.link(free_camera)

# Set camera position and make it look at the target
free_camera.location = mathutils.Vector(camera_position)
look_at(free_camera, camera_target)

# Set the scene's active camera
bpy.context.scene.camera = free_camera

# Render settings
bpy.context.scene.render.engine = 'CYCLES'  # Or 'BLENDER_EEVEE'
bpy.context.scene.render.filepath = '/tmp/rendered_scene.png'
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)


# import boto3
# from flask import send_file
# import bpy
# import sys

# # Assume the last three arguments are material_id, product_id, and scene_id
# args = sys.argv[sys.argv.index("--") + 1:]  # Get arguments after "--"
# material_id, product_id, scene_id = args

# # Set the output path dynamically, e.g., based on material_id, product_id, and scene_id
# output_path = f"/tmp/render_{material_id}_{product_id}_{scene_id}.png"

# # Set render settings
# bpy.context.scene.render.filepath = output_path
# bpy.context.scene.render.image_settings.file_format = 'PNG'  # Set output format to PNG

# # Render the scene
# bpy.ops.render.render(write_still=True)


# @app.route('/render_output/<material_id>/<product_id>/<scene_id>')
# def serve_render_output(material_id, product_id, scene_id):
#     # Construct the file path based on the request parameters
#     file_path = f"/tmp/render_{material_id}_{product_id}_{scene_id}.png"

#     # Check if file exists, if not return a 404 or similar
#     try:
#         return send_file(file_path, mimetype='image/png')
#     except FileNotFoundError:
#         return jsonify({"error": "File not found"}), 404


# # Example: Upload to S3 (simplified)


# def upload_to_s3(file_path, bucket_name, object_name):
#     s3_client = boto3.client('s3')
#     response = s3_client.upload_file(file_path, bucket_name, object_name)
#     return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
