from typing import Annotated

from fastapi import APIRouter, Depends, status, Request

from equigest.schemas.mare import MareCreateOrEditSchema, MareSchema

from equigest.models.user import User

from equigest.services.mare import (
    MareService,
    get_mare_service
)

from equigest.utils.security.oauth_token import get_current_user
from equigest.utils.mare import get_managment_schedule

from equigest.enums.enums import MareType

from equigest.setup import limiter

mare_router = APIRouter()

@mare_router.post(
    '/create',
    status_code=status.HTTP_201_CREATED,
    response_model=MareSchema,
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS : {
            'description': "You are sending too many requests..",
            'content': {
                'application/json': {
                    'example': {'detail': "You are sending too many requests."}
                }
            },
        },
    }
)
@limiter.limit("5/minute")
async def create(
    request: Request,
    mare: MareCreateOrEditSchema,
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
    responses={
        status.HTTP_403_FORBIDDEN: {
            'description': "You're not allowed to access this mare.",
            'content': {
                'application/json': {
                    'example': {'detail': "You're not allowed to access this mare."}
                }
            },
        },
        status.HTTP_429_TOO_MANY_REQUESTS : {
            'description': "You are sending too many requests..",
            'content': {
                'application/json': {
                    'example': {'detail': "You are sending too many requests."}
                }
            },
        },
    },
)
@limiter.limit("25/minute")
async def visualize(
    request: Request,
    mare_name: str,
    mare_service: Annotated[MareService, Depends(get_mare_service)],
    current_user: Annotated[User, Depends(get_current_user)]
):

    mare = await mare_service.get_mare(mare_name, current_user.id)

    managment_schedule = get_managment_schedule(mare.pregnancy_date)

    if mare.mare_type == MareType.HEADQUARTERS:
        managment_schedule.pop("P4", None)
    
    return {
        "mare": mare,
        "managment_schedule": managment_schedule
    }
