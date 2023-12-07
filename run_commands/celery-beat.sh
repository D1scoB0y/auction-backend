#!/bin/bash

celery -A src.celery_:celery beat --loglevel=info
