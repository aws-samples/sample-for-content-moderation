import boto3
from config import REGION_NAME


def init():
    return boto3.resource('dynamodb', region_name=REGION_NAME)


def save(table, info):
    response = table.put_item(Item=info)
    # logger.info(response)
