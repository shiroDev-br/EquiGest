from fastapi import HTTPException, status

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from equigest.models.mares import Mare

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
        'Herpes Vaccine': get_herpes_vaccine_schedule(pregnancy_date),
        "Birth Forecast": get_birth_forecast(pregnancy_date),
        "P4": get_p4_schedule(pregnancy_date),
    }

def check_mare_ownership(mare: Mare, user_id: int):
    if mare.user_owner != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You're not allowed to access this mare."
        )