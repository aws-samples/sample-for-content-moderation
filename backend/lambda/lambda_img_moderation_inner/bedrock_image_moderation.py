import os
from config import IMG_PROMPT_0325_CN, SYSTEM_0325_NOVA_VIDEO_CN, VIDEO_PROMPT_0325_CN, IMG_NOVA_SYSTEM_PROMPT_1_EN, \
    IMG_CLAUDE_SYSTEM_PROMPT
from bedrock_img_tool import invoke_claude, batch_invoke_nova, batch_invoke_claude
from bedrock_img_tool import invoke_nova
from log_config import get_logger
logger = get_logger(__name__)





class BedrockImageModeration:

    def moderate_video(self,img_model_id:str, image_path: str) -> dict:
        #Only supports Nova
        if "nova" in img_model_id:
            return invoke_nova(img_model_id, SYSTEM_0325_NOVA_VIDEO_CN,VIDEO_PROMPT_0325_CN, image_path,True)
        else:
            return {}

    def moderate_images(self, img_model_id,image_path_arr: list[str]) -> list[str]:

        return check_images(img_model_id,image_path_arr)

    def moderate_image(self, img_model_id:str,image_path: str) -> dict:
        if "nova" in img_model_id:
            return invoke_nova(img_model_id,IMG_NOVA_SYSTEM_PROMPT_1_EN, IMG_PROMPT_0325_CN, image_path,True)
        elif "claude" in img_model_id:
            return invoke_claude(img_model_id,IMG_CLAUDE_SYSTEM_PROMPT, IMG_PROMPT_0325_CN, image_path)
        else:
            return {}


    # def face_match(self, current_image_path: str, target_image_path) -> str:
    #     return "None"



def check_images(img_model_id,image_path_arr: list[str]) -> list[any]:
    '''
    :param images_dir_path:
    :return: False indicates that an issue was detected."
    '''

    moderation_img_arr=[]
    for file_path in image_path_arr:

        if not os.path.exists(file_path):
            logger.error(f"The image file does not exist: {file_path}")
            continue

        moderation_img_arr.append(str(file_path))

    result_arr=[]
    if "nova" in img_model_id:
        result_llm=batch_invoke_nova(img_model_id, IMG_NOVA_SYSTEM_PROMPT_1_EN,IMG_PROMPT_0325_CN, moderation_img_arr, True)

    elif "claude" in img_model_id:
        result_llm=batch_invoke_claude(img_model_id, IMG_CLAUDE_SYSTEM_PROMPT,IMG_PROMPT_0325_CN, moderation_img_arr)
    else:
        result_llm=[]
    for moderation_result in result_llm:
        if len(moderation_result['tag']) > 0:
            result_arr.append(moderation_result)

    return result_arr


if __name__ == "__main__":

    # images_dir_path = "../resources22/s"
    # logger.info(check_images(images_dir_path))
    # moderation_img_arr=["img.png"]

    # logger.info(batch_invoke_nova(IMG_MODEL_ID, SYSTEM_0325_NOVA_IMG_CN,IMG_PROMPT_0325_CN, moderation_img_arr, True))

    # 0000_1743234337_000006.mp4
    # 0000_1743234337_000007.mp4

    # IMG_MODEL_ID="us.amazon.nova-lite-v1:0"
    # IMG_MODEL_ID="us.amazon.nova-pro-v1:0"
    # print(invoke_nova(IMG_MODEL_ID, SYSTEM_0325_NOVA_VIDEO_CN, VIDEO_PROMPT_0325_CN,
    #                   "xxx.mp4", True))

    # IMG_MODEL_ID="us.anthropic.claude-3-5-sonnet-20240620-v1:0"
    # logger.info(batch_invoke_claude(IMG_MODEL_ID, SYSTEM_0325_CLAUDE_CN,IMG_PROMPT_0325_CN, moderation_img_arr, True))
    # result=moderate_img(img_arr,IMG_PROMPT)
    # logger.info(result)

    # image_path = 'images/frame_0032.png'
    # check_image(image_path)

    pass





