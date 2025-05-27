from typing import Annotated

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from equigest.infra.session import get_session

from equigest.models.mares import Mare
from equigest.schemas.mare import MareCreateSchema

class MareService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_mare(
        self,
        mare: MareCreateSchema,
        user_owner_id: int
    ) -> Mare:
        new_mare = Mare(
            **mare.model_dump(),
            user_owner = user_owner_id
        )

        self.session.add(new_mare)
        await self.session.commit()
        await self.session.refresh(new_mare)

        return new_mare
    
    async def get_mare(
        self,
        mare_name: str,
    ) -> Mare:
        mare = await self.session.scalar(
            select(Mare).where(Mare.mare_name == mare_name)
        )
        return mare

def get_mare_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MareService:
    return MareService(session)