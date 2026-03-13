import base62

from link_forge.redirect.schemas import RedirectInput, RedirectOutput
from link_forge.repos import LinkSQLRepo, RepoResp, RepoStatus


class LinkDecodeError(Exception):
    pass


class GetLinkError(Exception):
    pass


class LinkNotFoundError(Exception):
    pass


class RedirectUC:
    def __init__(self, link_repo: LinkSQLRepo) -> None:
        self.link_repo = link_repo

    async def redirect(self, input: RedirectInput) -> RedirectOutput:
        try:
            link_id = base62.decode(input.code)
        except ValueError:
            raise LinkDecodeError()

        get_resp: RepoResp = await self.link_repo.get_by_id(id=link_id)
        if not get_resp.ok:
            if get_resp.status == RepoStatus.NOT_FOUND:
                raise LinkNotFoundError()
            raise GetLinkError()
        link = get_resp.data

        return RedirectOutput(url=link.url)
