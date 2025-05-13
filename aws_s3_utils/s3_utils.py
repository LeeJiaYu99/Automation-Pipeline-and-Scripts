import boto3
from botocore.config import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import io
import numpy as np
import base64

def login_s3(url, hostname, access_key, secret_key, bucket_name, region, token, folder):
    host_url = url
    hostname = hostname
    access_key = access_key
    secert_key = secret_key
    bucket_name = bucket_name
    region_name = region
    public_key_token = token

    # Create a session using the specified credentials
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secert_key,
        # region_name=region_name,
        # aws_session_token=public_key_token
    )

    # Use the session to create an S3 client
    s3 = session.client('s3', endpoint_url=host_url
                        # , config=Config(s3={'addressing_style': 'path'})
                        )
    
    s3_bucket = boto3.resource('s3', endpoint_url=host_url).Bucket(folder)

    return s3, s3_bucket, bucket_name

def download_file_from_s3(s3, bucket_name, file_key, download_path):
    # Download the file
    try:
        s3.download_file(bucket_name, file_key, download_path)
        return "try", f'Successfully download {file_key}.'
    except NoCredentialsError:
        return "except", "Error: No credentials provided or could not find credentials."
    except PartialCredentialsError:
        return "except", "Error: Incomplete credentials provided."
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            return "except", f'Error: The object {file_key} does not exist in the bucket {bucket_name}'
        elif error_code == '403':
            return "except", f'Error: Access to the bucket {bucket_name} is denied. Check your credentials and permissions.\n{e}'
        elif error_code == 'InvalidAccessKeyId':
            return "except", 'Error: The AWS Access Key Id provided does not exist in our records.'
        elif error_code == 'SignatureDoesNotMatch' :
            return "except", 'Error: The request signature we calculated does not match the signature you provided. Check your Secret Access Key and signing method.'
        else:
            return "except", f"Unexpected error: {e}"
            
def full_s3_path(s3, bucket_name, partial_key):
    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=partial_key)
    matching_keys = []
    for page in page_iterator:
        matching_keys.extend([obj['Key'] for obj in page.get('Contents', []) if obj['Key'].startswitch(partial_key)])
    if len(matching_keys) > 0:
        return matching_keys[0]
    else:
        return partial_key

# if the file extracted is image
def get_image_s3(bucket, file_key):
    file_stream = io.BytesIO()
    bucket.Object(file_key).download_fileobj(file_stream)
    np_1d_array = np.frombuffer(file_stream.getbuffer(), dtype='uint8')

    image_bytes = np_1d_array.tobytes()
    base64_img = base64.b64encode(image_bytes)
    imgs = base64_img.decode("utf-8")
    return imgs