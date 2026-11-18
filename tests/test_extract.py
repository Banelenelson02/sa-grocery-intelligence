import pytest
import pandas as pd
from unittest.mock import patch


class TestOpenPriceEngineClient:
    def test_returns_dataframe_with_required_columns(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        sample_response = [{
            "Country": "South Africa",
            "Currency": "ZAR",
            "Store": "Pick n Pay",
            "Product Name": "PnP UHT Full Cream Milk 1L",
            "Price over time": [
                {"Date": "2026-10-01", "Price": 17.99},
                {"Date": "2026-10-02", "Price": 17.99},
            ],
        }]
        with patch("etl.extract.open_price_engine.requests.Session.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = sample_response
            client = OpenPriceEngineClient(api_key="test-key")
            df = client.fetch_prices(
                "PnP UHT Full Cream Milk 1L",
                start_date="2026-10-01",
                end_date="2026-10-30",
            )

        assert list(df.columns) == [
            "store_name", "product_name", "price_zar", "recorded_at", "source"
        ]
        assert len(df) == 2
        assert df.iloc[0]["price_zar"] == 17.99
        mock_get.assert_called_once()
        _, kwargs = mock_get.call_args
        assert kwargs["headers"] if "headers" in kwargs else True

    def test_uses_v1_endpoint_and_authorization_header(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        with patch("etl.extract.open_price_engine.requests.Session.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = []
            client = OpenPriceEngineClient(api_key="secret")
            client.fetch_prices("PnP UHT Full Cream Milk 1L",
                                start_date="2026-10-01", end_date="2026-10-30")
            assert mock_get.call_args.args[0] == (
                "https://openpricengine.com/api/v1/search/prices/query"
            )
            assert client.session.headers["Authorization"] == "secret"
            assert "Bearer" not in client.session.headers["Authorization"]

    def test_sends_store_product_and_date_parameters(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        with patch("etl.extract.open_price_engine.requests.Session.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = []
            client = OpenPriceEngineClient(api_key="test-key")
            client.fetch_prices("PnP Large Eggs 30 Pack", store="Pick n Pay",
                                start_date="2026-10-01", end_date="2026-10-30")
            params = mock_get.call_args.kwargs["params"]
            assert ("stores", "Pick n Pay") in params
            assert ("productname", "PnP Large Eggs 30 Pack") in params
            assert ("start_date", "2026-10-01") in params
            assert ("end_date", "2026-10-30") in params
            assert ("currency", "ZAR") in params

    def test_source_column_is_always_open_price_engine(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        payload = [{"Store": "Pick n Pay", "Product Name": "Milk",
                    "Price over time": [{"Date": "2026-10-01", "Price": 17.99}]}]
        with patch("etl.extract.open_price_engine.requests.Session.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = payload
            df = OpenPriceEngineClient(api_key="test").fetch_prices("Milk")
        assert (df["source"] == "open_price_engine").all()

    def test_handles_401_unauthorized(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient, OPEAuthError

        with patch("etl.extract.open_price_engine.requests.Session.get") as mock_get:
            mock_get.return_value.status_code = 401
            mock_get.return_value.ok = False
            client = OpenPriceEngineClient(api_key="bad-key")
            with pytest.raises(OPEAuthError, match="401"):
                client.fetch_prices("Milk")

    def test_handles_403_plan_restriction(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient, OPEAccessError

        with patch("etl.extract.open_price_engine.requests.Session.get") as mock_get:
            mock_get.return_value.status_code = 403
            mock_get.return_value.ok = False
            mock_get.return_value.json.return_value = {
                "detail": "Free tier has limited product access."
            }
            with pytest.raises(OPEAccessError, match="limited product access"):
                OpenPriceEngineClient(api_key="test").fetch_prices("restricted product")

    def test_handles_429_rate_limit(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient, OPERateLimitError

        with patch("etl.extract.open_price_engine.requests.Session.get") as mock_get, \
             patch("etl.extract.open_price_engine.time.sleep") as mock_sleep:
            mock_get.return_value.status_code = 429
            mock_get.return_value.ok = False
            client = OpenPriceEngineClient(api_key="test")
            with pytest.raises(OPERateLimitError, match="rate limit"):
                client.fetch_prices("Milk", max_retries=2, backoff_seconds=1)
            assert mock_get.call_count == 3
            assert mock_sleep.call_count == 2

    def test_empty_response_returns_empty_dataframe_with_columns(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        with patch("etl.extract.open_price_engine.requests.Session.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = []
            df = OpenPriceEngineClient(api_key="test").fetch_prices("unknown")
        assert df.empty
        assert list(df.columns) == [
            "store_name", "product_name", "price_zar", "recorded_at", "source"
        ]

    def test_expands_price_history_to_rows_and_parses_dates(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        payload = [{"Store": "Pick n Pay", "Product Name": "Milk",
                    "Price over time": [
                        {"Date": "2026-10-01", "Price": 17.99},
                        {"Date": "2026-10-02", "Price": 18.49},
                        {"Date": "2026-10-03", "Price": 18.49},
                    ]}]
        with patch("etl.extract.open_price_engine.requests.Session.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = payload
            df = OpenPriceEngineClient(api_key="test").fetch_prices("Milk")
        assert len(df) == 3
        assert pd.api.types.is_datetime64_any_dtype(df["recorded_at"])

    def test_search_products_returns_exact_names(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        payload = {"Pick n Pay": {"products": ["PnP UHT Full Cream Milk 1L"], "total": 1}}
        with patch("etl.extract.open_price_engine.requests.Session.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = payload
            products = OpenPriceEngineClient(api_key="test").search_products(
                "Pick n Pay", "milk"
            )
        assert products == ["PnP UHT Full Cream Milk 1L"]

    def test_rejects_invalid_date_range(self):
        from etl.extract.open_price_engine import OpenPriceEngineClient

        client = OpenPriceEngineClient(api_key="test")
        with pytest.raises(ValueError, match="start_date"):
            client.fetch_prices("Milk", start_date="2026-10-30", end_date="2026-10-01")


class TestBusinessTechParser:
    def test_loads_csv_into_dataframe(self, tmp_path):
        from etl.extract.businesstech import BusinessTechParser

        csv_content = "store,product,price_zar,recorded_month,category\nMakro,Bread 700g,19.99,2026-07-01,Staples\n"
        csv_file = tmp_path / "bt.csv"
        csv_file.write_text(csv_content)
        df = BusinessTechParser().load(str(csv_file))
        assert len(df) == 1
        assert df.iloc[0]["store_name"] == "Makro"

    def test_returns_standard_pipeline_columns(self, tmp_path):
        from etl.extract.businesstech import BusinessTechParser

        csv_content = (
            "store,product,price_zar,recorded_month,category\n"
            "Makro,Bread 700g,19.99,2026-07-01,Staples\n"
        )
        csv_file = tmp_path / "bt.csv"
        csv_file.write_text(csv_content)
        df = BusinessTechParser().load(str(csv_file))
        expected = ["store_name", "product_name", "price_zar",
                    "recorded_at", "category", "source"]
        for column in expected:
            assert column in df.columns
        assert df.iloc[0]["product_name"] == "Bread 700g"
        assert df.iloc[0]["category"] == "Staples"
        assert df.iloc[0]["source"] == "businesstech"

    def test_source_column_is_businesstech(self, tmp_path):
        from etl.extract.businesstech import BusinessTechParser

        csv_content = "store,product,price_zar,recorded_month,category\nMakro,Bread 700g,19.99,2026-07-01,Staples\n"
        csv_file = tmp_path / "bt.csv"
        csv_file.write_text(csv_content)
        df = BusinessTechParser().load(str(csv_file))
        assert (df["source"] == "businesstech").all()

    def test_raises_on_missing_required_column(self, tmp_path):
        from etl.extract.businesstech import BusinessTechParser

        csv_content = "store,product,recorded_month\nMakro,Bread 700g,2026-07-01\n"
        csv_file = tmp_path / "bad.csv"
        csv_file.write_text(csv_content)
        with pytest.raises(Exception):
            BusinessTechParser().load(str(csv_file))

    def test_price_zar_is_numeric(self, tmp_path):
        from etl.extract.businesstech import BusinessTechParser

        csv_content = "store,product,price_zar,recorded_month,category\nMakro,Bread 700g,19.99,2026-07-01,Staples\n"
        csv_file = tmp_path / "bt.csv"
        csv_file.write_text(csv_content)
        df = BusinessTechParser().load(str(csv_file))
        assert pd.api.types.is_numeric_dtype(df["price_zar"])

    def test_recorded_month_is_datetime(self, tmp_path):
        from etl.extract.businesstech import BusinessTechParser

        csv_content = "store,product,price_zar,recorded_month,category\nMakro,Bread 700g,19.99,2026-07-01,Staples\n"
        csv_file = tmp_path / "bt.csv"
        csv_file.write_text(csv_content)
        df = BusinessTechParser().load(str(csv_file))
        assert pd.api.types.is_datetime64_any_dtype(df["recorded_at"])
