from __future__ import annotations

from typing import Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def create_session_factory(database_url: str):
    connect_args = {}
    engine_kwargs = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if database_url.endswith(":memory:") or database_url.startswith("sqlite:///:memory"):
            engine_kwargs["poolclass"] = StaticPool

    engine = create_engine(database_url, connect_args=connect_args, **engine_kwargs)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return engine, SessionLocal
