import sys
import bpy
import mathutils
import math
import requests
import os


args = sys.argv[sys.argv.index("--") + 1:]
glb_file_path, material_id, product_id, scene_id, camera_position_arg, camera_target_arg, camera_rotation_arg = args

# Convert string arguments to appropriate data types
camera_position = tuple(map(float, camera_position_arg.split(',')))
camera_target = tuple(map(float, camera_target_arg.split(',')))
# Assuming these are in degrees
camera_rotation = tuple(map(float, camera_rotation_arg.split(',')))

# Import the GLB file
bpy.ops.import_scene.gltf(filepath=glb_file_path)
if "Cube" in bpy.data.objects:
    cube = bpy.data.objects["Cube"]
    bpy.data.objects.remove(cube, do_unlink=True)
# Setting up the camera
camera_data = bpy.data.cameras.new(name="FreeCameraData")
free_camera = bpy.data.objects.get("FreeCamera")
if not free_camera:
    free_camera = bpy.data.objects.new("FreeCamera", camera_data)
    bpy.context.collection.objects.link(free_camera)

# Camera properties
free_camera.data.clip_start = 1
free_camera.data.clip_end = 10000
free_camera.data.angle = 1.5  # Assuming a fixed FOV, adjust as needed
free_camera.data.sensor_fit = 'HORIZONTAL'
free_camera.location = mathutils.Vector(camera_position)

# Apply rotation directly, converting from degrees to radians and adjusting for coordinate system differences
# Assuming the rotation order in Babylon.js is XYZ, which is common
camera_rotation_radians = [math.radians(angle) for angle in camera_rotation]
# Set rotation mode to XYZ which is common in Blender
free_camera.rotation_mode = 'XYZ'
free_camera.rotation_euler = mathutils.Euler(
    (camera_rotation_radians[0], camera_rotation_radians[1], camera_rotation_radians[2]), 'XYZ')

bpy.context.scene.camera = free_camera
camera = bpy.context.scene.camera
# Print camera properties
print("Camera Location:", camera.location)
print("Camera Rotation Euler (radians):", camera.rotation_euler)

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
    'https://dp20tzm6ev3tb.cloudfront.net/materials/chair002/texture3/ao14.jpg',
    'https://dp20tzm6ev3tb.cloudfront.net/materials/chair002/texture3/bit14.jpg',
    'https://dp20tzm6ev3tb.cloudfront.net/materials/chair002/texture3/met14.jpg',
    'https://dp20tzm6ev3tb.cloudfront.net/materials/chair002/texture3/nor14.jpg',
    'https://dp20tzm6ev3tb.cloudfront.net/materials/chair002/texture3/rough14.jpg',
]

# Directory to save downloaded textures
save_dir = './textures/'

# Download each texture
for url in texture_urls:
    filename = url.split('/')[-1]  # Extract filename from URL
    filepath = save_dir + filename
    response = requests.get(url)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    print(f'Downloaded {filename}')


def setup_material_with_textures(texture_dir, object_name):
    if object_name not in bpy.data.objects:
        print(f"Object '{object_name}' not found.")
        return

    obj = bpy.data.objects[object_name]
    if obj.data.materials:
        mat = obj.data.materials[0]  # Use the first material if it exists
    else:
        mat = bpy.data.materials.new(name="CustomMaterial")
        obj.data.materials.append(mat)

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    output = nodes.new('ShaderNodeOutputMaterial')

    texture_types = {
        'ao': 'Base Color', 'bit': 'Base Color', 'met': 'Metallic',
        'nor': 'Normal', 'rough': 'Roughness'
    }

    for texture_type, bsdf_input in texture_types.items():
        texture_path = os.path.join(texture_dir, f'{texture_type}14.jpg')
        if not os.path.exists(texture_path):
            print(f"Texture file not found: {texture_path}")
            continue  # Skip if texture file does not exist

        image = bpy.data.images.load(texture_path)
        texture_node = nodes.new(type='ShaderNodeTexImage')
        texture_node.image = image
        texture_node.location = (-400, -200 *
                                 list(texture_types.keys()).index(texture_type))

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


# Example usage
# setup_material_with_textures('./textures/', 'sofa')

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


# Example usage
hdri_path = '2.hdr'  # Match the path used in Part 1
setup_world_hdri(hdri_path)
# Set the scene's active camera
bpy.context.scene.camera = free_camera
# Adjusting World background to solid white
# bpy.data.worlds['World'].use_nodes = True
# bg = bpy.data.worlds['World'].node_tree.nodes['Background']
# bg.inputs[0].default_value = (1, 1, 1, 1)  # Correct alpha value to 1
# bg.inputs[1].default_value = 1.0  # Strength of the background color

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
