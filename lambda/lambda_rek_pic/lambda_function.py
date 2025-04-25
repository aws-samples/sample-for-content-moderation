import asyncio
import json
import os
import uuid
import boto3
import ffmpeg
from as3_tool import batch_upload
# from config import region_name

region_name="us-east-1"


# 初始化 Rekognition 客户端
rekognition = boto3.client('rekognition', region_name=region_name)
s3 = boto3.client("s3", region_name=region_name)
ddb = boto3.resource('dynamodb', region_name=region_name)

s3_bucket_name = "video-moderation-a"
s3_images_dir = "images/"


random_uuid = uuid.uuid4()

# 本地视频目录
local_video_dir = f"/tmp/{random_uuid}/" # nosec
# 本地图片目录
local_image_dir = f"/tmp/{random_uuid}/img/" # nosec

# 截取间隔
interval = 1


def extract_image(input_file, output_dir, interval):

    '''
    提取图片
    :param input_file:
    :param output_dir:
    :return:
    '''
    directory = os.path.dirname(output_dir)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    print("准备提取图片")
    output_pattern = 'vm_%06d.png'
    stream = ffmpeg.input(input_file)
    stream = ffmpeg.filter(stream, 'fps', fps=1 / interval)
    stream = ffmpeg.output(stream, os.path.join(output_dir, output_pattern), start_number=0)
    ffmpeg.run(stream)


def check_img(image_path):
    '''
    审核图片
    :param image_path:
    :return:
    '''
    with open(image_path, 'rb') as image:
        image_bytes = image.read()

    # 检测不适当内容
    moderation_response = rekognition.detect_moderation_labels(
        # Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        Image={'Bytes': image_bytes}
    )

    label_arr = []
    for label in moderation_response['ModerationLabels']:
        # if label['Name'] in ['Explicit Nudity', 'Suggestive']:
        if label['TaxonomyLevel'] == 1:
            label_arr.append(f"检测到不适当内容: {label['Name']}, 置信度: {label['Confidence']:.2f}%")

    return label_arr


def scan_directory(root_dir):
    '''
    扫描目录中的图片
    :param root_dir:
    :return:
    '''
    resource_dir = os.listdir(root_dir)
    resources = [os.path.join(root_dir, item) for item in resource_dir]
    return resources


def download_from_s3(event):

    if 'Records' not in event:
        return {
            "error": "测试内容，无需处理"
        }


    body_string =event['Records'][0]['body']
    body_json = json.loads(body_string)

    if 'Records' not in body_json or 's3' not in body_json['Records'][0]:
        return {
            "error": "测试内容，无需处理"
        }

    if 'Event' in body_json:
        if 's3:TestEvent' == body_json['Event']:
            return {
                "error": "测试内容，无需处理"
            }

    # 提取所需的值
    bucket_name = body_json['Records'][0]['s3']['bucket']['name']
    object_key = body_json['Records'][0]['s3']['object']['key']


    # 分割 object_key 以获取文件夹名和文件名
    folder_name, filename = object_key.split('/')

    local_file_path = os.path.join(local_video_dir, filename)
    s3.download_file(bucket_name, object_key, local_file_path)

    print(f"本地视频地址为{local_file_path}")
    return local_file_path


def lambda_handler(event, context):
    print(json.dumps(event))

    #创建文件夹
    if not os.path.exists(local_image_dir):
        os.makedirs(local_video_dir)
    if not os.path.exists(local_image_dir):
        os.makedirs(local_image_dir)

    # 【0】S3视频下载到tmp目录
    print("下载视频")
    video_path = download_from_s3(event)
    # video_path = "/Users/tedli/workspace/defaultWorkSpace/content_moderation/backend/resources22/93.mp4"

    # 【1】截取图片
    print("截取视频")
    extract_image(video_path, local_image_dir, interval)

    # 【2】扫描图片
    print("扫描图片")
    resources = scan_directory(local_image_dir)

    # 【3】审核图片
    print(f"审核图片 {len(resources)}张")
    check_results = []
    for resource_path in resources:
        check_img_results = check_img(resource_path)
        if len(check_img_results) > 0:
            check_results.append({
                "img_path": resource_path,
                "check_infos": check_img_results
            })

    print(check_results)

    # 【4】信息上传DDB
    print("信息上传DDB")
    # table = ddb.Table("user_vp")
    # table.put_item(Item={"id":"112","email":"999999"})

    # 【5】信息存储S3
    print("文件存储S3")
    upload_files = []
    for check_obj in check_results:
        upload_files.append(
            (check_obj['img_path'], os.path.join(s3_images_dir, os.path.basename(check_obj['img_path']))))
    asyncio.run(batch_upload(s3_bucket_name, upload_files))

    print("ALL执行完成")

    return {
        'statusCode': 200,
        'body': 'Email sent successfully'
    }

