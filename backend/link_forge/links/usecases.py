from datetime import UTC, datetime

import base62

from link_forge.entities import Link
from link_forge.links.schemas import (
    CreateLinkInput,
    CreateLinkOutput,
    DeleteLinkInput,
    ListLinksInput,
    ListLinksOutput,
    UpdateLinkInput,
    UpdateLinkOutput,
)
from link_forge.repos import LinkSQLRepo, RepoResp, RepoStatus


class CreateLinkError(Exception):
    pass


class UpdateLinkError(Exception):
    pass


class ListLinksError(Exception):
    pass


class LinkNotFoundError(Exception):
    pass


class DeleteLinkError(Exception):
    pass


class LinkUC:
    def __init__(self, link_repo: LinkSQLRepo) -> None:
        self.link_repo = link_repo

    async def create(self, input: CreateLinkInput) -> CreateLinkOutput:
        now = datetime.now(UTC)
        create_link_resp: RepoResp = await self.link_repo.create(
            Link(
                user_id=input.user_id,
                url=input.url,
                created_at=now,
                updated_at=now,
            )
        )
        if not create_link_resp.ok:
            raise CreateLinkError()
        link = create_link_resp.data

        return CreateLinkOutput(
            id=link.id, code=base62.encode(link.id), url=link.url
        )

    async def update(self, input: UpdateLinkInput) -> UpdateLinkOutput:
        now = datetime.now()
        update_link_resp: RepoResp = await self.link_repo.update(
            Link(
                user_id=input.user_id,
                id=input.id,
                url=input.url,
                updated_at=now,
            )
        )
        if not update_link_resp.ok:
            if update_link_resp.status == RepoStatus.NOT_FOUND:
                raise LinkNotFoundError()

            raise UpdateLinkError()
        link = update_link_resp.data

        return UpdateLinkOutput(
            id=link.id, code=base62.encode(link.id), url=link.url
        )

    async def list(self, input: ListLinksInput) -> ListLinksOutput:
        get_resp: RepoResp = await self.link_repo.list_by_user_id(
            user_id=input.user_id
        )
        if not get_resp.ok:
            raise ListLinksError()
        links = get_resp.data

        return ListLinksOutput(
            links=[
                ListLinksOutput.Link(
                    id=link.id, code=base62.encode(link.id), url=link.url
                )
                for link in links
            ]
        )

    async def delete(self, input: DeleteLinkInput) -> None:
        delete_resp: RepoResp = await self.link_repo.delete_by_id_and_user_id(
            id=input.link_id, user_id=input.user_id
        )
        if not delete_resp.ok:
            if delete_resp.status == RepoStatus.NOT_FOUND:
                raise LinkNotFoundError()

            raise DeleteLinkError()
