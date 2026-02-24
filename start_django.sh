#!/bin/bash
cd /root/trayza-backend

if [ ! -d "venv" ]; then
    echo "venv not found. Creating a new virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
exec gunicorn trayza.wsgi:application --bind 127.0.0.1:8005