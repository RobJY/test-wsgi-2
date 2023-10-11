from flask import request, redirect, url_for, Flask, jsonify, make_response, send_from_directory, render_template
from utils.image import create_list_image_data, get_image_data, upload_image, list_files, list_imageIds
from utils.utils import load_yaml_vars
from flask_awscognito import AWSCognitoAuthentication
from flask_cors import CORS
from utils.keys import get_cognito_public_keys
from flask_jwt_extended import JWTManager, verify_jwt_in_request, set_access_cookies, get_jwt_identity, jwt_required
from jwt.algorithms import RSAAlgorithm
from flask_wtf.csrf import CSRFProtect
import sys

yaml_vars = load_yaml_vars()

app = Flask(__name__)
app.config["JWT_PUBLIC_KEY"] = RSAAlgorithm.from_jwk(get_cognito_public_keys())
app.config["AWS_COGNITO_USER_POOL_ID"] = yaml_vars['cognito_user_pool_id']
app.config["AWS_COGNITO_USER_POOL_CLIENT_ID"] = yaml_vars['cognito_user_pool_client_id']
app.config["AWS_COGNITO_USER_POOL_CLIENT_SECRET"] = yaml_vars['cognito_user_pool_client_secret']
app.config["AWS_COGNITO_REDIRECT_URL"] = yaml_vars['cognito_authenticated_url']
app.config["AWS_DEFAULT_REGION"] = yaml_vars['aws_region']
app.config["AWS_COGNITO_DOMAIN"] = yaml_vars['cognito_domain']
app.config["JWT_SECRET_KEY"] = yaml_vars['jwt_secret_key']
app.config["JWT_ALGORITHM"] = yaml_vars['jwt_algorithm']
app.config["JWT_COOKIE_CSRF_PROTECT"] = True
app.config['SECRET_KEY'] = yaml_vars['jwt_secret_key']

try:
    CORS(app)
    aws_auth = AWSCognitoAuthentication(app)
    jwt = JWTManager(app)
    csrf = CSRFProtect()
    csrf.init_app(app)
except Exception as e:
    print('start-up error: {}'.format(str(e)))
    sys.exit(1)

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

@app.route("/")
def base():
    return jsonify(message='Welcome to the base')

@app.route("/success")
def success():
    return jsonify(message='upload succeeded!')

@app.route("/fail")
def fail():
    return jsonify(message='upload failed!')

@app.route("/list_bucket")
def list():
    verify_jwt_in_request(locations = ['cookies'])
    print('jwt_identity')
    current_user = get_jwt_identity()
    print(current_user)
    if get_jwt_identity():
        contents = list_files()
        return render_template('collection.html', contents=contents)
    else:
        print('/list_bucket failed.  redirecting to sign in page')
        return redirect(aws_auth.get_sign_in_url())

@app.route("/upload_page")
def upload_page():
    verify_jwt_in_request(locations = ['cookies'])
    if get_jwt_identity():
        return render_template('upload.html')
    else:
        print('/upload_page failed.  redirecting to sign in page')
        return redirect(aws_auth.get_sign_in_url())


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

@app.route("/login")
def login():
    return redirect(aws_auth.get_sign_in_url())

@app.route("/secret/")
def protected():
    try:
        verify_jwt_in_request(optional = True,
                              locations = ['cookies'])
        if get_jwt_identity():
            return render_template("secret.html")
        else:
            return redirect(aws_auth.get_sign_in_url())

    except Exception as e:
        print('*** failed to verify jwt in request ***')
        print(e)
        return redirect(aws_auth.get_sign_in_url())

@app.route("/menu_submission/", methods=["POST"])
def menu_submission():
    token = request.form['token']
    selected_page = request.form['page_menu']
    if selected_page == 'list_bucket':
        resp = make_response(redirect(url_for("list")))
        set_access_cookies(resp, token, max_age=30*60)
        return resp
    elif selected_page == 'upload':
        resp = make_response(redirect(url_for("upload_page")))
        set_access_cookies(resp, token, max_age=30*60)
        return resp
    else:
        return redirect(url_for("fail"))

@app.route("/loggedin/")
def protected_menu():
    access_token = aws_auth.get_access_token(request.args)
    return render_template('secret_menu.html', token=access_token)

@app.route("/user_image_pref_page")
def user_image_pref_page():
    # get available images
    images = list_files()

    return render_template('user_image_prefs.html', images=images)



# old working authenticated endpoint
#@app.route("/loggedin/", methods=["GET"])
#def loggedin():
#    print('*** entering loggedin ***')
#    print('request.args = {}'.format(request.args))
#    access_token = aws_auth.get_access_token(request.args)
#    print('access_token: {}'.format(access_token))
#
#    resp = make_response(redirect(url_for("protected")))
#    set_access_cookies(resp, access_token, max_age=30*60)
#
#    print('*** leaving loggedin ***')
#    return resp
