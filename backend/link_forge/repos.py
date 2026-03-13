from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC
from enum import StrEnum
from functools import wraps
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, InterfaceError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from link_forge.db import DBManager
from link_forge.entities import Link, User
from link_forge.models import SQLLink, SQLUser


def safe_repo(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except (
            InterfaceError,
            OperationalError,
        ):
            return RepoResp(status=RepoStatus.DB_ERROR)

        except IntegrityError as error:
            error_message = str(error).lower()
            if 'unique' in error_message:
                return RepoResp(status=RepoStatus.DUPLICATED)
            if 'constraint' in error_message:
                return RepoResp(status=RepoStatus.CONSTRAINT)

            return RepoResp(status=RepoStatus.DB_ERROR)

    return wrapper


class RepoStatus(StrEnum):
    OK = 'ok'
    NOT_FOUND = 'not_found'
    DUPLICATED = 'duplicated'
    CONSTRAINT = 'constraint'
    DB_ERROR = 'db_error'


T = TypeVar('T')


@dataclass
class RepoResp(Generic[T]):
    status: RepoStatus = RepoStatus.OK
    data: T | None = None

    @property
    def ok(self) -> bool:
        return self.status == RepoStatus.OK


class SQLRepoBase:
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager

    @asynccontextmanager
    async def _ensure_session(
        self, existing_session: AsyncSession | None
    ) -> AsyncIterator[AsyncSession]:
        if existing_session:
            yield existing_session
        else:
            async with self.db_manager.session_scope() as session:
                yield session

    @property
    def _updatable_sql_fields(self) -> list[str]:
        return []


class UserSQLRepo(SQLRepoBase):
    @property
    def _updatable_sql_fields(self) -> list[str]:
        return [SQLUser.email.key, SQLUser.password_hash.key]

    @safe_repo
    async def get_by_id(
        self, id: str, session: AsyncSession | None = None
    ) -> RepoResp[User | None]:
        async with self._ensure_session(existing_session=session) as session:
            sql_user = await session.get(SQLUser, id)

            if not sql_user:
                return RepoResp(status=RepoStatus.NOT_FOUND)

            user = self._sql_to_user(sql_user=sql_user)
            return RepoResp(data=user)

    @safe_repo
    async def get_by_email(
        self, email: str, session: AsyncSession | None = None
    ) -> RepoResp[User | None]:
        async with self._ensure_session(existing_session=session) as session:
            sql_user = await session.scalar(
                select(SQLUser).where(SQLUser.email == email)
            )

            if not sql_user:
                return RepoResp(status=RepoStatus.NOT_FOUND)

            user = self._sql_to_user(sql_user=sql_user)
            return RepoResp(data=user)

    @safe_repo
    async def create(
        self, user: User, session: AsyncSession | None = None
    ) -> RepoResp[User]:
        async with self._ensure_session(existing_session=session) as session:
            sql_user = self._user_to_sql(user)
            session.add(sql_user)
            await session.flush()
            created_user = self._sql_to_user(sql_user)
            return RepoResp(data=created_user)

    def _sql_to_user(self, sql_user: SQLUser) -> User:
        return User(
            id=sql_user.id,
            email=sql_user.email,
            password_hash=sql_user.password_hash,
            created_at=sql_user.created_at.replace(
                tzinfo=UTC
            ),  # Ensure UTC when using in-memory SQLite
        )

    def _user_to_sql(self, user: User) -> SQLUser:
        return SQLUser(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at,
        )


class LinkSQLRepo(SQLRepoBase):
    @property
    def _updatable_sql_fields(self) -> list[str]:
        return [SQLLink.url.key, SQLLink.updated_at.key]

    async def get_by_id(
        self, id: int, session: AsyncSession | None = None
    ) -> RepoResp[Link]:
        async with self._ensure_session(existing_session=session) as session:
            sql_link = await session.get(SQLLink, id)

            if not sql_link:
                return RepoResp(status=RepoStatus.NOT_FOUND)

            link = self._sql_to_link(sql_link=sql_link)
            return RepoResp(data=link)

    async def list_by_user_id(
        self, user_id: int, session: AsyncSession | None = None
    ) -> RepoResp[list[Link]]:
        async with self._ensure_session(existing_session=session) as session:
            sql_links = (
                await session.scalars(
                    select(SQLLink).where(SQLLink.user_id == user_id)
                )
            ).all()

            links = [
                self._sql_to_link(sql_link=sql_link) for sql_link in sql_links
            ]
            return RepoResp(data=links)

    @safe_repo
    async def create(
        self, link: Link, session: AsyncSession | None = None
    ) -> RepoResp[Link]:
        async with self._ensure_session(existing_session=session) as session:
            sql_link = self._link_to_sql(link)
            session.add(sql_link)
            await session.flush()
            created_link = self._sql_to_link(sql_link=sql_link)
            return RepoResp(data=created_link)

    @safe_repo
    async def update(
        self, link: Link, session: AsyncSession | None = None
    ) -> RepoResp[Link]:
        async with self._ensure_session(existing_session=session) as session:
            sql_link = await session.scalar(
                select(SQLLink).where(
                    SQLLink.id == link.id,
                    SQLLink.user_id == link.user_id,
                )
            )

            if not sql_link:
                return RepoResp(status=RepoStatus.NOT_FOUND)

            new_sql_values = self._link_to_sql(link)
            for field in self._updatable_sql_fields:
                setattr(sql_link, field, getattr(new_sql_values, field))

            await session.flush()
            return RepoResp(data=self._sql_to_link(sql_link=sql_link))

    @safe_repo
    async def delete_by_id_and_user_id(
        self,
        id: int,
        user_id: int,
        session: AsyncSession | None = None,
    ) -> RepoResp[None]:
        async with self._ensure_session(existing_session=session) as session:
            sql_link = await session.scalar(
                select(SQLLink).where(
                    SQLLink.id == id,
                    SQLLink.user_id == user_id,
                )
            )

            if sql_link is None:
                return RepoResp(status=RepoStatus.NOT_FOUND)

            await session.delete(sql_link)
            return RepoResp()

    def _sql_to_link(self, sql_link: SQLLink) -> Link:
        return Link(
            id=sql_link.id,
            user_id=sql_link.user_id,
            url=sql_link.url,
            created_at=sql_link.created_at.replace(
                tzinfo=UTC
            ),  # Ensure UTC when using in-memory SQLite
        )

    def _link_to_sql(self, link: Link) -> SQLLink:
        return SQLLink(
            id=link.id,
            user_id=link.user_id,
            url=str(link.url),
            created_at=link.created_at,
            updated_at=link.updated_at,
        )
