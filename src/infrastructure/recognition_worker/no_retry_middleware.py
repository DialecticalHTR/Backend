from typing import Iterable

from taskiq import TaskiqMessage, TaskiqMiddleware, TaskiqResult


class NoRetryMiddleware(TaskiqMiddleware):
    """
    NoRetryMiddleware sets `retry_on_error` label to not retry the task if the exception 
    is in `ignored_exceptions`
    """
    
    def __init__(self, ignored_exceptions: Iterable[type[BaseException]] = []):
        self.ignored_exceptions = set(ignored_exceptions)

    async def on_error(
        self,
        message: TaskiqMessage,
        result: TaskiqResult,
        exception: BaseException,
    ):
        if exception in self.ignored_exceptions:
            message.labels["retry_on_error"] = False
    