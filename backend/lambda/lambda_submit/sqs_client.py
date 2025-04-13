
import boto3
from config import REGION_NAME

def init():
    sqs = boto3.client('sqs',region_name=REGION_NAME)
    return sqs



def instert(sqs,queueUrl,body):
    responses = sqs.send_message(
        QueueUrl=queueUrl,
        MessageBody=body
    )
    return responses
