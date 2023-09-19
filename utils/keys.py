import json
import os
import requests
from utils.utils import load_yaml_vars


def get_cognito_public_keys():
    yaml_vars = load_yaml_vars()
    region = yaml_vars['aws_region']
    pool_id = yaml_vars['cognito_user_pool_id']
    url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"

    resp = requests.get(url)
    return json.dumps(json.loads(resp.text)["keys"][1])