import boto3
from boto3.dynamodb.conditions import Key
from config import REGION_NAME


def init():
    return boto3.resource('dynamodb', region_name=REGION_NAME)


def save(table, info):
    response = table.put_item(Item=info)


def query_by_gsi(table,index, key,keyvalue):


    response = table.query(
        IndexName=index,
        KeyConditionExpression=f'{key} = :token_val',
        ExpressionAttributeValues={
            ':token_val': keyvalue
        }
    )

    return response['Items']

def query(table, keyvalue, fields=None):
    query_params = {
        'KeyConditionExpression': Key('id').eq(keyvalue)
    }

    if fields:
        # 如果指定了字段，添加 ProjectionExpression
        query_params['ProjectionExpression'] = ', '.join(fields)

    response = table.query(**query_params)
    return response['Items']


def update(table,pk, id, key, value):
    response = table.update_item(
        Key={pk: id},  # 'id' 是您的主键
        UpdateExpression=f"SET {key} = :val",
        ExpressionAttributeValues={':val': value},
        ReturnValues="UPDATED_NEW"
    )
    return response['Attributes']



if __name__ == '__main__':
    ddb = init()
    # table = ddb.Table("user_vp")
    # responses=query_by_gsi(table,"tokenz-index","tokenz","a1sdfsdf-qwerqwer-weqrweqr-werwqe")
    # logger.info(len(responses))

    # table = ddb.Table("info_vp")
    # responses=query(table,"v")
    # item=responses[0]
    # logger.info(item)
    # if (item.get('speaker_timeline') and
    #         item.get('email') and
    #         item.get('media_allinfo') and
    #         item.get('media_segment_summary') and
    #         item.get('media_summary') and
    #         item.get('media_words')):
    #     logger.info("All results are non-empty.")
    # else:
    #     logger.info("One or more results are empty or missing.")

    # save(table,{"id":"112","email":"999999"})

