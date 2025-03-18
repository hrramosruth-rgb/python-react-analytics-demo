from datetime import date
from pathlib import Path
from fastapi import FastAPI, HTTPException
from app.domain import load_sales, metrics

ROOT = Path(__file__).resolve().parents[2]

def create_app() -> FastAPI:
    rows = load_sales((ROOT / 'fixtures/sales.csv').read_text())
    app = FastAPI(title='Fixture analytics', version='1.0.0')

    @app.get('/api/metrics')
    def get_metrics(start: date | None = None, end: date | None = None):
        try:
            return metrics(rows, start, end)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    return app
