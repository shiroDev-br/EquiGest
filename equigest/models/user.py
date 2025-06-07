from typing import Optional

from datetime import datetime

from sqlalchemy import DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column

from equigest.infra.database import mapper_registry

from equigest.enums.enums import PaymentAccessStatus

@mapper_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    next_payment_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    payment_status: Mapped[PaymentAccessStatus] = mapped_column(
        Enum(PaymentAccessStatus), default=PaymentAccessStatus.TRIAL
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default=func.now()
    )