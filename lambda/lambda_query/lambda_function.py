import json
import os
import decimal

from dynamodb_client import init, query_by_gsi, query_by_pk
from sha_tool import get_unique_value
from config import TASK_DETAIL_TABLE_NAME, TASK_ID_QUERY_INDEX, TASK_ID_QUERY_INDEX_KEY_NAME, USER_TABLE_NAME


def convert_decimal(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)  # 或者 return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def lambda_handler(event, context):
    print(json.dumps(event))

    body_str = event['body']
    header_obj = event['headers']

    body_data = json.loads(body_str)

    user_id = header_obj.get('user_id')

    url = body_data.get('url')
    start_time = body_data.get('start_time')
    end_time = body_data.get('end_time')

    ddb = init()

    task_id = f"{user_id}_{get_unique_value(url)}"
    print(f"task_id {task_id}")
    table = ddb.Table(TASK_DETAIL_TABLE_NAME)
    try:
        response_ddb = query_by_pk(table, "task_id", task_id, "timestamp", start_time, end_time)
        # response_ddb = query_by_gsi(table, TASK_ID_QUERY_INDEX, TASK_ID_QUERY_INDEX_KEY_NAME,task_id)
    except Exception as e:
        print(e)
        response_ddb = []

    print(response_ddb)
    result_arr = []
    if len(response_ddb) != 0:
        for r in response_ddb:
            result_arr.append({
                "type": r['type'],
                "tag": r['tag'],
                "files": r['read_files'],
                # "original_content": r['original_content'],
                # "message": r['message'],
                "confidence": r['confidence'],
                # "time_info": [convert_decimal(i) for i in r['time_info']],
                "task_state": int(r['state']),
                "timestamp": int(r['timestamp']),
                "create_time": r['create_time']
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
        }, ensure_ascii=False)
    }


if __name__ == '__main__':
    a = {
        "url": "https://d14tamu6in7iln.cloudfront.net/sex/sex_e2.mp4",
        # "start_time" :1745641275943,
        # "end_time" :1745641273424,
    }
    event = {
        "headers": {"user_id": "InternalTask"},
        "body": json.dumps(a)
    }

    print(lambda_handler(event, None))
