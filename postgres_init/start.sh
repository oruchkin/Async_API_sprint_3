#!/bin/bash

# Запускаем все сервисы
docker-compose up -d --build

# Проверяем статус контейнера db_init до его завершения
while [ $(docker ps -f name=db_init -q | wc -l) -gt 0 ]; do
    sleep 1
done

# Удаляем контейнер db_init после его завершения
docker-compose rm -fv db_init
