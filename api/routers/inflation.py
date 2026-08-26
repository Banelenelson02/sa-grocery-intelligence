from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.db import get_db
from api.schemas import InflationPoint
from typing import List, Optional

router = APIRouter()


@router.get("", response_model=List[InflationPoint])
def get_inflation(
    months: int = Query(6, ge=1, le=36, description="Number of months of history"),
    store_name: Optional[str] = Query(None, description="Filter to a single store, e.g. 'Pick n Pay'"),
    db: Session = Depends(get_db)
):
    query = text("""
        WITH monthly AS (
            SELECT
                DATE_TRUNC('month', p.recorded_at) AS month,
                pr.category AS category,
                AVG(p.price_zar) AS avg_price_zar
            FROM prices p
            JOIN products pr ON pr.id = p.product_id
            WHERE p.recorded_at >= NOW() - INTERVAL ':months months'
            AND pr.category IS NOT NULL
            AND (:store_name IS NULL OR p.store_name = :store_name)
            GROUP BY DATE_TRUNC('month', p.recorded_at), pr.category
        )
        SELECT
            month,
            category,
            ROUND(avg_price_zar, 2) AS avg_price_zar,
            ROUND(
                (avg_price_zar - LAG(avg_price_zar) OVER (
                    PARTITION BY category ORDER BY month
                )) / NULLIF(LAG(avg_price_zar) OVER (
                    PARTITION BY category ORDER BY month
                ), 0) * 100,
                2
            ) AS pct_change
        FROM monthly
        ORDER BY category, month
    """)

    result = db.execute(query, {"months": months, "store_name": store_name})
    rows = result.fetchall()

    return [
        InflationPoint(
            month=row.month,
            category=row.category,
            avg_price_zar=row.avg_price_zar,
            pct_change=row.pct_change
        )
        for row in rows
    ]