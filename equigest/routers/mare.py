from typing import Annotated

from fastapi import APIRouter, Depends, status

from equigest.schemas.mare import MareCreateSchema, MareSchema

from equigest.models.user import User

from equigest.services.mare import (
    MareService,
    get_mare_service
)

from equigest.utils.security.oauth_token import get_current_user
from equigest.utils.mare import get_managment_schedule

mare_router = APIRouter()

@mare_router.post(
    '/create',
    status_code=status.HTTP_201_CREATED,
    response_model=MareSchema
)
async def create(
    mare: MareCreateSchema,
    mare_service: Annotated[MareService, Depends(get_mare_service)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    new_mare = await mare_service.create_mare(
        mare,
        current_user.id
    )

    return new_mare

@mare_router.get(
    '/visualize',
    status_code=status.HTTP_200_OK,
)
async def visualize(
    mare_name: str,
    mare_service: Annotated[MareService, Depends(get_mare_service)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    mare = await mare_service.get_mare(mare_name)
    calendar = get_managment_schedule(mare.pregnancy_date)

    return {'mare': mare, 'calendar': calendar}