from contextlib import contextmanager
from typing import Iterator

import pymysql
from pymysql.cursors import DictCursor

from app.config.settings import get_settings


@contextmanager
def get_connection() -> Iterator[pymysql.connections.Connection]:
    settings = get_settings()
    connection = pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        cursorclass=DictCursor,
        autocommit=False,
        ssl={} if settings.db_ssl else None,
    )
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
