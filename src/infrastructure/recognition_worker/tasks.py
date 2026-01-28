import uuid
from typing import Annotated

from taskiq import Context, TaskiqDepends
from taskiq_cancellation import CancellationType
from dishka.integrations.taskiq import FromDishka, inject

from src.application.exceptions import StaleDataException
from src.application.recognition.interactors import TextRecognitionInteractor

from .broker import broker, cancellation_backend, deduplication_backend


@broker.task
@cancellation_backend.cancellable(CancellationType.EDGE)
@deduplication_backend.task
@inject(patch_module=True)
async def recognize(
    task_id: uuid.UUID,
    interactor: FromDishka[TextRecognitionInteractor],
    context: Annotated[Context, TaskiqDepends()]
) -> str:
    try:
        return await interactor(task_id)
    except StaleDataException:
        # FIXME: update dishka to >1.7.2 after that releases
        await context.message.labels["dishka_container"].close()
        del context.message.labels["dishka_container"]

        await context.requeue()
        raise  # Context.requeue() will throw NoResultError
