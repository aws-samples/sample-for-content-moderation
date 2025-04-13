import json
import re

import boto3
from config import REGION_NAME

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

def invoke_claude(model_id, system_prompt, prompt, text):
    payload = {
        "modelId": model_id,
        "contentType": "application/json",
        "accept": "application/json",
        "body": {
            "system": system_prompt,
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type":"text","text": "用户输入的内容如下: "},
                        {"type":"text","text": text},
                        {"type":"text","text": prompt}
                    ]
                }
            ]
        }
    }

    response = bedrock_client.invoke_model(
        body=json.dumps(payload['body']).encode('utf-8'),
        contentType=payload['contentType'],
        accept=payload['accept'],
        modelId=payload['modelId']
    )

    response_body = json.loads(response['body'].read().decode('utf-8'))
    if 'content' in response_body and isinstance(response_body['content'], list):
        content = response_body['content'][0]
        if 'text' in content:
            analysis = content['text']
            analysis=get_jsonobj(analysis)
        else:
            analysis = None
    else:
        analysis = None
    return analysis


def invoke_nova(model_id, system_prompt, prompt, contents):
    system_list = [
        {
            "text": system_prompt
        }
    ]

    message_list = [
        {"role": "user", "content": [{"text": "用户输入的内容如下: "}]},
        {"role": "user", "content": [{"text": contents}]},
        {"role": "user", "content": [{"text": prompt}]}

    ]

    inf_params = {"max_new_tokens": 5000, "top_p": 0.9, "top_k": 20, "temperature": 0}

    request_body = {
        "schemaVersion": "messages-v1",
        "system": system_list,
        "messages": message_list,
        "inferenceConfig": inf_params,
    }
    print(request_body)
    response = bedrock_client.invoke_model(
        modelId=model_id, body=json.dumps(request_body)
    )

    response_body = json.loads(response['body'].read().decode('utf-8'))['output']['message']

    if 'content' in response_body and isinstance(response_body['content'], list):
        content = response_body['content'][0]['text']
        print(content)
        if "The generated text has been blocked by our content filters" in content:
            return json.dumps({
               "result":[
                  {
                      "tag":"Blocked",
                      "confidence":"High"
                  }
               ]
            },ensure_ascii=False)
        else:
            content = re.sub(r'```json\n|\n```', '', content)

        print(content)
        return content
    else:
        return None
