from dependency_injector import containers, providers
from plugin.bedrock_text_moderation import BedrockTextModeration
from plugin.bedrock_image_moderation import BedrockImageModeration
from plugin.rekogition_image_moderation import RekognitionImageModeration
from plugin.sagemaker_asr import SagemakerASR


class AppContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    #ASR
    speech_recognizer = providers.Factory(
        SagemakerASR
    )


    text_moderation = providers.Factory(
        BedrockTextModeration
    )


    image_moderation = providers.Factory(
        RekognitionImageModeration
    )
