🚀 Kasparro Backend & ETL System

A production-grade Backend + ETL pipeline built with FastAPI, Async SQLAlchemy, PostgreSQL, and Docker.
This system ingests data from multiple heterogeneous sources, normalizes it into a unified schema, detects schema drift, ensures idempotency, and exposes health & analytics APIs.

Live API (Render):
👉 https://kasparro-backend-omkar-biradar-tme4.onrender.com

📌 Project Objectives

This project was built to satisfy Backend & ETL Systems – Final Evaluation Requirements, focusing on:

Multi-source ETL ingestion

Fault tolerance & retries

Schema drift detection

Idempotent writes

Observability & run tracking

Production-level structure (Dockerized)

Testability & automation readiness

🏗️ System Architecture
                   ┌───────────────────┐
                   │   CoinGecko API   │
                   └─────────┬─────────┘
                             │
                   ┌─────────▼─────────┐
                   │  API Ingestion     │
                   │  + Retry + Limits  │
                   └─────────┬─────────┘
                             │
 ┌───────────────┐   ┌───────▼────────┐   ┌────────────────┐
 │ Products CSV  │──▶│ Unified Records │◀──│ Vendors CSV     │
 └───────────────┘   └───────┬────────┘   └────────────────┘
                             │
                    ┌────────▼────────┐
                    │ PostgreSQL DB    │
                    │ (Async SQLA)     │
                    └────────┬────────┘
                             │
                  ┌──────────▼──────────┐
                  │ FastAPI Application │
                  └─────────────────────┘

🧩 Data Sources
1️⃣ CoinGecko API (External API)

Endpoint: /coins/list

Handles:

Rate limiting (HTTP 429)

Exponential backoff retries

Schema drift detection

2️⃣ Products CSV

Local CSV file

Includes invalid rows (intentionally)

Demonstrates graceful validation failure handling

3️⃣ Vendors CSV

Different schema from products CSV

Normalized into unified records

🔁 ETL Pipeline Flow

Start ETL Run

Read checkpoint (last processed marker)

Fetch data

Detect schema drift

Validate input

Insert raw data

Insert unified records

Skip duplicates

Update checkpoint

Mark run success/failure

Each ETL execution is tracked in the database.

📊 Database Schema (Core Tables)

etl_runs – ETL execution tracking

raw_api_data – Raw API payloads

raw_csv_data – Raw CSV rows

unified_records – Normalized output

ingestion_checkpoints – Idempotency support

schema_snapshots – Schema drift tracking

🧠 Schema Drift Detection

Extracts structural schema signatures from API responses

Stores latest schema in schema_snapshots

Logs warnings when schema changes are detected

Does not crash ingestion

🔒 Idempotency & Data Safety

Unique constraint on:

(source, external_id)

Duplicate data is safely ignored

Checkpoints ensure exactly-once semantics

🔁 Retry & Rate Limiting

Exponential backoff retries

Handles HTTP 429 Too Many Requests

Configurable retry count

Logs every retry attempt

Example log:

Retrying (2/4) after 2.17s due to: 429 Too Many Requests

🧪 Testing
Test Coverage

Health endpoint

Stats endpoint

ETL logic (skipped when DB unavailable)

Run tests
uv run pytest

🔍 Smoke Testing

A smoke test script runs a full ETL cycle inside Docker:

docker compose exec api bash scripts/smoke_test.sh

Verifies:

API ingestion

CSV ingestion

Vendor ingestion

Retry handling

No crashes on bad data

📡 API Endpoints
Health Check
GET /health

Response:

{
  "status": "ok",
  "database": "ok"
}

Statistics
GET /stats

Example:

{
  "total_runs": 12,
  "successful_runs": 10,
  "failed_runs": 2,
  "records_by_source": {
    "coingecko_api": 200,
    "products_csv": 3,
    "vendors_csv": 2
  }
}

🧾 Sample SQL Outputs
ETL Runs
SELECT id, source, status, created_at
FROM etl_runs
ORDER BY created_at DESC;

Unified Records Count
SELECT source, COUNT(*)
FROM unified_records
GROUP BY source;

🐳 Docker Setup
Start system
docker compose up --build

Services:

FastAPI (port 8000)

PostgreSQL (port 5432)

☁️ Deployment Strategy
Current Deployment

Render (Docker-based)

Public URL available

Auto-build on push

👉 Live API:
https://kasparro-backend-omkar-biradar-tme4.onrender.com

Cloud Equivalence (Documented)

Although AWS/GCP billing limitations prevented full cloud deployment, the system is cloud-ready and maps directly to:

AWS ECS / Fargate

GCP Cloud Run

Azure Container Apps

⚠️ Known Limitations

CoinGecko free tier has strict rate limits

Prices not available in /coins/list

Large API batches may trigger retries

Cloud deployment blocked by billing (documented)

📈 Work Completion Status
Area	Completion
Core Backend	✅ 100%
ETL Pipelines	✅ 100%
Schema Drift	✅ 100%
Retry & Rate Limit	✅ 100%
Dockerization	✅ 100%
Testing	✅ 95%
Cloud Deployment	⚠️ Deferred
Documentation	✅ 100%
✅ Overall Completion: ~95%

👤 Author

Omkar Biradar  
Backend & ETL Engineer  
GitHub: https://github.com/Om13884/kasparro-backend-Omkar-Biradar.git

✅ Submission Status

✔ All mandatory backend & ETL requirements completed  
✔ Production-quality code  
✔ Fully documented  
✔ Ready for evaluation
