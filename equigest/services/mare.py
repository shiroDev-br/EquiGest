from typing import Annotated

from fastapi import Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from equigest.infra.session import get_session

from equigest.models.mares import Mare
from equigest.schemas.mare import MareCreateOrEditSchema

from equigest.utils.mare import check_mare_ownership

class MareService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_mare(
        self,
        mare: MareCreateOrEditSchema,
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
    
    async def edit_mare(
        self,
        mare_name: str,
        mare: MareCreateOrEditSchema,
        user_id: int,
    ) -> Mare:
        existing_mare = self.get_mare(mare_name, user_id)

        for field, value in mare.model_dump(excldue_unset=True).items():
            setattr(existing_mare, field, value)

        return existing_mare
    
    async def get_mare(
        self,
        mare_name: str,
        user_id: int
    ) -> Mare:
        mare = await self.session.scalar(
            select(Mare).where(Mare.mare_name == mare_name)
        )
        if not mare:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Mare with name "{mare_name}" not found'
            )

        check_mare_ownership(mare, user_id)
        return mare

def get_mare_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MareService:
    return MareService(session)