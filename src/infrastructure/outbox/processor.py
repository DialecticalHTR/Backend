import asyncio
import datetime
import logging

from dishka import AsyncContainer, Scope

from src.application.transaction import Transaction
from src.infrastructure.outbox.router import OutboxEventRouter

from .outbox import Outbox


logger = logging.getLogger(__name__)


class OutboxProcessor:
    def __init__(
        self,
        router: OutboxEventRouter,
        container: AsyncContainer
    ) -> None:
        self.router = router
        self.container = container

        self.task: asyncio.Task | None = None
        
    async def startup(self) -> None:
        if self.task is not None:
            self.task.cancel()

        self.task = asyncio.create_task(
            self._process_task()
        )
    
    async def shutdown(self) -> None:
        if self.task is not None:
            task = self.task
            self.task = None
            
            task.cancel()
            await task

    async def process(self) -> None:
        async with self.container(scope=Scope.REQUEST) as container:
            outbox = await container.get(Outbox)
            transaction = await container.get(Transaction)

            try:
                items = await outbox.get_batch(1000)

                item_count = 0
                for item in items:
                    await self.router.send(item.event)
                    await item.mark_as_processed()

                    item_count += 1

                await transaction.commit()
                
                if item_count > 0:
                    logger.debug(f"Processed {item_count} events at {datetime.datetime.now()}")
            except Exception as e:
                await transaction.rollback()
                logger.exception(
                    f"Failed to process outbox at {datetime.datetime.now()}",
                    exc_info=e
                )

    async def _process_task(self) -> None:
        # TODO: handle cancellation
        while True:
            await self.process()
            await asyncio.sleep(1.0)
