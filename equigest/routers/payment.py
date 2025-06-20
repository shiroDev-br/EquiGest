from typing import Annotated

from fastapi import APIRouter, Depends, status, Request, HTTPException

from equigest.settings import Settings

from equigest.models.user import User

from equigest.integrations.abacatepay.service import (
    AbacatePayIntegrationService,
    get_abacatepay_integration_service
)

from equigest.utils.security.oauth_token import get_current_user

from equigest.tasks import process_billing_paid

from equigest.setup import limiter

settings = Settings()
ABACATEPAY_WEBHOOK_SECURE_PROD = settings.ABACATEPAY_WEBHOOK_SECURE_PROD
ABACATEPAY_DEV_APIKEY = settings.ABACATEPAY_DEV_APIKEY

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
    """
    Create a new billing
    """
    billing_data = abacatepay_service.create_billing(current_user)

    return billing_data

@payment_router.post(
    '/webhook-listener',
    status_code=status.HTTP_200_OK,
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
@limiter.limit('30/minute')
async def webhook_listener(
    request: Request
):

    webhook_secret = request.query_params.get("webhookSecret")
    if webhook_secret != ABACATEPAY_WEBHOOK_SECURE_PROD and webhook_secret != ABACATEPAY_DEV_APIKEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook secret")

    payload = await request.json()
    process_billing_paid.delay(payload)
    
    return payload