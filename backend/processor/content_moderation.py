import asyncio
import json
import os
import traceback
import sys

from tools import sqs_client
from tools.log_config import get_logger, setup_logging
from tools.metadata_tool import load_metadata, save_metadata

logger = get_logger(__name__)
from tools.as3_tool import batch_upload
from config import MODERATION_BUCKET_NAME, S3BUCKET_CUSTOMER_DIR, IMAGE_MODERATION_SQS, AUDIO_MODERATION_SQS, \
    VIDEO_MODERATION_SQS
from tools.time_tool import process_time_from_video_audio_name, process_time_from_img_name

setup_logging()

sqs_url = "https://sqs.us-west-2.amazonaws.com/779846792662/Modetaion-77984679-011-ModerationSQSCallbackDLQ66B955DE-ikVShpSelSnQ"


def image_moderation(image_path_arr, task_id):
    print(f"image_moderation----------{image_path_arr}")
    logger.info("image_check")
    logger.info(image_path_arr)

    metadata_obj = load_metadata(task_id)

    if isinstance(metadata_obj, dict) and len(metadata_obj) == 0:
        logger.info("[Error] metadata_obj is empty!")
        return

    s3_file_arr = []
    try:
        # The image has issues, storing it to S3
        files_to_upload = []

        for img in image_path_arr:
            img_name = os.path.basename(img)

            s3_path = f"{S3BUCKET_CUSTOMER_DIR}/{task_id}/img/{img_name}"

            files_to_upload.append((img, s3_path))

            s3_file_obj = {}

            if metadata_obj.get('visual_moderation_type','image') == "image":
                s3_file_obj['time_info'] = process_time_from_img_name(img_name,metadata_obj.get("image_interval_seconds"))
            else:
                start_time_str, end_time_str = process_time_from_video_audio_name(img_name,metadata_obj.get("video_interval_seconds"))
                s3_file_obj['time_info']=[start_time_str,end_time_str]

            s3_file_obj['path'] = s3_path

            s3_file_arr.append(s3_file_obj)

        asyncio.run(batch_upload(MODERATION_BUCKET_NAME, files_to_upload))

    except Exception as e:
        logger.info(e)
        traceback.print_exc(file=sys.stdout)

    sqs = sqs_client.init()

    sqs_client.insert(sqs, IMAGE_MODERATION_SQS if metadata_obj.get('visual_moderation_type',
                                                                    '') == "image" else VIDEO_MODERATION_SQS,
                      json.dumps({
                          "task_id": task_id,
                          "user_id": metadata_obj.get('user_id', ''),
                          "media_url": metadata_obj.get('media_url', ''),
                          "visual_moderation_type": metadata_obj.get('visual_moderation_type', ''),
                          "model_id": metadata_obj.get('img_model_id', '') if metadata_obj.get('visual_moderation_type',
                                                                    '') == "image" else metadata_obj.get('video_model_id', '') ,
                          "save_flag": metadata_obj.get('save_flag', ''),
                          "s3_files": s3_file_arr
                      }))

    for img_path in image_path_arr:
        os.remove(img_path)

    print("img success")


def audio_moderation(audio_file, task_id):
    print("-audio_moderation---")
    metadata_obj = load_metadata(task_id)

    if isinstance(metadata_obj, dict) and len(metadata_obj) == 0:
        logger.info("[Error] metadata_obj is empty!")
        return

    # save to s3
    files_to_upload = []
    # 存储到S3
    logger.error("SAVE AUDIO TO S3")
    audio_name = os.path.basename(audio_file)

    s3_path = f"{S3BUCKET_CUSTOMER_DIR}/{task_id}/audio/{audio_name}"

    files_to_upload.append((audio_file, s3_path))
    asyncio.run(batch_upload(MODERATION_BUCKET_NAME, files_to_upload))

    #
    start_time_str, end_time_str = process_time_from_video_audio_name(audio_file,metadata_obj.get("audio_interval_seconds"))

    sqs = sqs_client.init()

    sqs_client.insert(sqs, AUDIO_MODERATION_SQS, json.dumps({
        "task_id": task_id,
        "user_id": metadata_obj.get('user_id', ''),
        "media_url": metadata_obj.get('media_url', ''),
        "visual_moderation_type": metadata_obj.get('visual_moderation_type', ''),
        "model_id": metadata_obj.get('text_model_id', ''),
        "save_flag": metadata_obj.get('save_flag', ''),
        "s3_files": [
            {
                "path": s3_path,
                "time_info": [start_time_str, end_time_str]
            }
        ]
    }))

    print("audio success")

    os.remove(audio_file)

    logger.info(f"Delete audio {audio_file}")


if __name__ == '__main__':
    # metadata_obj = {
    #     'user_id':"lee",
    #     'task_id':"aaa",
    #     # 'media_url':"media_url",
    #     'text_model_id':"model_id",
    #     'img_model_id':"model_id",
    #     'save_flag':"1",
    #     'visual_moderation_type':"image",
    # }
    #
    # logger.info("process_sqs_info")
    # logger.info(metadata_obj)
    #
    # save_metadata("aaa",metadata_obj)

    audio_moderation("0000_1744810192_000070.flac","aaa")




    # print(image_moderation([
    #     "0000_1744818871_000006.jpg","0000_1744818871_000008.jpg"
    # ], "aaa"))



    # print(image_moderation([
    #     "0000_1744810192_000069.mp4"
    # ], "aaa"))