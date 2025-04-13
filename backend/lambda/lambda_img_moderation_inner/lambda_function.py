import json
import os
import sys
import traceback

from config import MODERATION_BUCKET_NAME, S3_FILE_READABLE_EXPIRATION_TIME
from log_config import get_logger, setup_logging
from bedrock_image_moderation import BedrockImageModeration
from rekogition_image_moderation import RekognitionImageModeration
from save_info_alert import save_and_push_message
from s3_client import S3Client

setup_logging()
logger = get_logger(__name__)

'''
接收SQS发来的消息
从中解析出S3地址或Base64数据

对文本文件进行处理
然后调用Bedrock进行图片/视频审核
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
    s3_files_path = body_obj['s3_files']
    #save_flag 1 all save,  0 only save abnormal
    save_flag = body_obj['save_flag']
    start_time = body_obj['start_time']
    end_time = body_obj['end_time']
    model_id = body_obj['model_id']
    visual_moderation_type = body_obj['visual_moderation_type']
    # "image",

    s3_client = S3Client(MODERATION_BUCKET_NAME)

    result_arr = []
    moderation_results=None
    if visual_moderation_type =="image":
        # [2]download imgs
        local_file_dir = f"/tmp/"  # nosec

        local_file_arr=[]
        for s3_file_path in s3_files_path:
            file_name = s3_file_path.split('/')[-1]
            local_file_path = os.path.join(local_file_dir, file_name)
            download_file(s3_client, s3_file_path, local_file_path)
            local_file_arr.append(local_file_path)

            # 1 is abnormal  , 2 is normal
            result_arr.append({
                "s3_path": s3_file_path,
                "local_path": local_file_path,
                "state": 2,
            })


        # [3] moderation
        if model_id =="rekognition":
            img_moderation = RekognitionImageModeration()
            moderation_results =img_moderation.moderate_images(local_file_arr)

        else:
            img_moderation = BedrockImageModeration()
            moderation_results=img_moderation.moderate_images(model_id,local_file_arr)








    elif visual_moderation_type =="video":


        for s3_file_path in s3_files_path:
            # 1 is abnormal  , 2 is normal
            result_arr.append({
                "s3_path": s3_file_path,
                "state": 2,
            })


        for video_file in s3_files_path:
            img_moderation = BedrockImageModeration()

            print(f"s3://{MODERATION_BUCKET_NAME}/{video_file}")
            
            moderation_results=img_moderation.moderate_video(model_id,f"s3://{MODERATION_BUCKET_NAME}/{video_file}")

    else:
        return response("参数错误","",500)



    if moderation_results is None or len(moderation_results) == 0:
        logger.info("The image has no issues")
    else:

        try:
            for result in result_arr:
                if visual_moderation_type == "image":
                    matched_files = [f for f in moderation_results if f['path'] == result['local_path']]
                    result['s3_read_path'] = s3_client.get_presigned_url(MODERATION_BUCKET_NAME, result['s3_path'],
                                                                         S3_FILE_READABLE_EXPIRATION_TIME)
                else:
                    #video
                    matched_files = [f for f in moderation_results if f['path'] == f"s3://{MODERATION_BUCKET_NAME}/{result['s3_path']}"]
                    result['s3_read_path'] = s3_client.get_presigned_url(MODERATION_BUCKET_NAME, result['s3_path'],
                                                                         S3_FILE_READABLE_EXPIRATION_TIME)

                if len(matched_files) == 0:
                    logger.info(f"{ result['s3_path']}  has no issues")
                    result['confidence']="High"
                    result['tag']=""
                    result['state']=2

                else:
                    logger.info(f"{ result['s3_path']}  has issues")
                    result['confidence']=matched_files[0]['confidence']
                    result['tag']=matched_files[0]['tag']
                    result['state']=1

        except Exception as e:
            logger.info(e)
            traceback.print_exc(file=sys.stdout)

    for result in result_arr:

        # Only save exception file and information
        if save_flag == "0":

            #  state:  1 is abnormal  , 2 is normal
            if result['state']==2:
                logger.info("delete")
                # s3_client.delete_s3_file(MODERATION_BUCKET_NAME, result['s3_path'])

            elif result['state']==1:
                # Only save exception file and information
                save_and_push_message(task_id, user_id, result['s3_path'], result["s3_read_path"], "", start_time, end_time,
                                      result['confidence'] if 'confidence' in result else "", result['tag'], ",".join(result['tag']), visual_moderation_type,
                                      result['state'])

        else:
            # save all info
            save_and_push_message(task_id, user_id, result['s3_path'], result["s3_read_path"], "", start_time, end_time,
                              result['confidence'] if 'confidence' in result else "", result['tag'], ",".join(result['tag']), visual_moderation_type,
                              result['state'])



    return response("successful", "", 200)


if __name__ == '__main__':
    event = {
        "Records": [
            {
                "body": ""
            }
        ]
    }


    # event['Records'][0]['body'] = json.dumps({
    #     "user_id": "lee",
    #     "task_id": "12341234",
    #     "s3_files": ["93.mp4"],
    #     # "s3_files": ["sex.mp4"],
    #     "visual_moderation_type": "video",
    #     "save_flag": "1",
    #     "start_time": 1743765352,
    #     "end_time": 1743766352,
    #     "model_id": "us.amazon.nova-pro-v1:0"
    # })



    event['Records'][0]['body'] = json.dumps({
        "user_id": "lee",
        "task_id": "12341234",
        "s3_files": ["e.jpg","h.jpg","i.jpg","j.jpg"],
        "visual_moderation_type": "image",
        "save_flag": "0",
        "start_time": 1743765352,
        "end_time": 1743766352,
        # "model_id": "rekognition"
        "model_id": "us.amazon.nova-lite-v1:0"
        # "model_id": "us.anthropic.claude-3-sonnet-20240229-v1:0"
    })


    lambda_handler(event, {})

