import json
import os
from config import MODERATION_BUCKET_NAME, S3_FILE_READABLE_EXPIRATION_TIME, \
    TEXT_DEFAULT_PROMPT_CN, TEXT_DEFAULT_PROMPT_EN
from bedrock_text_moderation import BedrockTextModeration
from log_config import get_logger, setup_logging
from sagemaker_client import asr_local_file
from save_info_alert import save_and_push_message
from s3_client import S3Client

setup_logging()
logger = get_logger(__name__)

'''
接收SQS发来的消息
从中解析出S3地址或Base64数据

对音频文件进行语音识别
然后调用Bedrock进行文本审核
审核完成后将结果存入DDB，并存入新SQS

'''


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


def download_file(s3_client, s3_file_path, local_file_path):
    s3_client.download_file_from_s3(s3_file_path, local_file_path)
    logger.info(f"local vido path: {local_file_path}")

    return []


def lambda_handler(event, context):
    '''
    :param event:
    :param context:
    :return:
    '''
    print(json.dumps(event))

    # [1] Get Parameter
    body_string = event['Records'][0]['body']
    body_obj = json.loads(body_string)

    if "user_id" not in body_obj:
        return response("Parameter error", f"Error Param: {body_string}", 500)

    # 用户id  user_id
    user_id = body_obj['user_id']
    # 任务id  task id
    task_id = body_obj['task_id']
    s3_file_arr = body_obj['s3_files']
    # save_flag 1 all save,  0 only save abnormal
    save_flag = body_obj['save_flag']
    model_id = body_obj['model_id']

    s3_client = S3Client(MODERATION_BUCKET_NAME)

    # [2]download audio
    local_audio_dir = f"/tmp/"  # nosec

    s3_file_path=s3_file_arr[0]['path']
    file_name = s3_file_path.split('/')[-1]

    #customer_video/task_id/audio/0000_1744817861_000002.wav
    local_file_path = os.path.join(local_audio_dir, file_name)
    download_file(s3_client, s3_file_path, local_file_path)

    # [3]ASR
    content = asr_local_file(local_file_path)['text']


    logger.info(f"asr: {content}")
    original_content = content.strip()
    logger.info(original_content)

    # [4] moderation
    if original_content:
        text_moderation = BedrockTextModeration()
        bedrock_result = text_moderation.moderate(model_id, TEXT_DEFAULT_PROMPT_EN, original_content)

        # logger.info(f"bedrock : {bedrock_result}" )

        if bedrock_result is None:
            logger.info("bedrock: Audio analysis failed")
            return

        if isinstance(bedrock_result, str):
            bedrock_result_obj = json.loads(bedrock_result)
        else:
            bedrock_result_obj = bedrock_result

        s3_clients = S3Client(MODERATION_BUCKET_NAME)

        state = 2

        confidence = []
        tag = []
        des = []

        if len(bedrock_result_obj['result']) > 0:

            for r in bedrock_result_obj['result']:

                if 'tag' in r and r['tag'] != "" and r['tag'] != "None":
                    state = 1
                    tag.append(r['tag'])
                    if 'confidence' in r:
                        confidence.append(r['confidence'])
                    if 'des' in r:
                        confidence.append(r['des'])


        if save_flag == "0":
            # Only save exception file and information
            if state == 2:
                logger.info("delete")
                s3_client.delete_s3_file(MODERATION_BUCKET_NAME, s3_file_path)
            elif state == 1:
                s3_read_path = s3_clients.get_presigned_url(MODERATION_BUCKET_NAME, s3_file_path,
                                                            S3_FILE_READABLE_EXPIRATION_TIME)

                save_and_push_message(task_id, user_id, s3_file_path, s3_read_path, original_content, s3_file_arr[0]['time_info'],
                                      confidence,
                                      tag,
                                      des, "audio",
                                      state)

        else:
            # save all info
            s3_read_path = s3_clients.get_presigned_url(MODERATION_BUCKET_NAME, s3_file_path,
                                                        S3_FILE_READABLE_EXPIRATION_TIME)
            save_and_push_message(task_id, user_id, s3_file_path, s3_read_path, original_content, s3_file_arr[0]['time_info'],
                                  confidence,
                                  tag,
                                  des, "audio",
                                  state)

    return response("successful", "", 200)


if __name__ == '__main__':
    event = {
        "Records": [
            {
                "body": ""
            }
        ]
    }

    #us.anthropic.claude-3-haiku-20240307-v1:0
    #us.amazon.nova-micro-v1:0

    event['Records'][0]['body'] = json.dumps({
        "user_id": "lee",
        "task_id": "12341234",
        "s3_files": [
            {
                "path": "audio/2bd95247-c597-4f18-9b59-f23937a3b658.wav",
                "time_info": [3333,66666]
            }
        ],
        "save_flag": "1",
        "model_id": "us.amazon.nova-micro-v1:0",
    })

    print(lambda_handler(event, {}))
