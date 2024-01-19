docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

rollback:
	alembic downgrade -1

migrate:
	alembic upgrade head

migration:
	alembic revion --autogenerate -m "$(name)"

run-local:
	uvicorn api.solomon.main:app --reload

test:
	pytest -vv $(file) --cov-report term-missing --cov=. --cov-config=.coveragerc

test-cover:
	pytest --cov-report html --cov=. --cov-config=.coveragerc
