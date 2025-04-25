import boto3
from boto3.dynamodb.conditions import Key, Attr
from config import REGION_NAME,TASK_DETAIL_TABLE_NAME

def init():
    return boto3.resource('dynamodb', region_name=REGION_NAME)

def query_by_pk(table,key_name,key_value):
    response = table.query(
        KeyConditionExpression=Key(key_name).eq(key_value)
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
