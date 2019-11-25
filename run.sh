#!/bin/bash
gunicorn -w 1 -k eventlet -b 0.0.0.0:$APP_PORT --log-level debug --timeout 120 simoc_server:app