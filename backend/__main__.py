import json

from dependency_injector import providers

from base.plugin_config import AppContainer
from config import SPEECH_RECOGNIZER_PLUGIN, IMAGE_MODERATION_PLUGIN, TEXT_MODERATION_PLUGIN
from plugin.bedrock_image_moderation import BedrockImageModeration
from plugin.bedrock_text_moderation import BedrockTextModeration
from plugin.rekogition_image_moderation import RekognitionImageModeration
from plugin.sagemaker_asr import SagemakerASR
from tools.log_config import setup_logging, get_logger

setup_logging()

import multiprocessing
import sys
import time
from listener.sqs_listener import SQSListener

from processor.sqs_msg_processor import MessageProcessor

from scanner.file_scanner import scan_and_moderation_file


logger = get_logger(__name__)

'''
1. Monitor SQS tasks
2. Conduct content moderation
'''
class Listener:
    def __init__(self):
        self.sqs_listener = SQSListener()
        self.message_processor = MessageProcessor()

    def run(self):
        logger.info("Starting SQS message processor...")
        messages = self.sqs_listener.listen()
        for message in messages:
            # 处理消息
            self.message_processor.process(message)


def listen_media_task(process_queue):
    try:
        # Listening to SQS tasks
        listen = Listener()
        listen.run()

        # SQS任务执行完成，通知scan_file_and_moderation 停止扫描
        # SQS task execution is completed, notifying scan_file_and_moderation to stop scanning
        time.sleep(2) # nosemgrep
        logger.info("【L2】 All sqs tasks have been completed")
        process_queue.put("【listen_media_task】 is completed")

    except Exception as e:
        logger.error(f"【L2】 listen_media_task encountered an error : {e}")
        process_queue.put(f"【listen_media_task】 encountered an error")
    finally:
        sys.exit(0)


def scan_file_and_moderation(process_queue):
    '''
    Scan audio & image files for moderation
    :param process_queue:
    :return:
    '''

    try:
        init_plugin()


        #process_flag
        #0 Not executed  首次执行
        #1 Executed  执行过
        #2 Need to be closed 执行完毕
        process_flag=0
        while True:
            if  process_queue.empty():
                #process_queue中没有收到停止的消息，则持续执行扫描任务
                #If no stop message is received in process_queue, the scanning task will continue to be executed.

                if process_flag == 0:
                    scan_and_moderation_file(process_flag)
                    process_flag=1

                # 每隔10s判断1次状态
                # Check the status every 10 seconds
                time.sleep(10) # nosemgrep
            else:
                # process_queue中接收到停止的消息，执行最后一次扫描与审核
                # The process_queue receives a stop message and performs the last scan and audit

                message = process_queue.get()
                logger.info(f"The Scan Process has received the queue message : {message}")
                logger.info(f"Perform the final scan and task processing")

                process_flag=2

                scan_and_moderation_file(process_flag)
                break

    except Exception as e:
        logger.error(f"【L2】 scan_file_and_moderation encountered an error : {e}")

    finally:

        logger.info("【L2】The scanning task process has completed")
        #Notify ECS that the program has finished successfully.
        sys.exit(0)



def init_plugin():
    # 1. 创建容器实例
    container = AppContainer()

    # 2. 从配置文件加载配置
    # with open("plugin_config.json") as f:
    #     config_data = json.load(f)
    # container.config.from_dict(config_data)

    # 3. 根据配置初始化具体实现
    if SPEECH_RECOGNIZER_PLUGIN == "sagemaker":
        container.speech_recognizer.override(providers.Factory(SagemakerASR))

    if TEXT_MODERATION_PLUGIN == "bedrock":
        container.text_moderation.override(providers.Factory(BedrockTextModeration))

    if IMAGE_MODERATION_PLUGIN == "rekognition":
        container.image_moderation.override(providers.Factory(RekognitionImageModeration))
    elif IMAGE_MODERATION_PLUGIN == "bedrock":
        container.image_moderation.override(providers.Factory(BedrockImageModeration))


    container.wire(packages=["processor.content_moderation"])


if __name__ == "__main__":

    '''
    创建一个队列用于进程间通信,当SQS进程执行完毕时，会往队列存入信息，通知扫描与进行审核的进程结束任务。
    Create a queue for inter-process communication. When the SQS process is completed, 
    information will be stored in the queue to notify the scanning and auditing processes to complete the task.
    '''

    try:
        process_queue = multiprocessing.Queue()

        # Listen to SQS
        process1 = multiprocessing.Process(target=listen_media_task, args=(process_queue,))

        # Scan audio & image files for moderation
        process2 = multiprocessing.Process(target=scan_file_and_moderation, args=(process_queue,))

        process1.start()
        process2.start()

        process1.join()
        process2.join()

    except Exception as e:
        logger.error(f"【L1】The main process found an error: {e}")

    finally:
        logger.info("【L1】【Content moderation completed 】")
        sys.exit(0)