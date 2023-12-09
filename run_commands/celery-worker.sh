#!/bin/bash

celery -A src.celery_:celery worker --loglevel=info --max-memory-per-child 12000 --concurrency 1
