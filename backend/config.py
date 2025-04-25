import os
from tools.log_config import get_logger
logger=get_logger(__name__)

REGION_NAME = os.environ.get('REGION_NAME', 'us-west-2')

#程序类型 0:持续处理SQS消息   1:仅尝试处理1条SQS  2:持续处理SQS消息，直到监听x次消息队列后后没有消息响应
# Program types:
# 0: Continuously process SQS messages
# 1: Attempt to process only 1 SQS message
# 2: Continuously process SQS messages until no response after listening to the queue x times
PROGRAM_TYPE = int(os.environ.get('PROGRAM_TYPE', 2))

#SQS重试次数，直到尝试监听x次消息队列后后没有消息响应
# SQS retry count, until no response after attempting to listen to the message queue x times
ATTEMPT_COUNT = int(os.environ.get('ATTEMPT_COUNT', 2))

BATCH_PROCESS_IMG_NUMBER = int(os.environ.get('BATCH_PROCESS_IMG_NUMBER', 3))

logger.info(f"The environment variable is {PROGRAM_TYPE}")
logger.info(f"The number of message attempts is {ATTEMPT_COUNT}")


TASK_TABLE_NAME = os.environ.get('TASK_TABLE_NAME', 'Modetaion-77984679-016-ModerationTaskTableFADE4D13-15FBUUQMU9U5A')

MODERATION_BUCKET_NAME = os.environ.get('MODERATION_BUCKET_NAME', 'moderaion-77984679-027-bucket-us-west-2')

S3BUCKET_CUSTOMER_DIR = os.environ.get('S3BUCKET_CUSTOMER_DIR', 'customer_video')



MODERATION_SQS_URL= os.environ.get('MODERATION_SQS', 'https://sqs.us-west-2.amazonaws.com/779846792662/Moderaion-77984679-027-ModerationSQSModerationC44008E0-0d6TW0hB6TQ7')
#S3_MODERATION_SQS= os.environ.get('S3_MODERATION_SQS', 'https://sqs.us-west-1.amazonaws.com/xxxxx/s3_video_moderation')
IMAGE_MODERATION_SQS= os.environ.get('IMAGE_MODERATION_SQS', 'https://sqs.us-west-2.amazonaws.com/779846792662/Modetaion-77984679-016-ModerationSQSModerationIMG633EF1C3-JEeNTRCWHOtJ')
AUDIO_MODERATION_SQS= os.environ.get('AUDIO_MODERATION_SQS', 'https://sqs.us-west-2.amazonaws.com/779846792662/Modetaion-77984679-016-ModerationSQSModerationAudioCEEDCCD9-r1DNdJ5y9SqV')
VIDEO_MODERATION_SQS= os.environ.get('VIDEO_MODERATION_SQS', 'https://sqs.us-west-2.amazonaws.com/779846792662/Modetaion-77984679-016-ModerationSQSModerationVideoFB43E340-mwpd3iYiIKC9')


ROOT_RESOURCE_PATH= "ffmpeg_output"

METADATA_RESOURCE_PATH= "metadata"



# 首次建立连接 最大重连次数
# Maximum reconnect attempts for the first time establishing the connection
START_CONNECT_MAX_RETRIES = 10

# 直播结束后/意外断流 最大重连次数
# Maximum reconnect attempts after the live stream ends / unexpected disconnection
END_CONNECT_MAX_RETRIES = 5

# 重连尝试间隔x秒
# Reconnect attempt interval in x seconds
RETRY_DELAY = 1




