import json

import boto3

from config import USER_TABLE_NAME,USER_ID,TOKEN_ARN,CALLBACK_URL,REGION_NAME
from dynamodb_client import save,init


def lambda_handler(event, context):
    print(json.dumps(event))

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=REGION_NAME
    )
    token = client.get_secret_value(
        SecretId=TOKEN_ARN
    )


    ddb = init()

    table = ddb.Table(USER_TABLE_NAME)



    info = {
        "user_id": USER_ID,
        "token": token['SecretString'],
        "callback_url": CALLBACK_URL
    }
    save(table,info)
    print("init success")

    return {
        'statusCode': 200,
        'body': 'Sent successfully'
    }
