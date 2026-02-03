# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based toolkit for fetching and analyzing data from the Indonesia Stock Exchange (IDX). It leverages `curl_cffi` for scraping, Neo4j for graph analysis, and PostgreSQL for financial modeling.

## Architecture

```
idx-bei/
├── README.md             # Main documentation
├── CONTRIBUTING.md       # Contribution guidelines
├── LICENSE               # MIT License
├── docker-compose.yml    # Database orchestration
├── data/                 # Data output directory (JSON)
└── python/               # Core Python implementation
    ├── scrape_*.py       # Scraping utilities
    ├── neo4j_ingest.py   # Neo4j data ingestion
    ├── neo4j.ipynb       # Analysis & Ingestion Notebook
    └── pyproject.toml    # Dependencies (uv)
```

## Python Implementation Details

- **Dependency Management**: Controlled by `uv` via `python/pyproject.toml`.
- **Scraping**: Uses `curl_cffi` with `impersonate="chrome"` to bypass basic WAFs.
- **Database**: 
  - **Neo4j**: Primary graph database for network analysis.
  - **PostgreSQL**: Used for historical financial ratio analysis.
- **Data Format**: Scripts standardise on JSON output in the `data/` directory.

## Common Tasks

### 1. Synchronize Dependencies
```bash
cd python && uv sync
```

### 2. Start Services
```bash
docker-compose up -d
```

### 3. Run a Scraper
```bash
cd python && uv run scrape_company_profiles.py
```

### 4. Graph Ingestion
Run the cells in `python/neo4j.ipynb` or use `python/neo4j_ingest.py`.

## Code Style & Patterns

- Use **type hints** for all Python code.
- Follow **PEP 8** standards.
- Prefer **functional patterns** for data transformation.
- Ensure all scripts handle rate limiting gracefully (see `scrape_company_profiles.py` for patterns).
