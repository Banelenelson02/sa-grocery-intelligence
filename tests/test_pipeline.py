import pytest
import pandas as pd
from unittest.mock import patch, MagicMock


class TestPipeline:

    def test_pipeline_returns_summary_dict(self):
        from etl.pipeline import run_pipeline

        with patch("etl.pipeline.OpenPriceEngineClient") as mock_ope, \
             patch("etl.pipeline.BusinessTechParser"), \
             patch("etl.pipeline.normalize_dataframe") as mock_norm, \
             patch("etl.pipeline.validate_prices") as mock_validate, \
             patch("etl.pipeline.PostgresLoader") as mock_loader, \
             patch("etl.pipeline.os.path.exists", return_value=False):

            mock_ope.return_value.fetch_prices.return_value = pd.DataFrame([{
                "store_name": "Pick n Pay",
                "product_name": "Bread",
                "price_zar": 23.99,
                "recorded_at": pd.Timestamp("2026-07-01"),
                "source": "open_price_engine"
            }])

            valid_df = pd.DataFrame([{
                "store_name": "Pick n Pay",
                "product_name": "Bread",
                "price_zar": 23.99,
                "recorded_at": pd.Timestamp("2026-07-01"),
                "source": "open_price_engine"
            }])

            mock_norm.return_value = valid_df
            mock_validate.return_value = MagicMock(
                valid=valid_df, rejected=[]
            )
            mock_loader.return_value.load.return_value = {
                "inserted": 1,
                "duplicates_skipped": 0,
                "failed": 0
            }

            result = run_pipeline()

            assert "inserted" in result
            assert "rejected" in result
            assert "duplicates_skipped" in result

    def test_pipeline_handles_no_data(self):
        from etl.pipeline import run_pipeline

        with patch("etl.pipeline.OpenPriceEngineClient") as mock_ope, \
             patch("etl.pipeline.os.path.exists", return_value=False):

            mock_ope.return_value.fetch_prices.side_effect = Exception("API down")

            result = run_pipeline()

            assert result["inserted"] == 0

    def test_pipeline_skips_load_when_all_rejected(self):
        from etl.pipeline import run_pipeline

        with patch("etl.pipeline.OpenPriceEngineClient") as mock_ope, \
             patch("etl.pipeline.BusinessTechParser"), \
             patch("etl.pipeline.normalize_dataframe") as mock_norm, \
             patch("etl.pipeline.validate_prices") as mock_validate, \
             patch("etl.pipeline.PostgresLoader") as mock_loader, \
             patch("etl.pipeline.os.path.exists", return_value=False):

            mock_ope.return_value.fetch_prices.return_value = pd.DataFrame([{
                "store_name": "Pick n Pay",
                "product_name": "Bread",
                "price_zar": 23.99,
                "recorded_at": pd.Timestamp("2026-07-01"),
                "source": "open_price_engine"
            }])

            mock_norm.return_value = pd.DataFrame()
            mock_validate.return_value = MagicMock(
                valid=pd.DataFrame(),
                rejected=[{"row": {}, "reason": "null price"}]
            )

            run_pipeline()

            mock_loader.return_value.load.assert_not_called()