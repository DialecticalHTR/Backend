from taskiq import AckableMessage
from taskiq.receiver.receiver import Receiver


class RaisingReceiver(Receiver):
    """
    `raise_err` controls whenever the exception is raised when saving the result or `after_save` 
    middleware callback fails, in that case the message won't be acked after the save.
    
    :class:`ResultNotifierMiddleware` sends :class:`RecognitionCompleted` intergration event
    on `after_save` so we want to not ack the message to not lose the recognition result.
    """

    async def callback(self, message: bytes | AckableMessage, raise_err: bool = False) -> None:
        return await super().callback(message, raise_err=True)
