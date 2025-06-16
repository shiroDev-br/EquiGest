from pydantic import BaseModel
from datetime import date

from fastapi import Query


class MareQueryParams(BaseModel):
    start_date: date = Query(..., description="Data inicial do intervalo")
    end_date: date = Query(..., description="Data final do intervalo")
    page: int = Query(1, ge=1, description="Número da página")
    size: int = Query(10, ge=1, le=100, description="Itens por página")

class MareQueryByBirthForecastParams(BaseModel):
    mare_type: str
    page: int = Query(1, ge=1, description="Número da página")
    size: int = Query(10, ge=1, le=100, description="Itens por página")
