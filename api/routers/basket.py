from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.db import get_db
from api.schemas import BasketRequest, BasketResponse, StoreBasket

router = APIRouter()


@router.post("", response_model=BasketResponse)
def optimize_basket(
    request: BasketRequest,
    db: Session = Depends(get_db)
):
    product_ids = [item.product_id for item in request.items]
    qty_by_product = {item.product_id: item.qty for item in request.items}

    # Latest known price per (product, store) -- DISTINCT ON keeps only the
    # most recent recorded_at row for each product/store pair.
    query = text("""
        SELECT DISTINCT ON (product_id, store_name)
            product_id, store_name, price_zar
        FROM prices
        WHERE product_id = ANY(:product_ids)
        ORDER BY product_id, store_name, recorded_at DESC
    """)
    rows = db.execute(query, {"product_ids": product_ids}).fetchall()

    # price_matrix[store_name][product_id] = price_zar
    price_matrix: dict[str, dict[int, float]] = {}
    for row in rows:
        # Postgres NUMERIC columns come back as decimal.Decimal, not float --
        # cast here so downstream arithmetic doesn't mix Decimal and float.
        price_matrix.setdefault(row.store_name, {})[row.product_id] = float(row.price_zar)

    # Option A: cheapest single store that stocks every item in the basket.
    single_store = None
    for store_name, prices in price_matrix.items():
        if all(pid in prices for pid in product_ids):
            total = sum(prices[pid] * qty_by_product[pid] for pid in product_ids)
            if single_store is None or total < single_store["total"]:
                single_store = {"store_name": store_name, "total": total}

    single_store_basket = StoreBasket(
        store_name=single_store["store_name"] if single_store else "No single store has every item",
        total_zar=round(single_store["total"], 2) if single_store else 0.0,
        items=[{"product_id": pid, "qty": qty_by_product[pid]} for pid in product_ids]
    )

    # Option B: cheapest store for each item individually, regardless of store count.
    split_total = 0.0
    split_breakdown = []
    for pid in product_ids:
        cheapest_store, cheapest_price = None, None
        for store_name, prices in price_matrix.items():
            if pid in prices and (cheapest_price is None or prices[pid] < cheapest_price):
                cheapest_store, cheapest_price = store_name, prices[pid]
        if cheapest_store is not None:
            line_total = cheapest_price * qty_by_product[pid]
            split_total += line_total
            split_breakdown.append({
                "product_id": pid,
                "store_name": cheapest_store,
                "price_zar": cheapest_price,
                "qty": qty_by_product[pid]
            })

    split_stores = {
        "total_zar": round(split_total, 2),
        "items": split_breakdown
    }

    saving_zar = (
        round(single_store["total"] - split_total, 2)
        if single_store is not None else None
    )

    return BasketResponse(
        single_store=single_store_basket,
        split_stores=split_stores,
        saving_zar=saving_zar
    )