import os
import subprocess
from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from botocore.config import Config
load_dotenv()
app = Flask(__name__)


def upload_file_to_s3(file_name, bucket, object_name=None, region_name="us-east-1", content_type='application/octet-stream', make_public=False):
    """
    Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified, file_name is used
    :param region_name: AWS region name where the bucket exists
    :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    extra_args = {'ContentType': content_type}
    # if make_public:
    #     extra_args['ACL'] = 'public-read'
    # Ensure AWS credentials and region are correctly set
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    if not aws_access_key_id or not aws_secret_access_key:
        print("AWS credentials are not set correctly.")
        return False

    # Create an S3 client with explicit region
    s3_client = boto3.client(
        's3',
        config=Config(signature_version='s3v4'),
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    try:
        # Upload the file
        s3_client.upload_file(
            file_name, bucket, object_name, ExtraArgs=extra_args)
        # Construct the file URL
        file_url = f"https://{bucket}.s3.{region_name}.amazonaws.com/{object_name}"
        return file_url
    except Exception as e:
        print(f"Failed to upload file: {e}")
        return None


@app.route('/render', methods=['POST'])
def render_scene():
    data = request.json

    # Convert camera data to string arguments for the subprocess command
    camera_position_arg = "{X},{Y},{Z}".format(
        **data['cameraData']['position'])
    camera_target_arg = "{X},{Y},{Z}".format(**data['cameraData']['target'])
    camera_rotation_arg = "{X},{Y},{Z}".format(**data['cameraData'].get(
        'rotation', {'X': 0, 'Y': 0, 'Z': 0}))  # Default to 0 rotation if not provided

    glb_file_path = "./r4.glb"  # Ensure this path is correct
    blender_path = "/snap/bin/blender"  # Adjust to your Blender installation path
    script_file = "./blender_script.py"

    # Construct the command with dynamic values
    command = [
        blender_path,
        "--background",
        "--python", script_file,
        "--", glb_file_path,
        str(data.get('material_id', '')),  # Convert to string
        str(data.get('product_id', '')),   # Convert to string
        str(data.get('scene_id', '')),     # Convert to string
        camera_position_arg, camera_target_arg, camera_rotation_arg  # Include rotation
    ]

    # Make sure to adjust file_name, bucket_name, and object_name with actual values
    file_name = '/tmp/test3.png'
    bucket_name = 'inno-render'
    object_name = 'desired-object-name-in-s31.png'  # Optional
    content_type = 'image/jpeg'  # MIME type for a JPEG image
    region_name = "us-east-1"
    print("Executing command:", " ".join(command))
    subprocess.run(command)
    uploaded_file_url = upload_file_to_s3(
        file_name, bucket_name, object_name, region_name, content_type, make_public=True)

    if uploaded_file_url:
        print(f"File uploaded successfully: {uploaded_file_url}")
    else:
        print("Upload failed")

    return jsonify({"message": "Rendering started", "status": uploaded_file_url})


@app.route('/pano-render', methods=['POST'])
def render_scene_360():
    data = request.json

    # Convert camera data to string arguments for the subprocess command
    camera_position_arg = "{X},{Y},{Z}".format(
        **data['cameraData']['position'])
    camera_target_arg = "{X},{Y},{Z}".format(**data['cameraData']['target'])
    camera_rotation_arg = "{X},{Y},{Z}".format(**data['cameraData'].get(
        'rotation', {'X': 0, 'Y': 0, 'Z': 0}))  # Default to 0 rotation if not provided

    glb_file_path = "./r41.glb"  # Ensure this path is correct
    blender_path = "/snap/bin/blender"  # Adjust to your Blender installation path
    script_file = "./blender_script.py"

    # Construct the command with dynamic values
    command = [
        blender_path,
        "--background",
        "--python", script_file,
        "--", glb_file_path,
        str(data.get('material_id', '')),  # Convert to string
        str(data.get('product_id', '')),   # Convert to string
        str(data.get('scene_id', '')),     # Convert to string
        camera_position_arg, camera_target_arg, camera_rotation_arg  # Include rotation
    ]

    print("Executing command:", " ".join(command))
    subprocess.run(command)

    return jsonify({"message": "Rendering started", "status": "success"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
