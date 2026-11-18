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

    # ── EXTRACT ──────────────────────────────────────────
    raw_frames = []
    extraction_errors = []

    # Treat each source as optional: a missing API key or unavailable service
    # must not prevent the CSV source from being processed.
    try:
        ope_client = OpenPriceEngineClient()
        for product in PRODUCTS_TO_FETCH:
            try:
                df = ope_client.fetch_prices(
                    product=product,
                    store=OPE_STORE,
                    start_date=OPE_START_DATE,
                    end_date=OPE_END_DATE,
                )
                if not df.empty:
                    raw_frames.append(df)
                print(f"  Extracted {len(df)} rows for '{product}' from {OPE_STORE}")
            except OPEAccessError as exc:
                extraction_errors.append(f"Open Price Engine ({product}): {exc}")
                print(f"  Skipping restricted product '{product}': {exc}")
            except Exception as e:
                message = f"Open Price Engine ({product}): {e}"
                extraction_errors.append(message)
                print(f"  Warning: could not fetch '{product}': {e}")
    except Exception as e:
        message = f"Open Price Engine initialization: {e}"
        extraction_errors.append(message)
        print(f"  Warning: {message}")

    if os.path.exists(BUSINESSTECH_CSV):
        try:
            bt_df = BusinessTechParser().load(BUSINESSTECH_CSV)
            if not bt_df.empty:
                raw_frames.append(bt_df)
            print(f"  Extracted {len(bt_df)} rows from BusinessTech CSV")
        except Exception as e:
            message = f"BusinessTech CSV: {e}"
            extraction_errors.append(message)
            print(f"  Warning: could not load BusinessTech CSV: {e}")
    else:
        print(f"  Skipping BusinessTech CSV (not found at {BUSINESSTECH_CSV})")

    if not raw_frames:
        print("No data extracted. Exiting.")
        return {
            "status": "failed",
            "inserted": 0,
            "duplicates_skipped": 0,
            "failed": 0,
            "rejected": 0,
            "extraction_errors": extraction_errors,
        }

    raw_df = pd.concat(raw_frames, ignore_index=True)
    print(f"Total extracted: {len(raw_df)} rows")

    try:
        normalized_df = normalize_dataframe(raw_df)
        print(f"Normalized: {len(normalized_df)} rows")
    except Exception as e:
        print(f"Normalization failed: {e}")
        return {
            "status": "failed",
            "inserted": 0,
            "duplicates_skipped": 0,
            "failed": len(raw_df),
            "rejected": 0,
            "extraction_errors": extraction_errors,
        }

    report = validate_prices(normalized_df)
    print(f"Valid: {len(report.valid)} | Rejected: {len(report.rejected)}")

    for r in report.rejected:
        print(f"  Rejected — {r['reason']}: {r['row'].get('product_name', '?')}")

    if report.valid.empty:
        print("All rows rejected. Nothing to load.")
        return {
            "status": "failed",
            "inserted": 0,
            "duplicates_skipped": 0,
            "failed": 0,
            "rejected": len(report.rejected),
            "extraction_errors": extraction_errors,
        }

    loader = PostgresLoader()
    summary = loader.load(report.valid)
    summary["rejected"] = len(report.rejected)
    summary["extraction_errors"] = extraction_errors
    summary["status"] = (
        "completed_with_warnings" if extraction_errors or report.rejected or summary["failed"]
        else "completed"
    )

    print(f"Pipeline complete: {summary}")
    return summary


if __name__ == "__main__":
    run_pipeline()
