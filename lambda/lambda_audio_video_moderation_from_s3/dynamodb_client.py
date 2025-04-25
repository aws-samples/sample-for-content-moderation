import boto3
from boto3.dynamodb.conditions import Key, Attr

from config import REGION_NAME,TASK_DETAIL_TABLE_NAME


def init():
    return boto3.resource('dynamodb', region_name=REGION_NAME)


def save(table, info):
    response = table.put_item(Item=info)
    # logger.info(response)

def query_by_pk(table,key_name,key_value):
    response = table.query(
        KeyConditionExpression=Key(key_name).eq(key_value)
    )
    return response['Items']




if __name__ == '__main__':
    ddb = init()
    table = ddb.Table(TASK_DETAIL_TABLE_NAME)

    # delete_by_pk(table, "task_id", "lee_0a1322d469e3a4498baedf9850817249_1")
    # delete_by_gsi(table, "task_id_query","task_id_query", "lee_0a1322d469e3a4498baedf9850817249")
