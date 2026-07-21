# SA Grocery Price Intelligence Platform

> A data engineering pipeline that tracks South African grocery prices over time,
> surfaces category-level inflation trends, and optimises grocery baskets by cost.

## Live Demo
🔗 *Coming soon*

## Tech Stack
Python · PostgreSQL (Supabase) · Apache Airflow · FastAPI · React · Docker

## Quick Start
```bash
git clone https://github.com/Banelenelson02/sa-grocery-intelligence.git
cd sa-grocery-intelligence
cp .env.example .env
# Fill in your Supabase connection string and OPE API key
docker-compose up
```

## Data Sources
- Open Price Engine API (Pick n Pay + Woolworths, daily)
- BusinessTech monthly basket comparison (7 stores, monthly)

## Docs
> Track SA grocery prices across 10 retailers, surface inflation trends by category, and find the cheapest store combination for your weekly basket.

[![CI](https://img.shields.io/github/actions/workflow/status/Banelenelson02/sa-grocery-intelligence/test.yml?label=tests&style=flat-square)](https://github.com/Banelenelson02/sa-grocery-intelligence/actions)
[![Coverage](https://img.shields.io/badge/coverage-pytest-green?style=flat-square)](#running-tests)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-blue?style=flat-square)](https://supabase.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square)](https://react.dev)
[![Airflow](https://img.shields.io/badge/Airflow-2.9-red?style=flat-square)](https://airflow.apache.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square)](https://docker.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000?style=flat-square)](https://github.com/psf/black)

---

## The Problem

Comparing grocery prices in South Africa is a snapshot game — you can check who is cheapest today, but nobody shows you who has been *consistently* cheaper over time, how fast specific categories are inflating, or how to split a shopping list across stores to minimise total spend.

This project builds the data infrastructure to answer those questions.

---

## Live Demo

| | Link |
|---|---|
| 🌐 Dashboard | *Deploying September 2026* |
| 📡 API (Swagger UI) | *Deploying September 2026* |

**Dashboard wireframe — basket optimizer view:**

```
┌─────────────────────────────────────────────────────────────┐
│  🛒 Basket Optimizer                                         │
│  ─────────────────────────────────────────────────────────  │
│  + Bread 700g  x2      + Full Cream Milk 2L  x1             │
│  + Maize Meal 5kg  x1  + Eggs 6-pack  x2                    │
│                                                              │
│  Budget: R 500                    [ Find cheapest stores ]  │
│  ─────────────────────────────────────────────────────────  │
│  ✅ Single store:  Makro          Total: R 287.50            │
│  💡 Split stores:  Shoprite (staples) + Food Lover's (eggs)  │
│                                   Total: R 261.20  Save R26  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  📈 Price Trend — Albany White Bread 700g                    │
│                                                              │
│  R36 ┤                                          ╭── Woolies  │
│  R32 ┤              ╭────────────────────╮     │            │
│  R28 ┤─────────────╯  Pick n Pay         ╰─────╯            │
│  R24 ┤══════════════════════════════ Shoprite ══════        │
│      └────────────────────────────────────────────          │
│        Jul      Aug      Sep      Oct      Nov               │
└─────────────────────────────────────────────────────────────┘
```

---

## What It Does

- **Price trend tracking** — weekly price history per product across all stores, with week-over-week change calculated via SQL `LAG()` window functions
- **Store comparison** — ranks stores by average price for a given product category, cheapest first
- **Inflation analysis** — month-over-month price change per category per store, visualised as a colour-coded heatmap
- **Basket optimizer** — given a shopping list, returns the cheapest single-store option and the cheapest split across two stores, with the saving in Rand

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     DATA SOURCES                         │
│   Open Price Engine API        BusinessTech CSV          │
│   (Pick n Pay + Woolworths)    (10 stores, monthly)     │
│            daily                                         │
└──────────────────┬──────────────────┬───────────────────┘
                   │                  │
                   ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│            ETL PIPELINE  (Apache Airflow)                │
│       Extract → Normalize → Validate → Load              │
│                                                          │
│  • Retries: 2 attempts, 5-min delay on failure           │
│  • Rejected rows logged to data/rejected/ with reason    │
│  • Rate limit handling: exponential backoff on 429       │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL on Supabase                      │
│   stores | products | prices | baskets | basket_items    │
│                                                          │
│  • prices table is append-only (never UPDATE, only INSERT)│
│  • recorded_at column indexed for fast range queries     │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI  (Analytics API)                    │
│    /trends   /compare   /inflation   /basket             │
│                                                          │
│  • Pydantic validation on every request + response       │
│  • 422 on bad params, empty list on unknown IDs          │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│        React + Tailwind CSS  (Dashboard)                 │
│  Price trends | Store rankings | Basket optimizer        │
└─────────────────────────────────────────────────────────┘
```

---

## Database Schema (ERD)

```mermaid
erDiagram
    stores {
        int id PK
        varchar name
        varchar chain
        varchar region
    }

    products {
        int id PK
        varchar name
        varchar category
        varchar subcategory
        varchar unit
        varchar barcode
    }

    prices {
        int id PK
        int product_id FK
        int store_id FK
        numeric price_zar
        boolean on_promotion
        timestamptz recorded_at
        varchar source
    }

    baskets {
        int id PK
        varchar name
        timestamptz created_at
    }

    basket_items {
        int basket_id FK
        int product_id FK
        int quantity
    }

    stores ||--o{ prices : "store_id"
    products ||--o{ prices : "product_id"
    products ||--o{ basket_items : "product_id"
    baskets ||--o{ basket_items : "basket_id"
```

> **Key design decision:** The `prices` table is append-only history. When a price changes, a new row is inserted with the new date — the existing row is never modified. This is what makes trend analysis and inflation tracking possible.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.11 | ETL pipeline + API |
| Data processing | Pandas | Cleaning, normalizing, reshaping |
| Pipeline scheduling | Apache Airflow | Automated daily + monthly runs |
| Database | PostgreSQL (Supabase) | Price history storage |
| ORM | SQLAlchemy | Python ↔ PostgreSQL |
| API | FastAPI + Pydantic | Analytics endpoints + validation |
| Frontend | React 18 + Tailwind + Recharts | Dashboard |
| Containerization | Docker + Docker Compose | One-command local setup |
| CI/CD | GitHub Actions | Automated testing on every push |
| Code quality | black + flake8 | Formatting + linting |

---

## Data Sources

| Source | Stores covered | Frequency | Access |
|---|---|---|---|
| [Open Price Engine API](https://openpricengine.com) | Pick n Pay, Woolworths | Daily | Free API key (renewable monthly) |
| BusinessTech basket comparison | Shoprite, Checkers, PnP, SPAR, Woolworths, Food Lover's, Makro | Monthly | Public — manually maintained CSV |

---

## Quick Start

### 1. Prerequisites

- Docker + Docker Compose installed
- A free [Supabase](https://supabase.com) account (takes 60 seconds)
- A free [Open Price Engine](https://openpricengine.com) API key

### 2. Get your API keys

**Supabase (database):**
1. Go to [supabase.com](https://supabase.com) → New Project
2. Settings → Database → Connection string → URI
3. Copy the full connection string — it looks like: `postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres`

**Open Price Engine (grocery price data):**
1. Go to [openpricengine.com](https://openpricengine.com) → Sign up
2. Navigate to API Keys → Generate key
3. Note: free keys expire after 30 days — renew via the dashboard

### 3. Clone and configure

```bash
git clone https://github.com/Banelenelson02/sa-grocery-intelligence.git
cd sa-grocery-intelligence

cp .env.example .env
# Open .env and fill in:
# DATABASE_URL=postgresql://...   (from Supabase)
# OPE_API_KEY=...                 (from Open Price Engine)
```

### 4. Run the stack

```bash
# Start PostgreSQL + Airflow + FastAPI
docker-compose up

# First-time database setup
docker-compose run pipeline python scripts/seed_db.sh

# Run the pipeline manually (first data load)
docker-compose run pipeline python etl/pipeline.py

# Open the dashboard
open http://localhost:5173

# Open the API docs (Swagger UI)
open http://localhost:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check — confirms API + DB reachable |
| `GET` | `/trends?product_id=5&weeks=12` | Price over time with week-over-week % change |
| `GET` | `/compare?category=Staples` | Stores ranked cheapest first for a category |
| `GET` | `/inflation?store_id=2&months=6` | Month-over-month price change per category |
| `POST` | `/basket` | Basket optimizer — single store vs split recommendation |

**Example — basket request:**
```json
POST /basket
{
  "items": [
    { "product_id": 1, "qty": 2 },
    { "product_id": 5, "qty": 1 }
  ],
  "budget": 500
}
```

**Example — basket response:**
```json
{
  "single_store": { "store": "Makro", "total_zar": 287.50 },
  "split_stores": {
    "total_zar": 261.20,
    "stores": [
      { "store": "Shoprite", "subtotal": 142.00 },
      { "store": "Food Lovers", "subtotal": 119.20 }
    ]
  },
  "saving_zar": 26.30
}
```

Full API reference: [`docs/api_reference.md`](docs/api_reference.md)

---

## CI/CD & Code Quality

Every push to `main` or `develop` triggers the GitHub Actions pipeline:

```yaml
# .github/workflows/test.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: black --check .          # formatting
      - run: flake8 etl/ api/ tests/  # linting
      - run: pytest tests/ -v --tb=short  # full test suite
```

**Local code quality checks:**
```bash
# Format code
black .

# Lint
flake8 etl/ api/ tests/

# Run tests with coverage
pytest tests/ -v --cov=etl --cov=api --cov-report=term-missing
```

---

## Data Governance & Edge Cases

### API Rate Limiting
The Open Price Engine free tier is rate-limited. The extractor handles this with exponential backoff:
- On HTTP 429: wait 60 seconds, retry up to 2 times
- On HTTP 401: raise immediately with a clear message (expired key — renew at openpricengine.com)
- On timeout: raise after 10 seconds, Airflow retries the full task after 5 minutes

### Missing or Malformed Data
The BusinessTech CSV is manually maintained and occasionally has missing cells or formatting inconsistencies. The validation layer applies six rules before any row touches the database:

| Rule | Condition | Action |
|---|---|---|
| Null price | `price_zar` is null | Reject — log reason |
| Impossible price | `price_zar` ≤ 0 or > R5,000 | Reject — log reason |
| Future date | `recorded_at` is in the future | Reject — log reason |
| Unknown store | Store name not in canonical list | Reject — log reason |
| Duplicate row | Same product + store + date already in batch | Reject — log reason |

Every rejected row is written to `data/rejected/YYYY-MM-DD.log` with its reason. Nothing is silently dropped.

### Supabase Inactivity Pause
Supabase free tier pauses projects after 7 days of inactivity. Since the Airflow pipeline queries the database daily, inactivity is never reached during active development. If the pipeline is paused for more than 7 days, the project can be manually unpaused from the Supabase dashboard in under 30 seconds.

### Duplicate Prevention
The `PostgresLoader` uses `INSERT ... ON CONFLICT DO NOTHING` — running the pipeline twice on the same data inserts zero duplicate rows.

---

## Running Tests

```bash
# Full suite
pytest tests/ -v

# By layer
pytest tests/test_extract.py -v    # extractor tests (mocked API)
pytest tests/test_transform.py -v  # normalization + validation
pytest tests/test_load.py -v       # upsert logic (mocked DB)
pytest tests/test_api.py -v        # FastAPI endpoints (TestClient)

# With coverage report
pytest tests/ -v --cov=etl --cov=api --cov-report=term-missing
```

All tests run without a live database or API connection — every external dependency is mocked.

---

## Project Structure

```
sa-grocery-intelligence/
├── .github/workflows/test.yml  # GitHub Actions CI
├── etl/
│   ├── extract/                # OpenPriceEngineClient, BusinessTechParser
│   ├── transform/              # normalize.py, clean.py, categorize.py
│   ├── load/                   # PostgresLoader (upsert)
│   └── pipeline.py             # Orchestrator — E → T → V → L
├── dags/
│   ├── daily_prices_dag.py     # Runs at 08:00 daily
│   └── monthly_basket_dag.py   # Runs on 1st of each month
├── db/
│   ├── schema.sql              # Full schema reference
│   ├── migrations/             # Versioned schema changes
│   └── seed/                   # Stores + products seed data
├── api/
│   ├── routers/                # trends.py, compare.py, inflation.py, basket.py
│   ├── schemas.py              # Pydantic models
│   └── main.py                 # FastAPI app + CORS
├── frontend/src/
│   └── components/             # PriceTrendChart, StoreComparisonTable,
│                               # InflationHeatmap, BasketOptimizer
├── tests/                      # pytest — all layers mocked
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── api_reference.md
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

---

## Roadmap

- [x] Project structure and schema design
- [x] Architecture and UML documentation
- [ ] Open Price Engine extractor
- [ ] BusinessTech CSV parser
- [ ] Normalize + validate pipeline
- [ ] PostgreSQL loader with upsert
- [ ] Airflow DAGs (daily + monthly)
- [ ] FastAPI endpoints
- [ ] React dashboard
- [ ] GitHub Actions CI
- [ ] Deploy API to Render
- [ ] Deploy frontend to Vercel
- [ ] **Phase 2:** Expand to non-grocery retailers (Takealot, Makro, iStore)

---

## Background

This project started from a simple observation at university: splitting your grocery shopping across stores saves real money, but nobody had built the data infrastructure to prove it systematically or tell you exactly where to shop.

Built by **Banele Ntuli** — software development student at WeThinkCode_, Pretoria. Peer Tutor. Co-founder of [Handcrafted Sites](https://github.com/Banelenelson02).

---

## Docs

- [Architecture](docs/architecture.md)
- [Data Dictionary](docs/data_dictionary.md)
- [API Reference](docs/api_reference.md)
