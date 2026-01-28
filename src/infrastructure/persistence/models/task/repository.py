from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.task import TaskRepository
from src.domain.task.entity import Task
from src.application.exceptions import StaleDataException

from src.infrastructure.persistence.technology.sql import VersionCache 

from .model import TaskModel
from .mapper import TaskMapper, TaskStatusMapper


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession):
        self.session = session    

    async def insert(self, task: Task):
        model = await TaskMapper.from_domain(task)
        self.session.add(model)

    async def update(self, task: Task):
        # Get cached model from identity map and compare it to the current state in DB
        # Raise if the versions of the models have changed
        old_version = VersionCache.get_version(self.session.sync_session, TaskModel, str(task.id))
        if old_version is None:
            raise Exception(f"Couldn't find a record with id {task.id!r} for TaskModel in version cache. \
                            Get an instance from ORM before updating it.")

        model = await self.session.get(
            TaskModel, ident=str(task.id),
            with_for_update=True,
            populate_existing=True,
        )
        if model is None:
            raise Exception(f"Task with id {task.id!r} is not found")
        
        if old_version != model.update_version:
            raise StaleDataException(
                f"Attempted to update stale Task with id {task.id!r} \
                (old version={old_version}, new version={model.update_version})"
            )
        
        # Deleting status and flushing forbids SQLAlchemy to combine DELETE+INSERT into UPDATE
        # This causes issues when statuses are of different types
        # https://github.com/sqlalchemy/sqlalchemy/discussions/12939?#discussioncomment-14775381
        await self.session.delete(await model.awaitable_attrs.status)
        await self.session.flush()
        
        model.status = await TaskStatusMapper.from_domain(task.status)
        model.image_id = str(task.image_id)

        # TODO: Won't update automatically if only related objects changed
        model.update_version += 1  

        await self.session.flush()

    async def delete_by_id(self, task_id: UUID):
        model = await self.session.get(TaskModel, str(task_id))
        await self.session.delete(model)

    async def get_by_id(self, task_id: UUID) -> Task:
        model = await self.session.get(TaskModel, str(task_id))
        if model is None:
            raise Exception(f"Task with id {task_id!r} not found")
        
        return await TaskMapper.to_domain(model)
