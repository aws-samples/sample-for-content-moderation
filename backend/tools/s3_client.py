import boto3
from botocore.config import Config
from config import REGION_NAME

config = Config(max_pool_connections=100)


class S3Client(object):
    def __init__(self, bucket,):
        self.client = boto3.client("s3", region_name=REGION_NAME, config=config)
        self.bucket = bucket


    def download_file_from_s3(self, s3_file_path, local_file_path):
        try:
            # 下载文件
            self.client.download_file(self.bucket, s3_file_path, local_file_path)
            print(f"File downloaded successfully: {local_file_path}")
        except Exception as e:
            print(f"Error downloading file: {str(e)}")

    def get_presigned_url(self,bucket_name,key,expiration):
        url = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=expiration
        )

        return url
