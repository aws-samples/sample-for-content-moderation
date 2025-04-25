import os
from tools.log_config import get_logger
logger = get_logger(__name__)


def process_time_from_video_audio_name(filepath,audio_segment_duration):
    #0000_1744810192_%06d.wav

    start_time=0
    end_time=0

    # Get the file name (with extension)
    file_name = os.path.basename(filepath)

    # Extract the time portion from the file name.
    time_str = file_name.split('.')[0]
    time_info_arr=time_str.split("_")

    # Get the first number
    first_number = int(time_info_arr[0])
    first_timestamp_str = int(time_info_arr[1])

    # Get the last number
    last_number = int(time_info_arr[-1])

    if first_number==0:
        start_time=last_number*audio_segment_duration
        end_time=start_time+audio_segment_duration
    else:
        creation_time = int(os.path.getctime(filepath))
        logger.info(creation_time)
        logger.info(first_timestamp_str)

        time_diff = creation_time-first_timestamp_str

        start_time=time_diff
        end_time=start_time+audio_segment_duration

    return start_time, end_time


def process_time_from_img_name(filepath,segment_time):
    #0000_1744810192_000068.jpg
    return process_time_from_video_audio_name(filepath,segment_time)[0]

