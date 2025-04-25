from config import START_CONNECT_MAX_RETRIES, END_CONNECT_MAX_RETRIES, RETRY_DELAY,  TASK_TABLE_NAME
from processor.video_processor import process_video
from tools import dynamodb_client
from tools.log_config import get_logger
from tools.metadata_tool import save_metadata

logger = get_logger(__name__)
import json


def process_sqs_info(message):
    '''

    :param message:
    :return:
    '''

    print(message)
    print(json.dumps(message))
    # logger.info(json.dumps(message))
    body_string = message['Body']

    # if isinstance(body_string, str):
    body_json = json.loads(body_string)
    # else:
    #     body_json = body_string

    # 用户id user_id
    user_id = body_json.get('user_id', '')
    # 任务id task_id
    task_id = body_json.get('task_id', '')
    # 媒体文件url media_url
    media_url = body_json.get('media_url', '')

    text_model_id = body_json.get('text_model_id', '')
    img_model_id = body_json.get('img_model_id', '')
    video_model_id = body_json.get('video_model_id', '')
    save_flag = body_json.get('save_flag', '')
    image_interval_seconds = int(body_json.get('image_interval_seconds', 1))
    audio_interval_seconds = int(body_json.get('audio_interval_seconds', 10))
    video_interval_seconds = int(body_json.get('video_interval_seconds', 10))
    visual_moderation_type = body_json.get('visual_moderation_type', 'image')

    metadata_obj = {
        'user_id': user_id,
        'task_id': task_id,
        'media_url': media_url,
        'text_model_id': text_model_id,
        'img_model_id': img_model_id,
        'video_model_id': video_model_id,
        'save_flag': save_flag,
        'visual_moderation_type': visual_moderation_type,
        'image_interval_seconds': image_interval_seconds,
        'audio_interval_seconds': audio_interval_seconds,
        'video_interval_seconds': video_interval_seconds
    }

    logger.info("process_sqs_info")
    logger.info(metadata_obj)

    save_metadata(task_id, metadata_obj)

    ddb = dynamodb_client.init()
    task_table = ddb.Table(TASK_TABLE_NAME)
    dynamodb_client.update(task_table, "task_id", task_id, "task_state", "2")

    reponse = process_video(task_id, media_url, visual_moderation_type, START_CONNECT_MAX_RETRIES,
                            END_CONNECT_MAX_RETRIES, RETRY_DELAY, audio_interval_seconds,
                            image_interval_seconds if visual_moderation_type == "image" else video_interval_seconds)

    logger.info('Porcess success' if reponse else 'Process fail')


class MessageProcessor:

    def process(self, message):
        process_sqs_info(message)


if __name__ == '__main__':
    body = json.dumps({
        "user_id": "bbb",
        "task_id": "ccc",
        "media_url": "https://d14tamu6in7iln.cloudfront.net/sex/sex_e2.mp4",
        "text_model_id": "us.amazon.nova-lite-v1:0",
        "img_model_id": "rekognition",
        "video_model_id": "us.amazon.nova-pro-v1:0",
        "save_flag": "1",
        "visual_moderation_type": "image"
    })
    message = {"MessageId": "5e1c2425-4bf4-41b6-b30d-f71c089cc8f3",
               "ReceiptHandle": "AQEBbaR5KDAo/Or7HObgCaSFhQfky7X8WM/KrFpL/UyFX9EGSEaQFdBS18ZtA2NmcyOZGicYeNveVubjfT8uNS1syphwDm8QdAfi58sN/jbHcqffYm7KkakQ6EAeVGb0L2msnlj+NCjgdt7pjOWKW3RTDfhWSgi9cPZo4YjP5nRsrvaU04dpE4ENZ8IgX89CG+L4K8ZeCvl4IFPZEqEvwBYLP7d0ENeHvLVCwrxeONjgKhCYKYZk7Czlv50P5ObyYQGbWzfO/GRz9Apj9jNuXMc0ijLCexjeHTN05A7NFD55W+Ffbv14JCVr3watPLg8JEvutSolyRDAjKoQV+6oStabrKbmK0liYeW4XfL9PlHPILsrzdgt9fmeakF2lVyJ5K8q52gx+qBUtTcCa7f9teL2AoS3skqARl/TKnfVW6eOWBGX55pepNW2WiNN/uCRuxd1Qz3/7brb+atfc64+1bKQqA==",
               "MD5OfBody": "b4a0833cda378eee4405bdb806636d0d", "Body": body}
    process_sqs_info(message)
