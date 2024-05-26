alembic revision --autogenerate -m "create files table"
alembic upgrade head


создать миграцию
alembic revision --autogenerate -m "Добавление поля bucket в FileDbModel"
alembic revision --autogenerate

#применить миграцию
alembic upgrade head
