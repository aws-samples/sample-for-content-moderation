import base64
import json
import boto3
from config import IMG_NOVA_SYSTEM_PROMPT_1_EN,IMG_CLAUDE_SYSTEM_PROMPT, REGION_NAME, MODEL_ID, IMG_PROMPT_0325_CN
from bedrock_img_tool import invoke_claude, invoke_nova
from rekognition_tool import check_img_use_rek
bedrock_client = boto3.client('bedrock-runtime', region_name=REGION_NAME)




def check_img_use_bedrock(prompt, img_base64, model_id):
    if "nova" in model_id:
        response = invoke_nova(model_id, IMG_NOVA_SYSTEM_PROMPT_1_EN,prompt, img_base64)
    elif "claude" in model_id:
        response = invoke_claude(model_id, IMG_CLAUDE_SYSTEM_PROMPT,prompt, img_base64)
    else:
        return None

    return response



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
        }, ensure_ascii=False)
    }


def lambda_handler(event, context):
    print(json.dumps(event, ensure_ascii=False))

    # 从 event 的 body 字段中提取 JSON 字符串
    body_str = event['body']

    # 解析 body 中的 JSON 字符串
    body_data = json.loads(body_str)

    if 'type' not in body_data:
        return response("Parameter error", "", 500)

    type_flag = body_data['type']

    if 'img_base64' not in body_data:
        return response("Parameter error", "", 500)
    else:
        img_base64 = body_data['img_base64']
        # 解码 base64 图像
        image_bytes = base64.b64decode(img_base64)

    if type_flag == 1:
        label_arr = check_img_use_rek(image_bytes)
    else:
        if 'prompt' in body_data:
            prompt = body_data['prompt']
        else:
            prompt = IMG_PROMPT_0325_CN

        if 'model_id' in body_data:
            model_id = body_data['model_id']
        else:
            model_id = MODEL_ID

        label_arr = check_img_use_bedrock(prompt, img_base64, model_id)

    check_results = []
    print(label_arr)


    check_results.append({
        "check_infos": label_arr if label_arr else []
    })

    return response("Submission successful", check_results, 200)


if __name__ == '__main__':
    image_path = "db2.png"
    with open(image_path, 'rb') as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')


    #type 1 rekognition
    #type 2 bedrock

    # model_id="us.amazon.nova-lite-v1:0"
    model_id ="anthropic.claude-3-sonnet-20240229-v1:0"


    event = {
        "body": json.dumps({
            "prompt": IMG_PROMPT_0325_CN,
            "model_id": model_id,
            "img_base64": base64_image,
            "type": 2
        })
    }


    print(lambda_handler(event, None))
