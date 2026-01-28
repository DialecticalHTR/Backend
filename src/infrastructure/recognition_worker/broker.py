from taskiq import SimpleRetryMiddleware
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from taskiq_cancellation import ModularCancellationBackend, TaskCancellationException
from taskiq_cancellation.notifiers.redis import PubSubCancellationNotifier
from taskiq_cancellation.state_holders.redis import RedisCancellationStateHolder

from .settings import RecognitionTaskSettings
from .deduplication import (
    RedisDeduplicationBackend, DeduplicationMiddleware, TaskiqDuplicateException
)
from .notifier_middleware import ResultNotifierMiddleware
from .no_retry_middleware import NoRetryMiddleware

settings = RecognitionTaskSettings() # type: ignore

result_backend = RedisAsyncResultBackend(
    redis_url=settings.result_backend_url
)
cancellation_backend = ModularCancellationBackend(
    RedisCancellationStateHolder(url=settings.cancellation_state_holder_url),
    PubSubCancellationNotifier(url=settings.cancellation_notifier_url)
)
deduplication_backend = RedisDeduplicationBackend(url=settings.deduplication_backend_url)

broker = AioPikaBroker(
    url=settings.broker_url,
    exchange_name="taskiq_recognition_tasks",
    queue_name="taskiq_recognition_tasks"
).with_result_backend(
    result_backend
).with_middlewares(
    DeduplicationMiddleware(deduplication_backend),
    NoRetryMiddleware(
        ignored_exceptions=(TaskiqDuplicateException, TaskCancellationException,)
    ),
    SimpleRetryMiddleware(
        default_retry_count=3,
        default_retry_label=True
    ),
    ResultNotifierMiddleware()
)
