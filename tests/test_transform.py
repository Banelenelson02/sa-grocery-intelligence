import pytest
import pandas as pd
from etl.transform.normalize import normalize_store_name, normalize_dataframe


class TestNormalizeStoreName:

    def test_normalizes_pick_n_pay_variants(self):
        assert normalize_store_name("pick n pay") == "Pick n Pay"

    def test_normalizes_woolies_to_woolworths(self):
        assert normalize_store_name("woolies") == "Woolworths"

    def test_normalizes_uppercase(self):
        assert normalize_store_name("CHECKERS") == "Checkers"

    def test_strips_whitespace(self):
        assert normalize_store_name("  Shoprite  ") == "Shoprite"

    def test_raises_on_unknown_store(self):
        with pytest.raises(ValueError):
            normalize_store_name("RandomShop")


class TestNormalizeDataframe:

    def test_normalizes_store_names_in_dataframe(self):
        df = pd.DataFrame({
            "store_name": ["pick n pay", "woolies", "CHECKERS"],
            "product_name": ["Bread", "Milk", "Eggs"],
            "price_zar": [20.0, 15.0, 30.0],
            "recorded_at": ["2026-07-01", "2026-07-02", "2026-07-03"]
        })
        result = normalize_dataframe(df)
        assert result["store_name"].tolist() == ["Pick n Pay", "Woolworths", "Checkers"]

    def test_recorded_at_becomes_datetime(self):
        df = pd.DataFrame({
            "store_name": ["pick n pay"],
            "product_name": ["Bread"],
            "price_zar": [20.0],
            "recorded_at": ["2026-07-01"]
        })
        result = normalize_dataframe(df)
        assert pd.api.types.is_datetime64_any_dtype(result["recorded_at"])

    def test_raises_on_unknown_store_in_dataframe(self):
        df = pd.DataFrame({
            "store_name": ["UnknownStore"],
            "product_name": ["Bread"],
            "price_zar": [20.0],
            "recorded_at": ["2026-07-01"]
        })
        with pytest.raises(ValueError):
            normalize_dataframe(df)