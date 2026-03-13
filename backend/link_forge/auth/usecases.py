from datetime import UTC, datetime

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from link_forge.auth.schemas import (
    CreateUserInput,
    CreateUserOuput,
    LoginInput,
    LoginOutput,
)
from link_forge.entities import User
from link_forge.repos import RepoResp, RepoStatus, UserSQLRepo
from link_forge.security import (
    create_access_token,
    create_refresh_token,
    get_access_token_expires_at,
    get_refresh_token_expires_at,
)


class UserAlreadyExistsError(Exception):
    pass


class CreateUserError(Exception):
    pass


class LoginError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidSessionError(Exception):
    pass


class LogoutError(Exception):
    pass


class AuthUC:
    def __init__(self, user_repo: UserSQLRepo) -> None:
        self.user_repo = user_repo
        self.password_hasher = PasswordHasher()

    async def register(self, input: CreateUserInput) -> CreateUserOuput:
        create_resp: RepoResp = await self.user_repo.create(
            User(
                email=input.email,
                password_hash=self.password_hasher.hash(input.password),
                created_at=datetime.now(UTC),
            )
        )

        if not create_resp.ok:
            if create_resp.status == RepoStatus.DUPLICATED:
                raise UserAlreadyExistsError()

            raise CreateUserError()
        user = create_resp.data

        return CreateUserOuput(
            id=user.id,
            email=user.email,
            created_at=user.created_at,
        )

    async def login(self, input: LoginInput) -> LoginOutput:
        get_resp: RepoResp = await self.user_repo.get_by_email(
            email=input.email
        )
        if not get_resp.ok:
            if get_resp.status == RepoStatus.NOT_FOUND:
                raise InvalidCredentialsError()
            raise LoginError()
        user = get_resp.data

        try:
            self.password_hasher.verify(user.password_hash, input.password)
        except VerifyMismatchError:
            raise InvalidCredentialsError()

        return LoginOutput(
            access_token=create_access_token(subject=str(user.id)),
            access_token_expires_at=get_access_token_expires_at(),
            refresh_token=create_refresh_token(subject=str(user.id)),
            refresh_token_expires_at=get_refresh_token_expires_at(),
        )
