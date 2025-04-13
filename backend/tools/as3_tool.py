import asyncio
import aioboto3
from tools.log_config import get_logger
logger = get_logger(__name__)



async def upload_file(bucket_name, file_name, object_name):
    session = aioboto3.Session()
    async with session.client("s3") as s3:
        try:
            await s3.upload_file(file_name, bucket_name, object_name)
            logger.info(f"File {file_name} uploaded successfully to {bucket_name}/{object_name}")
        except Exception as e:
            logger.info(f"Error uploading file {file_name}: {str(e)}")


async def batch_upload(s3_bucket_name, files_to_upload):
    tasks = []
    for local_file, s3_file in files_to_upload:
        task = asyncio.create_task(upload_file(s3_bucket_name, local_file, s3_file))
        tasks.append(task)

    await asyncio.gather(*tasks)


