import enum
import typing


class TaskStatus:
    type: str

    def is_type(self, status_type: typing.Type["TaskStatus"]) -> bool:
        return self.type == status_type.type


class UninitializedStatus(TaskStatus):
    type: str = "uninitialized"


class CreatedStatus(TaskStatus):
    type: str = "created"


class QueuedStatus(TaskStatus):
    type: str = "queued"


class CancelledStatus(TaskStatus):
    type: str = "cancelled"


class CompletedStatus(TaskStatus):
    type: str = "completed"

    def __init__(self, recognized_text: str):
        self.recognized_text = recognized_text
    

class FailedStatus(TaskStatus):
    type: str = "failed"
    
    class ErrorCode(int, enum.Enum):
        Unknown = 0
    
    def __init__(
        self, 
        # error_code: ErrorCode, 
        error_text: typing.Optional[str] = None
    ):
        # TODO: Implement error codes instead of error messages for better client localization
        # self.error_code = error_code
        self.error_text = error_text


__all__ = [
    "TaskStatus",
    "UninitializedStatus",
    "CreatedStatus",
    "QueuedStatus",
    "CancelledStatus",
    "CompletedStatus",
    "FailedStatus"
]