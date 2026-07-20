import pandas as pd


class BusinessTechParser:
    REQUIRED_COLUMNS = ["store", "product", "price_zar", "recorded_month", "category"]

    def load(self, csv_path: str) -> pd.DataFrame:
        df = pd.read_csv(csv_path)

        # Check all required columns exist
        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Ensure price_zar is numeric
        df["price_zar"] = pd.to_numeric(df["price_zar"], errors="raise")

        # Parse recorded_month to datetime
        df["recorded_month"] = pd.to_datetime(df["recorded_month"])

        # Add source tag
        df["source"] = "businesstech"

        return df