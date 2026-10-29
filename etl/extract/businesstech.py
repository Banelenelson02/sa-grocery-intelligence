import pandas as pd


class BusinessTechParser:
    REQUIRED_COLUMNS = [
        "store",
        "product",
        "price_zar",
        "recorded_month",
        "category",
    ]

    def load(self, csv_path: str) -> pd.DataFrame:
        df = pd.read_csv(csv_path)

        # Check that the source CSV contains every required column.
        missing = [
            col for col in self.REQUIRED_COLUMNS
            if col not in df.columns
        ]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Convert the price and date into consistent data types.
        df["price_zar"] = pd.to_numeric(
            df["price_zar"], errors="raise"
        )
        df["recorded_month"] = pd.to_datetime(
            df["recorded_month"], errors="raise"
        )

        # Translate source column names into the standard ETL schema.
        df = df.rename(columns={
            "store": "store_name",
            "product": "product_name",
            "recorded_month": "recorded_at",
        })

        # Identify where these records came from.
        df["source"] = "businesstech"

        return df

