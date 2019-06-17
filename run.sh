#!/bin/bash
gunicorn -w 1 -k gevent -b 0.0.0.0:$APP_PORT simoc_server:app