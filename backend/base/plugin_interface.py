from abc import ABC, abstractmethod


class SpeechRecognizer(ABC):

    @abstractmethod
    def recognize(self, audio_path: str) -> str:
        pass


class TextModeration(ABC):
    @abstractmethod
    def moderate(self,  prompt: str,content: str) -> any:
        pass

class ImageModeration(ABC):

    @abstractmethod
    def moderate_video(self, image_path: str) -> dict:
        pass

    @abstractmethod
    def moderate_image(self, image_path: str) -> dict:
        pass

    @abstractmethod
    def moderate_images(self, image_path_arr: list[str]) -> list[str]:
        pass

    # @abstractmethod
    # def face_match(self, current_image_path: str, target_image_path: str) -> str:
    #     pass