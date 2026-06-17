#!/usr/bin/env bash
# Скрипт що Render виконує при кожному деплої
set -o errexit  # При першій помилці зупиняємось

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate