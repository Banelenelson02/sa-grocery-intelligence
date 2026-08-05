from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.db import get_db
from api.schemas import PricePoint
from typing import List

router = APIRouter()


@router.get("", response_model=List[PricePoint])
def get_price_trends(
    product_id: int = Query(..., gt=0, description="Product ID to query"),
    weeks: int = Query(12, ge=1, le=52, description="Number of weeks of history"),
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            recorded_at,
            store_name,
            price_zar,
            ROUND(
                (price_zar - LAG(price_zar) OVER (
                    PARTITION BY store_name
                    ORDER BY recorded_at
                )) / NULLIF(LAG(price_zar) OVER (
                    PARTITION BY store_name
                    ORDER BY recorded_at
                ), 0) * 100,
                2
            ) AS week_over_week_change
        FROM prices
        WHERE product_id = :product_id
        AND recorded_at >= NOW() - INTERVAL ':weeks weeks'
        ORDER BY store_name, recorded_at
    """)

    result = db.execute(query, {
        "product_id": product_id,
        "weeks": weeks
    })

    rows = result.fetchall()
    return [
        PricePoint(
            recorded_at=row.recorded_at,
            store_name=row.store_name,
            price_zar=row.price_zar,
            week_over_week_change=row.week_over_week_change
        )
        for row in rows
    ] if rows else []