from typing import Type, Any

from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.orm.util import identity_key as sql_identity_key


VersionMap = dict[object, int]


def _increment_version(context):
    current_version = context.get_current_parameters()["update_version"]
    return current_version + 1


class VersionMixin(object):    
    update_version: Mapped[int] = mapped_column(
        default=1, server_default='1', onupdate=_increment_version
    )

    @classmethod
    def __declare_first__(cls):
        @event.listens_for(cls, "load")
        def _load(instance, ctx):
            VersionCache._save_version(ctx.session, instance)


class VersionCache:
    session_map: dict[Session, VersionMap] = {}

    def __init__(self) -> None:
        raise Exception("VersionCache can't instantiated")
    
    @classmethod
    def get_version(
        cls, session: Session, 
        model_type: Type[VersionMixin], identity_key: Any, *,
        identity_token: Any = None
    ) -> int | None:
        if session not in cls.session_map:
            return None
        
        identity = sql_identity_key(model_type, identity_key, identity_token=identity_token)
        return cls.session_map[session].get(identity, None)

    @classmethod
    def _save_version(cls, session: Session, instance: VersionMixin):
        if session not in cls.session_map:
            cls.session_map[session] = {}
        version_map = cls.session_map[session]
        
        ident = sql_identity_key(instance=instance)
        version_map[ident] = instance.update_version
        
    @classmethod
    def _clear_session(cls, session: Session):
        if session in cls.session_map:
            cls.session_map[session].clear()


@event.listens_for(Session, "after_attach")
def _after_attach(session: Session, instance):
    if isinstance(instance, VersionMixin):
        VersionCache._save_version(session, instance)


@event.listens_for(Session, "after_commit")
def _after_commit(session: Session):
    VersionCache._clear_session(session)
