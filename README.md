# 🇿🇦 SA Grocery Price Intelligence

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rounded&color=0:0d1117,100:238636&height=180&section=header&text=SA%20Grocery%20Intelligence&fontSize=38&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Making%20grocery%20prices%20easier%20to%20understand&descAlignY=60&descSize=16" alt="SA Grocery Price Intelligence banner" />
</p>

<p align="center">
  A data engineering and analytics project exploring grocery prices in South Africa.
  <br />
  Ingest price data, store it, analyse historical changes, and help shoppers compare basket costs.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</p>

<p align="center">
  <a href="https://github.com/Banelenelson02/sa-grocery-intelligence/actions/workflows/test.yml">
    <img src="https://github.com/Banelenelson02/sa-grocery-intelligence/actions/workflows/test.yml/badge.svg" alt="Project checks" />
  </a>
  <a href="https://github.com/Banelenelson02/sa-grocery-intelligence">
    <img src="https://img.shields.io/badge/Project-WeThinkCode__-2ea043?style=flat" alt="WeThinkCode project" />
  </a>
</p>

---

## 🧭 Project overview

Comparing grocery prices can be difficult when prices change over time and information is spread across different retailers. This project brings price records into one PostgreSQL database and provides an API and dashboard for exploring that information.

The goal is to make it easier to answer questions such as:

- How has the recorded price of a product changed over time?
- Which store has the lowest average recorded price in a category?
- How have average prices in a category changed month by month?
- Is it cheaper to buy everything from one store or split a basket across stores?
- Does either basket option fit the shopper's budget?

### Project components

| Project | Description | Stack |
|---|---|---|
| **ETL pipeline** | Retrieves product price history, normalises records, validates data and loads it into PostgreSQL. | Python · pandas · Requests · Open Price Engine API |
| **Analytics API** | Exposes endpoints for price trends, store comparisons, monthly price changes and basket calculations. | Python · FastAPI · Pydantic · SQLAlchemy |
| **Interactive dashboard** | Lets users explore price trends, compare stores, view category changes and test shopping baskets. | React · Vite · Tailwind CSS · Recharts |
| **Data storage** | Stores product information, store names, price observations and basket data. | PostgreSQL 16 · SQL |
| **Automated checks** | Runs backend tests and builds the frontend when changes are pushed or a pull request is opened. | pytest · GitHub Actions · Node.js · npm |

## ✨ Features

- **Historical price trends:** Explore recorded prices for a product across stores and see the percentage change from the previous observation.
- **Store comparison:** Rank stores by average recorded price for a selected product category.
- **Monthly price analysis:** Compare average recorded prices by category, with an optional store filter. These are dataset-level calculations, not official South African CPI figures.
- **Basket optimiser:** Compare the cheapest complete basket from one store with a split basket that buys each item from its cheapest recorded store.
- **Budget-aware results:** See whether an option is within budget, over budget or incomplete because price records are missing.
- **Data validation:** Normalise incoming records and separate valid observations from rejected rows.
- **Repeatable ingestion:** Skip duplicate records when the same price history is loaded again.

## 📊 Data snapshot

<caption>Local database verification on 30 October 2026</caption>

| Measure | Verified snapshot |
|---|---:|
| Products | 13 |
| Stores | 4 |
| Price records | 558 |
| Earliest recorded date | 1 May 2026 |
| Latest recorded date | 27 October 2026 |

The database contains the original sample records and additional historical observations ingested from Open Price Engine. The latest ingestion test retrieved **78 observations** across three Pick n Pay products. Running the same pipeline again skipped those 78 records as duplicates.

These figures describe the local development database at the time it was checked. They are not a promise of current retailer coverage or live prices.

### Data sources

| Source | How it is used | Notes |
|---|---|---|
| Seeded sample data | Provides historical records for the initial dashboard and analytics. | Sample records are for development and demonstration. |
| [Open Price Engine](https://openpricengine.com/docs) | Supplies product names and historical price observations through its API. | Store and product access depends on the API key's plan. |
| BusinessTech basket CSV | Optional input supported by the ETL pipeline. | The file is skipped when `data/raw/businesstech_basket_latest.csv` is not present. |

**Important data limitations**

- The current Open Price Engine configuration defaults to Pick n Pay and three product names that were confirmed as available to the free API key. You can override the store and product list using environment variables.
- Open Price Engine may return access restrictions for stores or products outside the API key's plan. The pipeline reports these restrictions rather than treating them as successful extractions.
- The three newly ingested products currently need category mapping before they can contribute to category-based comparisons and monthly category analysis.
- Prices are historical observations. The dashboard is not a live checkout quote service.
- Category-level price changes are calculated from this project's dataset. They must not be described as official CPI or national inflation statistics.
- Split-basket totals do not include transport costs or the time and inconvenience of visiting multiple stores.

## 🏗️ Architecture

```text
                 Open Price Engine API
                           |
                           v
                  Python ETL pipeline
               Extract -> Transform -> Validate
                           |
                           v
                     PostgreSQL 16
                           |
                           v
                    FastAPI analytics
                           |
                         HTTP
                           |
                           v
                    React + Vite UI
```

The database and API run through Docker Compose. The React development server runs separately through Vite.

### Technology stack

| Layer | Technology | Purpose |
|---|---|---|
| Data extraction | Python, Requests | Retrieve historical price data from the external API |
| Data processing | pandas | Normalise and prepare price observations |
| Data validation | Python | Check incoming records before loading |
| API | FastAPI, Pydantic | Serve analytics endpoints and validate requests |
| Database access | SQLAlchemy | Execute database queries from the API |
| Database | PostgreSQL 16 | Persist products, prices and basket data |
| Frontend | React 18, Vite | Build the interactive dashboard |
| Styling | Tailwind CSS | Style the dashboard |
| Visualisations | Recharts | Display price trends and comparisons |
| Local environment | Docker Compose | Run PostgreSQL and the API |
| Testing and CI | pytest, GitHub Actions | Test backend and ETL behaviour and build the frontend |

## 🚀 Getting started

### Prerequisites

- Git
- Docker Engine
- Docker Compose plugin
- Node.js and npm
- Python 3.10 or newer (for running the test suite or ETL locally)

### 1. Clone the repository

```bash
git clone https://github.com/Banelenelson02/sa-grocery-intelligence.git
cd sa-grocery-intelligence
```

### 2. Start PostgreSQL and the API

```bash
docker compose up -d --build
docker compose ps
```

Wait until the database reports `healthy` and the API is running.

On a fresh database volume, PostgreSQL runs the schema and seed scripts mounted from `db/`. PostgreSQL only runs these initialisation scripts when the data directory is empty. Restarting an existing database does not automatically re-run them.

### 3. Check the API

```bash
curl -i http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

This confirms that the API is responding. It does not independently verify the database connection.

Interactive API documentation:

<http://localhost:8000/docs>

### 4. Start the React dashboard

Open a second terminal from the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Open <http://localhost:5173>.

The frontend uses `http://localhost:8000` as its default API base URL. To change it for local development, create `frontend/.env` using `frontend/.env.example` as a reference and set `VITE_API_BASE_URL`.

### 5. Stop the application

Stop the Vite server with `Ctrl+C`. From the repository root, run:

```bash
docker compose down
```

This keeps the named database volume. Do not use `docker compose down -v` unless you intentionally want to delete the database volume and its data.

## 🔑 Running the Open Price Engine ETL

The ETL pipeline can retrieve historical prices from Open Price Engine and load them into PostgreSQL.

### 1. Create a local environment file

Create a root-level `.env` file:

```env
OPE_API_KEY=your_api_key_here
OPE_STORE=Pick n Pay
```

Do not commit this file or paste your API key into source code. Keep it local. The repository's `.gitignore` should exclude `.env`.

### 2. Run the pipeline

Make sure the database is running:

```bash
docker compose up -d db
```

From the repository root, export the variables from `.env` and run the ETL container:

```bash
set -a
source .env
set +a

docker compose run --rm -e OPE_API_KEY api python -m etl.pipeline
```

The current default product list is:

- `PnP UHT Full Cream Milk 1L`
- `PnP Large Eggs 30 Pack`
- `McCain Savoury Rice 400g`

The default date window is the most recent 30 days. The pipeline can be configured with:

| Variable | Purpose |
|---|---|
| `OPE_API_KEY` | API key used to authenticate with Open Price Engine |
| `OPE_STORE` | Store to query; defaults to `Pick n Pay` |
| `OPE_PRODUCTS` | Comma-separated list of exact product names; defaults to the three products above |
| `OPE_START_DATE` | Optional start date in `YYYY-MM-DD` format |
| `OPE_END_DATE` | Optional end date in `YYYY-MM-DD` format |

For example, to use a different product list, add an `OPE_PRODUCTS` value to your local `.env` file. Product names must match the names available to your API key.

The pipeline handles authentication errors, plan restrictions, rate limits and request failures. It normalises and validates returned rows before loading them. Re-running the same date range should not create duplicate price records.

See the [Open Price Engine API documentation](https://openpricengine.com/docs) for current endpoints, product discovery and plan access.

## 🔌 API reference

Base URL: `http://localhost:8000`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | API health response |
| `GET` | `/trends?product_id=1&weeks=52` | Recorded price history for a product |
| `GET` | `/compare?category=Dairy` | Rank stores by average recorded price in a category |
| `GET` | `/inflation?months=6` | Monthly average price changes by category |
| `GET` | `/inflation?months=6&store_name=Pick%20n%20Pay` | Monthly price changes filtered to a store |
| `POST` | `/basket` | Compare single-store and split-store baskets against a budget |

### Price trends

```bash
curl "http://localhost:8000/trends?product_id=1&weeks=52"
```

- `product_id` is required and must be positive.
- `weeks` defaults to 12 and must be between 1 and 52.
- Results include `recorded_at`, `store_name`, `price_zar` and `week_over_week_change`.

### Store comparison

```bash
curl "http://localhost:8000/compare?category=Dairy"
```

The category must match a category in the database. Results include `store_name`, `avg_price_zar`, `product_count` and `rank`. The average is calculated from the available records, not live prices.

### Monthly price analysis

```bash
curl "http://localhost:8000/inflation?months=6"
curl "http://localhost:8000/inflation?months=6&store_name=Pick%20n%20Pay"
```

- `months` defaults to 6 and accepts values from 1 to 36.
- `store_name` is optional.
- Results include `month`, `category`, `avg_price_zar` and `pct_change`.

### Basket optimisation

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

The request requires a non-empty `items` array, positive product quantities and a positive `budget`.

The response includes:

- `single_store`: the cheapest single store that has every requested product, with its total and budget status.
- `split_stores`: the cheapest available store for each item, with a total and completeness information.
- `saving_zar`: the difference between the single-store and split-store totals when both can be compared.
- `budget_status`: `within_budget`, `over_budget` or `missing_prices`.
- `recommended_option`: the preferred complete option when one fits the budget; otherwise `null`.

The optimiser uses the latest recorded price for each product/store pair. It reports missing price data rather than presenting an incomplete basket as a complete recommendation. Split-basket totals do not include travel costs.

For full request and response schemas, visit <http://localhost:8000/docs> while the API is running.

## 🧪 Tests and frontend build

Run the backend and ETL test suite from the repository root:

```bash
python3 -m pytest -q
```

The latest local run recorded during development completed with **58 passed**. One pandas date-parsing warning was reported; it did not cause a test failure. Test counts and runtime may change as the project evolves.

Build the frontend:

```bash
cd frontend
npm ci
npm run build
```

GitHub Actions runs the pytest suite and builds the React frontend on pushes and pull requests targeting `main`.

## 🗄️ Database overview

The database schema is defined in `db/schema.sql`.

| Table | Purpose |
|---|---|
| `stores` | Store metadata |
| `products` | Product names, units, barcodes and categories |
| `prices` | Historical price observations, product IDs, store names, timestamps and source names |
| `baskets` | Basket metadata |
| `basket_items` | Products and quantities associated with a basket |

The `prices` table references products through `product_id` and stores the store name directly in `store_name`. It does not currently use `store_id` as a foreign key on price rows.

## 📁 Repository structure

```text
sa-grocery-intelligence/
├── api/
│   ├── routers/          # Trends, comparison, inflation and basket endpoints
│   ├── db.py             # SQLAlchemy connection and session setup
│   ├── schemas.py        # Pydantic request and response models
│   └── main.py           # FastAPI application and CORS configuration
├── db/
│   ├── schema.sql
│   └── seed/             # Store, product and sample price inserts
├── etl/
│   ├── extract/          # External data source clients and parsers
│   ├── transform/        # Normalisation and validation
│   ├── load/             # PostgreSQL loader
│   └── pipeline.py       # ETL orchestration
├── frontend/
│   └── src/              # React components, API clients and hooks
├── tests/
├── dags/                 # Airflow DAG definitions
├── docs/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🛣️ Roadmap

- [x] PostgreSQL schema and sample data
- [x] FastAPI analytics endpoints
- [x] React dashboard for trends, store comparisons, monthly analysis and basket optimisation
- [x] Local Docker Compose setup for PostgreSQL and the API
- [x] Open Price Engine v1 API integration
- [x] Product-name discovery for products available to the API key
- [x] ETL normalisation, validation and PostgreSQL loading
- [x] Duplicate detection during repeated ingestion
- [x] Budget-aware basket recommendations
- [x] Backend and ETL test suite
- [x] GitHub Actions checks for backend tests and frontend builds
- [ ] Add category mapping for newly ingested products
- [ ] Add database-backed integration tests
- [ ] Improve dashboard empty states and latest-data-date visibility
- [ ] Reduce frontend bundle size through code splitting
- [ ] Add scheduled ETL execution and monitoring
- [ ] Deploy the API and dashboard publicly

## 📌 Data interpretation

This project is an educational and analytical tool. Its outputs depend on the coverage, quality and dates of the underlying records.

- Historical records are not guaranteed to represent today's shelf prices.
- Missing records do not mean a product is unavailable in a store.
- Category averages are not official CPI measurements.
- Basket comparisons do not include travel costs, delivery fees or the time required to visit multiple stores.

## 👨‍💻 Author

**Banele Nelson Ntuli**

- GitHub: [@Banelenelson02](https://github.com/Banelenelson02)
- Project: [SA Grocery Price Intelligence](https://github.com/Banelenelson02/sa-grocery-intelligence)

Built as a personal data engineering project while developing practical experience with Python, APIs, SQL, ETL pipelines and analytics.

---

<p align="center">
  <i>Turning grocery price records into useful insights.</i>
</p>

<p align="center">
  WeThinkCode_ project reference: <b>WTC-E43X2F5H</b>
</p>
