# SA Grocery Price Intelligence Platform

A local South African grocery price analytics MVP for exploring historical price trends, comparing stores by category, analysing monthly price changes, and comparing single-store and split-store shopping baskets.

**Current status:** Local MVP; no public deployment yet.

## Features

- **Price trends:** View recorded prices for a product across stores and percentage changes from the previous recorded price.
- **Store comparison:** Rank stores by average recorded price for a selected product category.
- **Inflation analysis:** Compare monthly average recorded prices by category, optionally filtered to a store. These calculations describe this dataset; they are not official South African CPI statistics.
- **Basket optimizer:** Compare the cheapest one-store basket that covers all requested products with buying each item at its cheapest recorded store. The split option can involve several stores.

## Sample data and limitations

The local sample database was checked on 29 October 2026 and contained:

| Measure | Current sample |
|---|---:|
| Products | 10 |
| Stores | 4 |
| Price records | 480 |
| Earliest record | 1 May 2026 |
| Latest record | 17 July 2026 |

The four store names are Checkers, Pick n Pay, Shoprite, and Woolworths. These are **historical sample prices, not live supermarket prices**. As the latest date is 17 July 2026, short trends windows can legitimately return no records.

The basket API accepts a positive `budget`, but the current optimizer does not use the budget to constrain the recommendation. Its split-basket total also excludes travel costs and the inconvenience of visiting multiple stores.

ETL components exist in the repository, but the current Compose stack does not run an Airflow scheduler or refresh prices automatically.

## Architecture

```text
PostgreSQL 16 (Docker Compose)
          |
          v
FastAPI analytics API (Docker Compose, port 8000)
          ^
          | HTTP requests
          |
React + Vite frontend (development server, port 5173)
```

### Technology stack

| Layer | Technology | Role |
|---|---|---|
| API | Python, FastAPI, Pydantic | HTTP endpoints and request/response validation |
| Database | PostgreSQL 16 | Products, recorded prices, and basket tables |
| Database access | SQLAlchemy | Execute SQL queries from the API |
| Frontend | React 18, Vite | Interactive browser dashboard |
| Styling | Tailwind CSS | Interface styling |
| Charts | Recharts | Price trend visualisations |
| Containers | Docker Compose | Local database and API services |
| Tests | pytest | Automated backend and ETL tests |

## Quick start

### Prerequisites

Install Docker Engine with the Docker Compose plugin, Node.js, npm, and Git.

### 1. Get the code

```bash
git clone https://github.com/Banelenelson02/sa-grocery-intelligence.git
cd sa-grocery-intelligence
```

### 2. Start the database and API

```bash
docker compose up -d --build
docker compose ps
```

Wait for the database service to show `healthy` and the API service to be running. Compose starts PostgreSQL and FastAPI. The database is available to the API on Docker's internal network; PostgreSQL's port is not published on the host.

On the first run with a fresh named volume, PostgreSQL applies `db/schema.sql` and the seed SQL files mounted from `db/`. PostgreSQL initialization scripts are not re-run automatically on an already-initialized volume.

### 3. Check the API

```bash
curl -i http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

This endpoint confirms the API is responding. It does not independently check the database connection.

Interactive API documentation is available at <http://localhost:8000/docs>.

### 4. Start the frontend

Open another terminal in the repository root and run:

```bash
cd frontend
npm ci
npm run dev
```

Open <http://localhost:5173> in your browser. The frontend defaults to `http://localhost:8000` for API requests. To change this for local development, set `VITE_API_BASE_URL` in `frontend/.env` (the `frontend/.env.example` file provides the default value).

Keep the Compose services running while using the dashboard.

### 5. Stop services

Stop the Vite development server with `Ctrl+C`. From the repository root, stop the Docker services with:

```bash
docker compose down
```

This retains the named database volume. Avoid `docker compose down -v` unless you intentionally want to delete the database volume and its stored data.

## API endpoints

Base URL: `http://localhost:8000`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | API health response (`{"status":"ok"}`) |
| `GET` | `/trends?product_id=1&weeks=52` | Recorded price history for a product |
| `GET` | `/compare?category=Dairy` | Rank stores by average recorded price for a category |
| `GET` | `/inflation?months=6` | Monthly category price changes |
| `GET` | `/inflation?months=6&store_name=Pick%20n%20Pay` | Monthly category price changes filtered to a store |
| `POST` | `/basket` | Compare one-store and split-basket totals |

### Trends example

```bash
curl "http://localhost:8000/trends?product_id=1&weeks=52"
```

- `product_id` is required and must be positive.
- `weeks` defaults to 12 and must be between 1 and 52.
- Results include `recorded_at`, `store_name`, `price_zar`, and `week_over_week_change`.

### Compare example

```bash
curl "http://localhost:8000/compare?category=Dairy"
```

The category must match a category in the database. Results include `store_name`, `avg_price_zar`, `product_count`, and `rank`. The average is calculated from the recorded price rows in the dataset, not from live prices.

### Inflation example

```bash
curl "http://localhost:8000/inflation?months=6"
curl "http://localhost:8000/inflation?months=6&store_name=Pick%20n%20Pay"
```

- `months` defaults to 6 and allows values from 1 to 36.
- `store_name` is optional.
- Results contain `month`, `category`, `avg_price_zar`, and `pct_change`.

### Basket example

```bash
curl -X POST "http://localhost:8000/basket" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": 1, "qty": 2},
      {"product_id": 5, "qty": 1}
    ],
    "budget": 500
  }'
```

The request requires a non-empty `items` array, positive product quantities, and a positive `budget`. The response contains:

- `single_store`: `store_name`, `total_zar`, and the requested item quantities.
- `split_stores`: `total_zar` and an item-level breakdown including `product_id`, `store_name`, `price_zar`, and `qty`.
- `saving_zar`: the difference between the totals when a single store can cover all basket items.

The optimizer uses the latest recorded price for each product/store pair. For the full request/response schemas, open <http://localhost:8000/docs> while the API is running.

## Run tests and build the frontend

From the repository root, run the Python test suite:

```bash
python3 -m pytest -q
```

The current local test run completed with **53 passed in 0.49 seconds**. Runtime will vary by environment. ETL and API tests mock external dependencies where appropriate; no real Open Price Engine request is needed for the normal test run.

Build the frontend for production:

```bash
cd frontend
npm ci
npm run build
```

Vite may warn that the main JavaScript chunk exceeds its recommended size threshold. This is a non-blocking performance warning if the build completes successfully.

## Database overview

The schema is defined in `db/schema.sql`:

- `stores`: store metadata.
- `products`: product names, units, barcodes and categories.
- `prices`: historical prices, product IDs, store names, timestamps and source names.
- `baskets`: basket metadata.
- `basket_items`: basket product quantities.

The `prices` table references products through `product_id` and stores the store name directly in `store_name`. It does not currently use `store_id` as a foreign key on the price rows.

## Repository structure

```text
sa-grocery-intelligence/
├── api/
│   ├── routers/       # Trends, compare, inflation and basket endpoints
│   ├── db.py          # SQLAlchemy connection/session setup
│   ├── schemas.py     # Pydantic request and response models
│   └── main.py        # FastAPI application and CORS configuration
├── db/
│   ├── schema.sql
│   └── seed/          # Store, product and sample price inserts
├── etl/
│   ├── extract/
│   ├── transform/
│   ├── load/
│   └── pipeline.py
├── frontend/
│   └── src/           # React pages, API clients, hooks and components
├── tests/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Roadmap

- [x] PostgreSQL schema and seed data
- [x] FastAPI analytics endpoints
- [x] React dashboard for trends, comparison, inflation and basket optimization
- [x] Local Docker Compose setup for PostgreSQL and the API
- [x] Automated test suite (53 tests passed in the latest local run)
- [ ] Show the latest sample-data date clearly in the dashboard
- [ ] Improve empty states for periods with no price records
- [ ] Apply budget constraints to basket optimization
- [ ] Add database-backed integration tests
- [ ] Reduce the frontend JavaScript bundle size through code splitting
- [ ] Complete detailed API, architecture and data-dictionary documentation
- [x] Configure and verify GitHub Actions CI for backend tests
- [ ] Deploy the dashboard and API publicly

## Data interpretation

- Category comparisons and inflation calculations describe this dataset and should not be interpreted as official CPI statistics.
- Results can be incomplete or empty when records do not cover the requested time window.
- A split basket can cost less at checkout but require visits to multiple supermarkets; travel and time costs are not included.
- The sample prices are historical, not real-time price quotes.

## License

No license has been specified in this repository. Check licensing before redistributing or reusing this code.
## WeThinkCode_ Project Reference

Project reference: `WTC-E43X2F5H`
