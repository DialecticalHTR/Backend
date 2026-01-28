import logging
import traceback
from typing import AsyncIterable

from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

from src.application.transaction import Transaction

from .base import BaseSQLModel
from .settings import SQLSettings
from .transaction import AlchemyTransaction


logger = logging.getLogger(__name__)


class SQLAlchemyProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_settings(self) -> SQLSettings:
        return SQLSettings() # type: ignore

    @provide(scope=Scope.APP)
    async def provide_engine(self, settings: SQLSettings) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(
            url=settings.connection_url, 
            pool_pre_ping=True,
        )

        # FIXME: don't do this, use migrations
        # async with engine.begin() as conn:
        #     await conn.run_sync(BaseSQLModel.metadata.create_all)

        yield engine

        await engine.dispose()

    @provide(scope=Scope.REQUEST)
    async def provide_session(self, engine: AsyncEngine) -> AsyncIterable[AsyncSession]:
        # Making sure to handle any session exceptions
        # Source: https://github.com/reagento/dishka/issues/503
        try:
            async with AsyncSession(engine, expire_on_commit=False) as session:
                yield session
        except Exception as e:
            logger.error("Caught exception in AsyncSession provider", exc_info=e)

    transaction = provide(
        provides=Transaction,
        source=AlchemyTransaction,
        scope=Scope.REQUEST
    )
