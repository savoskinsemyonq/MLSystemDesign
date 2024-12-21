import os
import pandas as pd
from io import BytesIO
from minio import Minio
from dotenv import load_dotenv
import logging
load_dotenv()

MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")

def data_to_minio():
    client = Minio("minio:9000", access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)

    train_data = "train.csv"
    file_path = f"./data/{train_data}"
    csv_data = pd.read_csv(file_path).to_csv(index=False).encode("utf-8")
    client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=train_data,
        data=BytesIO(csv_data),
        length=len(csv_data),
        content_type="application/csv"
    )
    logging.info(f"Uploaded '{train_data}' to minio.")

    test_data = "test.csv"
    file_path = f"./data/{test_data}"
    csv_data = pd.read_csv(file_path).to_csv(index=False).encode("utf-8")
    client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=test_data,
        data=BytesIO(csv_data),
        length=len(csv_data),
        content_type="application/csv"
    )
    logging.info(f"Uploaded '{test_data}' to minio.")