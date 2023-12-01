#!/bin/bash

DIR=/home/backend-admin/auction-backend
VENV=venv/bin/activate
LOG_LEVEL=info

cd $DIR
source $DIR/$VENV

exec celery -A src.celery_:celery beat \
    --loglevel=$LOG_LEVEL
