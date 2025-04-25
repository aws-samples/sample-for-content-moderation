import base64
import os

from log_config import get_logger
logger = get_logger(__name__)

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_encoded = base64.b64encode(image_data).decode('utf-8')
            return base64_encoded
    except IOError:
        logger.info(f"Error: Unable to read the file. {image_path}")
        return None
    except Exception as e:
        logger.info(f"Error: {e}")
        return None

def encode_images(image_paths):
    encoded_images = []
    for image_path in image_paths:
        with open(image_path, "rb") as image_file:
            encoded_images.append(
                (os.path.splitext(image_path)[1][1:], base64.b64encode(image_file.read()).decode('utf-8')))
    return encoded_images