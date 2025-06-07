from datetime import datetime

from fastapi import HTTPException, status

from equigest.models.user import User
from equigest.services.user import UserService

from equigest.enums.enums import PaymentAccessStatus

async def check_if_paid(
    user_service: UserService,
    user: User
) -> dict:
    existing_user = await user_service.update_payment_status(user, datetime.now())

    if existing_user.payment_status == PaymentAccessStatus.DEFEATED:
        raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail='System access time expired. Make payment to resume use',
        headers={'X-Payment-Required': 'true'}
    )

    return {
        'payment_status': existing_user.PAYMENT_STATUS,
        'access': 'released'
    }