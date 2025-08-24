import json
import re
import boto3
from config import REGION_NAME, VIDEO_PROMPT_0325_CN, \
    SYSTEM_0325_NOVA_VIDEO_CN, IMG_CLAUDE_SYSTEM_PROMPT, IMG_PROMPT_0325_CN, IMG_NOVA_SYSTEM_PROMPT_1_EN
from base64_tool import encode_image, encode_images
from log_config import get_logger
from log_config import setup_logging

setup_logging()
logger = get_logger(__name__)

bedrock_client = boto3.client('bedrock-runtime', region_name=REGION_NAME)



def get_jsonobj(text):
    try:
        response_jsonobj = json.loads(text)
    except json.JSONDecodeError:
        # 匹配 JSON 对象的正则表达式
        match = re.search(r'\{.*?\}', text)
        if match:
            json_str = match.group()
            try:
                response_jsonobj = json.loads(json_str)
            except json.JSONDecodeError:
                print("JSON ERROR")
                return None
        else:
            print("can't find JSON")
            return None
    return response_jsonobj


def invoke_claude(model_id, system_prompt, prompt, img_path):
    content = []

    try:

        content.append({
            "type": "text",
            "text": "The image_index of the following figure is: 1  \n"
        })

        base64_image = encode_image(img_path)
        ext = img_path.split('.')[-1].lower()

        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": f"image/{'jpeg' if ext == 'jpg' else ext}",
                "data": base64_image
            }
        })
        content.append({
            "type": "text",
            "text": prompt
        })

        # content.append({"type": "text", "text": f"Frame {i}"})
    except Exception as e:
        print(f"Error")
        print(e)

    payload = {
        "modelId": model_id,
        "contentType": "application/json",
        "accept": "application/json",
        "body": {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }
    }

    # Convert the payload to bytes
    body_bytes = json.dumps(payload['body']).encode('utf-8')
    # Invoke the model
    response = bedrock_client.invoke_model(
        body=body_bytes,
        contentType=payload['contentType'],
        accept=payload['accept'],
        modelId=payload['modelId']
    )

    # Process the response
    response_body = json.loads(response['body'].read().decode('utf-8'))
    if 'content' in response_body and isinstance(response_body['content'], list):
        content = response_body['content'][0]
        if 'text' in content:
            analysis = content['text']
            analysis = re.sub(r'```json\n|\n```', '', analysis)
            print(f"llm result : {analysis}")
            response_jsonobj = get_jsonobj(analysis)

            if response_jsonobj is None:
                return None

            for r in response_jsonobj['result']:
                if 'tag' in r and len(r['tag']) > 0:
                    r['state'] = 1
                if r['state'] != 1 and r['state'] != 2:
                    r['state'] = "3"
                    print("state 错误")

            return response_jsonobj['result']

        else:
            analysis = None
    else:
        analysis = None
    return analysis


def batch_invoke_claude(model_id, system_prompt, prompt, image_arr):
    encoded_images = encode_images(image_arr)
    content = []
    try:
        for i, (ext, img) in enumerate(encoded_images, start=1):
            content.append({"type": "text", "text": f"The image_index of the following figure is: {i} "})
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/" + ("jpeg" if ext == 'jpg' else ext),
                    "data": img
                }
            })
    except Exception as e:
        logger.info(f"Error encoding frame : {str(e)}")
        # Skip this frame and continue with the next one

    content.append({"type": "text", "text": prompt})

    # logger.info(content)

    payload = {
        "modelId": model_id,
        "contentType": "application/json",
        "accept": "application/json",
        "body": {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "system": system_prompt,
            "messages": [

                {
                    "role": "user",
                    "content": content
                }
            ]
        }
    }

    # Convert the payload to bytes
    body_bytes = json.dumps(payload['body']).encode('utf-8')
    # Invoke the model
    response = bedrock_client.invoke_model(
        body=body_bytes,
        contentType=payload['contentType'],
        accept=payload['accept'],
        modelId=payload['modelId']
    )

    # Process the response
    response_body = json.loads(response['body'].read().decode('utf-8'))
    if 'content' in response_body and isinstance(response_body['content'], list):
        content = response_body['content'][0]
        if 'text' in content:
            analysis = content['text']
            analysis = re.sub(r'```json\n|\n```', '', analysis).strip()
            logger.info(f"图片识别结果为:{analysis}")

            response_jsonobj = json.loads(analysis)
            for r in response_jsonobj['result']:
                if 'tag' in r and len(r['tag']) > 0:
                    r['state'] = 1
                if r['state'] != 1 and r['state'] != 2:
                    r['state'] = "3"
                    print("state 错误")

                r['path'] = image_arr[r['img_index'] - 1]
            return response_jsonobj['result']

        else:
            analysis = None
    else:
        analysis = None
    return analysis




def batch_invoke_nova(model_id, system, prompt, image_arr, retry_state=True):
    encoded_images = encode_images(image_arr)

    payload = {
        "modelId": model_id,
        "contentType": "application/json",
        "accept": "application/json",
        "request_body": {
            "system": [
                {
                    "text": system
                }
            ],
            "messages": [
                {
                    "role": "user",
                    "content": []
                }
            ],
            "inferenceConfig": {
                "temperature": 0,
                "max_new_tokens": 5000
            }
        }
    }

    for i, (ext, img) in enumerate(encoded_images, start=1):
        payload['request_body']['messages'][0]["content"].append(
            {"text": f"The image_index of the following figure is: {i}  "})

        payload['request_body']['messages'][0]["content"].append(
            {"image": {"format": ext, "source": {"bytes": img}}})

    payload['request_body']['messages'][0]["content"].append({"text": prompt})

    # with open("t.test", 'w', newline='', encoding='utf-8-sig') as file:
    #     file.write(json.dumps(payload['request_body']))

    body_bytes = json.dumps(payload['request_body']).encode('utf-8')
    # Invoke the model
    response = bedrock_client.invoke_model(
        body=body_bytes,
        contentType=payload['contentType'],
        accept=payload['accept'],
        modelId=payload['modelId']
    )

    response_str = response['body'].read().decode('utf-8')
    print(response_str)
    response_body = json.loads(response_str)
    print("----------------")
    print(response_body)

    if 'output' in response_body and 'stopReason' in response_body and 'usage' in response_body:
        response_output_info = response_body['output']
        if response_output_info['message'].get('content'):
            content = response_output_info['message']['content'][0].get('text', '')
            logger.info(content)
            if " - The generated text has been blocked by our content filters." in content:
                logger.info("Reject review")
                if retry_state:
                    logger.info("try again")
                    return batch_invoke_nova(model_id, system, prompt, image_arr, False)
                else:
                    logger.info("don't try again")
                return None
            else:
                content = re.sub(r'```json\n|\n```', '', content)
                logger.info(content)
                response_jsonobj = json.loads(content)

                for r in response_jsonobj['result']:

                    if 'tag' in r and len(r['tag']) > 0:
                        r['state'] = 1
                    if r['state'] != 1 and r['state'] != 2:
                        r['state'] = "3"
                        print("state 错误")

                    r['path'] = image_arr[r['img_index'] - 1]

                return response_jsonobj['result']

    return None


def invoke_nova(model_id, system, prompt, img_path, retry_state=True):
    content_list = []

    logger.info("invoke_nova-process  " + img_path)

    try:

        if img_path.endswith('.mp4'):

            content_list.append({
                "text": "The image_index of the following figure is: 1  \n"
            })

            if img_path.startswith("s3://"):
                content_list.append({
                    "video": {
                        "format": img_path.split('.')[-1].lower(),
                        "source": {
                            "s3Location": {
                                "uri": img_path
                            }
                        }
                    }
                })
            else:

                content_list.append({
                    "text": "The video_index of the following figure is: 1  \n"
                })

                base64_image = encode_image(img_path)
                content_list.append({
                    "video": {
                        "format": img_path.split('.')[-1].lower(),
                        "source": {
                            "bytes": base64_image
                        }
                    }
                })
        else:
            base64_image = encode_image(img_path)
            content_list.append({
                "image": {
                    "format": img_path.split('.')[-1].lower(),
                    "source": {
                        "bytes": base64_image
                    }
                }
            })
        content_list.append({"text": prompt})

    except Exception as e:
        logger.info(f"Error encoding frame  {str(e)}")

    # content_list.append({
    #     "text": "请审核这张图片"
    # })

    payload = {
        "modelId": model_id,
        "contentType": "application/json",
        "accept": "application/json",
        "request_body":
            {
                "system": [
                    {
                        "text": system
                    }
                ],
                "messages": [
                    {
                        "role": "user",
                        "content": content_list
                    }
                ],
                "inferenceConfig": {
                    "temperature": 0
                }
            }
    }

    body_bytes = json.dumps(payload['request_body']).encode('utf-8')

    response = bedrock_client.invoke_model(
        body=body_bytes,
        contentType=payload['contentType'],
        accept=payload['accept'],
        modelId=payload['modelId']
    )

    logger.info(response)
    response_str = response['body'].read().decode('utf-8')
    response_body = json.loads(response_str)

    if 'output' in response_body and 'stopReason' in response_body and 'usage' in response_body:
        response_output_info = response_body['output']
        if response_output_info['message'].get('content'):
            content = response_output_info['message']['content'][0].get('text', '')
            # logger.info(content)
            if " - The generated text has been blocked by our content filters." in content:
                logger.info("Reject review")
                if retry_state:
                    logger.info("try again")
                    return invoke_nova(model_id, system, prompt, img_path, False)
                else:
                    logger.info("don't try again")
                return None
            else:
                logger.info(content)
                content = re.sub(r'```json\n|\n```', '', content)
                logger.info(content)
                response_jsonobj = json.loads(content)

                for r in response_jsonobj['result']:

                    if 'tag' in r and len(r['tag']) > 0:
                        r['state'] = 1
                    if r['state'] != 1 and r['state'] != 2:
                        r['state'] = "3"
                        print("state 错误")

                    r['path'] = img_path
                return response_jsonobj['result']

    return None


def get_image_type_from_base64(base64_string):
    image_types = {
        'iVBORw0KGgo': 'png',
        '/9j/': 'jpeg',
        'R0lGODlh': 'gif',
        'UklGRg': 'webp',
        'PD94bWwgdmVyc2lvbj0iMS4w': 'svg+xml'
    }

    if ',' in base64_string:
        base64_string = base64_string.split(',', 1)[1]

    for prefix, mime_type in image_types.items():
        if base64_string.startswith(prefix):
            return mime_type

    return None


if __name__ == '__main__':
    # model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    # response = invoke_claude(model_id, IMG_CLAUDE_SYSTEM_PROMPT, IMG_PROMPT_0325_CN, "/Users/tedli/workspace/defaultWorkSpace/content_moderation/backend/lambda/lambda_img_moderation/db1.jpg")
    # response = batch_invoke_claude(model_id, IMG_CLAUDE_SYSTEM_PROMPT, IMG_PROMPT_0325_CN, [
        # "/Users/tedli/workspace/defaultWorkSpace/content_moderation/backend/lambda/lambda_img_moderation/db1.jpg",
        # "/Users/tedli/workspace/defaultWorkSpace/content_moderation/backend/lambda/lambda_img_moderation/db2.png",
        # "/Users/tedli/workspace/defaultWorkSpace/content_moderation/lambda/lambda_img_moderation_inner/test_resource/img.png"])

    model_id = "us.amazon.nova-pro-v1:0"
    # response = invoke_nova(model_id, IMG_NOVA_SYSTEM_PROMPT_1_EN, IMG_PROMPT_0325_CN, "/Users/tedli/workspace/defaultWorkSpace/content_moderation/backend/lambda/lambda_img_moderation/db2.png")

    response=batch_invoke_nova(model_id,IMG_NOVA_SYSTEM_PROMPT_1_EN,IMG_PROMPT_0325_CN,
                               [
                                   # "/Users/tedli/workspace/defaultWorkSpace/content_moderation/backend/lambda/lambda_img_moderation/db2.png",
                                "/Users/tedli/workspace/defaultWorkSpace/content_moderation/lambda/lambda_img_moderation_inner/test_resource/img.png"])

    print(response)




    # model_id_info = "us.amazon.nova-pro-v1:0"
    # model_id_info = "us.amazon.nova-pro-v1:0"
    # model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    # logger.info(VIDEO_PROMPT_0325_CN)
    # response = invoke_nova(model_id_info, SYSTEM_0325_NOVA_VIDEO_CN,VIDEO_PROMPT_0325_CN, "s3://content-modreation-us-west2/93.mp4",True)
    # response = invoke_nova(model_id_info, SYSTEM_0325_NOVA_VIDEO_CN,VIDEO_PROMPT_0325_CN, "0000_1743234337_000007.mp4",True)

    # response = invoke_claude(model_id, SYSTEM_0325_NOVA_VIDEO_CN,VIDEO_PROMPT_0325_CN, "/Users/tedli/workspace/defaultWorkSpace/nova_test/sex.mp4")
    # response=invoke_nova(model_id, IMG_PROMPT, "93.png")
    # logger.info(response)
