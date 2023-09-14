# Serverless Framework Python Flask API on AWS

This is my first attempt at making a Flask API on AWS with Serverless

### requirements

You'll need to add a `vars.yml` file that contains values for the variables:
- bucket_data ( for image file storage )
- bucket_serverless ( for serverless file storage )
- image_table_name ( for image file metadata )
- aws_region
- cognito_user_pool_id
- cognito_user_pool_client_id
- cognito_user_pool_client_secret
- cognito_domain
- cognito_authenticated_url
- jwt_secret_key
- jwt_algorithm
