import json
from config import START_CONNECT_MAX_RETRIES, END_CONNECT_MAX_RETRIES, RETRY_DELAY, AUDIO_SEGMENT_DURATION, \
    SNAPSHOT_INTERVAL, TASK_TABLE_NAME, VISUAL_MODERATION_TYPE, SPLIT_VIDEO_INTERVAL
from processor.video_processor import process_video
from tools import dynamodb_client
from tools.log_config import get_logger
logger = get_logger(__name__)

def process_sqs_info(message):
    '''

    :param message:
    :return:
    '''
    # logger.info(json.dumps(message))
    body_string = message['Body']
    body_json = json.loads(body_string)

    #用户id  user_id
    user_id=body_json['user_id']
    #任务id  task id
    task_id=body_json['task_id']

    #媒体文件url media_file url
    media_url=body_json['url']

    logger.info(f"User ID: {user_id}, Task ID: {task_id}, Media URL: {media_url}")


    ddb = dynamodb_client.init()
    task_table = ddb.Table(TASK_TABLE_NAME)
    dynamodb_client.update(task_table,"task_id",task_id,"task_state","2")

    reponse=process_video(task_id,media_url, START_CONNECT_MAX_RETRIES, END_CONNECT_MAX_RETRIES, RETRY_DELAY,AUDIO_SEGMENT_DURATION,SNAPSHOT_INTERVAL if VISUAL_MODERATION_TYPE =="image" else SPLIT_VIDEO_INTERVAL)

    logger.info('Porcess success' if reponse else 'Process fail')


class MessageProcessor:

    def process(self, message):

        process_sqs_info(message)

if __name__ == '__main__':
    message={"MessageId": "5e1c2425-4bf4-41b6-b30d-f71c089cc8f3", "ReceiptHandle": "AQEBbaR5KDAo/Or7HObgCaSFhQfky7X8WM/KrFpL/UyFX9EGSEaQFdBS18ZtA2NmcyOZGicYeNveVubjfT8uNS1syphwDm8QdAfi58sN/jbHcqffYm7KkakQ6EAeVGb0L2msnlj+NCjgdt7pjOWKW3RTDfhWSgi9cPZo4YjP5nRsrvaU04dpE4ENZ8IgX89CG+L4K8ZeCvl4IFPZEqEvwBYLP7d0ENeHvLVCwrxeONjgKhCYKYZk7Czlv50P5ObyYQGbWzfO/GRz9Apj9jNuXMc0ijLCexjeHTN05A7NFD55W+Ffbv14JCVr3watPLg8JEvutSolyRDAjKoQV+6oStabrKbmK0liYeW4XfL9PlHPILsrzdgt9fmeakF2lVyJ5K8q52gx+qBUtTcCa7f9teL2AoS3skqARl/TKnfVW6eOWBGX55pepNW2WiNN/uCRuxd1Qz3/7brb+atfc64+1bKQqA==", "MD5OfBody": "b4a0833cda378eee4405bdb806636d0d", "Body": "{\"user_id\": \"internaltask\", \"url\": \"s3://contentmoderation12-moderations3bucketb3c8798d-cdjs8omidrkt/s3_video_moderation/modetation_video_03.mp4\", \"task_id\": \"internal_task_ff68a9829655495c685ec59ee1b62e63_1\", \"moderation_type\": 1}"}
    process_sqs_info(message)


