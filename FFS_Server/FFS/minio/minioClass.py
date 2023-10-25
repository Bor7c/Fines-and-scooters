from minio import Minio
from minio.error import S3Error
from io import BytesIO
from base64 import b64encode, b64decode
import os
import requests


from minio import Minio

               # опциональный параметр, отвечающий за вкл/выкл защищенное TLS соединение



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
            image = requests.get(image_url)
            image_data = b64decode(image)
            image_stream = BytesIO(image_data)
            self.client.put_object(bucket_name=bucket,
                                   object_name=f"{title}.png",
                                   data=image_stream,
                                   length=len(image_data))
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def getImage(self, bucket: str, fine_title: str):
        try:
            result = self.client.get_object(bucket_name=bucket,
                                            object_name=f"{fine_title}.png")
            # print (b64encode(BytesIO(result.data).read()).decode())
            return b64encode(BytesIO(result.data).read()).decode()
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def removeImage(self, username: str, image_id: str, image_extension: str):
        try:
            self.client.remove_object(bucket_name=username,
                                      object_name=f"{image_id}.{image_extension}")
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
# DB.getImage('fines', '1', 'png')
DB.addImage('fines','ABOBA','https://nadrovahdon.ru/wp-content/uploads/2023/05/Фон-баннер-пиво.jpg')