#!/bin/sh

uvicorn equigest.app:app --host 0.0.0.0 --port 8000 --reload &
celery -A equigest.celery.celery_app worker --loglevel=info --without-gossip --pool=solo

wait -n

exit $?
