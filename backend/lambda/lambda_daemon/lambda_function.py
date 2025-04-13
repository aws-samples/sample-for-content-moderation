import time
from ecs_tool import create_ecs_task
from config import REGION_NAME, MODERATION_SQS
import boto3


def count_sqs_number(sqs_url, sqs):
    check_sqs_count = 1
    sqs_message_number_arr = []

    while check_sqs_count < 4:
        print("The current number of SQS checks is", check_sqs_count)

        response = sqs.get_queue_attributes(QueueUrl=sqs_url, AttributeNames=["ApproximateNumberOfMessages"])
        sqs_message_numbers = int(response['Attributes']['ApproximateNumberOfMessages'])
        print(f"The number of messages in SQS is {sqs_message_numbers}")

        sqs_message_number_arr.append(sqs_message_numbers)

        check_sqs_count += 1
        time.sleep(5) # nosemgrep

    average_num = sum(sqs_message_number_arr) / len(sqs_message_number_arr)
    latest_num = sqs_message_number_arr[-1]

    # 如果最后一次数量>0，平均也>0
    # If the last count is > 0, and the average is also > 0
    if latest_num > 0 and average_num > 0:
        return latest_num
    else:
        return 0


def lambda_handler(event, context):
    # [1] Query SQS message count 3 times
    sqs = boto3.client('sqs', region_name=REGION_NAME)
    num = count_sqs_number(MODERATION_SQS, sqs)

    # [2] If the count exceeds the threshold, start ECS tasks
    if num > 0:
        create_ecs_task(num)
        print(f"Starting {num} tasks")
    else:
        print("No need to start tasks")

    return {'statusCode': 200}


if __name__ == '__main__':
    lambda_handler(None, None)
