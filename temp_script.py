import bpy

def set_cube_color(hex_color):
    color = [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    mat = bpy.data.materials.new(name="Cube_Material")
    mat.diffuse_color = color + [1.0]  # RGB + alpha
    cube = bpy.data.objects["Cube"]
    if cube.data.materials:
        cube.data.materials[0] = mat
    else:
        cube.data.materials.append(mat)

set_cube_color('YOUR_HEX_COLOR_HERE')
bpy.context.scene.render.filepath = full_output_path

bpy.ops.render.render(write_still=True)
