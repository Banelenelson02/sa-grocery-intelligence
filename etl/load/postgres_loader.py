import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()


class PostgresLoader:

    def __init__(self, connection_string: str = None):
        conn = connection_string or os.getenv("DATABASE_URL")
        if not conn:
            raise ValueError("No connection string provided and DATABASE_URL not set")
        self.engine = create_engine(conn)

    def load(self, df: pd.DataFrame) -> dict:
        if df.empty:
            return {"inserted": 0, "duplicates_skipped": 0, "failed": 0}

        inserted = 0
        duplicates_skipped = 0
        failed = 0

        with self.engine.connect() as conn:
            for _, row in df.iterrows():
                try:
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM prices
                        WHERE store_name = :store
                        AND product_name = :product
                        AND DATE(recorded_at) = DATE(:recorded_at)
                    """), {
                        "store": row["store_name"],
                        "product": row["product_name"],
                        "recorded_at": row["recorded_at"]
                    })

                    if result.scalar() > 0:
                        duplicates_skipped += 1
                        continue

                    conn.execute(text("""
                        INSERT INTO prices
                        (store_name, product_name, price_zar, recorded_at, source)
                        VALUES (:store, :product, :price, :recorded_at, :source)
                    """), {
                        "store": row["store_name"],
                        "product": row["product_name"],
                        "price": row["price_zar"],
                        "recorded_at": row["recorded_at"],
                        "source": row["source"]
                    })
                    inserted += 1

                except Exception as e:
                    failed += 1
                    print(f"Failed to insert row: {e}")

            conn.commit()

        return {
            "inserted": inserted,
            "duplicates_skipped": duplicates_skipped,
            "failed": failed
        }