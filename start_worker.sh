#!/bin/bash
export NO_FLASK=1
celery worker --app=celery_worker.tasks --concurrency=2 -O fair  -n worker@%h --loglevel=DEBUG -E
