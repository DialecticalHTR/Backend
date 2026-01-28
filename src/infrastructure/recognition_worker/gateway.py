import uuid

from src.application.recognition.gateway import RecognitionGateway

from .broker import result_backend, cancellation_backend
from .tasks import recognize


class TaskiqRecognitionGateway(RecognitionGateway):
    def __init__(self) -> None:
        super().__init__()

    async def submit_task(self, task_id: str):
        # Task only needs the id, the other parameters are dependency injected
        await recognize.kicker().with_task_id(task_id).kiq(uuid.UUID(task_id)) # type: ignore

    async def cancel_task(self, task_id: str):
        await cancellation_backend.cancel(task_id)

    async def get_task_result(self, task_id: str) -> str:
        result = await result_backend.get_result(task_id)
        if result.is_err is not None:
            return str(result.return_value)
        else:
            raise result.error
