import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from api.main import app
from api.db import get_db


@pytest.fixture
def client_with_mock_db():
    """
    Overrides FastAPI's get_db dependency with a MagicMock session, so these
    tests exercise real routing/validation/response-shaping logic without
    needing a live Postgres connection. Each test configures mock_db.execute
    to return whatever rows/scalar value it needs.
    """
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app), mock_db
    app.dependency_overrides.clear()


def make_row(**kwargs):
    """SQLAlchemy result rows support attribute access (row.column_name);
    MagicMock supports this out of the box via setattr."""
    row = MagicMock()
    for key, value in kwargs.items():
        setattr(row, key, value)
    return row


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestTrendsEndpoint:
    def test_returns_price_points(self, client_with_mock_db):
        client, mock_db = client_with_mock_db
        mock_db.execute.return_value.fetchall.return_value = [
            make_row(recorded_at="2026-08-01T00:00:00+00:00", store_name="Pick n Pay",
                     price_zar=19.99, week_over_week_change=None),
        ]

        response = client.get("/trends?product_id=1&weeks=12")

        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["store_name"] == "Pick n Pay"

    def test_rejects_non_positive_product_id(self, client_with_mock_db):
        client, _ = client_with_mock_db
        response = client.get("/trends?product_id=0&weeks=12")
        assert response.status_code == 422

    def test_rejects_weeks_out_of_range(self, client_with_mock_db):
        client, _ = client_with_mock_db
        response = client.get("/trends?product_id=1&weeks=100")
        assert response.status_code == 422

    def test_missing_product_id_is_required(self, client_with_mock_db):
        client, _ = client_with_mock_db
        response = client.get("/trends?weeks=12")
        assert response.status_code == 422


class TestCompareEndpoint:
    def test_returns_ranked_stores(self, client_with_mock_db):
        client, mock_db = client_with_mock_db
        mock_db.execute.return_value.fetchall.return_value = [
            make_row(store_name="Pick n Pay", avg_price_zar=46.18, product_count=4),
            make_row(store_name="Checkers", avg_price_zar=47.24, product_count=4),
        ]

        response = client.get("/compare?category=Staples")

        assert response.status_code == 200
        body = response.json()
        assert len(body) == 2
        assert body[0]["rank"] == 1
        assert body[1]["rank"] == 2
        assert body[0]["store_name"] == "Pick n Pay"

    def test_requires_category(self, client_with_mock_db):
        client, _ = client_with_mock_db
        response = client.get("/compare")
        assert response.status_code == 422


class TestInflationEndpoint:
    def test_returns_inflation_points(self, client_with_mock_db):
        client, mock_db = client_with_mock_db
        mock_db.execute.return_value.fetchall.return_value = [
            make_row(month="2026-07-01T00:00:00+00:00", category="Dairy",
                     avg_price_zar=52.88, pct_change=1.86),
        ]

        response = client.get("/inflation?months=6")

        assert response.status_code == 200
        body = response.json()
        assert body[0]["category"] == "Dairy"
        assert body[0]["pct_change"] == 1.86

    def test_rejects_months_out_of_range(self, client_with_mock_db):
        client, _ = client_with_mock_db
        response = client.get("/inflation?months=0")
        assert response.status_code == 422

    def test_defaults_months_to_six_when_omitted(self, client_with_mock_db):
        client, mock_db = client_with_mock_db
        mock_db.execute.return_value.fetchall.return_value = []
        response = client.get("/inflation")
        assert response.status_code == 200


class TestBasketEndpoint:
    def test_returns_basket_response(self, client_with_mock_db):
        client, mock_db = client_with_mock_db
        mock_db.execute.return_value.fetchall.return_value = [
            make_row(product_id=1, store_name="Woolworths", price_zar=18.69),
            make_row(product_id=1, store_name="Pick n Pay", price_zar=19.99),
        ]

        response = client.post("/basket", json={
            "items": [{"product_id": 1, "qty": 2}],
            "budget": 100
        })

        assert response.status_code == 200
        body = response.json()
        assert body["single_store"]["store_name"] == "Woolworths"
        assert body["single_store"]["total_zar"] == 37.38

    def test_rejects_empty_items(self, client_with_mock_db):
        client, _ = client_with_mock_db
        response = client.post("/basket", json={"items": [], "budget": 100})
        assert response.status_code == 422

    def test_rejects_non_positive_budget(self, client_with_mock_db):
        client, _ = client_with_mock_db
        response = client.post("/basket", json={
            "items": [{"product_id": 1, "qty": 1}],
            "budget": 0
        })
        assert response.status_code == 422

    def test_rejects_non_positive_quantity(self, client_with_mock_db):
        client, _ = client_with_mock_db
        response = client.post("/basket", json={
            "items": [{"product_id": 1, "qty": 0}],
            "budget": 100
        })
        assert response.status_code == 422

    def test_no_matching_store_still_returns_200(self, client_with_mock_db):
        """A product with no price data anywhere shouldn't crash the endpoint --
        it should degrade to an empty/zero result, per the sequence design."""
        client, mock_db = client_with_mock_db
        mock_db.execute.return_value.fetchall.return_value = []

        response = client.post("/basket", json={
            "items": [{"product_id": 9999, "qty": 1}],
            "budget": 50
        })

        assert response.status_code == 200
        body = response.json()
        assert body["saving_zar"] is None