from pydantic import BaseModel


class HealthResp(BaseModel):
    status: str
