#!/bin/bash

alembic stamp head
alembic revision --autogenerate
alembic upgrade head

gunicorn src.main:app -w 2 --worker-class uvicorn.workers.UvicornWorker -b "0.0.0.0:8000" --log-level info
