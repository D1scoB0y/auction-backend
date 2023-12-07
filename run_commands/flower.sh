#!/bin/bash

celery -A src.celery_:celery flower
