import json
import os

from dynamodb_client import init, query_by_gsi
from sha_tool import get_unique_value
from config import TASK_DETAIL_TABLE_NAME, TASK_ID_QUERY_INDEX, TASK_ID_QUERY_INDEX_KEY_NAME, USER_TABLE_NAME


def lambda_handler(event, context):
    print(json.dumps(event))

    body_str = event['body']
    header_obj = event['headers']

    body_data = json.loads(body_str)

    url = body_data.get('url')
    user_id = header_obj.get('user_id')

    ddb = init()


    task_id = f"{user_id}_{get_unique_value(url)}"

    table = ddb.Table(TASK_DETAIL_TABLE_NAME)
    # response_ddb = query_by_pk(table, "task_id", task_id)
    try:
        response_ddb = query_by_gsi(table, TASK_ID_QUERY_INDEX, TASK_ID_QUERY_INDEX_KEY_NAME,task_id)
    except Exception as e:
        print(e)
        response_ddb=[]

    print(response_ddb)
    result_arr = []
    if len(response_ddb) != 0:
        for r in response_ddb:
            result_arr.append({
                "type": r['type'],
                "tag": r['tag'],
                "level": str(r['level']),
                "files": r['read_files'].split("^_^"),
                "original_content": r['original_content'],
                "message": r['message'],
                "start_time": int(r['start_time']),
                "end_time": int(r['end_time']),
                "task_state": 1
            }
            )

    return response("Query successful", result_arr, 200)


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
        },ensure_ascii=False)
    }


if __name__ == '__main__':


    event = {
        "body": "{\"url\": \"https://xxxxxxxx.xxxx.xxxx/xxxx/93.mp4\"}"
    }

    print(lambda_handler(event, None))
