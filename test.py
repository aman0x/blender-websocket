[1, 1, 1] (3) [-0.09209910527435192, 2.5496445629635867, 0] (3) [1.555613934993744, 1.0919689610600471, 0.17366176843643188] 0.8 2.0012048192771084 0.1 10000


console.log(positionArray, rotationArray, positionTargetArray, fov, aspectRatio, nearPlane, farPlane)



{'material_id': 1, 'material_url': 'url.com', 'product_id': 1, 'scene_id': 1, 'cameraData': {'target': {'X': 1.555, 'Y': 1.091, 'Z': 0.173}, 'position': {'X': 1, 'Y': 1, 'Z': 1}, 'rotation': {'X': -0.092, 'Y': 2.549, 'Z': 0}}}
Executing command: /snap/bin/blender --background --python ./blender_script.py -- ./room6.glb 1 1 1 1,1,1 1.555,1.091,0.173 -0.092,2.549,0
Blender 4.0.2 (hash 9be62e85b727 built 2023-12-05 08:48:50)
Read prefs: "/home/mac/.config/blender/4.0/config/userpref.blend"
Data are loaded, start creating Blender stuff
glTF import finished in 8.52s
Camera Location: <Vector (1.0000, 1.0000, 1.0000)>
Camera Rotation Euler (radians): <Euler (x=-0.0016, y=0.0445, z=0.0000), order='XYZ'>



{'material_id': 1, 'material_url': 'url.com', 'product_id': 1, 'scene_id': 1, 'cameraData': {'target': {'X': 1.555, 'Y': 1.091, 'Z': 0.173}, 'position': {'X': 1, 'Y': 1, 'Z': 1}, 'rotation': {'X': -0.092, 'Y': 2.549, 'Z': 0}}}
Executing command: /snap/bin/blender --background --python ./blender_script.py -- ./room6.glb 1 1 1 1,1,1 1.555,1.091,0.173 -0.092,2.549,0
Blender 4.0.2 (hash 9be62e85b727 built 2023-12-05 08:48:50)
Read prefs: "/home/mac/.config/blender/4.0/config/userpref.blend"
Data are loaded, start creating Blender stuff
glTF import finished in 6.35s
Camera Location: <Vector (1.5550, 1.0910, 0.1730)>
Camera Rotation Euler (radians): <Euler (x=-0.0920, y=2.5490, z=0.0000), order='XYZ'>


import bpy
from mathutils import Vector, Euler
from math import radians, pi

def setup_camera_rotation(camera, target_position, position):
    # Calculate the direction vector from the camera to the target
    direction = target_position - position
    camera.location = direction0
    # Use the direction to calculate the rotation
    # Note: This simplistic approach may need adjustments for complex scenarios
    camera.rotation_mode = 'XYZ'
    # Calculate the XY plane rotation towards the target
    rot_z = (direction.xy).angle_signed(Vector((0,1)), 0)
    # Calculate the pitch towards the target
    rot_y = -direction.angle(Vector((0,0,1)), 0)
    camera.rotation_euler[2] = rot_z  # Apply yaw (Z rotation)
    camera.rotation_euler[1] = rot_y  # Apply pitch (Y rotation)
    
    # Babylon.js orientation adjustment: Rotate 180 degrees around Z axis
    camera.rotation_euler[2] += pi

camera_name = 'Camera.001'
target_position = Vector((1, 1.5, 0))  # Example target position
position = Vector((1, 1.5, 1))
camera = bpy.data.objects.get(camera_name)
if camera:
    setup_camera_rotation(camera, target_position , position)
else:
    print(f"Camera named '{camera_name}' not found.")












import sys
import bpy
import math
import requests
import os
import mathutils


args = sys.argv[sys.argv.index("--") + 1:]
glb_file_path, material_id, product_id, scene_id, camera_position_arg, camera_target_arg, camera_rotation_arg = args
bpy.ops.import_scene.gltf(filepath=glb_file_path)

if "Camera" in bpy.data.objects:  # Remove default camera
    bpy.data.objects.remove(bpy.data.objects["Camera"])
if "Cube" in bpy.data.objects:  # Remove default cube
    bpy.data.objects.remove(bpy.data.objects["Cube"])
    
# Print all camera names
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        print(f"Found camera: {obj.name}")

imported_camera = None

# Find the camera by name
camera_data = {
    "position": {"x": 1.0, "y": 2.0, "z": 3.0},
    "target": {"x": 0.0, "y": 1.0, "z": 2.0},
    "fov": 90  # in degrees
}

# Convert the position and target from Babylon.js to Blender's coordinate system
position = mathutils.Vector(
    (camera_data["position"]["x"], camera_data["position"]["z"], -camera_data["position"]["y"]))
target = mathutils.Vector(
    (camera_data["target"]["x"], camera_data["target"]["z"], -camera_data["target"]["y"]))

# Assuming you've found the camera object as shown in previous steps
camera_name = 'Camera.001'  # Replace with the actual name of your camera
camera_obj = bpy.data.objects.get(camera_name)

if camera_obj and camera_obj.type == 'CAMERA':
    camera_obj.location = position

    # Point the camera towards the target
    direction = target - camera_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera_obj.rotation_euler = rot_quat.to_euler()

    # Set FOV
    camera_obj.data.angle = math.radians(camera_data["fov"])
else:
    print(f"Camera object named '{camera_name}' not found.")

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
