from server.src.core.minio_storage import minio_client, BUCKET_NAME
from datetime import timedelta
from minio import S3Error


def generate_presigned_upload_url(object_key: str):
    return minio_client.presigned_put_object(
        bucket_name=BUCKET_NAME,
        object_name=object_key,
        expires=timedelta(minutes=10)
    )

def generate_presigned_access_url(object_key: str):
    return minio_client.presigned_get_object(
        bucket_name=BUCKET_NAME,
        object_name=object_key,
        expires=timedelta(minutes=5)
    )

def object_exists(object_key:str):
    try:
        minio_client.stat_object(BUCKET_NAME,object_key)
        return True
    except S3Error:
        return False

def delete_object(object_key: str):
    minio_client.remove_object(
        bucket_name=BUCKET_NAME,
        object_name=object_key
    )

def get_object_size(object_key: str):
    obj = minio_client.stat_object(
        BUCKET_NAME,
        object_key
    )
    return obj.size
