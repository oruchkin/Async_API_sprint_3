#!/bin/bash

# Путь к файлу .env на уровень выше
ENV_FILE="../.env"

# Загрузка переменных из .env файла
export $(grep -v '^#' $ENV_FILE | xargs)

# Переопределение POSTGRES_HOST для локального выполнения
POSTGRES_HOST="localhost"
POSTGRES_DB="postgres"

# Выполнение SQL-скрипта
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -f partitioning.sql

if [ $? -eq 0 ]; then
    echo "Partitioning script executed successfully."
else
    echo "Failed to execute partitioning script."
    exit 1
fi
