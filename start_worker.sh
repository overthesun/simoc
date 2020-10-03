#!/bin/bash
export NO_FLASK=1
celery -A celery_worker.tasks worker --concurrency=2 -O fair  -n worker@%h --loglevel=DEBUG -E
