import abc
import uuid

from .entity import Task


class TaskRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, task_id: uuid.UUID) -> Task:
        pass

    @abc.abstractmethod
    async def insert(self, task: Task):
        pass

    @abc.abstractmethod
    async def update(self, task: Task):
        pass

    @abc.abstractmethod
    async def delete_by_id(self, task_id: uuid.UUID):
        pass
