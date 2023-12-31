import boto3
from utils.utils import load_yaml_vars
from werkzeug.utils import secure_filename

def create_s3_client():
    s3 = boto3.client("s3")
    return s3

def upload_file_to_s3(file):
    yaml_vars = load_yaml_vars()
    filename = secure_filename(file.filename)
    s3 = create_s3_client()
    try:
        s3.upload_fileobj(
            Fileobj=file,
            Bucket=yaml_vars['bucket_data'],
            Key=filename
        )
    except Exception as e:
        return "Something Happened: " + " : " +  str(e)
    
    # after upload file to s3 bucket, return filename of the uploaded file
    return file.filename
