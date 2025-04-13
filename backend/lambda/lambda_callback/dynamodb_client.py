import boto3
from boto3.dynamodb.conditions import Key, Attr
from config import REGION_NAME,USER_TABLE_NAME


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


def query_with_conditions(table, partition_key, partition_value, conditions=None):

    key_condition = Key(partition_key).eq(partition_value)

    filter_expression = None
    if conditions:
        for attr, value in conditions.items():
            if filter_expression is None:
                filter_expression = Attr(attr).eq(value)
            else:
                filter_expression &= Attr(attr).eq(value)

    if filter_expression:
        response = table.query(
            KeyConditionExpression=key_condition,
            FilterExpression=filter_expression
        )
    else:
        response = table.query(
            KeyConditionExpression=key_condition
        )

    return response['Items']

if __name__ == '__main__':
    ddb = init()
    table = ddb.Table(USER_TABLE_NAME)
    info={
        "user_id":"nnn",
        "token":"bbb",
        "callback_url":"cccc"
    }

    save(table,info)
    # conditions = {'token': 'xxxx'}
    # resoponse=query_with_conditions(table,"user_id","jane",conditions)

    # print(resoponse)

    # delete_by_pk(table, "task_id", "lee_0a1322d469e3a4498baedf9850817249_1")
    # delete_by_gsi(table, "task_id_query","task_id_query", "lee_0a1322d469e3a4498baedf9850817249")
