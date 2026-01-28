from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.task.status import (
    CreatedStatus,
    CompletedStatus,
    FailedStatus,
    CancelledStatus,
    QueuedStatus,
    UninitializedStatus
)

from src.infrastructure.persistence.technology.sql import BaseSQLModel, VersionMixin


class TaskModel(VersionMixin, BaseSQLModel):
    __tablename__ = "task"

    id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    image_id: Mapped[str]

    status: Mapped["TaskStatusModel"] = relationship(
        back_populates="task", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, image_id={self.image_id!r})"
    

class TaskStatusModel(BaseSQLModel):
    __tablename__ = "task_status"

    task_id: Mapped[str] = mapped_column(
        ForeignKey("task.id"), primary_key=True
    )
    type: Mapped[str]

    task: Mapped[TaskModel] = relationship(back_populates="status", single_parent=True)

    __mapper_args__ = {
        # "polymorphic_identity": "status",
        "polymorphic_on": "type"
    }

    def __repr__(self) -> str:
        return f"TaskStatus(task_id={self.task_id!r}, type={self.type!r})"


class CompletedStatusModel(TaskStatusModel):
    __tablename__ = "task_completed_data"

    id: Mapped[str] = mapped_column(
        ForeignKey("task_status.task_id"), primary_key=True
    )
    text: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": CompletedStatus.type,
    }
    
    def __repr__(self) -> str:
        return f"CompletedTaskStatus(id={self.task_id!r}, text={self.text!r})"


class FailedStatusModel(TaskStatusModel):
    __tablename__ = "task_failed_data"

    id: Mapped[str] = mapped_column(
        ForeignKey("task_status.task_id"), primary_key=True
    )
    # error_code: Mapped[FailedStatus.ErrorCode] = FailedStatus.ErrorCode
    error_text: Mapped[Optional[str]]

    __mapper_args__ = {
        "polymorphic_identity": FailedStatus.type,
    }

# Status models below use single table inheritence in order to not create
# new tables in DB but still store the status in discriminator column
#
# If the status now requires to have data assosiated to it, add a __tablename__
# and foreign key to TaskStatusModel to switch to joined table inheritence
# Docs: https://docs.sqlalchemy.org/en/20/orm/inheritance.html

class UninitializedStatusModel(TaskStatusModel):
    __mapper_args__ = {
        "polymorphic_identity": UninitializedStatus.type
    }


class CreatedStatusModel(TaskStatusModel):
    __mapper_args__ = {
        "polymorphic_identity": CreatedStatus.type
    }


class QueuedStatusModel(TaskStatusModel):
    __mapper_args__ = {
        "polymorphic_identity": QueuedStatus.type
    }


class CancelledStatusModel(TaskStatusModel):
    __mapper_args__ = {
        "polymorphic_identity": CancelledStatus.type
    }
