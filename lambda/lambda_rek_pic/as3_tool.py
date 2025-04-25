import asyncio
import aioboto3

async def upload_file(bucket_name, file_name, object_name):
    session = aioboto3.Session()
    async with session.client("s3") as s3:
        try:
            await s3.upload_file(file_name, bucket_name, object_name)
            print(f"File {file_name} uploaded successfully to {bucket_name}/{object_name}")
        except Exception as e:
            print(f"Error uploading file {file_name}: {str(e)}")


async def batch_upload(s3_bucket_name, files_to_upload):
    tasks = []
    for local_file, s3_file in files_to_upload:
        task = asyncio.create_task(upload_file(s3_bucket_name, local_file, s3_file))
        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    print("准备执行")
    s3_bucket_name = "video-moderation-a"
    s3_dir = "customer_video/"
    files_to_upload = [
        ("../resources22/s/f1_01.mp4", s3_dir + "f1_01.mp4"),
        # ("../resources22/audio/a.flac",s3_dir+ "a.flac"),
        # ("../resources22/audio/f1_01.flac", s3_dir+"f1_01.flac"),
    ]

    asyncio.run(batch_upload(s3_bucket_name, files_to_upload))
    print("执行完成")
