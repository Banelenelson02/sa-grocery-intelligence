from dataclasses import dataclass
import pandas as pd
from datetime import datetime

CANONICAL_STORES = [
    "Shoprite", "Checkers", "Pick n Pay", "Woolworths",
    "SPAR", "Boxer", "Food Lover's Market",
    "Cambridge Food", "Makro", "Usave"
]


@dataclass
class ValidationReport:
    valid: pd.DataFrame
    rejected: list 


def validate_prices(df: pd.DataFrame) -> ValidationReport:
    valid_rows = []
    rejected_rows = []
    seen = set()

    for _, row in df.iterrows():
        reason = _check_row(row, seen)
        if reason:
            rejected_rows.append({"row": row.to_dict(), "reason": reason})
        else:
            key = (row["store_name"], row["product_name"],
                   str(row["recorded_at"])[:10])
            seen.add(key)
            valid_rows.append(row)

    return ValidationReport(
        valid=pd.DataFrame(valid_rows).reset_index(drop=True),
        rejected=rejected_rows
    )


def _check_row(row, seen: set) -> str | None:
    if pd.isnull(row["price_zar"]):
        return "null price"
    if row["price_zar"] <= 0 or row["price_zar"] > 5000:
        return "impossible price"
    if row["recorded_at"] > pd.Timestamp.today():
        return "future date"
    if row["store_name"] not in CANONICAL_STORES:
        return "unknown store"
    key = (row["store_name"], row["product_name"], str(row["recorded_at"])[:10])
    if key in seen:
        return "duplicate"
    return None