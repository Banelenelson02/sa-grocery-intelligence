import pytest
import pandas as pd
from unittest.mock import patch, MagicMock


@pytest.fixture
def clean_prices_df():
    return pd.DataFrame([
        {
            "store_name": "Pick n Pay",
            "product_name": "Albany White Bread 700g",
            "price_zar": 23.99,
            "recorded_at": pd.Timestamp("2026-07-01"),
            "source": "open_price_engine"
        },
        {
            "store_name": "Shoprite",
            "product_name": "Full Cream Milk 2L",
            "price_zar": 28.99,
            "recorded_at": pd.Timestamp("2026-07-01"),
            "source": "businesstech"
        }
    ])


class TestPostgresLoader:

    def test_raises_on_empty_connection_string(self):
        from etl.load.postgres_loader import PostgresLoader
        with pytest.raises(ValueError, match="connection"):
            PostgresLoader(connection_string="")

    def test_empty_dataframe_returns_zero_inserted(self):
        from etl.load.postgres_loader import PostgresLoader
        with patch("etl.load.postgres_loader.create_engine"):
            loader = PostgresLoader(connection_string="postgresql://test")
            result = loader.load(pd.DataFrame())
            assert result["inserted"] == 0

    def test_returns_summary_dict(self, clean_prices_df):
        from etl.load.postgres_loader import PostgresLoader
        with patch("etl.load.postgres_loader.create_engine") as mock_engine:
            mock_conn = MagicMock()
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_result = MagicMock()
            mock_result.scalar = MagicMock(return_value=0)
            mock_conn.execute = MagicMock(return_value=mock_result)
            mock_engine.return_value.connect = MagicMock(return_value=mock_conn)

            loader = PostgresLoader(connection_string="postgresql://test")
            result = loader.load(clean_prices_df)

            assert "inserted" in result
            assert "duplicates_skipped" in result
            assert "failed" in result

    def test_inserts_new_rows(self, clean_prices_df):
        from etl.load.postgres_loader import PostgresLoader
        with patch("etl.load.postgres_loader.create_engine") as mock_engine:
            mock_conn = MagicMock()
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_result = MagicMock()
            mock_result.scalar = MagicMock(return_value=0)
            mock_conn.execute = MagicMock(return_value=mock_result)
            mock_engine.return_value.connect = MagicMock(return_value=mock_conn)

            loader = PostgresLoader(connection_string="postgresql://test")
            result = loader.load(clean_prices_df)

            assert result["inserted"] == len(clean_prices_df)
            assert result["duplicates_skipped"] == 0

    def test_skips_duplicate_rows(self, clean_prices_df):
        from etl.load.postgres_loader import PostgresLoader
        with patch("etl.load.postgres_loader.create_engine") as mock_engine:
            mock_conn = MagicMock()
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_result = MagicMock()
            mock_result.scalar = MagicMock(return_value=1)
            mock_conn.execute = MagicMock(return_value=mock_result)
            mock_engine.return_value.connect = MagicMock(return_value=mock_conn)

            loader = PostgresLoader(connection_string="postgresql://test")
            result = loader.load(clean_prices_df)

            assert result["duplicates_skipped"] == len(clean_prices_df)
            assert result["inserted"] == 0

    def test_failed_row_does_not_stop_later_rows(self, clean_prices_df):
        from etl.load.postgres_loader import PostgresLoader

        with patch("etl.load.postgres_loader.create_engine") as mock_engine:
            mock_conn = MagicMock()
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_conn.begin_nested.return_value.__enter__ = MagicMock(return_value=None)
            mock_conn.begin_nested.return_value.__exit__ = MagicMock(return_value=False)

            price_insert_attempts = {"count": 0}

            def execute_side_effect(statement, params=None):
                sql = str(statement)
                result = MagicMock()

                if "SELECT id FROM products" in sql:
                    result.scalar.return_value = 1
                elif "SELECT COUNT(*) FROM prices" in sql:
                    result.scalar.return_value = 0
                elif "INSERT INTO prices" in sql:
                    price_insert_attempts["count"] += 1
                    if price_insert_attempts["count"] == 1:
                        raise RuntimeError("simulated row insert failure")
                return result

            mock_conn.execute.side_effect = execute_side_effect
            mock_engine.return_value.connect.return_value = mock_conn

            loader = PostgresLoader(connection_string="postgresql://test")
            result = loader.load(clean_prices_df)

            assert result["failed"] == 1
            assert result["inserted"] == 1
            assert result["duplicates_skipped"] == 0
            assert price_insert_attempts["count"] == 2
            assert mock_conn.begin_nested.call_count == 2
