from typing import Optional

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from equigest.infra.database import mapped_registry

@mapped_registry.mapped_as_dataclass
class ReceivingMare:
    __tablename__ = 'receiving_mare'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    mare_name: Mapped[str]
    stallion_name: Mapped[str]
    donor_name: Mapped[str]
    pregnancy_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    active_pregnancy: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default=func.now()
    )