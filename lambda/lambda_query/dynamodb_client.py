import boto3
from boto3.dynamodb.conditions import Key, Attr
from config import REGION_NAME,TASK_DETAIL_TABLE_NAME

def init():
    return boto3.resource('dynamodb', region_name=REGION_NAME)



def query_by_pk(table, key_name, key_value, timestamp_name=None, start_time=None, end_time=None):
    # 基础查询：主键等于key_value
    key_condition = Key(key_name).eq(key_value)

    # 如果提供了时间范围，增加额外的条件
    if timestamp_name and start_time and end_time:
        key_condition = key_condition & Key(timestamp_name).between(start_time, end_time)
    elif timestamp_name and start_time:
        key_condition = key_condition & Key(timestamp_name).gte(start_time)
    elif timestamp_name and end_time:
        key_condition = key_condition & Key(timestamp_name).lte(end_time)

    response = table.query(
        KeyConditionExpression=key_condition
    )
    return response['Items']


def query_by_gsi(table,index_name,key_name,key_value):
    response = table.query(
    IndexName = index_name,  # 替换为你的 GSI 名称
    KeyConditionExpression = Key(key_name).eq(key_value)
    )
    return response['Items']



if __name__ == '__main__':
    ddb = init()
    table = ddb.Table(TASK_DETAIL_TABLE_NAME)
