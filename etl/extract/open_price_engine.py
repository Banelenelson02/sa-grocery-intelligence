import time
import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class OpenPriceEngineError(Exception):
    """Base exception for all Open Price Engine client errors."""
    pass


class OPEAuthError(OpenPriceEngineError):
    """Raised on 401 — invalid or expired API key."""
    pass


class OPERateLimitError(OpenPriceEngineError):
    """Raised when rate limit retries are exhausted."""
    pass


class OPERequestError(OpenPriceEngineError):
    """Raised on unexpected non-200 responses or timeouts."""
    pass


class OpenPriceEngineClient:
    BASE_URL = "https://api.openpricengine.com"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPE_API_KEY")
        if not self.api_key:
            raise ValueError("OPE_API_KEY not found")

    def fetch_prices(self, product: str, max_retries: int = 2, backoff_seconds: int = 60) -> pd.DataFrame:
        attempt = 0
        while True:
            try:
                response = requests.get(
                    f"{self.BASE_URL}/products",
                    params={"product": product},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10
                )
            except requests.exceptions.Timeout:
                raise OPERequestError(f"Request timed out after 10s for product '{product}'")
            except requests.exceptions.RequestException as e:
                raise OPERequestError(f"Request failed: {e}")

            if response.status_code == 401:
                raise OPEAuthError("401 Unauthorized — check your OPE_API_KEY")

            if response.status_code == 429:
                if attempt >= max_retries:
                    raise OPERateLimitError(
                        f"429 Rate limit exceeded — gave up after {max_retries} retries"
                    )
                attempt += 1
                time.sleep(backoff_seconds)
                continue

            if response.status_code != 200:
                raise OPERequestError(f"Unexpected status code: {response.status_code}")

            break

        data = response.json()
        if not data:
            return pd.DataFrame(columns=[
                "store_name", "product_name", "price_zar",
                "recorded_at", "source"
            ])

        rows = []
        for item in data:
            store = item.get("Store", "")
            product_name = item.get("Product Name", "")
            for price_point in item.get("Price over time", []):
                rows.append({
                    "store_name": store,
                    "product_name": product_name,
                    "price_zar": float(price_point["Price"]),
                    "recorded_at": pd.to_datetime(price_point["Date"]),
                    "source": "open_price_engine"
                })
        return pd.DataFrame(rows)