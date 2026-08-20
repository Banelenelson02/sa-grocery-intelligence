CREATE TABLE stores (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    chain VARCHAR(80),
    region VARCHAR(80)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    unit VARCHAR(40),
    barcode VARCHAR(60),
    category VARCHAR(80),
    subcategory VARCHAR(80),
    UNIQUE (name, unit)
);

CREATE TABLE prices (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    store_name VARCHAR(120) NOT NULL,
    price_zar NUMERIC(10, 2) NOT NULL CHECK (price_zar > 0),
    on_promotion BOOLEAN NOT NULL DEFAULT FALSE,
    recorded_at TIMESTAMPTZ NOT NULL,
    source VARCHAR(40) NOT NULL
);

CREATE INDEX idx_prices_product_id ON prices(product_id);
CREATE INDEX idx_prices_store_name ON prices(store_name);
CREATE INDEX idx_prices_recorded_at ON prices(recorded_at);
CREATE INDEX idx_products_category ON products(category);

CREATE TABLE baskets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE basket_items (
    basket_id INTEGER NOT NULL REFERENCES baskets(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (basket_id, product_id)
);