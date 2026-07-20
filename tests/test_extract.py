import pytest
import pandas as pd
from unittest.mock import patch, MagicMock


class TestOpenPriceEngineClient:

    def test_returns_dataframe_with_required_columns(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        sample_response = [{
            "Country": "South Africa",
            "Currency": "ZAR",
            "Store": "Pick n Pay",
            "Product Name": "Albany Superior White Bread 700g",
            "Category": "Bakery",
            "Price over time": [
                {"Date": "2026-07-01", "Price": 23.99},
                {"Date": "2026-07-07", "Price": 24.49},
            ]
        }]

        with patch("etl.extract.open_price_engine.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = sample_response

            client = OpenPriceEngineClient(api_key="test-key")
            df = client.fetch_prices(product="bread")

            required_cols = ["store_name", "product_name", "price_zar",
                             "recorded_at", "source"]
            for col in required_cols:
                assert col in df.columns, f"Missing column: {col}"

    def test_source_column_is_always_open_price_engine(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        sample_response = [{
            "Store": "Pick n Pay",
            "Product Name": "Bread",
            "Price over time": [{"Date": "2026-07-01", "Price": 23.99}]
        }]

        with patch("etl.extract.open_price_engine.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = sample_response

            client = OpenPriceEngineClient(api_key="test-key")
            df = client.fetch_prices(product="bread")

            assert (df["source"] == "open_price_engine").all()

    def test_handles_401_unauthorized(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        with patch("etl.extract.open_price_engine.requests.get") as mock_get:
            mock_get.return_value.status_code = 401

            client = OpenPriceEngineClient(api_key="bad-key")
            with pytest.raises(Exception, match="401"):
                client.fetch_prices(product="bread")

    def test_handles_429_rate_limit(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        with patch("etl.extract.open_price_engine.requests.get") as mock_get:
            mock_get.return_value.status_code = 429

            client = OpenPriceEngineClient(api_key="test-key")
            with pytest.raises(Exception):
                client.fetch_prices(product="bread")

    def test_empty_response_returns_empty_dataframe(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        with patch("etl.extract.open_price_engine.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = []

            client = OpenPriceEngineClient(api_key="test-key")
            df = client.fetch_prices(product="obscure-product")

            assert len(df) == 0

    def test_price_over_time_expands_to_multiple_rows(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        sample_response = [{
            "Store": "Pick n Pay",
            "Product Name": "Bread",
            "Price over time": [
                {"Date": "2026-07-01", "Price": 23.99},
                {"Date": "2026-07-07", "Price": 24.49},
                {"Date": "2026-07-14", "Price": 24.49},
            ]
        }]

        with patch("etl.extract.open_price_engine.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = sample_response

            client = OpenPriceEngineClient(api_key="test-key")
            df = client.fetch_prices(product="bread")

            assert len(df) == 3

    def test_recorded_at_is_datetime_not_string(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        sample_response = [{
            "Store": "Pick n Pay",
            "Product Name": "Bread",
            "Price over time": [{"Date": "2026-07-01", "Price": 23.99}]
        }]

        with patch("etl.extract.open_price_engine.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = sample_response

            client = OpenPriceEngineClient(api_key="test-key")
            df = client.fetch_prices(product="bread")

            assert pd.api.types.is_datetime64_any_dtype(df["recorded_at"])


class TestBusinessTechParser:

    def test_loads_csv_into_dataframe(self, tmp_path):
        from etl.extract.businesstech import BusinessTechParser

        csv_content = "store,product,price_zar,recorded_month,category\nMakro,Bread 700g,19.99,2026-07-01,Staples\n"
        csv_file = tmp_path / "bt.csv"
        csv_file.write_text(csv_content)

        parser = BusinessTechParser()
        df = parser.load(str(csv_file))

        assert len(df) == 1
        assert df.iloc[0]["store"] == "Makro"

    def test_source_column_is_businesstech(self, tmp_path):
        from etl.extract.businesstech import BusinessTechParser

        csv_content = "store,product,price_zar,recorded_month,category\nMakro,Bread 700g,19.99,2026-07-01,Staples\n"
        csv_file = tmp_path / "bt.csv"
        csv_file.write_text(csv_content)

        parser = BusinessTechParser()
        df = parser.load(str(csv_file))

        assert (df["source"] == "businesstech").all()

    def test_raises_on_missing_required_column(self, tmp_path):
        from etl.extract.businesstech import BusinessTechParser

        csv_content = "store,product,recorded_month\nMakro,Bread 700g,2026-07-01\n"
        csv_file = tmp_path / "bad.csv"
        csv_file.write_text(csv_content)

        parser = BusinessTechParser()
        with pytest.raises(Exception):
            parser.load(str(csv_file))

    def test_price_zar_is_numeric(self, tmp_path):
        from etl.extract.businesstech import BusinessTechParser

        csv_content = "store,product,price_zar,recorded_month,category\nMakro,Bread 700g,19.99,2026-07-01,Staples\n"
        csv_file = tmp_path / "bt.csv"
        csv_file.write_text(csv_content)

        parser = BusinessTechParser()
        df = parser.load(str(csv_file))

        assert pd.api.types.is_numeric_dtype(df["price_zar"])

    def test_recorded_month_is_datetime(self, tmp_path):
        from etl.extract.businesstech import BusinessTechParser

        csv_content = "store,product,price_zar,recorded_month,category\nMakro,Bread 700g,19.99,2026-07-01,Staples\n"
        csv_file = tmp_path / "bt.csv"
        csv_file.write_text(csv_content)

        parser = BusinessTechParser()
        df = parser.load(str(csv_file))

        assert pd.api.types.is_datetime64_any_dtype(df["recorded_month"])