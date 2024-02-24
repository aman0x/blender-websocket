import bpy
import mathutils
import sys
import math

# Parse arguments from the command line
args = sys.argv[sys.argv.index("--") + 1:]
glb_file_path, material_id, product_id, scene_id, camera_position_arg, camera_target_arg, camera_rotation_arg = args

# Convert string arguments to appropriate data types
camera_position = tuple(map(float, camera_position_arg.split(',')))
camera_target = tuple(map(float, camera_target_arg.split(',')))
# Assuming these are in degrees
camera_rotation = tuple(map(float, camera_rotation_arg.split(',')))

# Import the GLB file
bpy.ops.import_scene.gltf(filepath=glb_file_path)

# Setting up the camera
camera_data = bpy.data.cameras.new(name="FreeCameraData")
free_camera = bpy.data.objects.get("FreeCamera")
if not free_camera:
    free_camera = bpy.data.objects.new("FreeCamera", camera_data)
    bpy.context.collection.objects.link(free_camera)

# Camera properties
free_camera.data.clip_start = 1
free_camera.data.clip_end = 10000
free_camera.data.angle = 1  # Assuming a fixed FOV, adjust as needed
free_camera.data.sensor_fit = 'HORIZONTAL'
free_camera.location = mathutils.Vector(camera_position)

# Apply rotation directly, converting from degrees to radians and adjusting for coordinate system differences
# Assuming the rotation order in Babylon.js is XYZ, which is common
camera_rotation_radians = [math.radians(angle) for angle in camera_rotation]
# Set rotation mode to XYZ which is common in Blender
free_camera.rotation_mode = 'XYZ'
free_camera.rotation_euler = mathutils.Euler(
    (camera_rotation_radians[0], camera_rotation_radians[1], camera_rotation_radians[2]), 'XYZ')


mesh_names = ["Corona Light001", "Corona Light002",
              "Corona Light003", "Corona Light003.009"]  # Add more names as needed

for mesh_name in mesh_names:
    mesh_light = bpy.data.objects.get(mesh_name)

    if mesh_light:
        # Create or get the emissive material
        mat = bpy.data.materials.get(
            "EmissiveMaterial") or bpy.data.materials.new(name="EmissiveMaterial")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()  # Clear existing nodes

        # Setup nodes
        emission = nodes.new('ShaderNodeEmission')
        # Adjust the strength as needed
        emission.inputs['Strength'].default_value = 50
        emission.inputs['Color'].default_value = (
            1, 1, 1, 1)  # Adjust the color as needed

        material_output = nodes.new('ShaderNodeOutputMaterial')

        # Here's where the correction is applied:
        links = mat.node_tree.links
        links.new(emission.outputs['Emission'],
                  material_output.inputs['Surface'])

        # Apply material to all material slots
        if mesh_light.data.materials:
            mesh_light.data.materials[0] = mat  # Replace the first material
        else:
            # Add a new material slot if none exist
            mesh_light.data.materials.append(mat)
    else:
        print(f"Mesh '{mesh_name}' not found")


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
sun.data.energy = 100
# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 1
# Choose 'CYCLES' or 'BLENDER_EEVEE'
bpy.context.scene.render.filepath = '/tmp/18.png'
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
bpy.context.scene.render.engine = 'CYCLES'

# 360


# s3 output
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
