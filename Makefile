up:
	docker compose up --build

down:
	docker compose down

test:
	uv run pytest

etl:
	docker compose exec api uv run python scripts/run_etl_loop.py
