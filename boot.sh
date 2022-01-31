#!/bin/sh
export FLASK_APP=run.py
flask db upgrade
exec gunicorn -w 1 -b 127.0.0.1:8000 --access-logfile logs/access.log --error-logfile logs/error.log run:app