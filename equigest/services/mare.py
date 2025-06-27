from fastapi import Depends, HTTPException, status

from fastapi_pagination import Params, Page

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import date, timedelta

from equigest.infra.session import get_session

from equigest.models.mares import Mare
from equigest.schemas.mare import MareCreateOrEditSchema

from equigest.enums.enums import MareType

from equigest.utils.mare import get_managment_schedule

class MareService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
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
        existing_mare = await self.get_mare(mare_name, user_id)

        for field, value in mare.model_dump(exclude_unset=True).items():
            setattr(existing_mare, field, value)

        await self.session.commit()
        await self.session.refresh(existing_mare)

        return existing_mare

    async def get_mares(
        self,
        user_id: int,
        mare_type: MareType,
        params: Params
    ) -> list[Mare]:
        query = select(Mare).where(
            Mare.user_owner == user_id,
            Mare.mare_type == mare_type
        )

        total_result = await self.session.execute(query)
        total = total_result.scalars().all()
        total_count = len(total)

        offset = (params.page - 1) * params.size
        limit = params.size

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        items = result.scalars().all()

        for mare in items:
            management_schedule = get_managment_schedule(mare.pregnancy_date)
            if mare.mare_type == MareType.HEADQUARTERS:
                management_schedule.pop("P4")
            
            setattr(mare, "management_schedule", management_schedule)

        return Page.create(items, total=total_count, params=params)


    async def get_mare_by_earlist(
        self,
        earlist_pregnancy: date,
        end: date,
        user_id: int,
        params: Params
    ) -> list[Mare]:

        query = select(Mare).where(
                Mare.pregnancy_date.between(
                    earlist_pregnancy,
                    end
                ),
                Mare.user_owner == user_id
            )

        total_result = await self.session.execute(query)
        total = total_result.scalars().all()
        total_count = len(total)

        offset = (params.page - 1) * params.size
        limit = params.size

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        items = result.scalars().all()

        return Page.create(items, total=total_count, params=params)

    async def get_mare_birthforecast(
        self,
        start: date,
        end: date,
        user_id: int,
        params: Params
    ) -> list[Mare]:

        query = select(Mare).where(
            Mare.pregnancy_date + timedelta(days=335) >= start,
            Mare.pregnancy_date + timedelta(days=335) <= end,
            Mare.user_owner == user_id
        )

        total_result = await self.session.execute(query)
        total = total_result.scalars().all()
        total_count = len(total)

        offset = (params.page - 1) * params.size
        limit = params.size

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        items = result.scalars().all()

        return Page.create(items, total=total_count, params=params)

    async def get_mare(
        self,
        mare_name: str,
        user_id: int
    ) -> Mare:
        mare = await self.session.scalar(
            select(Mare).where(Mare.mare_name == mare_name, Mare.user_owner == user_id)
        )
        if not mare:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Mare with name "{mare_name}" not found'
            )
        return mare
        
    async def delete_mare(
            self,
            mare_name: str,
            user_id: int
    ) -> dict:
        mare = await self.get_mare(mare_name, user_id)
        await self.session.delete(mare)
        await self.session.commit()

        return {"status": "deleted"}