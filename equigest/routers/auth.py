from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from equigest.schemas.user import UserCreateSchema, UserSchema
from equigest.schemas.token_schema import TokenSchema

from equigest.services.user import (
    UserService,
    get_user_service
)

from equigest.services.exceptions import UserAlreadyExists

from equigest.utils.security.oauth_token import create_access_token
from equigest.utils.security.hasher import check_password

from equigest.setup import limiter

auth_router = APIRouter()

@auth_router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchema,
    responses={
        status.HTTP_409_CONFLICT: {
            'description': 'Username already exists',
            'content': {
                'application/json': {
                    'example': {'detail': 'Username already exists'}
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
@limiter.limit("5/minute")
async def register(
    request: Request,
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

@auth_router.post(
    '/login',
    status_code=status.HTTP_200_OK,
    response_model=TokenSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Incorrect name or password',
            'content': {
                'application/json': {
                    'example': {'detail': 'Incorrect username or password'}
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
@limiter.limit("10/minute")
async def login(
    request: Request,
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    user = await user_service.get_user(login_data.username)

    if not user or not check_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
        )

    access_token = create_access_token(data={'sub': user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}