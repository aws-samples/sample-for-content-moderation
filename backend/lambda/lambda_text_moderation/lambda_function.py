import json
import boto3
from config import REGION_NAME, TEXT_NOVA_SYSTEM_PROMPT_1_EN, MODEL_ID, TEXT_CLAUDE_SYSTEM_PROMPT, \
    TEXT_DEFAULT_PROMPT_EN
from bedrock_text_tool import invoke_nova, invoke_claude

bedrock_client = boto3.client('bedrock-runtime', region_name=REGION_NAME)


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

    # 从 event 的 body 字段中提取 JSON 字符串

    if 'prompt' in body_data:
        prompt = body_data['prompt']
    else:
        prompt = TEXT_DEFAULT_PROMPT_EN

    if 'text' not in body_data:
        return response("Parameter error", "", 500)

    if 'model_id' in body_data:
        model_id = body_data['model_id']
    else:
        model_id = MODEL_ID

    if 'system_prompt' in body_data:
        system_prompt = body_data['system_prompt']
    else:
        if "nova" in model_id:
            system_prompt = TEXT_NOVA_SYSTEM_PROMPT_1_EN
        else:
            system_prompt = TEXT_CLAUDE_SYSTEM_PROMPT

    if "nova" in model_id:
        result = invoke_nova(model_id, system_prompt, prompt, body_data['text'])
    elif "claude" in model_id:
        result = invoke_claude(model_id, system_prompt, prompt, body_data['text'])
    else:
        return None
    print(result)

    if isinstance(result, str):
        bedrock_result_obj = json.loads(result)
    else:
        bedrock_result_obj = result

    return response("Submission successful", bedrock_result_obj, 200)


if __name__ == '__main__':
    # event = {
    #     "body": "{\"text\": \"我想打爆你的头.\", \"model_id\": \"us.amazon.nova-micro-v1:0\"}",
    # }

    # system_prompt='''你是一名严格的儿童学习社区审核人员，需要严格审核文本以维护网络环境，我们会根据你的意见对文本进行分级。'''

    prompt = '''
    
##请根据以下分类标准，请对每一类（如下所列）进行独立判断。
1. 涉政（Politics）：是否包含政治敏感内容，如政要评论、政党攻击、分裂言论等。  
2. 暴恐（Violence）：是否包含暴力、恐怖袭击、极端主义内容或威胁行为。  
3. 色情（Porn）：是否包含露骨的性描写、性暗示、淫秽内容或低俗挑逗。  
4. 违禁（Ban）：是否涉及违法违规内容，如毒品、枪支、赌博、非法交易等。  
5. 辱骂（Abuse）：是否包含人身攻击、侮辱性语言、歧视或仇恨言论。  
6. 黑名单（Blacklist）：是否涉及黑产、刷单、外挂、作弊工具、灰产行为等。  
7. 隐私（Privacy）：是否泄露他人隐私，如身份证号、手机号、家庭住址、银行信息等。  
8. 网络诈骗（Fraud）：是否存在诈骗倾向，如虚假中奖、钓鱼链接、金融欺诈等。  


##请使用以下Json格式返回,不要返回无关的解释
{
   "result":[
      {
          "tag":"Violence",
          "confidence":"Medium"
      }
   ],
   "state": 1
}

##字段解释
- result: 分类结果的数组
- tag: 标签(Politics/Violence/Porn/Ban/Abuse/Blacklist/Privacy/Fraud),请不需要虚构标签
- confidence：可信度(Low、Medium、High)
- state: 审核状态(2表示合规，1表示不合规)

'''

    event = {
        "body": json.dumps(
            {
                # "text": "今天天气不错",
                # "text": "把你卡号给我说一下？",
                # "text": "明天去市政府抗议",
                "text": "你有白粉么？",
                # "text": "Hey everyone, my name is Steve. I'm very dangerous. I have serious weapons. If you don't listen to me, I will kill you all.",
                # "text": "hello",
                # "text": "西藏是中国的吗？",
                # "system_prompt": system_prompt,
                # "prompt": prompt,
                "model_id": "us.amazon.nova-micro-v1:0"
                # "model_id": "anthropic.claude-3-haiku-20240307-v1:0"
            }),
    }

    # event = {
    #     "body": "{\"text\": \"I'm gonna blow your head off.\", \"prompt\": \"分析这个图。\", \"model_id\": \"anthropic.claude-3-sonnet-20240229-v1:0\"}",
    # }

    # anthropic.claude-3-haiku-20240307-v1:0
    #
    print(lambda_handler(event, None))
