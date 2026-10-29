from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from api.db import get_db
from api.schemas import BasketRequest, BasketResponse, StoreBasket

router = APIRouter()


@router.post("", response_model=BasketResponse)
def optimize_basket(
    request: BasketRequest,
    db: Session = Depends(get_db),
):
    product_ids = [item.product_id for item in request.items]
    qty_by_product = {item.product_id: item.qty for item in request.items}
    budget = float(request.budget)

    # Keep the latest recorded price for each product/store combination.
    query = text("""
        SELECT DISTINCT ON (product_id, store_name)
            product_id, store_name, price_zar
        FROM prices
        WHERE product_id = ANY(:product_ids)
        ORDER BY product_id, store_name, recorded_at DESC
    """)
    rows = db.execute(query, {"product_ids": product_ids}).fetchall()

    price_matrix: dict[str, dict[int, float]] = {}
    for row in rows:
        price_matrix.setdefault(row.store_name, {})[row.product_id] = float(row.price_zar)

    # A single-store option is valid only if that store has every requested item.
    single_store = None
    for store_name, prices in price_matrix.items():
        if all(pid in prices for pid in product_ids):
            total = round(sum(prices[pid] * qty_by_product[pid] for pid in product_ids), 2)
            if single_store is None or total < single_store["total"]:
                single_store = {"store_name": store_name, "total": total}

    # Split shopping is complete only when every requested product has a price.
    split_total = 0.0
    split_breakdown = []
    priced_product_ids = set()
    for pid in product_ids:
        cheapest_store, cheapest_price = None, None
        for store_name, prices in price_matrix.items():
            if pid in prices and (cheapest_price is None or prices[pid] < cheapest_price):
                cheapest_store, cheapest_price = store_name, prices[pid]

        if cheapest_store is not None:
            priced_product_ids.add(pid)
            split_total += cheapest_price * qty_by_product[pid]
            split_breakdown.append({
                "product_id": pid,
                "store_name": cheapest_store,
                "price_zar": cheapest_price,
                "qty": qty_by_product[pid],
                "line_total_zar": round(cheapest_price * qty_by_product[pid], 2),
            })

    split_complete = len(priced_product_ids) == len(product_ids)
    split_total = round(split_total, 2)
    single_within_budget = single_store is not None and single_store["total"] <= budget
    split_within_budget = split_complete and split_total <= budget

    single_store_basket = StoreBasket(
        store_name=single_store["store_name"] if single_store else "No single store has every item",
        total_zar=single_store["total"] if single_store else 0.0,
        items=[
            {"product_id": pid, "qty": qty_by_product[pid]}
            for pid in product_ids
        ],
        budget_zar=budget,
        within_budget=single_within_budget,
    )

    split_stores = {
        "total_zar": split_total,
        "items": split_breakdown,
        "complete": split_complete,
        "missing_product_ids": [pid for pid in product_ids if pid not in priced_product_ids],
        "budget_zar": budget,
        "within_budget": split_within_budget,
    }

    # Recommend a complete option that fits the budget, prioritizing the lower total.
    candidates = []
    if single_within_budget:
        candidates.append(("single_store", single_store["total"]))
    if split_within_budget:
        candidates.append(("split_stores", split_total))

    if candidates:
        recommended_option = min(candidates, key=lambda candidate: candidate[1])[0]
        budget_status = "within_budget"
    elif single_store is None and not split_complete:
        recommended_option = None
        budget_status = "missing_prices"
    else:
        recommended_option = None
        budget_status = "over_budget"

    saving_zar = (
        round(single_store["total"] - split_total, 2)
        if single_store is not None and split_complete else None
    )

    return BasketResponse(
        single_store=single_store_basket,
        split_stores=split_stores,
        saving_zar=saving_zar,
        budget_zar=budget,
        budget_status=budget_status,
        recommended_option=recommended_option,
    )
