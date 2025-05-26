from typing import Optional

from datetime import datetime

from sqlalchemy import DateTime, func, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from equigest.infra.database import mapper_registry
from equigest.enums.enums import MareType

@mapper_registry.mapped_as_dataclass
class Mare:
    __tablename__ = 'mares'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    mare_name: Mapped[str]
    mare_type: Mapped[MareType] = mapped_column(Enum(MareType))
    stallion_name: Mapped[str]
    user_owner: Mapped[int] = mapped_column(
        ForeignKey('users.id')
    )
    donor_name: Mapped[Optional[str]]
    pregnancy_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    active_pregnancy: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default=func.now()
    )
