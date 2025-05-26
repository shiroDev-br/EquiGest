from typing import Annotated

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from equigest.infra.session import get_session

from equigest.moodels.user import User
from equigest.schemas.user import UserCreateSchema

from equigest.services.exceptions import UserAlreadyExists

from equigest.utils.security.hasher import hash_password

class UserService:
    def __init__(self, session: AsyncSession) -> User:
        self.session = session
    
    async def create_user(
        self,
        user: UserCreateSchema
    ):  
        user.password = hash_password(user.password)

        existing_user = await self.session.scalar(
            select(User).where(User.username == user.username)
        )
        if existing_user:
            raise UserAlreadyExists('User already exists')

        new_user = User(
            **user.model_dump()
        )

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return new_user

    async def get_user(self, username: str) -> User:
        user = await self.session.scalar(
            select(User).where(User.username == username)
        )
        return user

def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(session)