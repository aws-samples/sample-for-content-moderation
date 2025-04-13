import json
import time
from tools.log_config import get_logger
logger = get_logger(__name__)
from config import CALLBACK_SQS_URL, TASK_DETAIL_TABLE_NAME, TASK_TABLE_NAME
from tools import sqs_client, dynamodb_client

def save_and_push_message(task_id, s3_path,s3_read_path, original_content, start_time, end_time, confidence,tag, moderation_info,type_info, state):
    ddb = dynamodb_client.init()
    task_detail_table = ddb.Table(TASK_DETAIL_TABLE_NAME)
    task_table = ddb.Table(TASK_TABLE_NAME)

    result = {
        "type": type_info,
        "files": s3_path,
        "read_files": s3_read_path,
        "original_content": original_content,
        "message": moderation_info if isinstance(moderation_info, str) else ",".join(moderation_info),
        "confidence": confidence if isinstance(confidence, str) else ",".join(confidence),
        "tag":  tag if isinstance(tag, str) else ",".join(tag),
        "start_time": start_time,
        "end_time": end_time,
        "state": state
    }

    # 1 is abnormal, 2 is normal
    if state == 1:
        if type_info=='audio':
            logger.info(f"【audio abnormal】:{original_content}")

        elif type_info=='image':
            logger.info(f"【images abnormal】:{s3_path} ")
        elif type_info=='video':
            logger.info(f"【images abnormal】:{s3_path} ")

        task_id_arr=task_id.split("_")
        result['task_id_query'] = f'{task_id_arr[0]}_{task_id_arr[1]}'
        result['task_id']=task_id
        result['timestamp'] = int(time.time() * 1000)

        push_message(result)
        dynamodb_client.save(task_detail_table, result)


    dynamodb_client.update(task_table,"task_id",task_id,"task_state","3")




def push_message(moderation_info):
    result_info = {
        "message": json.dumps(moderation_info)
    }
    sqs = sqs_client.init()
    sqs_client.instert(sqs, CALLBACK_SQS_URL, json.dumps(result_info,ensure_ascii=False))


if __name__ == '__main__':
    push_message("", "", "", "")
