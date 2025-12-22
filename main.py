from fastapi import FastAPI

app = FastAPI(
    title="Kasparro Backend & ETL",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "kasparro-backend-etl",
    }
