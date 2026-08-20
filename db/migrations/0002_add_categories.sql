-- Migration 0002: add category/subcategory to products
--
-- These columns are what /compare and /inflation group by (e.g. "cheapest
-- store for Staples", "how has Dairy inflated this year"). db/seed/products.sql
-- already inserts these values, so this migration just catches the schema up.

ALTER TABLE products ADD COLUMN category VARCHAR(80);
ALTER TABLE products ADD COLUMN subcategory VARCHAR(80);

-- /compare and /inflation both GROUP BY category, so this index matters
-- once the products table has real volume.
CREATE INDEX idx_products_category ON products(category);