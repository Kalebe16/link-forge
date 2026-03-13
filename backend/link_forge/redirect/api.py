from fastapi import APIRouter, HTTPException, Path, status
from starlette.responses import RedirectResponse

from link_forge.db import DBManager
from link_forge.redirect.schemas import RedirectInput, RedirectOutput
from link_forge.redirect.usecases import (
    GetLinkError,
    LinkDecodeError,
    LinkNotFoundError,
    RedirectUC,
)
from link_forge.repos import LinkSQLRepo

router = APIRouter(prefix='', tags=['Redirect'])


@router.get('/{code}', status_code=status.HTTP_302_FOUND)
async def redirect(code: str = Path()):
    redirect_uc = RedirectUC(link_repo=LinkSQLRepo(db_manager=DBManager()))

    try:
        redirect_output: RedirectOutput = await redirect_uc.redirect(
            input=RedirectInput(code=code)
        )

    except (LinkDecodeError, LinkNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    except GetLinkError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return RedirectResponse(
        url=redirect_output.url, status_code=status.HTTP_302_FOUND
    )
