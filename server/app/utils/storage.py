import os
import boto3
from botocore.exceptions import ClientError
from io import BytesIO

R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=R2_ENDPOINT_URL,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY
    )

def upload_image_to_r2(file_stream: BytesIO, filename: str) -> str:
    if not all([R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_PUBLIC_URL]):
        print("Warning: R2 Environment variables are not fully set.")
        return

    s3 = get_s3_client()
    try:
        # setelah mesin pembuat QR Code selesai menyimpan gambar, pointernya berada di paling akhir
        # agar bisa baca datanya dari awal maka perlu reset pointer pakai seek(0)
        file_stream.seek(0) # Reset pointer to the beginning of the stream
        s3.upload_fileobj(
            file_stream, 
            R2_BUCKET_NAME, 
            filename,
            ExtraArgs={'ContentType': 'image/png'}
        )
        public_url = f"{R2_PUBLIC_URL.rstrip('/')}/{filename}"
        return public_url
    except ClientError as e:
        print(f"Failed to upload to R2: {e}")
        raise Exception(f"Failed to upload image: {str(e)}")
