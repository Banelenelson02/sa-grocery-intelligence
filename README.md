# SA Grocery Price Intelligence Platform

> Track SA grocery prices across 10 retailers, surface inflation trends by category, and find the cheapest store combination for your weekly basket.

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-blue?style=flat-square)](https://supabase.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square)](https://react.dev)
[![Airflow](https://img.shields.io/badge/Airflow-2.9-red?style=flat-square)](https://airflow.apache.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square)](https://docker.com)

---

## The Problem

Comparing grocery prices in South Africa is a snapshot game — you can check who is cheapest today, but nobody shows you who has been *consistently* cheaper over time, how fast specific categories are inflating, or how to split a shopping list across stores to minimise total spend.

This project builds the data infrastructure to answer those questions.

---

## Live Demo

| | Link |
|---|---|
| 🌐 Dashboard | *Coming soon — deploying September 2026* |
| 📡 API (Swagger UI) | *Coming soon* |

---

## What It Does

- **Price trend tracking** — weekly price history per product across all stores, with week-over-week change calculated via SQL window functions
- **Store comparison** — ranks stores by average price for a given product category, cheapest first
- **Inflation analysis** — month-over-month price change per category per store, visualised as a heatmap
- **Basket optimizer** — given a shopping list, returns the cheapest single-store option and the cheapest split across two stores, with the saving in Rand

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   DATA SOURCES                       │
│  Open Price Engine API        BusinessTech CSV       │
│  (Pick n Pay + Woolworths)    (10 stores, monthly)  │
│           daily                                      │
└────────────────┬──────────────────┬─────────────────┘
                 │                  │
                 ▼                  ▼
┌─────────────────────────────────────────────────────┐
│              ETL PIPELINE  (Apache Airflow)          │
│         Extract → Normalize → Validate → Load        │
└───────────────────────────┬─────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────┐
│           PostgreSQL on Supabase                     │
│   stores | products | prices | baskets               │
└───────────────────────────┬─────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI  (Analytics API)                │
│    /trends   /compare   /inflation   /basket         │
└───────────────────────────┬─────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────┐
│         React + Tailwind CSS  (Dashboard)            │
│  Price trends | Store rankings | Basket optimizer    │
└─────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Data processing | Pandas |
| Pipeline scheduling | Apache Airflow |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy |
| API | FastAPI + Pydantic |
| Frontend | React 18 + Tailwind CSS + Recharts |
| Containerization | Docker + Docker Compose |

---

## Data Sources

| Source | Stores covered | Frequency |
|---|---|---|
| [Open Price Engine API](https://openpricengine.com) | Pick n Pay, Woolworths | Daily |
| BusinessTech basket comparison | Shoprite, Checkers, PnP, SPAR, Woolworths, Food Lover's, Makro | Monthly |

---

## Project Structure

```
sa-grocery-intelligence/
├── etl/
│   ├── extract/          # API + CSV extractors
│   ├── transform/        # Normalize, validate, categorize
│   ├── load/             # PostgreSQL upsert
│   └── pipeline.py       # Orchestrator
├── dags/                 # Airflow DAGs (daily + monthly)
├── db/
│   ├── schema.sql        # Full schema reference
│   ├── migrations/       # Versioned schema changes
│   └── seed/             # Stores + products seed data
├── api/
│   ├── routers/          # One file per endpoint
│   ├── schemas.py        # Pydantic models
│   └── main.py           # FastAPI app
├── frontend/
│   └── src/components/   # PriceTrendChart, BasketOptimizer, etc.
├── tests/                # pytest — extract, transform, load, API
├── docs/                 # Architecture + data dictionary
└── docker-compose.yml
```

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Banelenelson02/sa-grocery-intelligence.git
cd sa-grocery-intelligence

# 2. Set up environment variables
cp .env.example .env
# Fill in your Supabase connection string and Open Price Engine API key

# 3. Start the full stack
docker-compose up

# 4. Run the pipeline manually (first time)
docker-compose run pipeline python etl/pipeline.py

# 5. Open the dashboard
# http://localhost:5173

# 6. Open the API docs
# http://localhost:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/trends?product_id=5&weeks=12` | Price over time with week-over-week change |
| GET | `/compare?category=Staples` | Stores ranked cheapest first |
| GET | `/inflation?store_id=2&months=6` | Month-over-month price change per category |
| POST | `/basket` | Basket optimizer — single store vs split |

Full API reference: [`docs/api_reference.md`](docs/api_reference.md)

---

## Running Tests

```bash
# Full test suite
pytest tests/ -v

# Single layer
pytest tests/test_extract.py -v
pytest tests/test_transform.py -v
pytest tests/test_api.py -v
```

---

## Roadmap

- [x] Project structure and schema design
- [ ] Open Price Engine extractor
- [ ] BusinessTech CSV parser
- [ ] Normalize + validate pipeline
- [ ] PostgreSQL loader with upsert
- [ ] Airflow DAGs
- [ ] FastAPI endpoints
- [ ] React dashboard
- [ ] Deploy to Render + Vercel
- [ ] Phase 2: expand to non-grocery retailers (Takealot, Makro, iStore)

---

## Background

This project started from a simple observation at university: splitting your grocery shopping across stores saves real money, but nobody had built the data infrastructure to prove it systematically or tell you exactly where to shop.

Built by **Banele Ntuli** — software development student at WeThinkCode_, Pretoria.

*Inspired by the gap Grocify identified in the SA market — this project focuses on the analytics and data engineering layer rather than the comparison interface.*

---

## Docs

- [Architecture](docs/architecture.md)
- [Data Dictionary](docs/data_dictionary.md)
- [API Reference](docs/api_reference.md)

