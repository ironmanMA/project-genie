#!/bin/bash
set -eax
exec 1>/home/ubuntu/encoder-server/service.log 2>&1
cd /home/ubuntu/encoder-server
export FLASK_APP=/home/ubuntu/encoder-server/flask-server.py
python -m flask run --host=0.0.0.0
