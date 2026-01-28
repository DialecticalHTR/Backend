from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.technology.sql.base import BaseSQLModel


class OutboxEventModel(BaseSQLModel):
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    sent_at: Mapped[datetime] = mapped_column(default=datetime.now)
    payload: Mapped[str]
