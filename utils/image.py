import boto3
import concurrent.futures
import flask
from flask import jsonify, request, redirect
import os
from utils.aws import create_s3_client
from utils.aws import upload_multi_parallel_files_to_s3
from utils.utils import load_yaml_vars
import uuid

IMAGES_TABLE = os.environ['IMAGES_TABLE']

client_db = boto3.client('dynamodb')

ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif'}
# function to check file extension
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image_data(image_name):
    curr_uuid = str(uuid.uuid4())
    if not image_name:
        return jsonify({'error': 'Please provide imageName'}), 400

    resp = client_db.put_item(
        TableName=IMAGES_TABLE,
        Item={
            'imageId': {'S': curr_uuid },
            'imageName': {'S': image_name }
        }
    )
    if not resp:
        return jsonify({
            'error': 'failed to push image data to database!'
        })

    # return uuid for verification
    # TO DO: catch exception above and process accordingly
    return curr_uuid


def upload_image():
    file_list = request.files.getlist('image_multi')
    if len(file_list) < 1:
        return redirect("/fail")

    upload_multi_parallel_files_to_s3(file_list)

    mssg = 'upload succeeded'
    return jsonify(message=mssg)


''' working original
def upload_image():
    # check whether an input field with name 'image_file' exist
    if 'image_file' not in request.files:
        return redirect("/fail")

    # after confirm 'image_file' exist, get the file from input
    file = request.files['image_file']
    if not file:
        return redirect("/fail")
    
    # check whether a file is selected
    if file.filename == '':
        return redirect("/fail")

    # check file extension
    if not allowed_file(file.filename):
        return redirect("/fail")

    try:
        output = upload_file_to_s3(file)
    except Exception as e:
        mssg = "error uploading to s3: " + " : " +  str(e)
        return jsonify(message=mssg)
    
    # if upload success, return uploaded file name
    if output:
        save_return = save_image_data(file.filename)
        if not save_return:
            return jsonify({'error': 'Problem saving image metadata to database'})
        mssg = 'upload succeeded: {0}'.format(output)
        return jsonify(message=mssg)
        #return redirect("/success")

    # upload failed, redirect to fail page
    else:
        return redirect("/fail")
'''
    
def list_files():
    yaml_vars = load_yaml_vars()
    bucket = yaml_vars['bucket_data']
    s3_client = create_s3_client()
    link_data = []
    try:
        response = s3_client.list_objects_v2(Bucket=bucket)
        if not response:
            link_data.append('response is empty')
        else:
            # public_urls.append('1KeyCount: ' + str(response['KeyCount']))
            for content in response.get('Contents', []):
                presigned_url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': content['Key']}, ExpiresIn = 100)
                link_data.append((presigned_url, content['Key']))
    except Exception as e:
        link_data.append(bucket)
        link_data.append(e)
        pass
    return link_data

def list_imageIds():
    dynamodb = boto3.resource('dynamodb')
    image_table = dynamodb.Table(IMAGES_TABLE)
    response = image_table.scan()
    items = response['Items']
    image_id_list = []
    for item in items:
        image_id = item['imageId']
        image_id_list.append(image_id)
    return jsonify({'image_ids': image_id_list})

def get_image_data(image_id):
    resp = client_db.get_item(
        TableName=IMAGES_TABLE,
        Key={
            'imageId': { 'S': image_id }
        }
    )
    item = resp.get('Item')
    if not item:
        return jsonify({'error': 'Image does not exist'}), 404
    
    return jsonify({
        'imageId': item.get('imageId').get('S'),
        'imageName': item.get('imageName').get('S')
    })

def create_list_image_data():
    if flask.request.method == 'POST':

        curr_uuid = str(uuid.uuid4())
        image_name = request.form.get('imageName')
        if not image_name:
            return jsonify({'error': 'Please provide imageName'}), 400
    
        resp = client_db.put_item(
            TableName=IMAGES_TABLE,
            Item={
                'imageId': {'S': curr_uuid },
                'imageName': {'S': image_name }
            }
        )
        if not resp:
            return jsonify({
                'error': 'failed to push image data to database!'
            })

        return jsonify({
            'imageId': curr_uuid,
            'imageName': image_name 
        })
    
    elif flask.request.method == 'GET':
        # would need something different in production, but just using this for testing
        #   don't think we would actually use this in production anyway
        dynamodb = boto3.resource('dynamodb')
        image_table = dynamodb.Table(IMAGES_TABLE)
        response = image_table.scan()
        items = response['Items']
        image_name_list = []
        for item in items:
            image_name = item['imageName']
            image_name_list.append(image_name)
        return jsonify({'image_names': image_name_list})

