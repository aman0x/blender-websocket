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


# Hardcoded values for testing
glb_file_path = "./room4.glb"  # Adjust this path to your GLB file
camera_position = (1.00, 1.00, 1.00)
camera_target = (1.87, 0.97, 0.51)

# Import GLB file
try:
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
    # Link camera object to the current scene
    bpy.context.collection.objects.link(free_camera)

# Set camera properties (assuming perspective mode and FreeCamera type)
free_camera.data.type = 'PERSP'
free_camera.data.lens_unit = 'MILLIMETERS'
free_camera.data.clip_start = 0.1
free_camera.data.clip_end = 10000

# Set camera position and make it look at the target
free_camera.location = mathutils.Vector(camera_position)
look_at(free_camera, camera_target)

# Set the scene's active camera
bpy.context.scene.camera = free_camera

# Adjusting World background to solid white
bpy.data.worlds['World'].use_nodes = True
bg = bpy.data.worlds['World'].node_tree.nodes['Background']
bg.inputs[0].default_value = (1, 1, 1, 1)  # Correct alpha value to 1
bg.inputs[1].default_value = 1.0  # Strength of the background color

# Lighting setup
if "Sun" not in bpy.data.objects:
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
sun = bpy.data.objects['Sun']
sun.data.use_shadow = True  # Ensure shadows are enabled
sun.data.shadow_soft_size = 0.1  # Adjust for softer shadows

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 1
# Choose 'CYCLES' or 'BLENDER_EEVEE'
bpy.context.scene.render.filepath = '/tmp/rendered_scene.png'
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
bpy.context.scene.render.engine = 'CYCLES'

# Create or get the camera
camera_data = bpy.data.cameras.new(name="360CameraData")
camera_360 = bpy.data.objects.new("360Camera", camera_data)
bpy.context.collection.objects.link(camera_360)
bpy.context.scene.camera = camera_360

# Set the camera to panoramic and equirectangular type for 360 rendering
camera_360.data.type = 'PANO'
camera_360.data.cycles_panorama_type = 'EQUIRECTANGULAR'  # Corrected property access

# Optionally, set camera location and rotation
camera_360.location = (0, 0, 1)  # Example location, adjust as needed

# Configure render settings (resolution, samples, output path)
bpy.context.scene.render.resolution_x = 4096  # Adjust as needed
bpy.context.scene.render.resolution_y = 2048  # Adjust as needed
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.cycles.samples = 1

# Set output file path and render
bpy.context.scene.render.filepath = '/tmp/360_render.png'
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
