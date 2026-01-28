import json
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from events.integration.event import IntegrationEvent

from src.infrastructure.outbox import Outbox
from src.infrastructure.outbox.outbox import OutboxItem
from src.infrastructure.persistence.models.outbox import OutboxEventModel


class SQLOutboxItem(OutboxItem):
    def __init__(
        self,
        session: AsyncSession,
        model: OutboxEventModel, 
        event: IntegrationEvent
    ) -> None:
        super().__init__(event)

        self.model = model
        self.session = session

    async def mark_as_processed(self) -> None:
        await self.session.delete(self.model)


class SQLOutbox(Outbox):
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    async def put(self, event: IntegrationEvent) -> None:
        data = event.to_dict()
        payload = json.dumps(data)

        self.session.add(OutboxEventModel(payload=payload))

    async def get_batch(self, batch_size: int = 500) -> Iterable[OutboxItem]:
        models = (await self.session.execute(
            select(OutboxEventModel)
                .with_for_update(skip_locked=True)
                .order_by(OutboxEventModel.sent_at)
                .limit(batch_size)
        )).scalars().all()

        return [
            SQLOutboxItem(
                self.session,
                model,
                IntegrationEvent.from_dict(
                    json.loads(model.payload)
                )
            )
            for model in models
        ]
