import logging
import uuid

from dishka import Provider, Scope, provide_all
from events.domain.dispatcher import DomainEventDispatcher

# from src.framework.domain import DomainEventDispatcher
from src.domain.task import Task, TaskRepository, UninitializedStatus
from src.domain.image import Image, ImageRepository

from src.application.transaction import Transaction
from src.application.interactor.base import BaseInteractor
from src.application.recognition.gateway import RecognitionGateway


logger = logging.getLogger(__name__)


class SubmitTaskInteractor(BaseInteractor):
    def __init__(
        self,
        transaction: Transaction,
        event_dispatcher: DomainEventDispatcher,
        task_repository: TaskRepository,
        image_repository: ImageRepository
    ) -> None:
        self.transaction = transaction
        self.event_dispatcher = event_dispatcher
        self.task_repository = task_repository
        self.image_repository = image_repository

    async def __call__(self, image_data: bytes) -> Task:
        image = Image(uuid.uuid4(), image_data)
        await self.image_repository.update(image)
        
        self.event_dispatcher.from_entity(image)
        await self.event_dispatcher.process()
            
        try:
            task = Task(uuid.uuid4(), image.id, UninitializedStatus())
            task.initialize()
            await self.task_repository.insert(task)
            
            self.event_dispatcher.from_entity(task)
            await self.event_dispatcher.process()

            await self.transaction.commit()

            return task
        except Exception as e:
            await self.image_repository.delete_by_id(image.id)
            await self.transaction.rollback()

            logger.error("Failed to create new task", exc_info=e)
            raise


class CancelTaskInteractor(BaseInteractor):
    def __init__(
        self,
        transaction: Transaction,
        task_repository: TaskRepository,
        event_dispatcher: DomainEventDispatcher,
    ) -> None:
        self.transaction = transaction
        self.task_repository = task_repository
        self.event_dispatcher = event_dispatcher
    
    async def __call__(self, task_id: uuid.UUID) -> Task:
        try:
            task = await self.task_repository.get_by_id(task_id)
            task.cancel()
            await self.task_repository.update(task)

            self.event_dispatcher.from_entity(task)
            await self.event_dispatcher.process()

            await self.transaction.commit()
            return task
        except Exception as e:
            await self.transaction.rollback()

            logger.error(f"Failed to cancel task with id {task_id}", exc_info=e)
            raise


class CompleteTaskInteractor(BaseInteractor):
    def __init__( 
        self,
        transaction: Transaction,
        task_repository: TaskRepository,
        gateway: RecognitionGateway,
        event_dispatcher: DomainEventDispatcher
    ):
        self.transaction = transaction
        self.task_repository = task_repository
        self.gateway = gateway
        self.event_dispatcher = event_dispatcher
    
    async def __call__(self, task_id: uuid.UUID):
        try:
            task = await self.task_repository.get_by_id(task_id)
            
            text: str
            try:
                text = await self.gateway.get_task_result(str(task.id))
            except Exception as e:
                task.fail(error_text=str(e))
            else:
                task.complete(text=text)
            await self.task_repository.update(task)

            self.event_dispatcher.from_entity(task)
            await self.event_dispatcher.process()

            await self.transaction.commit()
        except Exception as e:
            logger.exception(
                "Error happened in CompleteTaskInteractor",
                exc_info=e
            )
            await self.transaction.rollback()
            raise


class GetTaskInteractor(BaseInteractor):
    def __init__( 
        self,
        task_repository: TaskRepository,
    ):
        self.task_repository = task_repository
    
    async def __call__(self, task_id: uuid.UUID):
        task = await self.task_repository.get_by_id(task_id)
        return task


class UpdateTaskTextInteractor(BaseInteractor):
    def __init__(
        self,
        task_repository: TaskRepository,
        event_dispatcher: DomainEventDispatcher,
        transaction: Transaction
    ) -> None:
        self.task_repository = task_repository
        self.event_dispatcher = event_dispatcher
        self.transaction = transaction

    async def __call__(self, task_id: uuid.UUID, new_text: str) -> Task:
        task = await self.task_repository.get_by_id(task_id)
        task.update_text(new_text)
        await self.task_repository.update(task)

        self.event_dispatcher.from_entity(task)
        await self.event_dispatcher.process()

        await self.transaction.commit()
        return task


class GetTaskImageInteractor(BaseInteractor):
    def __init__(
        self,
        task_repository: TaskRepository,
        image_repository: ImageRepository
    ) -> None:
        self.task_repository = task_repository
        self.image_repository = image_repository
    
    async def __call__(self, task_id: uuid.UUID) -> Image:
        task = await self.task_repository.get_by_id(task_id)
        image = await self.image_repository.get_by_id(task.image_id)

        return image
    

class TaskInteractorsProvider(Provider):
    scope = Scope.REQUEST

    interactors = provide_all(
        GetTaskInteractor,
        GetTaskImageInteractor,
        CancelTaskInteractor,
        SubmitTaskInteractor,
        CompleteTaskInteractor,
        UpdateTaskTextInteractor
    )
