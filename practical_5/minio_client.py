import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

DEFAULT_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
DEFAULT_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
DEFAULT_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
DEFAULT_BUCKET = "analytics-metrics"

def get_s3_client(endpoint_url=DEFAULT_ENDPOINT, access_key=DEFAULT_ACCESS_KEY, secret_key=DEFAULT_SECRET_KEY):
    """
    Creates and returns a boto3 S3 client configured for MinIO.
    """
    return boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
        region_name='us-east-1'
    )

def ensure_bucket_exists(bucket_name=DEFAULT_BUCKET, client=None):
    """
    Ensures that the specified MinIO bucket exists. Creates it if missing.
    """
    if client is None:
        client = get_s3_client()
    try:
        client.head_bucket(Bucket=bucket_name)
        print(f"[MinIO] Bucket '{bucket_name}' already exists.")
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code in ['404', 'NoSuchBucket']:
            client.create_bucket(Bucket=bucket_name)
            print(f"[MinIO] Successfully created bucket '{bucket_name}'.")
        else:
            raise e

if __name__ == "__main__":
    print("[MinIO Helper] Testing connection to MinIO...")
    try:
        s3 = get_s3_client()
        ensure_bucket_exists()
        print("[MinIO Helper] Connection and bucket creation test passed!")
    except Exception as ex:
        print(f"[MinIO Helper] Connection test failed: {ex}")
