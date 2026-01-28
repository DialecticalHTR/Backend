import uuid

from dishka import Provider, Scope, provide_all

from src.domain.task import TaskRepository
from src.domain.image import ImageRepository
from src.domain.recognizer import Recognizer


class TextRecognitionInteractor:
    def __init__(
        self,
        task_repository: TaskRepository,
        image_repository: ImageRepository,
        recognizer: Recognizer
    ):
        self.task_repository = task_repository
        self.image_repository = image_repository
        self.recognizer = recognizer
    
    async def __call__(self, task_id: uuid.UUID) -> str:
        task = await self.task_repository.get_by_id(task_id)
        if not task.can_be_completed():
            raise Exception("Task can't be completed")
        
        image = await self.image_repository.get_by_id(task.image_id)
        result = await self.recognizer.recognize(image)

        return result


class RecognitionInteractorsProvider(Provider):
    scope = Scope.REQUEST

    interactors = provide_all(
        TextRecognitionInteractor
    )
