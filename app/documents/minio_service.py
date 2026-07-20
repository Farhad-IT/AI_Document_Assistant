from fastapi import UploadFile
from minio import Minio

from app.minio_client import bucket


class MinioService:
    def __init__(self, minio_client: Minio):
        self.minio_client = minio_client

    async def upload_document(self, object_name: str, file: UploadFile):
        res = self.minio_client.put_object(
            bucket_name=bucket,
            object_name=object_name,
            data=file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=file.content_type,
        )
        return res

    def get_file_stream(self, object_key: str, filepath: str):
        res = self.minio_client.fget_object(
            bucket_name=bucket,
            object_name=object_key,
            file_path=filepath,
        )
        return res

    async def delete_document(self, object_name: str):
        res = self.minio_client.remove_object(bucket, object_name)
        return res