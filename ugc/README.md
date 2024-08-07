## Проектная работа 9 спринта

В этом спринте наша команда:


- Проработала [архитектуру](https://github.com/oruchkin/Async_API_sprint_3/blob/1a8354d345d56a2877e9ae7b9330e52757130f55/docs/diagrams/out/ugc_service.png
) UGC (User Generated Content) системы.
- Подключила Kafka для обработки сообщений.
- Разработала UGC сервис на Flask, который отправляет данные в Kafka.
- Развернула UI сервис для работы с Kafka.
- Развернула ClickHouse для хранения данных.
- Написала ETL сервис для интеграции Kafka и ClickHouse.


### Доска, на которой мы вели задачи:
[Канбан доска](https://github.com/users/oruchkin/projects/11/views/1)

### Как запустить проект:
Из корневой папки проекта выполните команду:

```
docker-compose --profile ugc --profile etl up --build
```

Эта команда запустит все необходимые сервисы, включая `api`, `Kafka`, `ClickHouse` и `ETL`.

### Инициализация базы данных (`обязательно!`):
Для создания базы данных и таблицы в ClickHouse выполните скрипт `create_tables.sql` из папки `etl_service`.


### Сравнительная характеристика ClickHouse и Vertica:
Результаты сравнительного анализа ClickHouse и Vertica находятся в файлах [vertica_results.md](https://github.com/oruchkin/Async_API_sprint_3/blob/da3178d66e5d740c1d5889ee8cefe040df665d48/ugc/compare/src/vertica_results.md) и [clickhouse_results.md](https://github.com/oruchkin/Async_API_sprint_3/blob/da3178d66e5d740c1d5889ee8cefe040df665d48/ugc/compare/src/clickhouse_results.md) в папке `/compare/src/`.

### Сервисы и их назначение:

- **API сервис (Flask)**:
  - Обрабатывает пользовательские события и отправляет их в Kafka.

- **Kafka**:
  - Используется как брокер сообщений для временного хранения событий перед их обработкой и загрузкой в ClickHouse.

- **UI сервис для Kafka**:
  - Позволяет визуализировать и управлять сообщениями в Kafka.
  - Доступен по адресу: [http://localhost:8080](http://localhost:8080)

- **ETL сервис**:
  - Извлекает данные из Kafka, преобразует их и загружает в ClickHouse.

- **ClickHouse**:
  - Хранилище данных для аналитики.


### Заключение:
В этом спринте мы успешно интегрировали несколько ключевых компонентов для обработки пользовательского контента, включая Kafka, ClickHouse и ETL сервис. Это позволит нам эффективно собирать, обрабатывать и анализировать данные, генерируемые пользователями.
