#!/bin/bash
set -e

echo "Ожидание доступности PostgreSQL..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "PostgreSQL недоступен, ожидаем..."
  sleep 1
done

>&2 echo "PostgreSQL доступен. Продолжаем выполнение..."

>&2 echo "Выполнение DDL скрипта..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -a -f /app/movies_database.ddl

>&2 echo "Загрузка данных..."

python /app/load_data.py

>&2 echo "Скрипт инициализации успешно выполнен."

exit 0
