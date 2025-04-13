
import boto3
from config import REGION_NAME


def init():
    sqs = boto3.client('sqs',region_name=REGION_NAME)
    return sqs


def query(sqs,queueUrl):
    response = sqs.receive_message(
        QueueUrl=queueUrl,
        AttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=10,
        WaitTimeSeconds=10
    )
    return response


def instert(sqs,queueUrl,body):
    responses = sqs.send_message(
        QueueUrl=queueUrl,
        MessageBody=body
    )
    return responses


def delete(sqs,queueUrl,receiptHandle):
    responses = sqs.delete_message(
        QueueUrl=queueUrl,
        ReceiptHandle=receiptHandle
    )
    return responses



