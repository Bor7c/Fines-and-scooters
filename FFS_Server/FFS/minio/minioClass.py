from minio import Minio
from minio.error import S3Error
from io import BytesIO
from base64 import *
import os
import pip._vendor.requests as requests
import io
from datetime import timedelta

# sudo minio server ~/minio --console-address :9090


class MinioClass:
    def __init__(self):
        try:
            self.client = Minio(endpoint="172.17.0.1:9000",
                                access_key='minioadmin',
                                secret_key='minioadmin',
                                secure=False)
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def addUser(self, username: str):
        try:
            self.client.make_bucket(username)
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def removeUser(self, username: str):
        try:
            self.client.remove_bucket(username)
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def addImage(self, bucket: str, title: str, image_url: str):
        try:
            response = requests.get(image_url)
            image_stream = io.BytesIO(response.content)
            self.client.put_object(bucket_name=bucket,
                                   object_name=f"{title}.png",
                                   data=image_stream,
                                   length=len(response.content))
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def getImage(self, bucket: str, fine_title: str):
        try:
            result = self.client.get_presigned_url(
                method='GET',
                bucket_name=bucket,
                object_name=f"{fine_title}.png",
                expires=timedelta(minutes=1),
                )
            # print (result)
            return result
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def removeImage(self, bucket: str, title: str):
        try:
            self.client.remove_object(bucket_name=bucket,
                                      object_name=f"{title}.png")
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def check_bucket_exists(self, bucket_name):
        info_bucket = self.client.bucket_exists(bucket_name)
        if (info_bucket):
            print(f'[{info_bucket}] Бакет "{bucket_name}" существует')
        else:
            print(f'[{info_bucket}] Бакет "{bucket_name}" не существует')



DB = MinioClass()
# DB.addImage('fines','ABOBA','https://polinka.top/uploads/posts/2023-06/1686249023_polinka-top-p-znak-svetofor-kartinka-instagram-32.png')
DB.getImage('fines', 'ABOBA')


# DB.removeImage('fines', 'ABOBA')