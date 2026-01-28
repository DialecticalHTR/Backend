import abc
from typing import Protocol


class RecognitionGateway(Protocol):
    @abc.abstractmethod
    async def submit_task(self, task_id: str):
        pass
    
    @abc.abstractmethod
    async def cancel_task(self, task_id: str):
        pass

    @abc.abstractmethod
    async def get_task_result(self, task_id: str) -> str:
        pass
