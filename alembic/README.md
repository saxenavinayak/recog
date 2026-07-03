## Running migrations
- Before commiting any db changes, update any corresponding migrations that need to take place with `uv run alembic revision --autogenerate -m "Initial migration with pgvector"`
- You can then apply db changes with `uv run alembic upgrade head`
- `env.py` already pulls the existing config (models, db url) so that alembic knows what to apply where
