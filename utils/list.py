from utils.upload import create_s3_client
from utils.upload import load_yaml_vars

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
