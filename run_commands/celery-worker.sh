#!/bin/bash

celery -A src.celery_:celery worker --loglevel=info
