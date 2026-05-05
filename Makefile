.PHONY: install test lint api ui docker-up

install:
	cd backend && pip install -r requirements.txt
	cd frontend && pip install -r requirements.txt

test:
	cd backend && pytest

lint:
	cd backend && ruff check app tests

api:
	cd backend && uvicorn app.main:app --reload --port 8000

ui:
	cd frontend && streamlit run streamlit_app.py

docker-up:
	docker compose up --build
