#!/bin/bash
gunicorn -w 1 -k gevent -b 0.0.0.0:$PORT simoc_server:app