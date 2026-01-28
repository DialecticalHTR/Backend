import uuid
from typing import Annotated

import magic
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import File, WebSocket
from fastapi.routing import APIRouter
from fastapi.responses import Response
from events.integration.topology import IntegrationEventBusRegistration
from events.integration.topology.consumer import EventHandlerConsumer

from src.domain.task.repository import Task
from src.application.bus import FanoutIntegrationEventBus
from src.application.interactor.factory import InteractorFactory
from src.application.task.events import TaskStatusUpdatedV1
from src.application.task.interactors import (
    GetTaskInteractor, 
    SubmitTaskInteractor, 
    CancelTaskInteractor, 
    UpdateTaskTextInteractor,
    GetTaskImageInteractor,
)
from src.infrastructure.messaging.utils import get_event_topic

from ..dto.task import TaskDTO, TaskSubscriptionDTO, TaskMapper


router = APIRouter(prefix="/task")


@router.get("/")
@inject
async def get_task(
    task_id: uuid.UUID,
    interactor: FromDishka[GetTaskInteractor]
) -> TaskDTO:
    task = await interactor(task_id)
    return TaskMapper.from_domain(task)


@router.post("/submit")
@inject
async def submit_task(
    image: Annotated[bytes, File()],
    interactor: FromDishka[SubmitTaskInteractor]
) -> TaskDTO:
    task = await interactor(image_data=image)
    return TaskMapper.from_domain(task)


@router.post("/cancel")
@inject
async def cancel_task(
    task_id: uuid.UUID,
    interactor: FromDishka[CancelTaskInteractor]
) -> TaskDTO:
    task = await interactor(task_id=task_id)
    return TaskMapper.from_domain(task)


@router.put("/update_text")
@inject
async def update_task_text(
    task_id: uuid.UUID,
    new_text: str,
    interactor: FromDishka[UpdateTaskTextInteractor]
) -> TaskDTO:
    task = await interactor(task_id, new_text)
    return TaskMapper.from_domain(task)


@router.websocket("/status")
@inject
async def listen_for_status_updates(
    socket: WebSocket,
    get_task_factory: FromDishka[InteractorFactory[GetTaskInteractor]],
    fanout_bus: FromDishka[FanoutIntegrationEventBus]
):
    ids: set[uuid.UUID] = set()

    async def get_task(task_id: uuid.UUID) -> Task:
        async with get_task_factory as interactor:
            return await interactor(task_id)

    async def get_dto(task_id: uuid.UUID) -> TaskDTO:
        task = await get_task(task_id)
        dto = TaskMapper.from_domain(task)
        return dto

    async def process_status_update(
        event: TaskStatusUpdatedV1
    ):
        received_id = uuid.UUID(event.task_id)
        if received_id not in ids:
            return
        
        dto = await get_dto(received_id)
        await socket.send_text(
            dto.model_dump_json()
        )

    try:
        await socket.accept()

        consumer = EventHandlerConsumer(
            name="",
            handlers={
                TaskStatusUpdatedV1: [process_status_update,]
            }
        )

        await fanout_bus.register(
            IntegrationEventBusRegistration(
                consumer=consumer,
                topic=get_event_topic(TaskStatusUpdatedV1),
                events=[TaskStatusUpdatedV1]
            )
        )

        while True:
            data = await socket.receive_json()
            subscription = TaskSubscriptionDTO.model_validate(data)
            ids.add(subscription.id)

            # Notify of the current status
            dto = await get_dto(subscription.id)
            await socket.send_text(
                dto.model_dump_json()
            )
    finally:
        pass


@router.get("/image")
@inject
async def get_task_image(
    task_id: uuid.UUID,
    get_task_image_interactor: FromDishka[GetTaskImageInteractor]
):
    image = await get_task_image_interactor(task_id)
    mime_type = magic.from_buffer(image.data, mime=True)

    return Response(content=image.data, media_type=mime_type)
