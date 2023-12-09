#!/bin/bash

celery -A src.celery_:celery flower --basic-auth=admin:password
