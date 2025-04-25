"""
@File    : rekognition_tool.py
@Time    : 2025/3/1 16:04
@Author  : tedli
@Email   : tedli@amazon.com
@Description: 
    This file is for...
"""
import boto3

from config import REGION_NAME

rekognition = boto3.client('rekognition', region_name=REGION_NAME)


def check_img_use_rek(image_bytes):
    # 检测不适当内容
    moderation_response = rekognition.detect_moderation_labels(
        Image={'Bytes': image_bytes}
    )

    label_arr = []
    for label in moderation_response['ModerationLabels']:
        # if label['Name'] in ['Explicit Nudity', 'Suggestive']:
        if label['TaxonomyLevel'] == 1:
            label_arr.append(f"检测到不适当内容: {label['Name']}, 置信度: {label['Confidence']:.2f}%")

    return label_arr