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
                    # Each row uses a savepoint. If one insert fails, rolling
                    # back that savepoint keeps PostgreSQL's outer transaction
                    # usable so later valid rows can still be loaded.
                    with conn.begin_nested():
                        product_id = self._get_or_create_product_id(
                            conn, row["product_name"]
                        )

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

    @staticmethod
    def _classify_product(product_name: str) -> tuple[str | None, str | None]:
        """Assign a conservative catalogue category from a product name."""
        name = product_name.casefold()

        if any(term in name for term in ("milk", "cheese", "yoghurt", "yogurt", "butter")):
            return "Dairy", "Milk" if "milk" in name else "Other dairy"
        if any(term in name for term in ("egg", "chicken", "beef", "pork", "fish", "mince")):
            return "Protein", "Eggs" if "egg" in name else "Meat"
        if any(term in name for term in ("rice", "bread", "maize meal", "flour", "pasta", "sugar", "oil")):
            return "Staples", "Rice" if "rice" in name else "Other staples"
        if any(term in name for term in ("tomato", "banana", "apple", "potato", "onion", "spinach")):
            return "Produce", "Other produce"
        return None, None

    def _get_or_create_product_id(self, conn, product_name: str) -> int:
        result = conn.execute(text("""
            SELECT id FROM products WHERE name = :name
        """), {"name": product_name})
        existing_id = result.scalar()
        category, subcategory = self._classify_product(product_name)

        if existing_id is not None:
            if category is not None:
                conn.execute(text("""
                    UPDATE products
                    SET category = COALESCE(category, :category),
                        subcategory = COALESCE(subcategory, :subcategory)
                    WHERE id = :product_id
                """), {
                    "category": category,
                    "subcategory": subcategory,
                    "product_id": existing_id,
                })
            return existing_id

        result = conn.execute(text("""
            INSERT INTO products (name, category, subcategory)
            VALUES (:name, :category, :subcategory)
            RETURNING id
        """), {
            "name": product_name,
            "category": category,
            "subcategory": subcategory,
        })
        return result.scalar()
