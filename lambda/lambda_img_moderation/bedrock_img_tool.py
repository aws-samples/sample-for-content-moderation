import base64
import json
import re
import boto3
from config import REGION_NAME, IMG_PROMPT_0325_CN, IMG_NOVA_SYSTEM_PROMPT_1_EN, IMG_CLAUDE_SYSTEM_PROMPT

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



def invoke_claude(model_id,system_prompt, prompt, img_base64):
    content = []
    try:

        content.append({
            "type": "text",
            "text":  "The image_index of the following figure is: 1  \n"
        })

        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": f"image/{get_image_type_from_base64(img_base64)}",
                "data": img_base64
            }
        })
        content.append({
            "type": "text",
            "text":prompt
        })

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
            response_jsonobj=get_jsonobj(analysis)

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


def invoke_nova(model_id,system_prompt,prompt, img_base64):
    content_list = []
    try:

        content_list.append({
            "text":  "The image_index of the following figure is: 1  \n "
        })
        content_list.append({
            "image": {
                "format":  get_image_type_from_base64(img_base64),
                "source": {
                    "bytes":img_base64
                }
            }
        })

        content_list.append({
            "text":prompt
        })

    except Exception as e:
        print(f"Error")
        print(e)


    payload = {
        "modelId": model_id,
        "contentType": "application/json",
        "accept": "application/json",
        "request_body": {"system": [
            {
                "text": system_prompt
            }
        ],
            "messages": [
                {
                    "role": "user",
                    "content": content_list
                }
            ], "inferenceConfig": {
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

    # Process the response
    response_str = response['body'].read().decode('utf-8')

    response_body = json.loads(response_str)
    # print(response_body)
    if 'output' in response_body and 'stopReason' in response_body and 'usage' in response_body:
        response_output_info = response_body['output']
        content = response_output_info['message']['content'][0].get('text', '')

        if content:
            if " - The generated text has been blocked by our content filters." in content:
                return "Blocked"
            else:
                content = re.sub(r'```json\n|\n```', '', content)
                print(content)
                response_jsonobj = json.loads(content)

                for r in response_jsonobj['result']:

                    if 'tag' in r and len(r['tag']) > 0:
                        r['state'] = 1
                    if r['state'] != 1 and r['state'] != 2:
                        r['state'] = "3"
                        print("state 错误")

                return response_jsonobj

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
    image_path="db1.jpg"
    with open(image_path, 'rb') as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    response=invoke_claude(model_id, IMG_CLAUDE_SYSTEM_PROMPT,IMG_PROMPT_0325_CN, base64_image)


    # print(response)

    # model_id = "us.amazon.nova-lite-v1:0"
    # response=invoke_nova(model_id, IMG_NOVA_SYSTEM_PROMPT_1_EN,IMG_PROMPT_0325_CN, base64_image)
    # print(response)