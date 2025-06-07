from typing import Annotated, List

from datetime import date, timedelta

from fastapi import APIRouter, Depends, status, Request, Query

from fastapi_pagination import Page, Params

from equigest.schemas.mare import MareCreateOrEditSchema, MareSchema

from equigest.models.user import User

from equigest.services.mare import (
    MareService,
    get_mare_service
)

from equigest.utils.security.oauth_token import get_current_user
from equigest.utils.mare import get_managment_schedule, is_in_p4_range, is_in_herpes_range

from equigest.integrations.abacatepay.service import validate_paid_user

from equigest.enums.enums import MareType

from equigest.setup import limiter

mare_router = APIRouter(
    prefix="/mares"
)

@mare_router.get(
    '/',
    status_code=status.HTTP_200_OK,
    response_model=Page[MareSchema],
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
async def get_mares(
    request: Request,
    page: Annotated[int, Query(ge=1, description="Número da página")],
    size: Annotated[int, Query(ge=1, le=100, description="Itens por página")],
    mare_service: Annotated[MareService, Depends(get_mare_service)],
    current_user: Annotated[User, Depends(validate_paid_user)]
) -> Page[MareSchema]:
    params = Params(page=page, size=size)
    return await mare_service.get_mares(current_user.id, params)

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

@mare_router.get(
    '/visualize-birthforecast-beetwen',
    status_code=status.HTTP_200_OK,
    response_model=List[MareSchema],
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
@limiter.limit("25/minute")
async def visualize_birthforecast_beetwen(
    request: Request,
    start_date: date,
    end_date: date,
    mare_service: Annotated[MareService, Depends(get_mare_service)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    mares = await mare_service.get_mare_birthforecast(
        start_date,
        end_date,
        current_user.id
    )
    
    return mares

@mare_router.get(
    '/visualize-p4-beetwen',
    status_code=status.HTTP_200_OK,
    response_model=List[MareSchema],
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
@limiter.limit("25/minute")
async def visualize_p4_beetwen(
    request: Request,
    start_date: date,
    end_date: date,
    mare_service: Annotated[MareService, Depends(get_mare_service)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    mares = await mare_service.get_mare_by_earlist(
        start_date - timedelta(105),
        end_date,
        current_user.id
    )

    return [
        mare for mare in mares 
        if is_in_p4_range(mare.pregnancy_date, start_date, end_date) and mare.mare_type == MareType.RECEIVER
    ]

@mare_router.get(
    '/visualize-herpes-beetwen',
    status_code=status.HTTP_200_OK,
    response_model=List[MareSchema],
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
@limiter.limit("25/minute")
async def visualize_herpes_beetwen(
    request: Request,
    start_date: date,
    end_date: date,
    mare_service: Annotated[MareService, Depends(get_mare_service)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    mares = await mare_service.get_mare_by_earlist(
        start_date - timedelta(270),
        end_date,
        current_user.id
    )

    return [
        mare for mare in mares 
        if is_in_herpes_range(mare.pregnancy_date, start_date, end_date)
    ]

@mare_router.put(
    '/edit',
    status_code=status.HTTP_200_OK,
    response_model=MareSchema,
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
            'description': "You are sending too many requests.",
            'content': {
                'application/json': {
                    'example': {'detail': "You are sending too many requests."}
                }
            },
        },
    },
)
@limiter.limit("10/minute")
async def edit_mare(
    request: Request,
    mare_name: str,
    mare: MareCreateOrEditSchema,
    mare_service: Annotated[MareService, Depends(get_mare_service)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    existing_mare = await mare_service.edit_mare(
        mare_name,
        mare,
        current_user.id
    )

    return existing_mare