import json
import time

from dynamodb_client import save, query_by_pk
import dynamodb_client
import sqs_client
from config import TEXT_MODEL_ID, VIDEO_MODEL_ID, VISUAL_MODERATION_TYPE,IMG_MODEL_ID
from sha_tool import get_unique_value
from datetime import datetime
from ecs_tool import create_ecs_task
from config import MODERATION_SQS,TASK_TABLE_NAME,USER_TABLE_NAME
import mimetypes



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




def is_media_url(url: str):
    media_types = {
        "audio": ["audio/wav", "audio/mp3", "audio/flac", "audio/mpeg", "audio/w-wav", "audio/x-flac"],
        "video": ["video/mp4"],
        "live": ["m3u8", "rtmp"],
    }

    mime_type, _ = mimetypes.guess_type(url)
    print(mime_type)
    if mime_type:
        if any(mime_type.startswith(mt) for mt in media_types["audio"]):
            return True

        if any(mime_type.startswith(mt) for mt in media_types["video"]):
            return True

    if any(url.lower().endswith(ext) for ext in media_types["live"]):
        return True


    if ".m3u8" in url.lower():
        return True


    if url.lower().startswith("rtmp"):
        return True

    return False


def lambda_handler(event, context):
    print(json.dumps(event))

    body_str = event['body']
    header_obj = event['headers']

    body_data = json.loads(body_str)

    url = body_data.get('url')
    user_id = header_obj.get('user_id')

    text_model_id = body_data.get('text_model_id', TEXT_MODEL_ID)
    img_model_id = body_data.get('img_model_id', IMG_MODEL_ID)
    video_model_id = body_data.get('video_model_id', VIDEO_MODEL_ID)

    # 提取可选参数，设置默认值
    visual_moderation_type = body_data.get('visual_moderation_type', VISUAL_MODERATION_TYPE)  # 默认为图像审核
    video_interval_seconds = int(body_data.get('video_interval_seconds', 10))
    image_interval_seconds = int(body_data.get('image_interval_seconds', 1))
    audio_interval_seconds = int(body_data.get('audio_interval_seconds', 10))
    save_flag = int(body_data.get('save_flag', 1))



    ddb = dynamodb_client.init()


    if is_url_not_empty(url) is False:
        return response("Link exception", "", 415)

    if is_media_url(url) is False:
        return response("This type is not supported, please use wav/mp3/flac/mp4/m3u8/rtmp.", "", 415)

    #Temporarily cancel the face verification function. The previous setting was 1 for content verification and 2 for face verification.
    #task_id = f"{user_id}_{get_unique_value(url)}_{moderation_type.replace(',', '^')}"

    task_id = f"{user_id}_{get_unique_value(url)}"


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
             "user_id": user_id,
             # "moderation_type": 1
         })

    create_ecs_task()

    sqs = sqs_client.init()

    # 准备SQS消息
    sqs_message = {
        "task_id": task_id,
        "media_url": url,
        "user_id": user_id,
        "video_interval_seconds": video_interval_seconds,
        "image_interval_seconds": image_interval_seconds,
        "audio_interval_seconds": audio_interval_seconds,
        "request_time": int(time.time()),
        'text_model_id': text_model_id,
        'img_model_id': img_model_id,
        'video_model_id': video_model_id,
        'save_flag': save_flag,
        'visual_moderation_type': visual_moderation_type
    }

    sqs_client.insert(sqs, MODERATION_SQS, json.dumps(sqs_message,ensure_ascii=False))

    print("Creation successful")

    return response("Creation successful", "", 200)


if __name__ == '__main__':


    body = {
        "url": "https://d14tamu6in7iln.cloudfront.net/sex/93.mp4",

        "video_interval_seconds": 10,
        "image_interval_seconds": 1,
        "audio_interval_seconds": 10,

        "text_model_id": "us.anthropic.claude-3-haiku-20240307-v1:0",
        "img_model_id": "us.amazon.nova-lite-v1:0",
        "video_model_id": "us.amazon.nova-pro-v1:0",

        "save_flag": 1,
        "visual_moderation_type": "image"
    }

    event = {
        "headers": {"user_id": "111"},
        "body": json.dumps(body),
    }

    print(lambda_handler(event, None))

