from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class BaseSQLModel(DeclarativeBase, AsyncAttrs):
    pass
