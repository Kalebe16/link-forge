from pydantic import BaseModel, HttpUrl


class RedirectInput(BaseModel):
    code: str


class RedirectOutput(BaseModel):
    url: HttpUrl
