from yaml import safe_load

def load_yaml_vars():
    with open('vars.yml', 'r') as file_in:
        vars = safe_load(file_in)
    return vars
