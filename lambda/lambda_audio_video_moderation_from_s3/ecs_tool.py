import json

import boto3
from botocore.exceptions import ClientError
from config import (REGION_NAME, CLUSTER_NAME, TASK_DEFINITION_ARN, SUBNET_IDS, PROGRAM_TYPE, CONTAINER_NAME,
                    ATTEMPT_COUNT, MODERATION_SQS, CALLBACK_SQS_URL, TASK_TABLE_NAME, TASK_DETAIL_TABLE_NAME,
                    MODERATION_BUCKET_NAME,
                    S3BUCKET_CUSTOMER_DIR, WHISPER_ENDPOINT_NAME, TEXT_MODEL_ID, SECURITY_GROUP_ID, TAGS,
                    S3_MODERATION_SQS,
                    IMG_MODEL_ID, BATCH_PROCESS_IMG_NUMBER, SPEECH_RECOGNIZER_PLUGIN, TEXT_MODERATION_PLUGIN,
                    IMAGE_MODERATION_PLUGIN, VISUAL_MODERATION_TYPE, VIDEO_MODEL_ID)

'''
Note that the ECS_TOOL here is different from the ECS_TOOL for real-time audit, and the SQS to be monitored is different
注意此处的ECS_TOOL和实时审核的ECS_TOOL不同，需要监听的SQS不同
'''

def run_ecs_task(cluster_name, task_definition, subnet_ids,container_name,environment_variables=None,count=1):

    ecs_client = boto3.client('ecs', region_name=REGION_NAME)

    # Define task parameters
    task_params = {
        'cluster': cluster_name,
        'taskDefinition': task_definition,
        'launchType': 'FARGATE',
        'networkConfiguration': {
            'awsvpcConfiguration': {
                'subnets': subnet_ids,
                'assignPublicIp': 'ENABLED'
            }
        },
        'count': count  # 指定要启动的任务数量 Specify the number of tasks to start
    }

    if SECURITY_GROUP_ID != 'NONE':
        task_params['networkConfiguration']['awsvpcConfiguration']['securityGroups']=[SECURITY_GROUP_ID]


    if TAGS != 'NONE':
        task_params['tags']=json.loads(TAGS)




    if environment_variables:
        task_params['overrides'] = {
            'containerOverrides': [
                {
                    'name': container_name,
                    'environment': [
                        {'name': key, 'value': value}
                        for key, value in environment_variables.items()
                    ]
                }
            ]
        }

    try:
        print(task_params)

        response = ecs_client.run_task(**task_params)
        if response['tasks']:
            task_arn = response['tasks'][0]['taskArn']
            print(f"Task started successfully. ARN: {task_arn}")
        else:
            print("Task failed to start.")
            if 'failures' in response:
                for failure in response['failures']:
                    print(f"Failure reason: {failure['reason']}")
    except ClientError as e:
        print(f"Error running task: {e}")

def create_ecs_task(count=1):
    cluster_name =CLUSTER_NAME
    task_definition = TASK_DEFINITION_ARN  # 指定任务定义名称和版本 Specify task definition name and version
    subnet_ids = SUBNET_IDS.split(",")

    environment_variables = {
        'PROGRAM_TYPE': PROGRAM_TYPE,
        'ATTEMPT_COUNT': ATTEMPT_COUNT,
        'MODERATION_SQS': S3_MODERATION_SQS,
        'CALLBACK_SQS': CALLBACK_SQS_URL,
        'TASK_TABLE_NAME': TASK_TABLE_NAME,
        'TASK_DETAIL_TABLE_NAME': TASK_DETAIL_TABLE_NAME,
        'MODERATION_BUCKET_NAME': MODERATION_BUCKET_NAME,
        'S3BUCKET_CUSTOMER_DIR': S3BUCKET_CUSTOMER_DIR,
        'WHISPER_ENDPOINT_NAME': WHISPER_ENDPOINT_NAME,
        'TEXT_MODEL_ID': TEXT_MODEL_ID,
        'IMG_MODEL_ID': IMG_MODEL_ID,
        'VIDEO_MODEL_ID': VIDEO_MODEL_ID,
        'BATCH_PROCESS_IMG_NUMBER': BATCH_PROCESS_IMG_NUMBER,
        'SPEECH_RECOGNIZER_PLUGIN': SPEECH_RECOGNIZER_PLUGIN,
        'TEXT_MODERATION_PLUGIN': TEXT_MODERATION_PLUGIN,
        'IMAGE_MODERATION_PLUGIN': IMAGE_MODERATION_PLUGIN,
        'VISUAL_MODERATION_TYPE': VISUAL_MODERATION_TYPE

    }

    container_name=CONTAINER_NAME

    run_ecs_task(cluster_name, task_definition, subnet_ids,container_name,environment_variables,count)


if __name__ == '__main__':
    create_ecs_task(1)
