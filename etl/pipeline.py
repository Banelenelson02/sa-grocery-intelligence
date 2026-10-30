import os
import pandas as pd
from dotenv import load_dotenv

from etl.extract.open_price_engine import OpenPriceEngineClient, OPEAccessError
from etl.extract.businesstech import BusinessTechParser
from etl.transform.normalize import normalize_dataframe
from etl.transform.clean import validate_prices
from etl.load.postgres_loader import PostgresLoader

load_dotenv()

# These are exact product names confirmed through the free-tier product search.
# Override with a comma-separated OPE_PRODUCTS value in the local .env file.
DEFAULT_OPE_PRODUCTS = [
    "PnP UHT Full Cream Milk 1L",
    "PnP Large Eggs 30 Pack",
    "McCain Savoury Rice 400g",
]
OPE_STORE = os.getenv("OPE_STORE", "Pick n Pay")
PRODUCTS_TO_FETCH = [
    product.strip()
    for product in os.getenv("OPE_PRODUCTS", ",".join(DEFAULT_OPE_PRODUCTS)).split(",")
    if product.strip()
]
OPE_START_DATE = os.getenv("OPE_START_DATE")
OPE_END_DATE = os.getenv("OPE_END_DATE")
BUSINESSTECH_CSV = "data/raw/businesstech_basket_latest.csv"


def run_pipeline() -> dict:
    print("Starting pipeline run...")
    ope_client = OpenPriceEngineClient()
    raw_frames = []

    for product in PRODUCTS_TO_FETCH:
        try:
            df = ope_client.fetch_prices(
                product=product,
                store=OPE_STORE,
                start_date=OPE_START_DATE,
                end_date=OPE_END_DATE,
            )
            raw_frames.append(df)
            print(f"  Extracted {len(df)} rows for '{product}' from {OPE_STORE}")
        except OPEAccessError as exc:
            print(f"  Skipping restricted product '{product}': {exc}")
        except Exception as exc:
            print(f"  Warning: could not fetch '{product}': {exc}")

    if os.path.exists(BUSINESSTECH_CSV):
        try:
            bt_df = BusinessTechParser().load(BUSINESSTECH_CSV)
            raw_frames.append(bt_df)
            print(f"  Extracted {len(bt_df)} rows from BusinessTech CSV")
        except Exception as exc:
            print(f"  Warning: could not load BusinessTech CSV: {exc}")
    else:
        print(f"  Skipping BusinessTech CSV (not found at {BUSINESSTECH_CSV})")

    non_empty_frames = [frame for frame in raw_frames if not frame.empty]
    if not non_empty_frames:
        print("No data extracted. Exiting.")
        return {"inserted": 0, "duplicates_skipped": 0, "failed": 0, "rejected": 0}

    raw_df = pd.concat(non_empty_frames, ignore_index=True)
    print(f"Total extracted: {len(raw_df)} rows")

    try:
        normalized_df = normalize_dataframe(raw_df)
        print(f"Normalized: {len(normalized_df)} rows")
    except Exception as exc:
        print(f"Normalization failed: {exc}")
        return {"inserted": 0, "duplicates_skipped": 0,
                "failed": len(raw_df), "rejected": 0}

    report = validate_prices(normalized_df)
    print(f"Valid: {len(report.valid)} | Rejected: {len(report.rejected)}")
    for rejected in report.rejected:
        print(f"  Rejected — {rejected['reason']}: "
              f"{rejected['row'].get('product_name', '?')}")

    if report.valid.empty:
        print("All rows rejected. Nothing to load.")
        return {"inserted": 0, "duplicates_skipped": 0,
                "failed": 0, "rejected": len(report.rejected)}

    summary = PostgresLoader().load(report.valid)
    summary["rejected"] = len(report.rejected)
    print(f"Pipeline complete: {summary}")
    return summary


if __name__ == "__main__":
    run_pipeline()
