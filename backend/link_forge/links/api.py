from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Request,
    status,
)

from link_forge.db import DBManager
from link_forge.entities import User
from link_forge.links.schemas import (
    CreateLinkBody,
    CreateLinkInput,
    CreateLinkOutput,
    CreateLinkResp,
    DeleteLinkInput,
    ListLinksInput,
    ListLinksOutput,
    ListLinksResp,
    UpdateLinkBody,
    UpdateLinkInput,
    UpdateLinkOutput,
    UpdateLinkResp,
)
from link_forge.links.usecases import (
    CreateLinkError,
    DeleteLinkError,
    LinkNotFoundError,
    LinkUC,
    ListLinksError,
    UpdateLinkError,
)
from link_forge.repos import LinkSQLRepo
from link_forge.security import require_access_token

router = APIRouter(prefix='/api/links', tags=['Links'])


@router.post(
    '', status_code=status.HTTP_201_CREATED, response_model=CreateLinkResp
)
async def create_link(
    request: Request,
    body: CreateLinkBody = Body(),
    user: User = Depends(require_access_token),
):
    link_uc = LinkUC(
        link_repo=LinkSQLRepo(db_manager=DBManager()),
    )

    try:
        create_link_output: CreateLinkOutput = await link_uc.create(
            input=CreateLinkInput(user_id=user.id, url=body.url)
        )
    except CreateLinkError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return CreateLinkResp(
        id=create_link_output.id,
        short_url=f'{request.base_url}{create_link_output.code}',
        url=create_link_output.url,
    )


@router.put(
    '/{id}', status_code=status.HTTP_200_OK, response_model=UpdateLinkResp
)
async def update_link(
    request: Request,
    id: int = Path(),
    body: UpdateLinkBody = Body(),
    user: User = Depends(require_access_token),
):
    link_uc = LinkUC(
        link_repo=LinkSQLRepo(db_manager=DBManager()),
    )

    try:
        update_link_output: UpdateLinkOutput = await link_uc.update(
            UpdateLinkInput(user_id=user.id, id=id, url=body.url)
        )

    except LinkNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    except UpdateLinkError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return UpdateLinkResp(
        id=update_link_output.id,
        url=update_link_output.url,
        short_url=f'{request.base_url}{update_link_output.code}',
    )


@router.get('', status_code=status.HTTP_200_OK, response_model=ListLinksResp)
async def list_links(
    request: Request, user: User = Depends(require_access_token)
):
    link_uc = LinkUC(
        link_repo=LinkSQLRepo(db_manager=DBManager()),
    )

    try:
        list_links_output: ListLinksOutput = await link_uc.list(
            ListLinksInput(user_id=user.id)
        )

    except ListLinksError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ListLinksResp(
        links=[
            ListLinksResp.Link(
                id=link.id,
                url=link.url,
                short_url=f'{request.base_url}{link.code}',
            )
            for link in list_links_output.links
        ]
    )


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    id: int = Path(), user: User = Depends(require_access_token)
):
    link_uc = LinkUC(
        link_repo=LinkSQLRepo(db_manager=DBManager()),
    )

    try:
        await link_uc.delete(
            input=DeleteLinkInput(link_id=id, user_id=user.id)
        )

    except LinkNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    except DeleteLinkError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
