import pandas as pd

from etl.extract.businesstech import BusinessTechParser
from etl.transform.clean import validate_prices
from etl.transform.normalize import normalize_dataframe


def test_businesstech_rows_flow_through_normalization_and_validation(tmp_path):
    csv_path = tmp_path / "businesstech.csv"
    csv_path.write_text(
        "store,product,price_zar,recorded_month,category\n"
        "makro,Test Bread 700g,24.99,2026-07-01,Bakery\n"
        "Shoprite,Test Milk 2L,0,2026-07-01,Dairy\n",
        encoding="utf-8",
    )

    extracted = BusinessTechParser().load(str(csv_path))

    assert list(extracted["source"].unique()) == ["businesstech"]
    assert {"store_name", "product_name", "price_zar", "recorded_at", "category", "source"}.issubset(extracted.columns)

    normalized = normalize_dataframe(extracted)
    assert normalized["store_name"].tolist() == ["Makro", "Shoprite"]
    assert pd.api.types.is_datetime64_any_dtype(normalized["recorded_at"])

    report = validate_prices(normalized)

    assert len(report.valid) == 1
    assert report.valid.iloc[0]["product_name"] == "Test Bread 700g"
    assert report.valid.iloc[0]["price_zar"] == 24.99
    assert len(report.rejected) == 1
    assert report.rejected[0]["reason"] == "impossible price"
