import pandas as pd
from etl.extract.open_price_engine import OpenPriceEngineClient
from etl.extract.businesstech import BusinessTechParser
from etl.transform.normalize import normalize_dataframe
from etl.transform.clean import validate_prices
from etl.load.postgres_loader import PostgresLoader
import os
from dotenv import load_dotenv

load_dotenv()

PRODUCTS_TO_FETCH = [
    "bread", "milk", "eggs", "maize meal",
    "sunflower oil", "butter", "rice", "sugar"
]

BUSINESSTECH_CSV = "data/raw/businesstech_basket_latest.csv"


def run_pipeline() -> dict:
    print("Starting pipeline run...")

    # ── EXTRACT ──────────────────────────────────────────
    ope_client = OpenPriceEngineClient()
    raw_frames = []

    for product in PRODUCTS_TO_FETCH:
        try:
            df = ope_client.fetch_prices(product=product)
            raw_frames.append(df)
            print(f"  Extracted {len(df)} rows for '{product}'")
        except Exception as e:
            print(f"  Warning: could not fetch '{product}': {e}")

    bt_parser = BusinessTechParser()
    if os.path.exists(BUSINESSTECH_CSV):
        try:
            bt_df = bt_parser.load(BUSINESSTECH_CSV)
            raw_frames.append(bt_df)
            print(f"  Extracted {len(bt_df)} rows from BusinessTech CSV")
        except Exception as e:
            print(f"  Warning: could not load BusinessTech CSV: {e}")
    else:
        print(f"  Skipping BusinessTech CSV (not found at {BUSINESSTECH_CSV})")

    if not raw_frames:
        print("No data extracted. Exiting.")
        return {"inserted": 0, "duplicates_skipped": 0,
                "failed": 0, "rejected": 0}

    raw_df = pd.concat(raw_frames, ignore_index=True)
    print(f"Total extracted: {len(raw_df)} rows")

    # ── TRANSFORM ─────────────────────────────────────────
    try:
        normalized_df = normalize_dataframe(raw_df)
        print(f"Normalized: {len(normalized_df)} rows")
    except Exception as e:
        print(f"Normalization failed: {e}")
        return {"inserted": 0, "duplicates_skipped": 0,
                "failed": len(raw_df), "rejected": 0}

    # ── VALIDATE ──────────────────────────────────────────
    report = validate_prices(normalized_df)
    print(f"Valid: {len(report.valid)} | Rejected: {len(report.rejected)}")

    for r in report.rejected:
        print(f"  Rejected — {r['reason']}: {r['row'].get('product_name', '?')}")

    if report.valid.empty:
        print("All rows rejected. Nothing to load.")
        return {"inserted": 0, "duplicates_skipped": 0,
                "failed": 0, "rejected": len(report.rejected)}

    # ── LOAD ──────────────────────────────────────────────
    loader = PostgresLoader()
    summary = loader.load(report.valid)
    summary["rejected"] = len(report.rejected)

    print(f"Pipeline complete: {summary}")
    return summary


if __name__ == "__main__":
    run_pipeline()