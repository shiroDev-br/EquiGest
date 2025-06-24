from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from equigest.schemas.user import UserCreateSchema
from equigest.schemas.token_schema import TokenSchema

from equigest.integrations.abacatepay.schemas.create_customer import CreateCustomerSchema

from equigest.services.user import (
    UserService,
)

from equigest.integrations.abacatepay.service import (
    AbacatePayIntegrationService,
    get_abacatepay_integration_service
)

from equigest.infra.redis_client import async_redis_client

from equigest.services.exceptions import UserAlreadyExists

from equigest.utils.security.oauth_token import create_access_token
from equigest.utils.security.hasher import check_password

from equigest.setup import limiter

auth_router = APIRouter()

@auth_router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=TokenSchema,
    responses={
        status.HTTP_409_CONFLICT: {
            'description': 'User already exists',
            'content': {
                'application/json': {
                    'example': {'detail': 'User already exists'}
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
        status.HTTP_502_BAD_GATEWAY : {
            'description': "Error in customer create.",
            'content': {
                'application/json': {
                    'example': {'detail': "Error in customer create"}
                }
            },
        },
    },
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user: UserCreateSchema,
    user_service: Annotated[UserService, Depends()],
    abacatepay_service: Annotated[AbacatePayIntegrationService, Depends(get_abacatepay_integration_service)],
):
    """
    Create a user in the internal database and as a system client in AbacatePay

    - **username**: Name of the user account to be created
    - **password**: Password of the user account that will by hashed and added to user
    - **email**: Email of the user account to be created
    - **cellphone**: Cellphne of the user account to be created
    - **cpf_cnpj**: The CPF or CNPJ of the user account to be created

    """
    try:
        customer_id = abacatepay_service.create_customer(
            CreateCustomerSchema(
                name=user.username,
                email=user.email,
                cellphone=user.cellphone,
                tax_id=user.cpf_cnpj
            )
        )

        user.abacatepay_client_id = customer_id['customer_id']

        user = await user_service.create_user(user)

        await async_redis_client.hset_initial(f"user:{user.id}", {
            "total_pregnancies": 0,
            "pregnancies_in_progress": 0,
            "failed_pregnancies": 0,
            "successful_pregnancies": 0,
        })
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User already exists',
        )
    
    access_token = create_access_token(data={'sub': user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}

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
async def login(
    request: Request,
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends()],
):

    """
    Log in with an already registered user

    - **username**: Previously registered username
    - **password**: Previously registered password
    
    """
    user = await user_service.get_user(login_data.username)

    if not user or not check_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
        )

    access_token = create_access_token(data={'sub': user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}