import uuid
import typing

from events.domain.aggregate import AggregateRoot

from .status import (
    TaskStatus,
    CreatedStatus,
    UninitializedStatus,
    QueuedStatus,
    CancelledStatus,
    FailedStatus,
    CompletedStatus,
)
from .event import (
    TaskInitialized,
    TaskCompleted,
    TaskFailed,
    TaskCancelled,
    TaskFinished,
    TaskStatusUpdated
)


class Task(AggregateRoot):
    def __init__(
        self, 
        id: uuid.UUID,
        image_id: uuid.UUID, 
        status: TaskStatus = UninitializedStatus(), 
    ):
        super().__init__()
        
        self.id = id
        self.image_id = image_id
        self._status: TaskStatus = status

    def initialize(self):
        if not self.status.is_type(UninitializedStatus):
            raise Exception("Can't initialize initialized task")
        
        self.status = CreatedStatus()
        self.publish_event(TaskInitialized(self))

    def enqueue(self):
        if self.status.is_type(QueuedStatus) or self._is_finished():
            raise Exception("Can't queue this task")
        
        self.status = QueuedStatus()
    
    def cancel(self):
        if self._is_finished() or self.status.is_type(CancelledStatus):
            raise Exception("Can't cancel finished task")
        
        self.status = CancelledStatus()
        self.publish_event(TaskCancelled(self))
    
    def complete(self, text: str):
        if not self.can_be_completed():
            raise Exception("Can't complete finished task")
        
        self.status = CompletedStatus(recognized_text=text)

        self.publish_event(TaskCompleted(self, text))
        self.publish_event(TaskFinished(self))
    
    def can_be_completed(self):
        return not (self._is_finished() or self.status.is_type(CancelledStatus))
    
    def fail(self, error_text: typing.Optional[str] = None):
        if self._is_finished():
            raise Exception("Can't fail finished task")
        
        self.status = FailedStatus(
            # error_code=error_code, 
            error_text=error_text
        )
        
        self.publish_event(TaskFailed(self, error_text))
        self.publish_event(TaskFinished(self))

    def update_text(self, new_text: str):
        if not isinstance(self.status, CompletedStatus):
            raise Exception("Can't update a non-completed task")
        
        self.status = CompletedStatus(new_text)

    def _is_finished(self):
        return any(self.status.is_type(t) for t in [CompletedStatus, FailedStatus])
    
    def _set_status(self, status: TaskStatus):
        self._status = status
        self.publish_event(TaskStatusUpdated(self, self._status))
    
    def _get_status(self):
        return self._status
    
    status = property(
        fget=_get_status,
        fset=_set_status
    )

