from typing import Annotated

from datetime import datetime, timezone

from fastapi import HTTPException, status, Depends

from equigest.models.user import User

from equigest.services.user import (
    UserService,
    get_user_service
)

from equigest.utils.security.oauth_token import get_current_user

from equigest.enums.enums import PaymentAccessStatus

async def validate_paid_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    existing_user = await user_service.update_payment_status(current_user, datetime.now(timezone.utc))

    if existing_user.payment_status == PaymentAccessStatus.DEFEATED:
        raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail='System access time expired. Make payment to resume use',
        headers={'X-Payment-Required': 'true'}
    )

    return existing_user