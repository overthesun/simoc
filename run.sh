#!/bin/bash
gunicorn -w $WORKERS -k gevent -b 0.0.0.0:$PORT simoc_server:app