#!/bin/bash
celery worker --app=celery_worker.tasks --pool=gevent --concurrency=$CELERY_THREADS  -n worker@%h --loglevel=INFO
