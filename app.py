from flask import request, redirect, url_for, Flask, jsonify, make_response, send_from_directory, render_template
from utils.image import create_list_image_data, get_image_data, upload_image, list_files, list_imageIds
from utils.utils import load_yaml_vars
from flask_awscognito import AWSCognitoAuthentication
from flask_cors import CORS
from utils.keys import get_cognito_public_keys
from flask_jwt_extended import JWTManager, verify_jwt_in_request, set_access_cookies, get_jwt_identity, jwt_required

# do we need this??
# import jwt  # will collide with jwt in set-up block


from jwt.algorithms import RSAAlgorithm

# from flask_wtf.csrf import CSRFProtect

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
# seems like the following vars are not needed
#app.config['PROPAGATE_EXCEPTIONS'] = True
#app.config['JWT_TOKEN_LOCATION'] = ['cookies']
# will want to add this when we harden the system
#app.config["JWT_COOKIE_CSRF_PROTECT"] = False   # will want to harden this!

try:
    print('*** starting set-up ***')
    CORS(app)
    aws_auth = AWSCognitoAuthentication(app)
    jwt = JWTManager(app)
    ## csrf = CSRFProtect(app)
    print('*** finished set-up ***')
except Exception as e:
    print('**** set-up error: {}'.format(str(e)))


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


# just wanted to test and it works   
# @app.route("/test_cognito")
# def test_cognito():
#     return get_cognito_public_keys()


'''  working code  '''
@app.route("/login")
def login():
    print('*** entering login ***')
    print(aws_auth.get_sign_in_url())
    print('*** leaving login ***')
    test_url = 'https://rob-test-serverless-flask.auth.us-east-1.amazoncognito.com/login?client_id=5hep2oo4uu2rnkhk7l61fit9u2&response_type=code&scope=email+openid+phone&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Faws_cognito_redirect'
    return redirect(aws_auth.get_sign_in_url())

@app.route("/secret/")
def protected():
    print('*** entering protected ***')
    print('request.args = {}'.format(request.args))
    print(dir(request))
    print(f'request.headers = {request.headers}')
    try:
        verify_jwt_in_request(optional = True,
                              locations = ['cookies'])
        print(f'jwt identity: {get_jwt_identity()}')
        if get_jwt_identity():
            return render_template("secret.html")
        else:
            return redirect(aws_auth.get_sign_in_url())

    except Exception as e:
        print('*** failed to verify jwt in request ***')
        print(e)
        return redirect(aws_auth.get_sign_in_url())

    print('*** leaving protected ***')
    return jsonify(logged_in_as=current_user), 200


@app.route("/loggedin/", methods=["GET"])
def loggedin():
    print('*** entering loggedin ***')
    print('request.args = {}'.format(request.args))
    # print('access_token = {}'.format(aws_auth.get_access_token(request.args)))
    access_token = aws_auth.get_access_token(request.args)
    print('access_token: {}'.format(access_token))

    #resp = make_response(redirect(url_for('protected')))
    # set_access_cookies(resp, access_token, max_age=30 * 60)
    #resp.set_cookie('access_token', access_token)
    #headers = { 'HTTP_AUTHORIZATION': access_token }
    #resp.headers = headers

    #resp = Response(url_for("protected"), 
    #                status=302, 
    #                headers={ 'HTTP_AUTHORIZATION': access_token, 'Location': url_for("protected") })
    # try:
    resp = make_response(redirect(url_for("protected")))
    set_access_cookies(resp, access_token, max_age=30*60)

    # except Exception as e:
    #     print('*** failed to set access cookies ***')
    #     print(e)
    #     return redirect(url_for("fail"))

    # resp = redirect(url_for('protected'))
    # resp.data = ''
    # # resp.set_cookie('access_token', access_token)
    # resp.headers = { 'HTTP_AUTHORIZATION': access_token }
    # #resp.headers = headers

    print('*** leaving loggedin ***')
    return resp

''' end working code '''

# @app.route('/base')
# @aws_auth.authentication_required
# def index():
#     claims = aws_auth.claims # also available through g.cognito_claims
#     return jsonify({'claims': claims})


#@app.route('/aws_cognito_redirect')
#def aws_cognito_redirect():
#    access_token = aws_auth.get_access_token(request.args)
#    return jsonify({'access_token': access_token})

#@app.route('/sign_in')
#def sign_in():
#    print(aws_auth.get_sign_in_url())
#    print()
#    return redirect(aws_auth.get_sign_in_url())


#aws_auth = AWSCognitoAuthentication(app)

#@app.route('/')
#def index():   
#    return ('index')

#@app.route('/loggedin')
#def aws_cognito_redirect():
#    print('request.args')
#    print(request.args)
#    print(request.args.to_dict())
#    #request_args_json = json.dumps(request.args.to_dict())
#    #print(request_args_json)
#    #print('requesting access token...')
#    #access_token = aws_auth.get_access_token(request.args)
#    #print('access token: {}'.format(access_token))
#    #request.headers.get(access_token)   
#    #url = "http://127.0.0.1:5000/secret"
#    #headers = {'Authorization': 'Bearer ' + str(access_token)}
#    #response = requests.get(url, headers=headers) 
#    #return response.content
#    return jsonify(message=request.args)

'''
#@app.route('/sign_in')
#def sign_in():
#    return redirect(aws_auth.get_sign_in_url())

#@app.route('/secret')
#@aws_auth.authentication_required
#def loggedin():
#    return ('logged in successfully!')
 
#if __name__ == "__main__":
#    app.run(debug=True, use_reloader=False)


#aws_auth = AWSCognitoAuthentication(app)


#@app.route('/')
#@aws_auth.authentication_required
#def index():
#    claims = aws_auth.claims # also available through g.cognito_claims
#    return jsonify({'claims': claims})


#@app.route('/loggedin')
#def aws_cognito_redirect():
#    access_token = aws_auth.get_access_token(request.args)
#    return jsonify({'access_token': access_token})


#@app.route('/sign_in')
#def sign_in():
#    return redirect(aws_auth.get_sign_in_url())


#if __name__ == '__main__':
#    app.run(debug=True)

'''