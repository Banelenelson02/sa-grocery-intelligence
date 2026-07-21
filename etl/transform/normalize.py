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
    df["store_name"] = df["store_name"].apply(normalize_store_name)
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])
    return df