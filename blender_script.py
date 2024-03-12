import sys
import bpy
import mathutils
import math
import requests
import os
from mathutils import Vector
from math import radians
import os
import re

args = sys.argv[sys.argv.index("--") + 1:]
glb_file_path, material_id, product_id, scene_id, camera_position_arg, camera_target_arg, camera_rotation_arg = args

bpy.ops.import_scene.gltf(filepath=glb_file_path)
camera_name = 'Camera.001'  # Use the actual name of your camera object
camera = bpy.data.objects.get(camera_name)


def setup_camera_rotation(camera, camera_target_arg, camera_position_arg, camera_rotation_arg):
    # Calculate the direction vector from the camera to the target

    camera_position = tuple(map(float, camera_position_arg.split(',')))
    camera_target = tuple(map(float, camera_target_arg.split(',')))
    # Assuming these are in degrees
    camera_rotation = tuple(map(float, camera_rotation_arg.split(',')))

    # Calculate the direction vector from position to target
    direction = (camera_target[0] - camera_position[0],
                 camera_target[1] - camera_position[1],
                 camera_position[2] - camera_target[2])
    camera.location = direction

    rotation_x = 1.5 + camera_rotation[0]  # +1
    rotation_y = 0  # always 0
    rotation_z = 5.4 + camera_rotation[2]  # +5.5 + y

    # Create a Euler rotation object from these values, assuming XYZ order
    euler_rotation = mathutils.Euler(
        (rotation_x, rotation_y, rotation_z), 'XYZ')

    # Apply this rotation to the camera
    # Assuming the active object is the camera, otherwise, you need to reference your camera object directly
    bpy.context.object.rotation_euler = euler_rotation


for obj_name in ["Camera", "Cube"]:
    if obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[obj_name])
if camera is None:
    print(f"Camera named '{camera_name}' not found.")
else:
    if camera:
        setup_camera_rotation(camera, camera_target_arg,
                              camera_position_arg, camera_rotation_arg)
        camera.data.type = 'PERSP'


# Camera properties
print("\nCamera Data Properties:")
# Print camera data properties
for prop in camera.bl_rna.properties:
    if not prop.is_readonly:
        prop_value = getattr(camera, prop.identifier)
        print(f"{prop.identifier}: {prop_value}")

camera.data.angle = 1.2  # Example FOV, adjust as needed

bpy.context.scene.camera = camera


mesh_names = ["light 300zww", "light 300", "Corona Light001", "Corona Light001.001", "light 600", "light 600.002", "light 600.004", "light 600.005", "lamp015.006", "lamp015.007", "lamp015.009", "lamp015.008",
              "light 600.003", "light 600.001", "light 300zww", "light 300", "light 600.002", ]  # Add more names as needed

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
        emission.inputs['Strength'].default_value = 20
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


# List of texture URLs
texture_urls = [
    'https://dp20tzm6ev3tb.cloudfront.net/materials/chair002/texture2/ao9.jpg',
    'https://dp20tzm6ev3tb.cloudfront.net/materials/chair002/texture2/bit9.jpg',
    'https://dp20tzm6ev3tb.cloudfront.net/materials/chair002/texture2/met9.jpg',
    'https://dp20tzm6ev3tb.cloudfront.net/materials/chair002/texture2/nor9.jpg',
    'https://dp20tzm6ev3tb.cloudfront.net/materials/chair002/texture2/rou9.jpg',
]

# Directory to save downloaded textures
save_dir = './textures/'

# Empty the directory before downloading new textures
for filename in os.listdir(save_dir):
    file_path = os.path.join(save_dir, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f'Failed to delete {file_path}. Reason: {e}')

# Download each texture into the unique directory
for url in texture_urls:
    filename = url.split('/')[-1]  # Extract filename from URL
    filepath = os.path.join(save_dir, filename)
    response = requests.get(url)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    print(f'Downloaded {filename}')


def setup_material_with_textures(texture_dir, object_name):
    # Ensure the object exists
    if object_name not in bpy.data.objects:
        print(f"Object '{object_name}' not found.")
        return

    # Ensure the texture directory exists
    if not os.path.isdir(texture_dir):
        print(f"Directory '{texture_dir}' not found.")
        return

    obj = bpy.data.objects[object_name]
    # Assign or create a new material
    if obj.data.materials:
        mat = obj.data.materials[0]
    else:
        mat = bpy.data.materials.new(name="CustomMaterial")
        obj.data.materials.append(mat)

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    output = nodes.new('ShaderNodeOutputMaterial')

    # Improved texture types to BSDF input mapping
    texture_types_to_bsdf_input = {
        'ao': 'Base Color', 'bit': 'Base Color', 'met': 'Metallic',
        'nor': 'Normal', 'rough': 'Roughness'
    }

    # Dynamically load textures based on files in the directory
    texture_dir = './textures/'
    for filename in os.listdir(texture_dir):
        texture_path = os.path.join(texture_dir, filename)

        # Initialize texture_type with a default value or None
        texture_type = None

        # Use regular expressions to extract texture type
        match = re.search(r'(\w+)(\d+)\.jpg', filename)
        if match:
            # Extract last 3 characters of texture type
            texture_type = match.group(1)[-3:]

        # Check if texture_type is recognized
        if texture_type and texture_type in texture_types_to_bsdf_input:
            bsdf_input = texture_types_to_bsdf_input[texture_type]
            # Proceed with loading the texture and setting up the material node
        else:
            print(f"Unknown or unhandled texture type in file: {filename}")
            continue  # Skip this file and move to the next one

            bsdf_input = texture_types_to_bsdf_input[texture_type]

        # Load the texture and create a texture node
        image = bpy.data.images.load(texture_path)
        texture_node = nodes.new(type='ShaderNodeTexImage')
        texture_node.image = image
        texture_node.location = (-400, -200 *
                                 list(texture_types_to_bsdf_input.keys()).index(texture_type))

        if texture_type == 'nor':
            normal_map = nodes.new(type='ShaderNodeNormalMap')
            normal_map.location = (-200, bsdf.location[1] - 200)
            links.new(texture_node.outputs['Color'],
                      normal_map.inputs['Color'])
            links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
        else:
            if texture_type in ['met', 'rough']:
                texture_node.image.colorspace_settings.name = 'Non-Color'
            links.new(texture_node.outputs['Color'], bsdf.inputs[bsdf_input])

    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    print(f"Material setup completed for '{object_name}'.")


save_dir = './textures/'
setup_material_with_textures(save_dir, 'sofa')


def setup_world_hdri(hdri_path):
    # Ensure we're using Cycles render engine for HDRIs

    # Get the world and clear any existing nodes
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()

    # Create new nodes: Environment Texture, Background, and World Output
    env_texture = nodes.new(type='ShaderNodeTexEnvironment')
    background = nodes.new(type='ShaderNodeBackground')
    world_output = nodes.new(type='ShaderNodeOutputWorld')

    # Set the HDRI image
    env_texture.image = bpy.data.images.load(hdri_path)

    # Link the nodes
    links = world.node_tree.links
    links.new(env_texture.outputs['Color'], background.inputs['Color'])
    links.new(background.outputs['Background'], world_output.inputs['Surface'])

    print("World setup with HDRI completed.")


def delete_objects_by_names(obj_names):
    bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
    for obj_name in obj_names:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            obj.select_set(True)  # Select the specific object
    bpy.ops.object.delete()  # Delete all selected objects


# Function to load a GLB file
def load_glb(filepath):
    # Ensure the Blender is in Object Mode
    if bpy.context.object:
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.import_scene.gltf(filepath=filepath)


# Import the new GLB model
load_glb(glb_path)


# Define the object names to delete (e.g., the original model and its parts)
objects_to_replace_names = ['sofa', 'sofa leg',
                            'sofa_leg_2', 'sofa_leg_3', 'sofa_leg_4']

# Assuming 'product_id' is defined; for example:
product_id_l = 15807
# The directory where the GLB files are stored
items_dir = './items/'
new_glb_path = os.path.join(items_dir, f"{product_id_l}.glb")

# Delete the original model(s)
delete_objects_by_names(objects_to_replace_names)

# Import the new model
load_glb(new_glb_path)


# Example usage
hdri_path = '2.hdr'  # Match the path used in Part 1
setup_world_hdri(hdri_path)

# Lighting setup
if "Sun" not in bpy.data.objects:
    bpy.ops.object.light_add(type='SUN', location=(-10.14, -5.55, 3.08))
sun = bpy.data.objects['Sun']
sun.data.use_shadow = True  # Ensure shadows are enabled
sun.data.shadow_soft_size = 0.1  # Adjust for softer shadows
sun.data.color = (1.0, 0.9, 0.8)  # Warm light, for example

# Set Sun rotation (example: 45 degrees on the Z-axis, 30 degrees on the Y-axis)
# Convert degrees to radians for Blender
sun.rotation_euler[0] = math.radians(57.11)  # Rotation around X-axis
sun.rotation_euler[1] = math.radians(-60.06)  # Rotation around Y-axis
sun.rotation_euler[2] = math.radians(-14.46)  # Rotation around Z-axis
sun.data.energy = 15
sun.data.angle = math.radians(28.7)  # Convert degrees to radians if necessary

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 1
# Choose 'CYCLES' or 'BLENDER_EEVEE'
bpy.context.scene.render.filepath = '/tmp/sample.png'
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
