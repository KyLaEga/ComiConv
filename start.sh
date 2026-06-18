#!/bin/bash
echo "Установка зависимостей..."
python3 -m pip install -r requirements.txt
echo "Запуск Desktop-приложения ComiConv..."
python3 main.py
