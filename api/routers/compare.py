from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.db import get_db
from api.schemas import StoreRanking
from typing import List

router = APIRouter()


@router.get("", response_model=List[StoreRanking])
def get_store_comparison(
    category: str = Query(..., min_length=1, description="Product category to compare, e.g. 'Staples'"),
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            p.store_name,
            ROUND(AVG(p.price_zar), 2) AS avg_price_zar,
            COUNT(DISTINCT p.product_id) AS product_count
        FROM prices p
        JOIN products pr ON pr.id = p.product_id
        WHERE pr.category = :category
        GROUP BY p.store_name
        ORDER BY avg_price_zar ASC
    """)

    result = db.execute(query, {"category": category})
    rows = result.fetchall()

    return [
        StoreRanking(
            store_name=row.store_name,
            avg_price_zar=row.avg_price_zar,
            product_count=row.product_count,
            rank=i + 1
        )
        for i, row in enumerate(rows)
    ]