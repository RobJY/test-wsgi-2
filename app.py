from flask import Flask, jsonify, make_response
from flask import send_from_directory, render_template
from utils.image import create_list_image_data, get_image_data, upload_image, list_files, list_imageIds

app = Flask(__name__)

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

@app.route("/success")
def success():
    return jsonify(message='upload succeeded!')

@app.route("/fail")
def fail():
    return jsonify(message='upload failed!')

@app.route("/list_bucket")
def list():
    contents = list_files()
    return render_template('collection.html', contents=contents)

@app.route("/upload_page")
def upload_page():
    return send_from_directory("pages", "upload_page.html")    

@app.route("/upload", methods=["POST"])
def upload():
    return upload_image()

@app.route("/images/<string:image_id>")
def get_image(image_id):
    return get_image_data(image_id)

@app.route("/create_db_entry")
def create_db_entry():
    return send_from_directory("pages", "create_db_entry.html")    

@app.route("/imageIds")
def get_image_ids():
    return list_imageIds()

@app.route("/images", methods=["GET", "POST"])
def create_image():
    return create_list_image_data()    
    