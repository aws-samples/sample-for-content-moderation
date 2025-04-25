import os


'''
Create ECS Parameters
'''
#程序类型 0:持续处理SQS消息   1:仅尝试处理1条SQS  2:持续处理SQS消息，直到监听x次消息队列后后没有消息响应
# Program types:
# 0: Continuously process SQS messages
# 1: Attempt to process only 1 SQS message
# 2: Continuously process SQS messages until no response after listening to the queue x times

PROGRAM_TYPE = os.environ.get('PROGRAM_TYPE', "2")

#SQS重试次数，直到尝试监听x次消息队列后后没有消息响应
# SQS retry count, until no response after attempting to listen to the message queue x times
ATTEMPT_COUNT = os.environ.get('ATTEMPT_COUNT', "2")

USER_TABLE_NAME = os.environ.get('USER_TABLE_NAME', 'ModerationUser')

TASK_TABLE_NAME = os.environ.get('TASK_TABLE_NAME', 'Modetaion-77984679-016-ModerationTaskTableFADE4D13-15FBUUQMU9U5A')

TASK_DETAIL_TABLE_NAME = os.environ.get('TASK_DETAIL_TABLE_NAME', 'task_detail_moderation')

REGION_NAME = os.environ.get('REGION_NAME', 'us-west-2')

CLUSTER_NAME = os.environ.get('CLUSTER_NAME', 'vm_cluster')

TASK_DEFINITION_ARN = os.environ.get('TASK_DEFINITION_ARN', 'arn:aws:ecs:us-east-1:account_id:task-definition/contentmoderation_3:11')

SUBNET_IDS = os.environ.get('SUBNET_IDS', 'subnet-02a8e392bba3ce0a2,subnet-07c91d052b99a704c')

SECURITY_GROUP_ID = os.environ.get('SECURITY_GROUP_ID','NONE')

CONTAINER_NAME = os.environ.get('CONTAINER_NAME', 'cm3')


S3BUCKET_CUSTOMER_DIR = os.environ.get('S3BUCKET_CUSTOMER_DIR', 'customer_video')



MODERATION_SQS= os.environ.get('MODERATION_SQS', 'https://sqs.us-west-2.amazonaws.com/779846792662/Modetaion-77984679-016-ModerationSQSModerationC44008E0-kGDTzlbylbrB')

IMAGE_MODERATION_SQS= os.environ.get('IMAGE_MODERATION_SQS', 'https://sqs.us-west-2.amazonaws.com/779846792662/Modetaion-77984679-016-ModerationSQSModerationIMG633EF1C3-JEeNTRCWHOtJ')
AUDIO_MODERATION_SQS= os.environ.get('AUDIO_MODERATION_SQS', 'https://sqs.us-west-2.amazonaws.com/779846792662/Modetaion-77984679-016-ModerationSQSModerationAudioCEEDCCD9-r1DNdJ5y9SqV')
VIDEO_MODERATION_SQS= os.environ.get('VIDEO_MODERATION_SQS', 'https://sqs.us-west-2.amazonaws.com/779846792662/Modetaion-77984679-016-ModerationSQSModerationVideoFB43E340-mwpd3iYiIKC9')


MODERATION_BUCKET_NAME = os.environ.get('MODERATION_BUCKET_NAME', 'video-moderation-a')


CALLBACK_SQS_URL=os.environ.get('CALLBACK_SQS', 'https://sqs.us-east-1.amazonaws.com/account_id/video_moderation_alert')

VISUAL_MODERATION_TYPE = os.environ.get('VISUAL_MODERATION_TYPE', "video")

TEXT_MODEL_ID = os.environ.get('TEXT_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
IMG_MODEL_ID = os.environ.get('IMG_MODEL_ID', "us.amazon.nova-lite-v1:0")
VIDEO_MODEL_ID = os.environ.get('VIDEO_MODEL_ID', "us.amazon.nova-pro-v1:0")


TAGS = os.environ.get('TAGS', 'NONE')
