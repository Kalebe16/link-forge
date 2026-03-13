from fastapi import APIRouter, status

from link_forge.health.schemas import HealthResp

router = APIRouter(prefix='/health', tags=['Health'])


@router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=HealthResp,
)
def health():
    return HealthResp(status='ok')
