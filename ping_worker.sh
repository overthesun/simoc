#!/bin/bash
celery inspect ping -b "redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/" -d worker@$HOSTNAME
