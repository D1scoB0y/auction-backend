#!/bin/bash

gunicorn src.main:app -w 2 --worker-class uvicorn.workers.UvicornWorker -b "0.0.0.0:8000" --log-level info
