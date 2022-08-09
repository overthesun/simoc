#!/bin/bash
celery -b "redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/" inspect ping -d worker@$HOSTNAME
