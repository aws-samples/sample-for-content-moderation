import queue
import threading
import time
import traceback
import sys
from config import ROOT_RESOURCE_PATH, BATCH_PROCESS_IMG_NUMBER, VISUAL_MODERATION_TYPE
from processor.content_moderation import audio_moderation,image_moderation
import os
from tools.log_config import get_logger
logger = get_logger(__name__)

'''
main_process_stop_event_queue
存储SQS进程的执行状态，当SQS进程执行完毕时，会存入结束消息。通知进行扫描与审核的子线程结束任务。
Stores the execution status of the SQS process. When the SQS process is completed, 
an end message will be stored to notify the scanning and review sub-threads to finish their tasks.
'''

main_process_stop_event_queue = queue.Queue()

'''
thread_stop_status_queue: Queue for the thread's stop status

共有4个线程需要关闭，分别为
扫描图片文件的线程、扫描音频文件的线程、处理图片文件的线程、处理音频文件的线程

There are 4 threads that need to be stopped:
Thread for scanning image files
Thread for scanning audio files
Thread for processing image files
Thread for processing audio files"
'''
thread_stop_status_queue = queue.Queue()


#待处理图片任务的队列 Queue of image processing tasks.
img_process_task_fifo_queue = queue.Queue()
#待处理音频任务的队列 Queue of audio processing tasks.
audio_process_task_fifo_queue = queue.Queue()


'''
1.Scan local files.  扫描本地文件
2.Perform moderation.  进行审核
3.Upload moderation information. 上传审核信息
'''



def scan_and_moderation_file(process_flag):
    '''
    scan_and_moderation_file
    :param process_flag:
    :return:
    '''

    if process_flag==0:
        # First execution: Create and start the scanning thread.
        # Create and start a scan thread

        scan_thread_audio = threading.Thread(target=scan_directory, args=(ROOT_RESOURCE_PATH,"audio"))
        scan_thread_audio.daemon = True
        scan_thread_audio.start()

        scan_thread_image = threading.Thread(target=scan_directory, args=(ROOT_RESOURCE_PATH,"image"))
        scan_thread_image.daemon = True
        scan_thread_image.start()

        time.sleep(1) # nosemgrep

        # 创建并启动音频处理线程
        # Create and start the audio processing thread
        process_thread_audio = threading.Thread(target=process_audio)
        process_thread_audio.daemon = True
        process_thread_audio.start()

        # 创建并启动图片处理线程
        # Create and start the image processing thread
        process_thread_image = threading.Thread(target=process_images)
        process_thread_image.daemon = True
        process_thread_image.start()

    else:

        time.sleep(10) # nosemgrep

        #The SQS message has been processed, notifying the sub-thread to finish the task.

        main_process_stop_event_queue.put("stop")
        while True:
            qsize=thread_stop_status_queue.qsize()
            if qsize !=4:
                logger.info(f"There are {4 - qsize} tasks remaining.")

            else:
                logger.info(f"{qsize} tasks have been completed.")
                logger.info("【L3】process_file: Scan and process file tasks completed.")
                break
            time.sleep(5) # nosemgrep


def scan_directory(root_dir,task_type):


    while main_process_stop_event_queue.empty():
        # 如果SQS进程仍在执行
        # If the SQS process is still running..

        #持续扫描本地文件
        #Continuously scan local files.

        logger.info(f"scan_directory {task_type}")
        try:
            if not os.path.exists(root_dir):
                os.makedirs(root_dir)

        except Exception as e:
            logger.info(e)

        processing_dir = os.path.join(root_dir, "processing")
        resource_items = os.listdir(root_dir)

        media_folders = [item for item in resource_items if os.path.isdir(os.path.join(root_dir, item))]
        if len(media_folders) > 0:

            for task_id in media_folders:

                if task_type =='audio':
                    media_folder_audio_path = os.path.join(root_dir, task_id, "audio")
                    if not os.path.exists(media_folder_audio_path):
                        os.makedirs(media_folder_audio_path)
                    audio_slice_arr = os.listdir(media_folder_audio_path)

                    # Traverse audio files and add them to the queue.
                    move_file(audio_slice_arr, root_dir, processing_dir, media_folder_audio_path, task_id, "audio")

                elif task_type =='image':

                    media_folder_img_path = os.path.join(root_dir, task_id, "image")
                    if not os.path.exists(media_folder_img_path):
                        os.makedirs(media_folder_img_path)
                    img_slice_arr = os.listdir(media_folder_img_path)

                    # Traverse images files and add them to the queue.
                    move_file(img_slice_arr, root_dir, processing_dir, media_folder_img_path, task_id, "image")


        time.sleep(2) # nosemgrep


    thread_stop_status_queue.put(f"scan_directory {task_type} Stop execution.")
    logger.info(f"scan_directory {task_type} Stop execution.")




def is_file_recently_modified(filepath, threshold=3):
    '''
    判断最近是否被修改过
    Check if the file has been modified recently.

    :param filepath:
    :param threshold:
    :return:  最后变更时间 是否小于指定秒 True if the last modification time is less than the specified threshold, otherwise False.
    '''
    current_time = time.time()
    file_mtime = os.path.getmtime(filepath)
    return (current_time - file_mtime) <= threshold


def move_file(slice_arr, root_dir, processing_dir, media_folder_path, task_id, type_flag):
    '''
    将未处理的文件 移动到 处理中
    Move the unprocessed files to the 'Processing' folder
    :param slice_arr:
    :param root_dir:
    :param processing_dir:
    :param media_folder_path:
    :param task_id:
    :param type:
    :return:
    '''
    temp_img_arr = []

    # 遍历媒体文件  Traverse media files.
    for slice_name in slice_arr:
        file_path = os.path.join(media_folder_path, slice_name)

        if is_file_recently_modified(file_path,3):
            logger.info(f"Writing in progress, not moving {file_path} yet.")

            continue

        logger.info(f"Processing {file_path}")

        new_path = file_path.replace(root_dir, processing_dir)

        dst_dir = os.path.dirname(new_path)

        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir)


        old_file_size = os.path.getsize(file_path)
        if old_file_size == 0:
            logger.info(f"old_file_size, not moving yet: {old_file_size}")
            continue

        os.replace(file_path,new_path)

        new_file_size = os.path.getsize(new_path)
        logger.info(f"new_file_size: {new_file_size}")


        if type_flag == 'audio':

            audio_process_task_fifo_queue.put({
                "task_id": task_id,
                "file_paths": new_path,
            })
        else:
            #Images need to be processed in bulk.
            temp_img_arr.append(new_path)

    # Batch processing of images.
    if type_flag == "image":
        if temp_img_arr:

            if VISUAL_MODERATION_TYPE =="video":
                chunk_size= 1
            else:
                # Split into groups of x
                chunk_size = BATCH_PROCESS_IMG_NUMBER
            new_arr = [temp_img_arr[i:i + chunk_size] for i in range(0, len(temp_img_arr), chunk_size)]

            for arr in new_arr:
                img_process_task_fifo_queue.put({
                    "task_id": task_id,
                    "file_paths": arr,
                })




def process_images():

    #主线程没有通知关闭 则一直执行
    #If the main thread does not send a shutdown notification, it will keep running
    while True:

        qsize = thread_stop_status_queue.qsize()

        try:
            image_info = img_process_task_fifo_queue.get(timeout=3)
            logger.info(f"Processing image: {image_info}")


            image_moderation(image_info['file_paths'], image_info['task_id'])

            img_process_task_fifo_queue.task_done()
        except queue.Empty:
            logger.info("img_process_task_fifo_queue: empty")
            pass
        except Exception as e:
            logger.info(f"process img error: {str(e)}")
            traceback.print_exc(file=sys.stdout)

        if img_process_task_fifo_queue.empty()  and  qsize>=2 and not main_process_stop_event_queue.empty():
            #两个扫描目录的程序已完成 并且 消息队列任务执行完成， 则终止任务
            #If both directory scanning programs are completed and the message queue tasks are finished, then terminate the task.

            logger.info("thread :process_images stop")
            break

    thread_stop_status_queue.put(f"process_images Stop execution.")
    logger.info(f"process_images Stop execution.")


def process_audio():


    while True:
        qsize = thread_stop_status_queue.qsize()

        try:
            audio_info = audio_process_task_fifo_queue.get(timeout=3)
            logger.info(f"Processing audio: {audio_info}")

            audio_moderation(audio_info['file_paths'],audio_info['task_id'])

            audio_process_task_fifo_queue.task_done()
        except queue.Empty:
            logger.info("audio_process_task_fifo_queue消息队列为空")
            pass
        except Exception as e:
            logger.info(f"audio process error: {str(e)}")
            traceback.print_exc(file=sys.stdout)


        if audio_process_task_fifo_queue.empty()  and  qsize>=2 and not main_process_stop_event_queue.empty():
            #两个扫描目录的程序已完成 并且 消息队列任务执行完成， 则终止任务
            #If both directory scanning programs are completed and the message queue tasks are finished, then terminate the task.

            logger.info("thread: process_audio stop")
            break


    thread_stop_status_queue.put(f"process_audio Stop execution.")
    logger.info(f"process_audio Stop execution.")




if __name__ == '__main__':
    #Test
    scan_and_moderation_file(0)
    try:
        while True:
            time.sleep(10) # nosemgrep
    except KeyboardInterrupt:
        logger.info("The program was interrupted by the user")
