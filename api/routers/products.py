from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional

from api.db import get_db
from api.schemas import Product

router = APIRouter()


@router.get("", response_model=List[Product])
def get_products(
    search: Optional[str] = Query(None, min_length=1, max_length=200),
    category: Optional[str] = Query(None, max_length=80),
    db: Session = Depends(get_db),
):
    """Return products with their latest available cross-store price summary."""
    query = text("""
        SELECT
            p.id,
            p.name,
            p.unit,
            p.category,
            p.subcategory,
            low.price_zar AS lowest_price_zar,
            low.store_name AS lowest_price_store,
            COALESCE(stats.store_count, 0) AS store_count,
            COALESCE(stats.price_records, 0) AS price_records
        FROM products AS p
        LEFT JOIN LATERAL (
            SELECT latest.store_name, latest.price_zar
            FROM (
                SELECT DISTINCT ON (store_name)
                    store_name, price_zar, recorded_at
                FROM prices
                WHERE product_id = p.id
                ORDER BY store_name, recorded_at DESC, id DESC
            ) AS latest
            ORDER BY latest.price_zar ASC, latest.store_name
            LIMIT 1
        ) AS low ON TRUE
        LEFT JOIN LATERAL (
            SELECT
                COUNT(DISTINCT store_name) AS store_count,
                COUNT(*) AS price_records
            FROM prices
            WHERE product_id = p.id
        ) AS stats ON TRUE
        WHERE
            (:search IS NULL OR p.name ILIKE '%' || :search || '%')
            AND (:category IS NULL OR p.category = :category)
        ORDER BY p.category NULLS LAST, p.name
    """)
    rows = db.execute(query, {
        "search": search.strip() if search else None,
        "category": category,
    }).mappings().all()
    return [Product(**dict(row)) for row in rows]
