#!/usr/bin/env bash

gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker -c gunicorn_conf.py
