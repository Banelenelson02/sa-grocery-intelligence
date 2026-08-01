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
    
class TestValidatePrices:

    def test_rejects_null_price(self, messy_prices_df):
        from etl.transform.clean import validate_prices
        report = validate_prices(messy_prices_df)
        assert any("null" in r["reason"].lower()
                   for r in report.rejected)

    def test_rejects_zero_price(self, messy_prices_df):
        from etl.transform.clean import validate_prices
        report = validate_prices(messy_prices_df)
        assert any(r["row"].get("price_zar") == 0.0
                   for r in report.rejected)

    def test_rejects_price_above_ceiling(self, messy_prices_df):
        from etl.transform.clean import validate_prices
        report = validate_prices(messy_prices_df)
        rejected_prices = [r["row"].get("price_zar")
                          for r in report.rejected]
        assert 99999.99 in rejected_prices

    def test_rejects_future_date(self, messy_prices_df):
        from etl.transform.clean import validate_prices
        report = validate_prices(messy_prices_df)
        assert any("future" in r["reason"].lower() or
                   "date" in r["reason"].lower()
                   for r in report.rejected)

    def test_rejects_unknown_store(self, messy_prices_df):
        from etl.transform.clean import validate_prices
        report = validate_prices(messy_prices_df)
        assert any("RandomShop" in str(r["row"])
                   for r in report.rejected)

    def test_removes_duplicates(self, messy_prices_df):
        from etl.transform.clean import validate_prices
        report = validate_prices(messy_prices_df)
        valid = report.valid
        if len(valid) > 0:
            dedup = valid[["store_name", "product_name",
                           "recorded_at"]].duplicated()
            assert not dedup.any()

    def test_valid_rows_are_preserved(self, messy_prices_df):
        from etl.transform.clean import validate_prices
        report = validate_prices(messy_prices_df)
        assert len(report.valid) > 0

    def test_rejected_rows_have_reasons(self, messy_prices_df):
        from etl.transform.clean import validate_prices
        report = validate_prices(messy_prices_df)
        for r in report.rejected:
            assert "reason" in r
            assert len(r["reason"]) > 0

    def test_counts_add_up(self, messy_prices_df):
        from etl.transform.clean import validate_prices
        report = validate_prices(messy_prices_df)
        assert len(report.valid) + len(report.rejected) == len(messy_prices_df)
