from flask import Flask, jsonify, make_response
from flask import request, redirect
from flask import send_from_directory, render_template
from utils.upload import upload_file_to_s3
from utils.upload import allowed_file
from utils.list import list_files

import boto3
import os

app = Flask(__name__)


@app.route("/success")
def success():
    outstr = 'upload succeeded!'
    return jsonify(message=outstr)

@app.route("/fail")
def fail():
    return jsonify(message='upload failed!')

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

@app.route("/list")
def list():
    contents = list_files()
    return render_template('collection.html', contents=contents)

@app.route("/upload_page")
def upload_page():
    return send_from_directory("pages", "upload_page.html")    

@app.route("/upload", methods=["POST"])
def upload():

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
        mssg = "Something Happened in App: " + " : " +  str(e)
        return jsonify(message=mssg)
    
    # if upload success, return uploaded file name
    if output:
        mssg = 'good here: {0}'.format(output)
        return jsonify(message=mssg)
        #return redirect("/success")

    # upload failed, redirect to fail page
    else:
        return redirect("/fail")

IMAGES_TABLE = os.environ['IMAGES_TABLE']
# IMAGES_TABLE = 'RobImagesDynamoDBTable'

client_db = boto3.client('dynamodb')

@app.route("/images/<string:image_id>")
def get_image(image_id):
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

@app.route("/create_db_entry")
def create_db_entry():
    return send_from_directory("pages", "create_db_entry.html")    

@app.route("/images", methods=["POST"])
def create_user():

    image_id = request.form.get('imageId')
    image_name = request.form.get('imageName')
    if not image_id or not image_name:
        return jsonify({'error': 'Please provide imageId and name'}), 400
    
    resp = client_db.put_item(
        TableName=IMAGES_TABLE,
        Item={
            'imageId': {'S': image_id },
            'imageName': {'S': image_name }
        }
    )

    return jsonify({
        'imageId': image_id,
        'imageName': image_name 
    })