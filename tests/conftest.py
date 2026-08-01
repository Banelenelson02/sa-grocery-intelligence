import pytest
import pandas as pd


@pytest.fixture
def messy_prices_df():
    return pd.DataFrame([
        {
            "store_name": "Pick n Pay",
            "product_name": "Albany White Bread 700g",
            "price_zar": 23.99,
            "recorded_at": pd.Timestamp("2026-07-01"),
            "source": "open_price_engine"
        },
        {
            "store_name": "pick n pay",
            "product_name": "Full Cream Milk 2L",
            "price_zar": 32.99,
            "recorded_at": pd.Timestamp("2026-07-01"),
            "source": "open_price_engine"
        },
        {
            "store_name": "Checkers",
            "product_name": "Sunflower Oil 2L",
            "price_zar": None,
            "recorded_at": pd.Timestamp("2026-07-01"),
            "source": "businesstech"
        },
        {
            "store_name": "Shoprite",
            "product_name": "Eggs 6-pack",
            "price_zar": 0.00,
            "recorded_at": pd.Timestamp("2026-07-01"),
            "source": "businesstech"
        },
        {
            "store_name": "SPAR",
            "product_name": "Maize Meal 5kg",
            "price_zar": 99999.99,
            "recorded_at": pd.Timestamp("2026-07-01"),
            "source": "businesstech"
        },
        {
            "store_name": "Pick n Pay",
            "product_name": "Albany White Bread 700g",
            "price_zar": 23.99,
            "recorded_at": pd.Timestamp("2026-07-01"),
            "source": "open_price_engine"
        },
        {
            "store_name": "RandomShop",
            "product_name": "Butter 500g",
            "price_zar": 45.99,
            "recorded_at": pd.Timestamp("2026-07-01"),
            "source": "businesstech"
        },
        {
            "store_name": "Woolworths",
            "product_name": "Butter 500g",
            "price_zar": 55.99,
            "recorded_at": pd.Timestamp("2099-01-01"),
            "source": "open_price_engine"
        },
    ])
