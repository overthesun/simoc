#!/bin/bash
gunicorn -w 1 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -b 0.0.0.0:8080 --log-level debug --timeout 120 simoc_server:app
