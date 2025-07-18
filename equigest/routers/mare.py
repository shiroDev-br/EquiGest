from typing import Annotated

from datetime import timedelta

from fastapi import APIRouter, Depends, status, Request

from fastapi_pagination import Page, Params

from equigest.schemas.mare import MareCreateOrEditSchema, MareSchema, DeleteMareSchema, MareListWithManagementScheduleSchema
from equigest.schemas.query import MareQueryParams, MareQueryByBirthForecastParams

from equigest.models.user import User

from equigest.services.mare import (
    MareService,
)

from equigest.infra.redis_client import async_redis_client

from equigest.utils.mare import get_managment_schedule, is_in_p4_range, is_in_herpes_range, update_success_or_fail_counters
from equigest.utils.user import validate_paid_user

from equigest.enums.enums import MareType

from equigest.setup import limiter

mare_router = APIRouter(
    prefix="/mares"
)

@mare_router.get(
    '/',
    status_code=status.HTTP_200_OK,
    response_model=Page[MareListWithManagementScheduleSchema],
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS : {
            'description': "You are sending too many requests..",
            'content': {
                'application/json': {
                    'example': {'detail': "You are sending too many requests."}
                }
            },
        },
        status.HTTP_402_PAYMENT_REQUIRED : {
            'description': "System access time expired. Make payment to resume use.",
            'content': {
                'application/json': {
                    'example': {'detail': "System access time expired. Make payment to resume use."}
                }
            },
        },
    }
)
@limiter.limit("5/minute")
async def get_mares(
    request: Request,
    query: Annotated[MareQueryByBirthForecastParams, Depends()],
    mare_service: Annotated[MareService, Depends()],
    current_user: Annotated[User, Depends(validate_paid_user)]
) -> Page[MareSchema]:
    """
    List all mares from their type

    - **mare_type**: Type of Mare (RECEIVER or HEADQUARTERS)
    - **page**: The page that you want see
    - **size**: The number of items per page
    
    """
    params = Params(page=query.page, size=query.size)
    return await mare_service.get_mares(current_user.id, query.mare_type, params)

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
        status.HTTP_402_PAYMENT_REQUIRED : {
            'description': "System access time expired. Make payment to resume use.",
            'content': {
                'application/json': {
                    'example': {'detail': "System access time expired. Make payment to resume use."}
                }
            },
        },
    }
)
@limiter.limit("5/minute")
async def create(
    request: Request,
    mare: MareCreateOrEditSchema,
    mare_service: Annotated[MareService, Depends()],
    current_user: Annotated[User, Depends(validate_paid_user)]
):
    """
    Register a mare in the database

    - **mare_name**: Mare's name to be registered
    - **mare_type**: Mare's type to be registered (RECEIVER or HEADQUARTERS)
    - **stallion_name**: Mare's stallion name to be registered
    - **donor_name**: OPTIONAL Mare's donor name to be registered
    - **pregnancy_date**: Mare's pregnancy_date to be registered
    """
    new_mare = await mare_service.create_mare(
        mare,
        current_user.id
    )

    await async_redis_client.hincryby_fields(
        f"user:{current_user.id}",
        total_pregnancies=1,
        pregnancies_in_progress=1
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
        status.HTTP_402_PAYMENT_REQUIRED : {
            'description': "System access time expired. Make payment to resume use.",
            'content': {
                'application/json': {
                    'example': {'detail': "System access time expired. Make payment to resume use."}
                }
            },
        },
    },
)
@limiter.limit("25/minute")
async def visualize(
    request: Request,
    mare_name: str,
    mare_service: Annotated[MareService, Depends()],
    current_user: Annotated[User, Depends(validate_paid_user)]
):

    """
    View an individual mare

    - **mare_name**: Name of the mare you are looking to view
    """

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
    response_model=Page[MareListWithManagementScheduleSchema],
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS : {
            'description': "You are sending too many requests..",
            'content': {
                'application/json': {
                    'example': {'detail': "You are sending too many requests."}
                }
            },
        },
        status.HTTP_402_PAYMENT_REQUIRED : {
            'description': "System access time expired. Make payment to resume use.",
            'content': {
                'application/json': {
                    'example': {'detail': "System access time expired. Make payment to resume use."}
                }
            },
        },
    }
)
@limiter.limit("25/minute")
async def visualize_birthforecast_beetwen(
    request: Request,
    query: Annotated[MareQueryParams, Depends()],
    mare_service: Annotated[MareService, Depends()],
    current_user: Annotated[User, Depends(validate_paid_user)]
):
    """
    View mares due to calve within the date range

    - **start_date**: Initial date of interval
    - **end_date**: Final date of interval
    - **page**: The page that you want see
    - **size**: The number of items per page
    - **mare_type**: OPTIONAL Mare's that will be returned by their type
    """
    params = Params(page=query.page, size=query.size)
    mares = await mare_service.get_mare_birthforecast(
        query.start_date,
        query.end_date,
        current_user.id,
        params,
        query.mare_type
    )
    
    return mares

@mare_router.get(
    '/visualize-p4-beetwen',
    status_code=status.HTTP_200_OK,
    response_model=Page[MareListWithManagementScheduleSchema],
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS : {
            'description': "You are sending too many requests..",
            'content': {
                'application/json': {
                    'example': {'detail': "You are sending too many requests."}
                }
            },
        },
        status.HTTP_402_PAYMENT_REQUIRED : {
            'description': "System access time expired. Make payment to resume use.",
            'content': {
                'application/json': {
                    'example': {'detail': "System access time expired. Make payment to resume use."}
                }
            },
        },
    }
)
@limiter.limit("25/minute")
async def visualize_p4_beetwen(
    request: Request,
    query: Annotated[MareQueryParams, Depends()],
    mare_service: Annotated[MareService, Depends()],
    current_user: Annotated[User, Depends(validate_paid_user)]
):
    """
    View mares with P4 hormone in the date range

    - **start_date**: Initial date of interval
    - **end_date**: Final date of interval
    - **page**: The page that you want see
    - **size**: The number of items per page
    - **mare_type**: OPTIONAL Mare's that will be returned by their type
    """
    params = Params(page=query.page, size=query.size)
    paginated = await mare_service.get_mare_by_earlist(
        query.start_date - timedelta(105),
        query.end_date,
        current_user.id,
        params
    )

    filtered_items = [
        mare for mare in paginated.items
        if is_in_p4_range(mare["mare"].pregnancy_date, query.start_date, query.end_date) and mare["mare"].mare_type == MareType.RECEIVER
    ]

    return Page.create(items=filtered_items, total=len(filtered_items), params=params)

@mare_router.get(
    '/visualize-herpes-beetwen',
    status_code=status.HTTP_200_OK,
    response_model=Page[MareListWithManagementScheduleSchema],
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS : {
            'description': "You are sending too many requests..",
            'content': {
                'application/json': {
                    'example': {'detail': "You are sending too many requests."}
                }
            },
        },
        status.HTTP_402_PAYMENT_REQUIRED : {
            'description': "System access time expired. Make payment to resume use.",
            'content': {
                'application/json': {
                    'example': {'detail': "System access time expired. Make payment to resume use."}
                }
            },
        },
    }
)
@limiter.limit("25/minute")
async def visualize_herpes_beetwen(
    request: Request,
    query: Annotated[MareQueryParams, Depends()],
    mare_service: Annotated[MareService, Depends()],
    current_user: Annotated[User, Depends(validate_paid_user)]
):
    """
    View mares with Herpes Vaccine in the date range

    - **start_date**: Initial date of interval
    - **end_date**: Final date of interval
    - **page**: The page that you want see
    - **size**: The number of items per page
    - **mare_type**: OPTIONAL Mare's that will be returned by their type
    """
    params = Params(page=query.page, size=query.size)
    paginated = await mare_service.get_mare_by_earlist(
        query.start_date - timedelta(270),
        query.end_date,
        current_user.id,
        params
    )

    if query.mare_type:
        filtered_items = [
            mare for mare in paginated.items
            if is_in_herpes_range(mare["mare"].pregnancy_date, query.start_date, query.end_date) and mare["mare"].mare_type == query.mare_type
        ]
    else:
        filtered_items = [
            mare for mare in paginated.items
            if is_in_herpes_range(mare["mare"].pregnancy_date, query.start_date, query.end_date)
        ]

    return Page.create(items=filtered_items, total=len(filtered_items), params=params)

@mare_router.get(
    '/graphic-counters',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS : {
            'description': "You are sending too many requests.",
            'content': {
                'application/json': {
                    'example': {'detail': "You are sending too many requests."}
                }
            },
        },
        status.HTTP_402_PAYMENT_REQUIRED : {
            'description': "System access time expired. Make payment to resume use.",
            'content': {
                'application/json': {
                    'example': {'detail': "System access time expired. Make payment to resume use."}
                }
            },
        },
    },
)
@limiter.limit("50/minute")
async def graphic_counters(
    request: Request,
    current_user: Annotated[User, Depends(validate_paid_user)]
):
    """
    Return the statistic of user account
    """
    return await async_redis_client.hget_all(f"user:{current_user.id}")

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
        status.HTTP_402_PAYMENT_REQUIRED : {
            'description': "System access time expired. Make payment to resume use.",
            'content': {
                'application/json': {
                    'example': {'detail': "System access time expired. Make payment to resume use."}
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
    mare_service: Annotated[MareService, Depends()],
    current_user: Annotated[User, Depends(validate_paid_user)]
):
    """
    Edit an already registered mare

    QUERY PARAM:
    - **mare_name**: Name of the mare you are looking to edit
    
    EDIT PARAMS
    - **mare_name**: Mare's name to be registered
    - **mare_type**: Mare's type to be registered (RECEIVER or HEADQUARTERS)
    - **stallion_name**: Mare's stallion name to be registered
    - **donor_name**: OPTIONAL Mare's donor name to be registered
    - **pregnancy_date**: Mare's pregnancy_date to be registered
    """
    existing_mare = await mare_service.edit_mare(
        mare_name,
        mare,
        current_user.id
    )

    return existing_mare

@mare_router.delete(
    '/delete',
    status_code=status.HTTP_204_NO_CONTENT,
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
        status.HTTP_402_PAYMENT_REQUIRED : {
            'description': "System access time expired. Make payment to resume use.",
            'content': {
                'application/json': {
                    'example': {'detail': "System access time expired. Make payment to resume use."}
                }
            },
        },
    },
)
@limiter.limit("5/minute")
async def delete(
    request: Request,
    query: DeleteMareSchema,
    mare_service: Annotated[MareService, Depends()],
    current_user: Annotated[User, Depends(validate_paid_user)]
):
    """
    Delete a mare for a purpose; pregnancy failed or pregnancy worked.

    - **mare_name**: Name of mare to be deleted
    - **delete_type**: Type of delete (SUCCESS_PREGNANCY or FAIL_PREGNANCY)
    """
    await mare_service.delete_mare(query.mare_name, current_user.id)
    await update_success_or_fail_counters(user_id=current_user.id, delete_type=query.delete_type)