from fastapi import APIRouter, Body, Depends, HTTPException, Response, status

from link_forge.auth.schemas import (
    CreateUserBody,
    CreateUserInput,
    CreateUserOuput,
    CreateUserResp,
    LoginBody,
    LoginInput,
    LoginOutput,
    LoginResp,
    LogoutResp,
    MeResp,
    RefreshResp,
)
from link_forge.auth.usecases import (
    AuthUC,
    CreateUserError,
    InvalidCredentialsError,
    LoginError,
    UserAlreadyExistsError,
)
from link_forge.db import DBManager
from link_forge.entities import User
from link_forge.repos import UserSQLRepo
from link_forge.security import (
    create_access_token,
    get_access_token_expires_at,
    require_access_token,
    require_refresh_token,
)

router = APIRouter(prefix='/api/auth', tags=['Auth'])


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=CreateUserResp,
)
async def register(body: CreateUserBody = Body()):
    auth_uc = AuthUC(
        user_repo=UserSQLRepo(db_manager=DBManager()),
    )

    try:
        create_user_output: CreateUserOuput = await auth_uc.register(
            input=CreateUserInput(email=body.email, password=body.password)
        )

    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User with this email already exists',
        )

    except CreateUserError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return CreateUserResp(
        id=create_user_output.id,
        email=create_user_output.email,
        created_at=create_user_output.created_at,
    )


@router.post(
    '/login', status_code=status.HTTP_200_OK, response_model=LoginResp
)
async def login(response: Response, body: LoginBody = Body()):
    auth_uc = AuthUC(
        user_repo=UserSQLRepo(db_manager=DBManager()),
    )

    try:
        login_output: LoginOutput = await auth_uc.login(
            input=LoginInput(email=body.email, password=body.password)
        )

    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    except LoginError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    response.set_cookie(
        path='/',
        key='access_token',
        value=login_output.access_token,
        httponly=True,
        secure=False,
        samesite='lax',
        expires=login_output.access_token_expires_at,
    )
    response.set_cookie(
        path='/',
        key='refresh_token',
        value=login_output.refresh_token,
        httponly=True,
        secure=False,
        samesite='lax',
        expires=login_output.refresh_token_expires_at,
    )

    return LoginResp(message='Logged in')


@router.post(
    '/refresh', status_code=status.HTTP_200_OK, response_model=RefreshResp
)
def refresh(
    response: Response,
    user=Depends(require_refresh_token),
):
    access_token = create_access_token(subject=str(user.id))

    response.set_cookie(
        path='/',
        key='access_token',
        value=access_token,
        httponly=True,
        secure=False,
        samesite='lax',
        expires=get_access_token_expires_at(),
    )

    return RefreshResp(message='Token refreshed')


@router.get('/me', status_code=status.HTTP_200_OK, response_model=MeResp)
def me(user: User = Depends(require_access_token)):
    return MeResp(id=user.id, email=user.email, created_at=user.created_at)


@router.post(
    '/logout', status_code=status.HTTP_200_OK, response_model=LogoutResp
)
def logout(response: Response):
    response.delete_cookie(path='/', key='access_token')
    response.delete_cookie(path='/', key='refresh_token')

    return LogoutResp(message='Logged out')
