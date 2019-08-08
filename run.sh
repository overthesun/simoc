#!/bin/bash
gunicorn -w $WSGI_WORKERS -k gevent -b 0.0.0.0:$APP_PORT --log-level debug --timeout 120 simoc_server:app