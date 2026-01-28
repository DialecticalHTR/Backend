from dishka import Provider, Scope, provide

from src.domain.task import TaskRepository

from .repository import SQLAlchemyTaskRepository


class TaskProvider(Provider):
    task_repo = provide(
        provides=TaskRepository,
        source=SQLAlchemyTaskRepository,
        scope=Scope.REQUEST
    )
