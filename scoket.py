from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})  # Allow all origins to access for now (not secure for production)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

def render_cube_with_blender(color, filename):
    # Replace the placeholder in the script with the chosen color
    with open('temp_script.py', 'r') as f:
        script_content = f.read()
        script_content = script_content.replace('YOUR_HEX_COLOR_HERE', color)
        script_content = script_content.replace('YOUR_OUTPUT_FILENAME_HERE', filename) # Changed from full_output_path

    # Write the modified script to a temporary file
    temp_script_path = 'modified_temp_script.py'
    with open(temp_script_path, 'w') as f:
        f.write(script_content)  # Changed from script to script_content

    # Run Blender with the modified script
    command = ["blender", "-b", "-P", temp_script_path]
    subprocess.run(command)

    # Cleanup: remove the modified script (optional)
    os.remove(temp_script_path)

@socketio.on('connect')
def connected():
    emit('session_id', {'session_id': request.sid})

@socketio.on('update_cube')
def handle_message(data):
    color = data['color']
    session_id = data['session_id']  
    output_filename = f"/home/mac/Work/important/self/nodejs-server-boilerplate/blender-3d/output_{session_id}.png"
    render_cube_with_blender(color, output_filename)
    response_data = {
        "message": "Cube updated!",
        "color": color,
        "image_path": output_filename
    }
    socketio.emit('cube_updated', response_data)

if __name__ == '__main__':
    socketio.run(app)

