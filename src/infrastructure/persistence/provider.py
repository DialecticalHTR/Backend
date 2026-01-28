from dishka import Provider

from src.infrastructure.persistence.outbox.provider import OutboxProvider
from .technology.s3.provider import S3Provider
from .technology.sql.provider import SQLAlchemyProvider
from .models.image.provider import ImageProvider
from .models.task.provider import TaskProvider


def get_persistence_providers() -> list[Provider]:
    return [
        S3Provider(),
        SQLAlchemyProvider(),
        ImageProvider(),
        TaskProvider(),
        OutboxProvider()
]
