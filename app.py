import boto3, botocore
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response
from flask import request, redirect, url_for
from flask import send_from_directory
import os
from werkzeug.utils import secure_filename
import utils

load_dotenv()

app = Flask(__name__)


@app.route("/")
def hello_from_root():
    return jsonify(message='Hello from root!')


@app.route("/hello")
def hello():
    return jsonify(message='Hello from path!')


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# function to check file extension
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload_page")
def upload_page():
    return send_from_directory("pages", "upload_page.html")    

@app.route("/upload", methods=["POST"])
def create():

    # check whether an input field with name 'user_file' exist
    
    if 'user_file' not in request.files:
        flash('No user_file key in request.files')
        return redirect(url_for('new'))

    # after confirm 'user_file' exist, get the file from input
    file = request.files['user_file']

    # check whether a file is selected
    #if file.filename == '':
    #    flash('No selected file')
    #    return redirect(url_for('new'))

    # check whether the file extension is allowed (eg. png,jpeg,jpg,gif)
    #if file and allowed_file(file.filename):
    #    output = upload_file_to_s3(file) 
        
        # if upload success,will return file name of uploaded file
    #    if output:
    #        # write your code here 
    #        # to save the file name in database

    #        flash("Success upload")
    #        return redirect(url_for('show'))

        # upload failed, redirect to upload page
    #    else:
    #        flash("Unable to upload, try again")
    #        return redirect(url_for('new'))
        
    # if file extension not allowed
    #else:
    #    flash("File type not accepted,please try again.")
    #    return redirect(url_for('new'))