from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from equigest.schemas.user import UserCreateSchema
from equigest.services.user import (
    UserService,
    get_user_service
)

from equigest.services.exceptions import UserAlreadyExists

auth_router = APIRouter()

@auth_router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            'description': 'Username already exists',
            'content': {
                'application/json': {
                    'example': {'detail': 'Username already exists'}
                }
            },
        },
    },
)
async def register(
    user: UserCreateSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        user = await user_service.create_user(user)
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Username already exists',
        )
    
    return user