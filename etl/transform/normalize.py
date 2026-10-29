import pandas as pd

STORE_NAME_MAP = {
    "pick n pay": "Pick n Pay",
    "pnp": "Pick n Pay",
    "pick n pay stores": "Pick n Pay",
    "checkers": "Checkers",
    "shoprite": "Shoprite",
    "woolworths": "Woolworths",
    "woolies": "Woolworths",
    "spar": "SPAR",
    "food lovers": "Food Lover's Market",
    "food lover's market": "Food Lover's Market",
    "food lovers market": "Food Lover's Market",
    "makro": "Makro",
    "boxer": "Boxer",
    "cambridge food": "Cambridge Food",
    "usave": "Usave",
}


def normalize_store_name(raw: str) -> str:
    clean_raw = raw.strip().lower()
    if clean_raw in STORE_NAME_MAP:
        return STORE_NAME_MAP[clean_raw]
    raise ValueError(f"Unknown store name: {raw}")


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Work on a copy so callers' raw extracted data remains unchanged.
    normalized = df.copy()

    # Keep unknown names unchanged. validate_prices() can then reject those
    # individual rows without aborting normalization of the whole batch.
    def normalize_or_preserve(raw: str) -> str:
        try:
            return normalize_store_name(raw)
        except (AttributeError, ValueError):
            return raw

    normalized["store_name"] = normalized["store_name"].apply(normalize_or_preserve)
    normalized["recorded_at"] = pd.to_datetime(normalized["recorded_at"])
    return normalized
