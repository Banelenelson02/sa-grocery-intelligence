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
- [Architecture](docs/architecture.md)
- [Data Dictionary](docs/data_dictionary.md)
- [API Reference](docs/api_reference.md)
