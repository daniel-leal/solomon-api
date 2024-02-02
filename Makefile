docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-database:
	docker-compose up -d db

rollback:
	alembic downgrade -1

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(name)"

run-local:
	uvicorn app.solomon.main:app --reload

test:
	pytest -vv $(file)

test-cover:
	pytest -vv $(file) --cov-report term-missing --cov=. --cov-config=.coveragerc

test-cover-html:
	pytest -vv $(file) --cov-report html --cov=. --cov-config=.coveragerc
