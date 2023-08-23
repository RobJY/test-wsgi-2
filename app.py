from flask import Flask, jsonify, make_response
from flask import request, redirect
from flask import send_from_directory, render_template
from utils.upload import upload_file_to_s3
from utils.upload import allowed_file
from utils.list import list_files

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

    # check whether an input field with name 'user_file' exist
    if 'user_file' not in request.files:
        return redirect("/fail")

    # after confirm 'user_file' exist, get the file from input
    file = request.files['user_file']
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
    
    # if upload success,will return file name of uploaded file
    if output:
        mssg = 'good here: {0}'.format(output)
        return jsonify(message=mssg)
        #return redirect("/success")

    # upload failed, redirect to fail page
    else:
        return redirect("/fail")
    
