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
                    # prices.product_id is a foreign key -- it needs a real row
                    # in products to point at. The ETL pipeline only ever sees
                    # product *names* (from the source APIs/CSVs), never IDs,
                    # so this resolves name -> id, creating the product row
                    # the first time a given name is seen.
                    product_id = self._get_or_create_product_id(conn, row["product_name"])

                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM prices
                        WHERE store_name = :store
                        AND product_id = :product_id
                        AND DATE(recorded_at) = DATE(:recorded_at)
                    """), {
                        "store": row["store_name"],
                        "product_id": product_id,
                        "recorded_at": row["recorded_at"]
                    })

                    if result.scalar() > 0:
                        duplicates_skipped += 1
                        continue

                    conn.execute(text("""
                        INSERT INTO prices
                        (product_id, store_name, price_zar, recorded_at, source)
                        VALUES (:product_id, :store, :price, :recorded_at, :source)
                    """), {
                        "product_id": product_id,
                        "store": row["store_name"],
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

    def _get_or_create_product_id(self, conn, product_name: str) -> int:
        result = conn.execute(text("""
            SELECT id FROM products WHERE name = :name
        """), {"name": product_name})
        existing_id = result.scalar()

        if existing_id is not None:
            return existing_id

        result = conn.execute(text("""
            INSERT INTO products (name) VALUES (:name)
            RETURNING id
        """), {"name": product_name})
        return result.scalar()