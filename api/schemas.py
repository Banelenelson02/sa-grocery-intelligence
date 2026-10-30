from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List


class Product(BaseModel):
    id: int
    name: str
    unit: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    lowest_price_zar: Optional[float] = None
    lowest_price_store: Optional[str] = None
    store_count: int = 0
    price_records: int = 0


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

    @validator("qty")
    @classmethod
    def qty_must_be_positive(cls, v):
        if v < 1:
            raise ValueError("qty must be at least 1")
        return v


class BasketRequest(BaseModel):
    items: List[BasketItem]
    budget: float

    @validator("items")
    @classmethod
    def items_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("items list cannot be empty")
        return v

    @validator("items")
    @classmethod
    def product_ids_must_be_unique(cls, v):
        product_ids = [item.product_id for item in v]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("each product_id may only appear once")
        return v

    @validator("budget")
    @classmethod
    def budget_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("budget must be greater than 0")
        return v


class StoreBasket(BaseModel):
    store_name: str
    total_zar: float
    items: List[dict] = []
    budget_zar: Optional[float] = None
    within_budget: Optional[bool] = None


class BasketResponse(BaseModel):
    single_store: StoreBasket
    split_stores: Optional[dict] = None
    saving_zar: Optional[float] = None
    budget_zar: Optional[float] = None
    budget_status: str
    recommended_option: Optional[str] = None