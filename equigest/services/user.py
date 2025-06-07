from typing import Annotated

from datetime import datetime, timedelta

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from equigest.infra.session import get_session

from equigest.models.user import User
from equigest.schemas.user import UserCreateSchema

from equigest.services.exceptions import UserAlreadyExists

from equigest.enums.enums import PaymentAccessStatus

from equigest.utils.security.hasher import hash_password
from equigest.utils.security.cryptographer import encrypt_fields

class UserService:
    def __init__(self, session: AsyncSession) -> User:
        self.session = session
        self.sensive_fields = ['cellphone', 'cpf_cnpj']
    
    async def create_user(
        self,
        user: UserCreateSchema
    ):  
        user.password = hash_password(user.password)
        encrypt_fields(user, self.sensive_fields)

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


    async def update_payment_status(
        self,
        user: User,
        now: datetime,
        update_to_paid: bool = False
    ) -> User:
        is_past_due = user.next_payment_date and user.next_payment_date < now

        if user.payment_status == PaymentAccessStatus.PAYED or user.payment_status == PaymentAccessStatus.TRIAL and is_past_due:
            user.payment_status = PaymentAccessStatus.DEFEATED

        if update_to_paid:
            user.payment_status = PaymentAccessStatus.PAYED
            user.next_payment_date += timedelta(days=30)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get_user_by_customer_id(
        self,
        customer_id: int
    ) -> User:
        user = await self.session.scalar(
            select(User).where(User.abacatepay_client_id == customer_id)
        )
        return user

    async def get_user(self, username: str) -> User:
        user = await self.session.scalar(
            select(User).where(User.username == username)
        )
        return user

def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(session)