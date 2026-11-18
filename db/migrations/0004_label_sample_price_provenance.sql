-- Migration 0004: identify seeded demonstration prices accurately
--
-- The initial prices are loaded from db/seed/sample_prices.sql. They are
-- demonstration data, not records fetched from the Open Price Engine API.
-- Keep provenance accurate for existing databases as well as fresh installs.

UPDATE prices
SET source = 'sample_seed'
WHERE source = 'open_price_engine'
  AND recorded_at >= TIMESTAMPTZ '2026-05-01 00:00:00+00'
  AND recorded_at <= TIMESTAMPTZ '2026-07-17 23:59:59+00';
