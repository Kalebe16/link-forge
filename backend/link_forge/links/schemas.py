from pydantic import BaseModel, HttpUrl


# Create Link
class CreateLinkBody(BaseModel):
    url: HttpUrl


class CreateLinkInput(BaseModel):
    user_id: int
    url: HttpUrl


class CreateLinkOutput(BaseModel):
    id: int
    code: str
    url: HttpUrl


class CreateLinkResp(BaseModel):
    id: int
    short_url: HttpUrl
    url: HttpUrl


# Update Link
class UpdateLinkBody(BaseModel):
    url: HttpUrl


class UpdateLinkInput(BaseModel):
    user_id: int
    id: int
    url: HttpUrl


class UpdateLinkOutput(BaseModel):
    id: int
    code: str
    url: HttpUrl


class UpdateLinkResp(BaseModel):
    id: int
    short_url: HttpUrl
    url: HttpUrl


# List Links
class ListLinksInput(BaseModel):
    user_id: int


class ListLinksOutput(BaseModel):
    class Link(BaseModel):
        id: int
        code: str
        url: HttpUrl

    links: list[Link]


class ListLinksResp(BaseModel):
    class Link(BaseModel):
        id: int
        url: HttpUrl
        short_url: HttpUrl

    links: list[Link]


# Delete Link
class DeleteLinkInput(BaseModel):
    link_id: int
    user_id: int
