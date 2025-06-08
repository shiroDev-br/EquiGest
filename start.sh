#!/bin/sh

uvicorn equigest.app:app --host 0.0.0.0 --port 8000 --reload &
celery -A equigest.celery.celery_app worker --loglevel=debug --pool=solo -E

wait -n

exit $?
