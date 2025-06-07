from typing import Annotated

from fastapi import APIRouter, Depends, status, Request

from equigest.models.user import User

from equigest.integrations.abacatepay.service import (
    AbacatePayIntegrationService,
    get_abacatepay_integration_service
)

from equigest.utils.security.oauth_token import get_current_user

from equigest.setup import limiter

payment_router = APIRouter(prefix='/payments')

@payment_router.post(
    '/create-billing',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_502_BAD_GATEWAY : {
            'description': "Error in billing create.",
            'content': {
                'application/json': {
                    'example': {'detail': "Error in billing create"}
                }
            },
        },
    },
)
@limiter.limit("10/minute")
async def create_billing(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    abacatepay_service: Annotated[AbacatePayIntegrationService, Depends(get_abacatepay_integration_service)],
):
    billing_data = abacatepay_service.create_billing(current_user)

    return billing_data