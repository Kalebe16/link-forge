import os
from contextlib import asynccontextmanager

from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DBManager(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.db_url = os.environ['DATABASE_URL']

        self.engine = create_async_engine(self.db_url, echo=False)
        self.SessionMaker = async_sessionmaker(
            bind=self.engine, autoflush=True, expire_on_commit=False
        )

        if 'sqlite' in self.db_url:

            @event.listens_for(self.engine, 'connect')
            def _set_sqlite_pragmas(dbapi_connection, connection_record):
                """
                Applies SQLite-specific PRAGMA settings (foreign_keys=ON).
                This only has effect when using a SQLite database.
                """
                cursor = dbapi_connection.cursor()
                cursor.execute('PRAGMA foreign_keys=ON')
                cursor.close()

    @asynccontextmanager
    async def session_scope(self):
        session = self.SessionMaker()

        try:
            yield session
            await session.commit()

        except Exception:
            await session.rollback()
            raise

        finally:
            await session.close()
