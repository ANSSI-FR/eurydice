from minio.error import S3Error

from eurydice.common import minio


def object_exists(bucket: str, key: str) -> bool:
    result = True
    response = None
    try:
        response = minio.client.get_object(
            bucket_name=bucket,
            object_name=key,
        )
    except S3Error as e:
        if e.code != "NoSuchKey":
            raise
        result = False
    finally:
        if response:
            response.close()
            response.release_conn()
    return result


__all__ = ("object_exists",)
