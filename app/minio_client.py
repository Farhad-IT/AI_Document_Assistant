import os

from minio import Minio

MINIO_ROOT_USER=os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD=os.getenv("MINIO_ROOT_PASSWORD")

client = Minio(
    endpoint="localhost:9000",
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False,
)

bucket = "documents"

if not client.bucket_exists(bucket):
    client.make_bucket(bucket)