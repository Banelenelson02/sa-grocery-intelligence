from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional, List


class PricePoint(BaseModel):
    recorded_at: datetime
    store_name: str
    price_zar: float
    week_over_week_change: Optional[float] = None


class StoreRanking(BaseModel):
    store_name: str
    avg_price_zar: float
    product_count: int
    rank: int


class InflationPoint(BaseModel):
    month: datetime
    category: str
    avg_price_zar: float
    pct_change: Optional[float] = None


class BasketItem(BaseModel):
    product_id: int
    qty: int = 1

    @field_validator("qty")
    @classmethod
    def qty_must_be_positive(cls, v):
        if v < 1:
            raise ValueError("qty must be at least 1")
        return v


class BasketRequest(BaseModel):
    items: List[BasketItem]
    budget: float

    @field_validator("items")
    @classmethod
    def items_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("items list cannot be empty")
        return v

    @field_validator("budget")
    @classmethod
    def budget_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("budget must be greater than 0")
        return v


class StoreBasket(BaseModel):
    store_name: str
    total_zar: float
    items: List[dict] = []


class BasketResponse(BaseModel):
    single_store: StoreBasket
    split_stores: Optional[dict] = None
    saving_zar: Optional[float] = None