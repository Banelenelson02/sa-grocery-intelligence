from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional

from api.db import get_db
from api.schemas import Product

router = APIRouter()


@router.get("", response_model=List[Product])
def get_products(db: Session = Depends(get_db)):
    """Return the product catalogue, including products added by the ETL pipeline."""
    result = db.execute(text("""
        SELECT id, name, category, subcategory
        FROM products
        ORDER BY category NULLS LAST, name
    """))
    return [
        Product(
            id=row.id,
            name=row.name,
            category=row.category,
            subcategory=row.subcategory,
        )
        for row in result.fetchall()
    ]
