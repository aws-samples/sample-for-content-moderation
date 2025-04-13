"""
@File    : __init__.py.py
@Time    : 2025/3/1 21:41
@Author  : tedli
@Email   : tedli@amazon.com
@Description: 
    This file is for...
"""
import json
from config import USER_TABLE_NAME
import dynamodb_client


def lambda_handler(event, context):
    print(event)
    print(context)

    print("Received event:", json.dumps(event, indent=2))

    # 获取请求头中的 token 和 user_id
    headers = event.get("headers", {})
    token = headers.get("token", "")
    user_id = headers.get("user_id", "")


    
    # 解析 API Gateway 请求信息
    method_arn = event.get("methodArn", "")
    region_id = method_arn.split(":")[3]
    account_id = method_arn.split(":")[4]
    api_id = method_arn.split(":")[5].split("/")[0]
    stage = method_arn.split("/")[1]
    http_verb = method_arn.split("/")[2]
    resource = "/".join(method_arn.split("/")[3:])

    ddb = dynamodb_client.init()
    user_table = ddb.Table(USER_TABLE_NAME)
    conditions = {'token': token}
    resoponse = dynamodb_client.query_with_conditions(user_table, "user_id", user_id, conditions)

    if len(resoponse) == 0:
        effect = "Deny"
    else:
        effect = "Allow"

    # 构造 policyDocument
    auth_response = {
        "principalId": user_id or "anonymous",  # 默认 "anonymous"
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": f"arn:aws:execute-api:{region_id}:{account_id}:{api_id}/{stage}/{http_verb}/{resource}"
                }
            ]
        },
        "context": {
            "stringKey": "some_value",
            "numberKey": "1",
            "booleanKey": "true",
            "user_id": user_id
        },
        "usageIdentifierKey": "your-api-key"
    }

    print("Auth Response:", json.dumps(auth_response, indent=2))
    return auth_response

