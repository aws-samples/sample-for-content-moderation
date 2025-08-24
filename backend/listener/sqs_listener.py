import boto3
from config import MODERATION_SQS_URL, PROGRAM_TYPE, ATTEMPT_COUNT, REGION_NAME
from tools.log_config import get_logger
logger = get_logger(__name__)

class SQSListener:
    def __init__(self):
        self.sqs = boto3.client('sqs', region_name=REGION_NAME)
        self.queue_url = MODERATION_SQS_URL

    def listen(self):
        logger.info(f"Listening for SQS messages...v20250802... {self.queue_url}")

        '''
        program_type  程序类型 0:持续处理SQS消息   1:仅处理1条SQS  2:持续处理SQS消息，直到监听x次消息队列后后没有消息响应
        attempt_count  获取SQS消息失败后的重试次数
        
        
        program_type   Program type  0: Continuously process SQS messages   1: Process only 1 SQS message   2: Continuously process SQS messages until no message response after listening to the message queue x times
        attempt_count   Number of retry attempts after failing to retrieve SQS messages
        '''

        temp_attempt_count=ATTEMPT_COUNT

        while True:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )

            messages = response.get('Messages', [])
            if messages:
                for message in messages:
                    yield message

                    logger.info(f"delete message {message['ReceiptHandle']}")
                    self.sqs.delete_message(
                        QueueUrl=self.queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )

                temp_attempt_count = ATTEMPT_COUNT
                logger.info("Reset and recalculate retry count")

            # 程序类型 0:持续处理SQS消息   1:仅处理1条SQS  2:持续处理SQS消息，直到监听x次消息队列后后没有消息响应
            # Program type 0: Continuously process SQS messages
            # 1: Process only 1 SQS message
            # 2: Continuously process SQS messages until no message response after listening to the message queue x times

            if PROGRAM_TYPE=="1" or PROGRAM_TYPE == 1:
                logger.info("Type is 1, process only 1 SQS message")
                break

            if PROGRAM_TYPE=="2" or PROGRAM_TYPE == 2:
                logger.info(f"Type is 2, still need to retry {temp_attempt_count} times")

                temp_attempt_count-=1
                if temp_attempt_count<0:
                    logger.info("All retries completed")
                    break

        logger.info("SQS listening ended")
