"""Client for the Open Price Engine v1 API.

The API key is sent in the Authorization header without a Bearer prefix.
"""
from datetime import date, timedelta
import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


class OpenPriceEngineError(Exception):
    """Base exception for Open Price Engine client errors."""


class OPEAuthError(OpenPriceEngineError):
    """Raised when the API key is missing, invalid, or unauthorized."""


class OPEAccessError(OpenPriceEngineError):
    """Raised when the API plan does not allow a requested store or product."""


class OPERateLimitError(OpenPriceEngineError):
    """Raised when rate-limit retries are exhausted."""


class OPERequestError(OpenPriceEngineError):
    """Raised for unexpected API responses and network failures."""


class OpenPriceEngineClient:
    BASE_URL = "https://openpricengine.com/api/v1"
    SOURCE = "open_price_engine"
    PRICE_COLUMNS = [
        "store_name", "product_name", "price_zar", "recorded_at", "source"
    ]

    def __init__(self, api_key: str | None = None, timeout: int = 20):
        self.api_key = api_key or os.getenv("OPE_API_KEY")
        if not self.api_key:
            raise ValueError("OPE_API_KEY not found. Add it to your local .env file.")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Authorization": self.api_key, "Accept": "application/json"})

    def _get(self, path: str, params: dict, max_retries: int = 2,
             backoff_seconds: int = 2):
        for attempt in range(max_retries + 1):
            try:
                response = self.session.get(
                    f"{self.BASE_URL}{path}", params=params, timeout=self.timeout
                )
            except requests.exceptions.Timeout as exc:
                raise OPERequestError(f"Open Price Engine request timed out: {exc}") from exc
            except requests.exceptions.RequestException as exc:
                raise OPERequestError(f"Open Price Engine request failed: {exc}") from exc

            if response.status_code == 401:
                raise OPEAuthError("401 Unauthorized. Check that OPE_API_KEY is valid.")
            if response.status_code == 403:
                try:
                    detail = response.json().get("detail", response.text)
                except ValueError:
                    detail = response.text
                raise OPEAccessError(
                    f"Open Price Engine plan restriction: {detail}"
                )
            if response.status_code == 429:
                if attempt >= max_retries:
                    raise OPERateLimitError(
                        f"429 rate limit exceeded after {max_retries} retries."
                    )
                time.sleep(backoff_seconds * (attempt + 1))
                continue
            if not response.ok:
                raise OPERequestError(
                    f"Open Price Engine returned HTTP {response.status_code}: "
                    f"{response.text[:500]}"
                )
            try:
                return response.json()
            except ValueError as exc:
                raise OPERequestError("Open Price Engine returned invalid JSON.") from exc

        raise OPERateLimitError("Open Price Engine rate limit retries exhausted.")

    def search_products(self, store: str, search: str,
                        page: int = 1, page_size: int = 20) -> list[str]:
        """Return exact product names available to this API key for a store."""
        if not store.strip() or not search.strip():
            raise ValueError("Both store and search must be non-empty.")
        if page < 1 or not 1 <= page_size <= 100:
            raise ValueError("page must be >= 1 and page_size must be between 1 and 100.")

        data = self._get(
            "/stores/products/names",
            {"stores": store, "search": search, "page": page, "page_size": page_size},
        )
        if not isinstance(data, dict):
            raise OPERequestError("Unexpected product search response format.")
        store_data = next(iter(data.values()), {})
        if not isinstance(store_data, dict):
            return []
        return store_data.get("products", [])

    def fetch_prices(self, product: str, store: str = "Pick n Pay",
                     start_date: str | None = None, end_date: str | None = None,
                     currency: str = "ZAR", max_retries: int = 2,
                     backoff_seconds: int = 2) -> pd.DataFrame:
        """Fetch daily historical prices for an exact product and store."""
        if not product.strip() or not store.strip():
            raise ValueError("Both product and store must be non-empty.")

        end = date.fromisoformat(end_date) if end_date else date.today()
        start = date.fromisoformat(start_date) if start_date else end - timedelta(days=29)
        if start > end:
            raise ValueError("start_date must be on or before end_date.")

        data = self._get(
            "/search/prices/query",
            [
                ("stores", store),
                ("productname", product),
                ("start_date", start.isoformat()),
                ("end_date", end.isoformat()),
                ("currency", currency),
            ],
            max_retries=max_retries,
            backoff_seconds=backoff_seconds,
        )
        if not isinstance(data, list):
            raise OPERequestError("Unexpected price search response format.")

        rows = []
        for item in data:
            store_name = item.get("Store", store)
            product_name = item.get("Product Name", product)
            for point in item.get("Price over time", []):
                try:
                    price = float(point["Price"])
                    recorded_at = pd.to_datetime(point["Date"], errors="raise")
                except (KeyError, TypeError, ValueError) as exc:
                    raise OPERequestError(
                        f"Invalid price observation returned for {product_name}: {exc}"
                    ) from exc
                rows.append({
                    "store_name": store_name,
                    "product_name": product_name,
                    "price_zar": price,
                    "recorded_at": recorded_at,
                    "source": self.SOURCE,
                })

        return pd.DataFrame(rows, columns=self.PRICE_COLUMNS)
