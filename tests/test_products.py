from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from api.db import get_db
from api.main import app
from etl.load.postgres_loader import PostgresLoader


def test_products_endpoint_returns_database_catalogue():
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchall.return_value = [
        MagicMock(id=11, name="PnP UHT Full Cream Milk 1L",
                  category="Dairy", subcategory="Milk"),
        MagicMock(id=12, name="PnP Large Eggs 30 Pack",
                  category="Protein", subcategory="Eggs"),
        MagicMock(id=13, name="McCain Savoury Rice 400g",
                  category="Staples", subcategory="Rice"),
    ]
    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = TestClient(app).get("/products")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {"id": 11, "name": "PnP UHT Full Cream Milk 1L",
         "category": "Dairy", "subcategory": "Milk"},
        {"id": 12, "name": "PnP Large Eggs 30 Pack",
         "category": "Protein", "subcategory": "Eggs"},
        {"id": 13, "name": "McCain Savoury Rice 400g",
         "category": "Staples", "subcategory": "Rice"},
    ]


def test_product_classification_covers_new_ingested_products():
    assert PostgresLoader._classify_product("PnP UHT Full Cream Milk 1L") == (
        "Dairy", "Milk"
    )
    assert PostgresLoader._classify_product("PnP Large Eggs 30 Pack") == (
        "Protein", "Eggs"
    )
    assert PostgresLoader._classify_product("McCain Savoury Rice 400g") == (
        "Staples", "Rice"
    )


def test_unknown_product_is_left_uncategorised_for_manual_review():
    assert PostgresLoader._classify_product("Mystery household item") == (
        None, None
    )
