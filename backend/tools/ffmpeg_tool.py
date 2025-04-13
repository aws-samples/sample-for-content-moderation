import ffmpeg
from tools.log_config import get_logger
logger = get_logger(__name__)

def output_video(stream, output_pattern, segment_duration):
    video_output = ffmpeg.output(stream, output_pattern,
                                 c='copy',
                                 f='segment',
                                 segment_time=segment_duration,
                                 start_number=999,
                                 reset_timestamps=1
                                 )
    return video_output

def output_silent_video(stream, output_pattern, segment_duration):
    print(output_pattern,segment_duration)
    video_output = ffmpeg.output(stream.video, output_pattern,
                                 c='copy',
                                 f='segment',
                                 segment_time=segment_duration,
                                 reset_timestamps=1
                                 )
    return video_output

def output_audio(stream, output_pattern, segment_duration):
    audio_output = ffmpeg.output(stream['a:0'], output_pattern,
                                 acodec='pcm_s16le',
                                 ar=16000,
                                 ac=1,
                                 f='segment',
                                 segment_time=segment_duration,
                                 reset_timestamps=1,
                                 )
    return audio_output


def output_img(stream, image_output_pattern, segment_duration=1):
    image_output = ffmpeg.output(stream['v'], image_output_pattern,
                                 vf=f'fps=1/{segment_duration}',
                                 start_number=0,
    )
    return image_output




def is_black_audio(input_file):
    #Temporarily return non-empty
    # TODO
    return False



def is_black_image(image_path):
    '''
    Check if the image is empty.
    :param image_path: Path to the image.
    :return: True if the image is empty.
    '''

    try:
        params = {
            'vf': 'blackdetect=d=0:pix_th=0.00',
            'f': 'null'
        }

        process = (
            ffmpeg
            .input(image_path)
            .output('-', **params)
            .global_args('-loglevel', 'info')
            .run_async(pipe_stderr=True)
        )

        out, err = process.communicate()

        return 'black_duration' in err.decode()

    except ffmpeg.Error as e:
        logger.info(f"An error occurred: {e.stderr.decode()}")
        return False
