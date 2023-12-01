#!/bin/bash

NAME=fastapi-app
DIR=/home/backend-admin/auction-backend
USER=backend-admin
GROUP=backend-admin
WORKERS=2
WORKER_CLASS=uvicorn.workers.UvicornWorker
VENV=venv/bin/activate
BIND=localhost:8000
LOG_LEVEL=info

cd $DIR
source $DIR/$VENV

exec gunicorn src.main:app \
  --name $NAME \
  --workers $WORKERS \
  --worker-class $WORKER_CLASS \
  --user=$USER \
  --group=$GROUP \
  --bind=$BIND \
  --log-level=$LOG_LEVEL \
  --access-logfile=- \
  --log-file=-
