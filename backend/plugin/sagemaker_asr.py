import json
import os

import boto3

from base.plugin_interface import SpeechRecognizer
from config import WHISPER_ENDPOINT_NAME, REGION_NAME
from tools.log_config import get_logger

logger = get_logger(__name__)



class SagemakerASR(SpeechRecognizer):
    def recognize(self, audio_path: str) -> str:
        return asr_local_file(audio_path)


def asr_local_file(local_file):
    logger.info(f"The audio ASR file address is {local_file}")
    if not os.path.exists(local_file):
        logger.info(f"Audio file does not exist: {local_file}")
        return ""

    file_size = os.path.getsize(local_file)
    if file_size == 0:
        logger.info(f"Audio file is empty: {local_file}")
        return ""

    with open(local_file, 'rb') as audio_file:
        audio_data = audio_file.read()

    if not audio_data:
        logger.info("Audio data is empty。。。。")
        return ""

    else:
        result = call_sagemaker(WHISPER_ENDPOINT_NAME, audio_data)
        logger.info(result)
        return result.get("text","")



def call_sagemaker(endpoint_name, audio_data):
    sagemaker_runtime = boto3.client('sagemaker-runtime',REGION_NAME)
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='audio/x-audio',
        Body=audio_data
    )
    return json.loads(response['Body'].read().decode())




if __name__ == '__main__':

    from tools.log_config import setup_logging
    setup_logging()

    local_file="sample1.flac"
    asr_local_file(local_file)

