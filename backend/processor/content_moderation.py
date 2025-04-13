import asyncio
import json
import os
import traceback
import sys
from dependency_injector.wiring import inject, Provide
from base.plugin_config import AppContainer
from tools.log_config import get_logger

logger = get_logger(__name__)
from processor.save_info_alert import save_and_push_message
from tools.as3_tool import batch_upload
from config import MODERATION_BUCKET_NAME, FACE_RESOURCE_PATH, S3BUCKET_CUSTOMER_DIR, \
    S3_FILE_READABLE_EXPIRATION_TIME, VISUAL_MODERATION_TYPE, TEXT_DEFAULT_PROMPT_EN
from tools.ffmpeg_tool import is_black_audio, is_black_image
from tools.time_tool import process_time_from_audio_name, process_time_from_img_name
from tools.s3_client import S3Client


def image_moderation(image_path_arr, task_id):
    logger.info("image_check")
    logger.info(image_path_arr)

    results = check_images(image_path_arr)

    if results is None or len(results) == 0:
        logger.info("The image has no issues")
    else:
        try:
            # The image has issues, storing it to S3
            files_to_upload = []

            s3_clients = S3Client(MODERATION_BUCKET_NAME)

            for img in results:
                img_name = os.path.basename(img['path'])

                s3_path = f"{S3BUCKET_CUSTOMER_DIR}/{task_id}/img/{img_name}"

                files_to_upload.append((img['path'], s3_path))
                img['time'] = int(process_time_from_img_name(img_name))

                img['s3_read_path'] = s3_clients.get_presigned_url(MODERATION_BUCKET_NAME, s3_path,
                                                                   S3_FILE_READABLE_EXPIRATION_TIME)
                img['s3_path'] = s3_path

            asyncio.run(batch_upload(MODERATION_BUCKET_NAME, files_to_upload))

            for img in results:
                save_and_push_message(task_id, img['s3_path'], img["s3_read_path"], "", img['time'], img['time'],
                                      img['confidence'] if 'confidence' in img else "", img['tag'], ",".join(img['tag']), "video" if VISUAL_MODERATION_TYPE == "video" else "image",
                                      1)




        except Exception as e:
            logger.info(e)
            traceback.logger.info_exc(file=sys.stdout)

    for img_path in image_path_arr:
        os.remove(img_path)


@inject
def audio_moderation(audio_file, task_id, speech_recognizer=Provide[AppContainer.speech_recognizer],
                     text_moderation=Provide[AppContainer.text_moderation]
                     ):
    if is_black_audio(audio_file) is False:

        # asr
        content = speech_recognizer.recognize(audio_file)

        logger.info(f"asr: {content}")

        trimmed_text = content.strip()

        if trimmed_text:

            bedrock_result = text_moderation.moderate(TEXT_DEFAULT_PROMPT_EN, content)

            logger.info("bedrock :")
            logger.info(bedrock_result)

            if bedrock_result is None:
                logger.info("bedrock: Audio analysis failed")
                return

            if isinstance(bedrock_result, str):
                bedrock_result_obj = json.loads(bedrock_result)
            else:
                bedrock_result_obj = bedrock_result

            # State 1 indicates an error, and state 2 indicates normal
            s3_clients = S3Client(MODERATION_BUCKET_NAME)

            s3_path = ""
            s3_read_path = ""

            logger.info( len(bedrock_result_obj['result']))

            state = 2

            confidence = []
            tag = []
            des = []

            if len(bedrock_result_obj['result']) > 0:
                state = 1

                for r in bedrock_result_obj['result']:

                    if 'tag' in r and r['tag'] != "" and r['tag'] != "None":
                        tag.append(r['tag'])
                        if 'confidence' in r:
                            confidence.append(r['confidence'])
                        if 'des' in r:
                            confidence.append(r['des'])

                # save to s3
                files_to_upload = []
                # 存储到S3
                logger.error("SAVE AUDIO TO S3")
                audio_name = os.path.basename(audio_file)

                s3_path = f"{S3BUCKET_CUSTOMER_DIR}/{task_id}/audio/{audio_name}"

                files_to_upload.append((audio_file, s3_path))
                asyncio.run(batch_upload(MODERATION_BUCKET_NAME, files_to_upload))

                s3_read_path = s3_clients.get_presigned_url(MODERATION_BUCKET_NAME, s3_path,
                                                            S3_FILE_READABLE_EXPIRATION_TIME)

            start_time_str, end_time_str = process_time_from_audio_name(audio_file)
            save_and_push_message(task_id, s3_path, s3_read_path, trimmed_text, start_time_str, end_time_str, confidence,tag,
                                  des,
                                  "audio", state)


    else:
        logger.info("Blank audio")

    os.remove(audio_file)
    logger.info(f"Delete audio {audio_file}")


@inject
def check_images(image_arr, img_moderation=Provide[AppContainer.image_moderation]):
    '''
    :param img_moderation:
    :param image_arr:
    :param image_moderation:
    :return: False indicates that an issue was detected."
    '''

    '''
    [
            {
                "img_index": 1,
                "tag": ["Ban"],
                "confidence": "High",
                "state": 1
            },
            {
                "img_index": 2,
                "tag": ["Behavior2"],
                "confidence": "High", 
                "state": 1
            },
            {
                "img_index": 3,
                "tag": [],
                "confidence": "None",
                "state": 2
            }
    ]
    '''

    if VISUAL_MODERATION_TYPE == "video":
        # only suppots llm - nova
        results_arr = []
        for video in image_arr:

            if not os.path.exists(video):
                logger.error(f"The video file does not exist: {video}")
                continue

            moderation_result = img_moderation.moderate_video(video)
            if moderation_result:

                for moderation_result in moderation_result:
                    if len(moderation_result['tag']) > 0:
                        results_arr.append(moderation_result)
        return results_arr
    else:
        return img_moderation.moderate_images(image_arr)




