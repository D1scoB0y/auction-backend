#!/bin/bash

NAME=fastapi-app
DIR=/home/backend-admin/auction-backend
USER=backend-admin
GROUP=backend-admin
WORKERS=2
WORKER_CLASS=uvicorn.workers.UvicornWorker
VENV=venv/bin/activate
BIND=unix:$DIR/run/gunicorn.sock
LOG_LEVEL=info
ACCESS_LOG_FORMAT='%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

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
  --access-logformat=$ACCESS_LOG_FORMAT
