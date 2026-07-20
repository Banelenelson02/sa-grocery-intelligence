import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class OpenPriceEngineClient:
    BASE_URL = "https://api.openpricengine.com"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPE_API_KEY")
        if not self.api_key:
            raise ValueError("OPE_API_KEY not found")

    def fetch_prices(self, product: str) -> pd.DataFrame:
        response = requests.get(
            f"{self.BASE_URL}/products",
            params={"product": product},
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10
        )

        if response.status_code == 401:
            raise Exception("401 Unauthorized — check your OPE_API_KEY")

        if response.status_code == 429:
            raise Exception("429 Rate limit exceeded — try again later")

        if response.status_code != 200:
            raise Exception(f"Unexpected status code: {response.status_code}")

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