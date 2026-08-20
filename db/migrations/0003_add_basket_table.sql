-- Migration 0003: baskets and basket_items, for POST /basket
--
-- api/schemas.py's BasketItem already has a product_id field, so basket_items
-- follows the same normalized-by-product pattern as prices.

CREATE TABLE baskets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- basket_items is a many-to-many join: one basket has many products,
-- and (in theory) a product could appear in many baskets.
-- The composite primary key (basket_id, product_id) means a single product
-- can only appear once per basket -- adding it twice should update quantity,
-- not create a duplicate row.
CREATE TABLE basket_items (
    basket_id INTEGER NOT NULL REFERENCES baskets(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (basket_id, product_id)
);