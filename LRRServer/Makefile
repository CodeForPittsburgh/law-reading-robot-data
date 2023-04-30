db-migrate:
	pipenv run alembic revision --autogenerate

db-downgrade:
	pipenv run alembic downgrade -1

db-upgrade:
	pipenv run alembic upgrade head

serve:
	pipenv run uvicorn lawreadingrobot.main:app --reload
