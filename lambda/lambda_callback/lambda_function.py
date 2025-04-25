import json
# import os
# import sys
# current_dir = os.path.dirname(os.path.abspath(__file__))
# lib_dir = os.path.join(current_dir, 'lib')
# sys.path.append(lib_dir)

'''
import requests



# from config import USER_TABLE_NAME
# from dynamodb_client import query_by_pk,init

def callback(callback_url, message_obj):

    url = callback_url

    payload = json.dumps({
        "param1": "param1",
        "param2": "param2"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
'''

def lambda_handler(event, context):
    print(json.dumps(event))

    body = event['Records'][0]['body']
    body_obj = json.loads(body)
    print(body_obj)

    message_obj=body_obj['message']


    return {
        'statusCode': 200,
        'body':"Need to be implemented according to own service verification mechanism"
    }


'''

ddb = init()
table = ddb.Table(USER_TABLE_NAME)



resoponse=query_by_pk(table,"user_id",message_obj['user_id'])
if len(resoponse)>0:
    callback_url=resoponse[0]['callback_url']
    print(callback_url)
    callback(callback_url, message_obj)

    return {
        'statusCode': 200,
        'body': 'Sent successfully'
    }
else:
    return {
        'statusCode': 401,
        'body': 'User does not exist'
    }
    
'''



