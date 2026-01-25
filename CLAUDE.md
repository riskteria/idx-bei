# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Node.js library for fetching data from the Indonesia Stock Exchange (IDX) API at https://www.idx.co.id. The project provides a comprehensive set of functions to access market data, company information, and financial statistics.

**Key Features:**
- Node.js API client for IDX data
- Python Neo4j graph database integration for network analysis
- PostgreSQL integration for financial ratio analysis
- Python utilities for iXBRL processing

## Architecture

### Core Structure

```
idx-bei/
├── index.js                              # Main entry point - exports all public APIs
├── fetchUtil.js                          # Core HTTP client with caching, retry, and rate limiting
├── utils/template.js                     # Legacy fetch helper (older implementation pattern)
├── listed-companies/
│   └── companyProfiles.js                # Company profile and detail APIs
├── members-and-participants/
│   └── memberProfiles.js                 # Broker, participant, and dealer APIs
├── market-data/
│   ├── trading-summary/                  # Stock/index trading data
│   ├── bonds-sukuk/                      # Bond/sukuk market data
│   ├── derivatives-data/                 # Futures and derivatives
│   ├── statistical-reports/              # Statistical reports and factsheets
│   └── ... (more market data categories)
├── data/                                 # JSON data files (gitignored)
├── examples/                             # Usage examples
└── python/                               # Python utilities for data processing
```

### Module System

- Uses **ES Modules** ( `"type": "module"` in package.json)
- All public APIs are exported from `index.js` for easy imports
- Example: `import { getCompanyProfiles, getTradeSummary } from 'idx-bei';`

### Core Utilities (`fetchUtil.js`)

The `fetchData` function provides:
- **In-memory caching** with 5-minute TTL (configurable)
- **Rate limiting** (5 requests per second by default)
- **Retry logic** with exponential backoff (3 retries max)
- **Headers** mimicking a browser for CORS compatibility

Key exports:
- `fetchData(url, options, cacheOptions, retryOptions)` - Main fetch function
- `clearCache()` - Clear all cached responses
- `setRateLimit(config)` - Adjust rate limits
- `shouldRetry(error)` - Determine if an error should trigger retry

### API Patterns

Each module follows a consistent pattern:

```javascript
import { fetchData } from '../fetchUtil.js';

const BASE_URL = 'https://www.idx.co.id/primary';
const DEFAULT_CACHE_OPTIONS = { useCache: true, ttl: 15 * 60 * 1000 };
const DEFAULT_RETRY_OPTIONS = { maxRetries: 3, baseDelay: 1000 };

export const getSomeData = (param, options = {}, cacheOptions = {}) =>
  fetchData(
    `${BASE_URL}/SomeEndpoint?param=${param}`,
    { ...DEFAULT_OPTIONS, ...options },
    { ...DEFAULT_CACHE_OPTIONS, ...cacheOptions },
    DEFAULT_RETRY_OPTIONS
  );
```

### Python Utilities

The `python/` directory contains:

#### Neo4j Graph Database Integration (`neo4j.ipynb`)
A comprehensive Jupyter notebook for ingesting IDX data into Neo4j for graph-based network analysis. Key features:

**Data Ingestion:**
- Company profiles with directors, commissioners, corporate secretaries, audit committee members
- Shareholder ownership relationships with ownership percentages
- Subsidiary relationships
- Stock trading data (TradeDay nodes with OHLCV data)

**Node Types:**
- `Company` - Listed companies with all profile data
- `Insider` - Directors, commissioners, shareholders, corporate officers
- `Subsidiary` - Subsidiary companies
- `TradeDay` - Daily stock trading data

**Relationship Types:**
- `DIRECTOR_OF`, `COMMISSIONER_OF`, `CORPORATE_SECRETARY_OF`, `AUDIT_COMMITTEE_MEMBER_OF`
- `OWNS` - Shareholder ownership (with jumlah, kategori, pengendali, persentase)
- `SUBSIDIARY_OF` - Subsidiary relationships
- `HAS_TRADE_DAY` - Company to daily trading data

**Example Cypher Queries:**
```cypher
// Find insider ownership value
MATCH (i:Insider)-[owns:OWNS]->(c:Company)-[:HAS_TRADE_DAY]->(td:TradeDay)
WITH i, owns.jumlah AS sharesOwned, c, td.close AS latestClosePrice
WITH i, sum(sharesOwned * latestClosePrice) AS totalValue
RETURN i.name AS InsiderName, totalValue
ORDER BY totalValue DESC

// Find company network (directors, shareholders, subsidiaries)
MATCH (i:Insider)-[r1:DIRECTOR_OF|COMMISSIONER_OF]->(c:Company {kode: 'BBCA'})
OPTIONAL MATCH (s:Subsidiary)-[r2:SUBSIDIARY_OF]->(c)
RETURN DISTINCT i, r1, c, r2, s
```

**Note:** Requires Neo4j running on localhost:7687 with credentials (default: neo4j/password)

**Additional Features in neo4j.ipynb:**
- **PostgreSQL EDA** - Analyzes financial ratios from PostgreSQL database with Buffett-style filtering
- **yfinance integration** - Collects data from Yahoo Finance for Indonesian stocks (`.JK` tickers)
- **Insider visualization** - Plots total ownership value of insiders
- **Data analysis** - PER analysis, clustering, and stock screening

#### Other Python Files:
- `ixbrl.py` - Extracts inline XBRL data from HTML financial reports using BeautifulSoup
- `financial_ratios_json2pg.py` - Data transformation scripts
- `reset_ipynb.py` - Jupyter notebook utilities
- `neo4j.ipynb` - Main Neo4j ingestion notebook (includes EDA with PostgreSQL, yfinance data collection, and visualization)

## Common Tasks

### Running Examples

```bash
# Run main entry point
npm run main

# Run specific example
node examples/company-profiles.js
node examples/broker-search.js
node examples/financial-ratio.js
```

### Installing Dependencies

```bash
npm install
```

### Python Scripts

```bash
# Install Python dependencies
pip install beautifulsoup4 lxml neo4j pandas sqlalchemy psycopg2-binary yfinance tqdm matplotlib seaborn scikit-learn

# Run iXBRL parser
python python/ixbrl.py

# Run Neo4j ingestion (requires running Neo4j instance)
jupyter notebook python/neo4j.ipynb
```

### Code Patterns to Follow

1. **New endpoint modules** should follow the pattern in `listed-companies/companyProfiles.js`:
   - Use `fetchData` from `fetchUtil.js`
   - Configure proper cache and retry options
   - Export `configureRateLimit` and `clearApiCache` utilities

2. **Legacy modules** use `utils/template.js` (older pattern) - prefer `fetchUtil.js` for new code

3. **Example scripts** show real-world usage patterns including:
   - Pagination handling
   - Error recovery with delays
   - Incremental data saving

### Important Considerations

- The IDX API has rate limits - the `fetchUtil.js` handles this automatically
- Cache is in-memory only (cleared on process restart)
- Data is often paginated - check `examples/company-profiles.js` for pagination patterns
- Some endpoints may return empty data or require specific referrer headers
- Network errors and 429 responses trigger automatic retry with exponential backoff

### Directory Structure

Market data is organized by asset type:
- `trading-summary/` - Real-time trading data (stocks, indexes, brokers)
- `bonds-sukuk/` - Fixed income markets
- `derivatives-data/` - Futures and options
- `statistical-reports/` - Aggregated statistics and factsheets
- `structured-warrant-sw/` - Structured warrants

### Data Output

The `data/` directory contains cached JSON files from example scripts:
- `allCompanies.json` - List of all listed companies
- `companyDetailsByKodeEmiten.json` - Detailed company data
- `brokerSearch.json` - Broker member data
- `financial_ratio.json` - Financial ratio data

### Version

Current version: `1.0.0-prealpha.3`

### License

ISC
