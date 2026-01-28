import abc
import inspect
import logging
from typing import Annotated, ParamSpec, TypeVar, Callable, cast

from taskiq import TaskiqMessage, Context, TaskiqMiddleware, TaskiqDepends
from taskiq_cancellation.utils import combines


logger = logging.getLogger(__name__)

Params = ParamSpec("Params")
Result = TypeVar("Result")


class TaskiqDuplicateException(Exception):
    pass


class DeduplicationBackend(abc.ABC):
    @abc.abstractmethod
    async def set_message_id(self, task_id: str, message_id: str):
        pass
        
    @abc.abstractmethod
    async def get_message_id(self, task_id: str) -> str | None:
        pass

    @abc.abstractmethod
    def next_message_id(self) -> str:
        pass

    async def is_duplicate(self, message: TaskiqMessage) -> bool:
        message_id = await self.get_message_id(message.task_id)

        if message_id is None:
            return False
        return message_id != message.labels["message_id"] 
    
    @staticmethod
    def task(func: Callable[Params, Result]) -> Callable[Params, Result]:
        if not inspect.iscoroutinefunction(func):
            raise NotImplementedError("Function needs to be asynchronous")
        
        @combines(func)
        async def wrapper(
            *args,
            dedup_taskiq_context: Annotated[Context, TaskiqDepends()],
            **kwargs
        ) -> Result:
            message = dedup_taskiq_context.message
            
            if message.labels.get("is_duplicate") is True:
                logger.debug("Cancelling a task as a duplicate")
                raise TaskiqDuplicateException()

            return await func(*args, **kwargs)
        
        casted_wrapper = cast(
            Callable[Params, Result], wrapper
        )
        return casted_wrapper


class DeduplicationMiddleware(TaskiqMiddleware):
    """
    Middleware that sets a label when `deduplication_backend` determines the task is a duplicate
    """

    def __init__(self, deduplication_backend: DeduplicationBackend):
        self.dedup_backend = deduplication_backend

    async def pre_send(self, message: TaskiqMessage):
        if "message_id" not in message.labels:
            message.labels["message_id"] = self.dedup_backend.next_message_id()
            
        return message

    async def pre_execute(self, message: TaskiqMessage):
        is_duplicate = await self.dedup_backend.is_duplicate(message)
        message.labels["is_duplicate"] = is_duplicate
        
        if not is_duplicate:        
            await self.dedup_backend.set_message_id(
                message.task_id, message.labels["message_id"]
            )
        return message
