from fastapi import HTTPException, status

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date

from equigest.models.mares import Mare

from equigest.enums.enums import DeleteType

from equigest.infra.redis_client import async_redis_client

def get_birth_forecast(
    pregnancy_date: datetime
) -> datetime:
    return pregnancy_date + timedelta(days=335)

def get_p4_schedule(
    pregnancy_date: datetime
) -> list[datetime]:
    schedule = []

    current_date = pregnancy_date
    end_date = pregnancy_date + timedelta(days=105)

    while current_date <= end_date:
        schedule.append(current_date)
        current_date += timedelta(days=15)
    
    return schedule

def get_herpes_vaccine_schedule(
    pregnancy_date: datetime
) -> list[datetime]:
    return [
        pregnancy_date + relativedelta(months=5),
        pregnancy_date + relativedelta(months=7),
        pregnancy_date + relativedelta(months=9)
    ]

def get_managment_schedule(
    pregnancy_date: datetime
) -> dict[str, list[datetime]]:
    return {
        'herpes_vaccine': get_herpes_vaccine_schedule(pregnancy_date),
        "birth_forecast": get_birth_forecast(pregnancy_date),
        "P4": get_p4_schedule(pregnancy_date),
    }

def is_in_p4_range(pregnancy_date: datetime, start_date: date, end_date: date) -> bool:
    return any(start_date <= d.date() <= end_date for d in get_p4_schedule(pregnancy_date))

def is_in_herpes_range(pregnancy_date: datetime, start_date: date, end_date: date) -> bool:
    return any(start_date <= d.date() <= end_date for d in get_herpes_vaccine_schedule(pregnancy_date))

def check_mare_ownership(mare: Mare, user_id: int):
    if mare.user_owner != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You're not allowed to access this mare."
        )
    
async def update_success_or_fail_counters(user_id: int, delete_type: DeleteType):
    if delete_type == DeleteType.SUCCESS_PREGNANCY:
        await async_redis_client.hincryby_fields(
            f"user:{user_id}",
            successful_pregnancies=1,
            pregnancies_in_progress=-1
        )
    else:
        await async_redis_client.hincryby_fields(
            f"user:{user_id}",
            failed_pregnancies=1,
            pregnancies_in_progress=-1
        )