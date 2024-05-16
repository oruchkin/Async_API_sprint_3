#!/bin/bash
set -e

# Ожидание доступности PostgreSQL
/usr/wait-for-it.sh prac_db_postgres:5432 --timeout=30


#echo "Ожидание 5 секунд..."
#sleep 5
echo "dbname=${DB_NAME} user=${DB_USER} password=${DB_PASSWORD} host=${DB_HOST} port=${DB_PORT}"

echo "Выполнение фейковой миграции..."
python manage.py migrate movies --fake

echo "Выполнение миграций django"
python manage.py migrate

echo "Собираем статику"
python manage.py collectstatic --no-input

# Запуск UWSGI
echo "Запуск UWSGI..."
exec uwsgi --ini uwsgi.ini

