import mimetypes
import os
import time
from urllib.parse import urlparse

import ffmpeg
import requests
from tools import ffmpeg_tool
from config import ROOT_RESOURCE_PATH, VISUAL_MODERATION_TYPE
from tools.log_config import get_logger,setup_logging
from tools.s3_client import S3Client

setup_logging()

logger = get_logger(__name__)


def is_live_stream(media_url):
    '''
    Determine if it's a live stream
    :param media_url:
    :return:
    '''

    if media_url.startswith('s3'):
        return False

    # [1]检查文件扩展名 Translation: "Check file extension
    non_live_extensions = [
        # 视频文件扩展名 Translation: "Video file extension
        '.mp4', '.avi', '.mkv', '.webm', '.mov', '.wmv', '.flv', '.3gp', '.mpg', '.mpeg', '.ogg', '.ts',
        # 音频文件扩展名 Translation: "Audio file extension
        '.mp3', '.wav', '.aac', '.m4a', '.wma', '.flac', '.alac', '.aiff', '.ogg', '.opus'
    ]

    file_extension = os.path.splitext(media_url)[1].lower()

    if file_extension in non_live_extensions:
        logger.info("Non-streaming media format")
        return False

    # 检查是否是常见的流媒体协议 Check if it's a common streaming media protocol
    if media_url.startswith(('rtmp://', 'rtsp://', 'wss://')):
        logger.info("live")
        return True

    # [2]检查m3u8格式 Check m3u8 format
    response = requests.get(media_url,timeout=30)
    content = response.text

    if "#EXT-X-ENDLIST" not in content:
        logger.info("live")
        return True
    else:
        logger.info("Non-live")
        return False



def process_video(task_id, media_url, start_connect_max_retries=60, end_connect_max_retries=15, retry_delay=1,
                  audio_segment_duration=10, snapshot_interval=1):
    '''
    Video processing - Extract audio and images from video

    :param media_url:
    :param start_connect_max_retries:
    :param end_connect_max_retries:
    :param retry_delay:
    :param audio_segment_duration:
    :param snapshot_interval:
    :return:
    '''

    # 非流媒体 非直播结束后无需重试  Non-streaming and non-live, no need to retry after it ends.
    try:
        if is_live_stream(media_url) is False:
            end_connect_max_retries = 0
    except Exception as e:
        logger.info(f"Connect Error: {e}")
        return False

    '''
    处理视频文件。直播流结束后需要重试
    :param input_url:
    :param dir_name:
    :param start_connect_max_retries:
    :param end_connect_max_retries:
    :param retry_delay:
    :return:
    '''
    retries = 0
    connect_flag = "First connection retry"
    max_retries = start_connect_max_retries

    # First start time
    first_time = int(time.time())

    dir_start_number = 0
    while retries < max_retries:
        logger.info(f"【{connect_flag}】:Reconnecting")

        result_state = split_video(task_id, media_url, dir_start_number, audio_segment_duration, snapshot_interval,
                                   first_time)

        if result_state:

            # logger.info(f"直播结束，防止意外断，重试{end_connect_max_retries}次")
            logger.info(f"Live stream ended, to prevent unexpected disconnection, retrying {end_connect_max_retries} times")

            connect_flag = "Retry after completion"
            max_retries = end_connect_max_retries
            if max_retries==0:
                break
            retries = 0
            dir_start_number += 1
        else:

            logger.info(f"【{connect_flag}】: Connection failed")
            retries += 1
            if retries < max_retries:

                logger.info(f"【{connect_flag}】: Attempted {retries} times, {max_retries - retries} attempts remaining")
                time.sleep(retry_delay) # nosemgrep
            else:
                logger.info(f"【{connect_flag}】: Maximum retry attempts reached, abandoning detection")

                break

    logger.info("Media file processing completed")

    return True


def get_file_type(filename):
    mime_type, _ = mimetypes.guess_type(filename.lower())
    if mime_type:
        return mime_type.split('/')[0]
    else:
        logger.info(f"mime_type--{mime_type}")
        if filename.endswith("m4a") or filename.endswith("flac"):
            return "audio"

    return None


def split_video(task_id, media_url, dir_start_time, audio_segment_duration=10, snapshot_interval=1, first_time=0):
    '''
    Trim a segment from the video.
    :param rtmp_url:
    :param output_dir:
    :param segment_duration:
    :return:
    '''
    audio_dir = os.path.join(ROOT_RESOURCE_PATH, task_id, "audio")
    img_dir = os.path.join(ROOT_RESOURCE_PATH, task_id, "image")

    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    if media_url.startswith('s3://'):
        #example  media_url  s3://bucket_name/s3_video_moderation/aaaa.mp4

        parsed_url = urlparse(media_url)
        bucket_name = parsed_url.netloc

        file_name = os.path.basename(parsed_url.path)
        s3_file_path = parsed_url.path.lstrip('/')


        #download fron s3
        pedning_review_dir = os.path.join(ROOT_RESOURCE_PATH, task_id, "pending_review")
        if not os.path.exists(pedning_review_dir):
            os.makedirs(pedning_review_dir)
        local_file_path = os.path.join(str(pedning_review_dir),file_name)
        s3_clients = S3Client(bucket_name)
        s3_clients.download_file_from_s3(s3_file_path, local_file_path)

        #process media file
        stream = ffmpeg.input(local_file_path)
    else:
        stream = ffmpeg.input(media_url)


    audio_output_pattern = os.path.join(str(audio_dir), f'{dir_start_time:04d}_{first_time}_%06d.wav')

    if VISUAL_MODERATION_TYPE =="video":
        image_output_pattern = os.path.join(str(img_dir), f'{dir_start_time:04d}_{first_time}_%06d.mp4')
    else:
        image_output_pattern = os.path.join(str(img_dir), f'{dir_start_time:04d}_{first_time}_%06d.jpg')

    media_type=get_file_type(media_url)
    logger.info(f"media_type:{media_type}")

    if media_type == 'audio':

        logger.info("audio moderation")
        output_stream = ffmpeg_tool.output_audio(stream, audio_output_pattern, audio_segment_duration)

    else:
        logger.info("video moderation")

        audio_output = ffmpeg_tool.output_audio(stream, audio_output_pattern, audio_segment_duration)

        if VISUAL_MODERATION_TYPE == "video":
            image_output = ffmpeg_tool.output_silent_video(stream, image_output_pattern, snapshot_interval)
        else:
            image_output = ffmpeg_tool.output_img(stream, image_output_pattern, snapshot_interval)

        # Merge two output streams
        output_stream = ffmpeg.merge_outputs(audio_output, image_output)

    process = None
    try:
        # Run FFmpeg command
        process = ffmpeg.run_async(output_stream, pipe_stdout=True, pipe_stderr=True)

        # Print FFmpeg output in real-time
        while True:
            output = process.stderr.readline().decode('utf-8', errors='replace')
            if output == '' and process.poll() is not None:
                break
            if output:
                logger.info(output.strip())

        # Wait for the process to complete
        process.wait()

        if process.returncode != 0:
            # 0 is success
            # 8: Input stream issue / network issue / input-output permission issue
            logger.info(f"FFmpeg process exited with code {process.returncode}")
            return False
    except ffmpeg.Error as e:
        logger.info(f"FFmpeg error occurred: {e.stderr.decode('utf-8')}")
        return False
    except Exception as e:
        logger.info(f"An error occurred: {e}")
        return False
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait()

    logger.info("Capture completed.")

    time.sleep(2) # nosemgrep

    return True



if __name__ == '__main__':
    # print(get_file_type("/Users/tedli/workspace/defaultWorkSpace/nova_test/93.mp4"))

    # split_video("task_id", "/Users/tedli/workspace/defaultWorkSpace/nova_test/93.mp4", 0, audio_segment_duration=10, snapshot_interval=10, first_time=0)
    pass