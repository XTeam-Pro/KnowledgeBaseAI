"""
S3/MinIO utilities for presigned URLs
Provides functions for generating presigned URLs for upload and download
"""

import os
from typing import Dict
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

# Initialize S3/MinIO client
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "")
S3_BUCKET = os.getenv("S3_BUCKET", "knowledgebase")
S3_REGION = os.getenv("S3_REGION", "us-east-1")

try:
    s3_client = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name=S3_REGION,
        config=Config(signature_version='s3v4')
    )
    print(f"✅ Connected to S3/MinIO at {S3_ENDPOINT}")
except Exception as e:
    print(f"⚠️ Warning: Could not connect to S3/MinIO: {e}")
    s3_client = None


def presign_put(key: str, expiry_sec: int = 600) -> Dict[str, str]:
    """
    Generate a presigned URL for uploading a file to S3/MinIO

    Args:
        key: Object key (file path) in S3 bucket
        expiry_sec: URL expiration time in seconds (default 600)

    Returns:
        Dictionary with presigned URL and metadata
    """
    if not s3_client:
        return {
            "status": "error",
            "message": "S3 client not initialized"
        }

    try:
        # Ensure bucket exists
        try:
            s3_client.head_bucket(Bucket=S3_BUCKET)
        except ClientError:
            # Bucket doesn't exist, create it
            s3_client.create_bucket(Bucket=S3_BUCKET)
            print(f"✅ Created S3 bucket: {S3_BUCKET}")

        # Generate presigned URL for PUT
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': key
            },
            ExpiresIn=expiry_sec,
            HttpMethod='PUT'
        )

        return {
            "status": "success",
            "url": url,
            "method": "PUT",
            "bucket": S3_BUCKET,
            "key": key,
            "expires_in": expiry_sec
        }
    except ClientError as e:
        return {
            "status": "error",
            "message": f"Failed to generate presigned URL: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def presign_get(key: str, expiry_sec: int = 600) -> Dict[str, str]:
    """
    Generate a presigned URL for downloading a file from S3/MinIO

    Args:
        key: Object key (file path) in S3 bucket
        expiry_sec: URL expiration time in seconds (default 600)

    Returns:
        Dictionary with presigned URL and metadata
    """
    if not s3_client:
        return {
            "status": "error",
            "message": "S3 client not initialized"
        }

    try:
        # Check if object exists
        try:
            s3_client.head_object(Bucket=S3_BUCKET, Key=key)
        except ClientError:
            return {
                "status": "error",
                "message": f"Object not found: {key}"
            }

        # Generate presigned URL for GET
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': key
            },
            ExpiresIn=expiry_sec,
            HttpMethod='GET'
        )

        return {
            "status": "success",
            "url": url,
            "method": "GET",
            "bucket": S3_BUCKET,
            "key": key,
            "expires_in": expiry_sec
        }
    except ClientError as e:
        return {
            "status": "error",
            "message": f"Failed to generate presigned URL: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def delete_object(key: str) -> Dict[str, str]:
    """
    Delete an object from S3/MinIO

    Args:
        key: Object key (file path) in S3 bucket

    Returns:
        Result dictionary with status
    """
    if not s3_client:
        return {
            "status": "error",
            "message": "S3 client not initialized"
        }

    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=key)

        return {
            "status": "success",
            "bucket": S3_BUCKET,
            "key": key
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def list_objects(prefix: str = "", max_keys: int = 100) -> Dict:
    """
    List objects in S3/MinIO bucket

    Args:
        prefix: Filter objects by prefix
        max_keys: Maximum number of objects to return

    Returns:
        Dictionary with list of objects
    """
    if not s3_client:
        return {
            "status": "error",
            "message": "S3 client not initialized",
            "objects": []
        }

    try:
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix=prefix,
            MaxKeys=max_keys
        )

        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append({
                    "key": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat()
                })

        return {
            "status": "success",
            "bucket": S3_BUCKET,
            "count": len(objects),
            "objects": objects
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "objects": []
        }
