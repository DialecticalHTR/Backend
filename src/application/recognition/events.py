import uuid
from dataclasses import dataclass

from events.integration.event import IntegrationEvent


@dataclass
class RecognitionFinishedV1(IntegrationEvent):
    type = "recognition.finished"
    version = 1
    
    task_id: str

    def __repr__(self) -> str:
        return f"RecognitionFinishedEvent({self.task_id!s})"


@dataclass
class RecognitionCompletedV1(IntegrationEvent):
    type = "recognition.task_completed"
    version = 1
    
    task_id: str
