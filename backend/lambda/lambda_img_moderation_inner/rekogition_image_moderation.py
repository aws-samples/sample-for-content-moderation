import os

import boto3
from config import REGION_NAME, MODERATION_BUCKET_NAME
from tools.ffmpeg_tool import is_black_image
from tools.log_config import get_logger

logger = get_logger(__name__)

rekognition = boto3.client('rekognition', region_name=REGION_NAME)


class RekognitionImageModeration():

    def moderate_video(self, image_path: str) -> dict:
        # Not supported yet
        return {}

    def moderate_images(self, image_path_arr: list[str]) -> list[str]:
        return check_images(image_path_arr)

    def moderate_image(self, image_path: str) -> dict:
        return moderate_img(image_path)

    # def face_match(self, current_image_path: str, target_image_path) -> str:
    #     return face_match(current_image_path, target_image_path)


def moderate_img(image_path: str):
    """
    检查本地图片中是否有不适当内容
    Check if the local image contains  inappropriate content

    :param image_path: 本地图片路径
    :return:
    """
    with open(image_path, 'rb') as image:
        image_bytes = image.read()

    # detect moderation labels
    moderation_response = rekognition.detect_moderation_labels(
        Image={'Bytes': image_bytes}
    )

    risk_label_arr = []
    for label in moderation_response['ModerationLabels']:
        if label['TaxonomyLevel'] == 1:
            risk_label_arr.append(label['Name'])

    return {
        "tag": risk_label_arr
    }


def face_match(current_image_path: str, s3_image_path: str):
    with open(current_image_path, 'rb') as source_image_file:
        source_bytes = source_image_file.read()
    try:
        response = rekognition.compare_faces(
            SourceImage={
                'S3Object': {
                    'Bucket': MODERATION_BUCKET_NAME,
                    'Name': s3_image_path
                }
            },
            TargetImage={'Bytes': source_bytes},
            SimilarityThreshold=80
        )

        if len(response['FaceMatches']) > 0:
            similarity = response['FaceMatches'][0]['Similarity']
            return str(similarity)

        else:
            return str(0)
    except Exception as e:
        logger.info("No faces in the image")
        logger.info(f"{e}")
        pass

    return str(0)


def check_image(image_path):
    '''
    moderate img
    :param image_path:
    :return: True indicates an issue
    '''

    result = {
        "path": image_path,
        "code": 0,
        "level": 0,
        "tag": []
    }

    try:
        # Image review
        moderate_result= moderate_img(image_path)

        result["tag"]=moderate_result["tag"]

        if len(moderate_result["tag"]) > 0:
            result['code'] = 1

    except Exception as e:
        logger.error(f"An error occurred during the execution of the program: {str(e)}")

    logger.info(result)
    return result


def check_images(image_path_arr: list[str]) -> list[any]:
    '''
    :param images_dir_path:
    :return: False indicates that an issue was detected."
    '''

    result_arr = []

    for file_path in image_path_arr:

        if not os.path.exists(file_path):
            logger.error(f"The image file does not exist: {file_path}")
            continue

        blank_flag = is_black_image(str(file_path))
        if blank_flag is False:
            result = check_image(str(file_path))
            if len(result['tag']) > 0:
                result_arr.append(result)
            pass
        else:
            print(f"{str(file_path)} is blank img")
    return result_arr


if __name__ == '__main__':
    # print(check_image("a.png"))

    # print(check_images(["a.png","b.jpg","c.jpg"]))
    pass