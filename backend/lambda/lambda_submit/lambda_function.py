import json

from dynamodb_client import save, query_by_pk
import dynamodb_client
import sqs_client
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
    # moderation_type = body_data.get('moderation_type')
    user_id = header_obj.get('user_id')

    ddb = dynamodb_client.init()


    if is_url_not_empty(url) is False:
        return response("Link exception", "", 415)

    if is_media_url(url) is False:
        return response("This type is not supported, please use wav/mp3/flac/mp4/m3u8/rtmp.", "", 415)

    #Temporarily cancel the face verification function. The previous setting was 1 for content verification and 2 for face verification.
    #task_id = f"{user_id}_{get_unique_value(url)}_{moderation_type.replace(',', '^')}"

    task_id = f"{user_id}_{get_unique_value(url)}_1"


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

    sqs_client.instert(sqs, MODERATION_SQS, json.dumps({
        "user_id": user_id,
        "url": url,
        "task_id": task_id,
        "moderation_type": 1,
    }))

    print("Creation successful")

    return response("Creation successful", "", 200)


if __name__ == '__main__':
    # event = {
    #     "queryStringParameters": {
    #         "token": "6666",
    #         "url": "https://d14tamu6in7iln.cloudfront.net/sex/shehaojici.mp4"
    #     }
    # }
    #

    event = {
        "headers": {"user_id":"111"},
        "body": "{\"token\": \"xxxx\", \"url\": \"http://d14tamu6in7iln.cloudfront.net/audio/e5a82e15-6cae-490e-906f-4f09ec21c67a.mp3\", \"moderation_type\": \"1\"}",
    }

    #https://d14tamu6in7iln.cloudfront.net/sex/93.mp4
    #https://d14tamu6in7iln.cloudfront.net/audio/e5a82e15-6cae-490e-906f-4f09ec21c67a.wav
    print(lambda_handler(event, None))

    # url=" "
    # print(is_url_not_empty(url))
