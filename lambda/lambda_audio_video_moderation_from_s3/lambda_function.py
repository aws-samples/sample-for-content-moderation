import json

from dynamodb_client import save, query_by_pk
import dynamodb_client
import sqs_client
from sha_tool import get_unique_value
from datetime import datetime
from ecs_tool import create_ecs_task
from config import S3_MODERATION_SQS, TASK_TABLE_NAME, USER_ID, TEXT_MODEL_ID, IMG_MODEL_ID, VIDEO_MODEL_ID, \
    VISUAL_MODERATION_TYPE


def response(message, result_info, statusCode):
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps({
            "message": message,
            "code": statusCode,
            "body": result_info
        })
    }


def get_current_formatted_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d_%H%M%S")

    return formatted_time


def is_url_not_empty(url):
    return bool(url.strip())


def lambda_handler(event, context):
    print(json.dumps(event))


    if 'Records' not in event or 's3' not in event['Records'][0]:
        return {
            "error": "Skip if not an S3 event"
        }

    # 提取所需的值
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    print(f"bucket_name  {bucket_name}")
    print(f"object_key  {object_key}")
    # 分割 object_key 以获取文件夹名和文件名
    folder_name, filename = object_key.split('/')
    print(bucket_name, object_key, folder_name, filename)
    if filename =="":
        return response("File does not exist", "", 200)

    ddb = dynamodb_client.init()

    url=f"s3://{bucket_name}/{object_key}"
    if is_url_not_empty(url) is False:
        return response("Link exception", "", 415)

    task_id = f"{USER_ID}_{get_unique_value(url)}_1"

    table = ddb.Table(TASK_TABLE_NAME)

    response_ddb = query_by_pk(table, "task_id", task_id)

    print(response_ddb)


    current_time = get_current_formatted_time()

    save(table,
         {
             "task_id": task_id,
             "create_time": current_time,
             "modify_time": current_time,
             "url": url,
             "task_state": "1",
             "user_id": USER_ID,
             # "moderation_type": 1
         })

    create_ecs_task()

    sqs = sqs_client.init()



    sqs_message = {
        "task_id": task_id,
        "media_url": url,
        "user_id": USER_ID,
        "video_interval_seconds": "10",
        "image_interval_seconds": "1",
        "audio_interval_seconds": "10",
        'text_model_id': TEXT_MODEL_ID,
        'img_model_id': IMG_MODEL_ID,
        'video_model_id': VIDEO_MODEL_ID,
        'save_flag': "1",
        'visual_moderation_type': VISUAL_MODERATION_TYPE
    }

    sqs_client.insert(sqs, S3_MODERATION_SQS, json.dumps(sqs_message))




    print("Creation successful")

    return response("Creation successful", "", 200)



