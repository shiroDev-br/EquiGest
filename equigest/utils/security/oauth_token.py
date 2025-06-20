from typing import Annotated

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer

import jwt
import datetime

from equigest.settings import Settings
from equigest.services.user import (
    UserService,
)


settings = Settings()
SECRET_KEY = settings.SECRET_KEY

oauth2_scheme = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    to_encode.update({'exp': expiration_time})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    user_service: Annotated[UserService, Depends()],
    credentials: Annotated[str, Depends(oauth2_scheme)],
):
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload: dict = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject_username = payload.get('sub')

        if not subject_username:
            raise credentials_exception
    except jwt.DecodeError:
        raise credentials_exception

    user = await user_service.get_user(subject_username)

    if user is None:
        raise credentials_exception

    return user