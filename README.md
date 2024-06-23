## Проектная работа 6 спринта

В этом спринте наша команда: 
- Развернула S3 хранилище ```minio```, 
- Написала сервис ```File_Service``` для взаимодействия с ```S3``` харнилищем,
- Внесла изменения в ```Django``` проект, чтобы он мог работать с ```S3```
- Внесла изменения в ```ETL``` проект, чтобы он мог обновлять данные с ```S3```
- Доработала сервис ```Api Movies```
- Написала тесты

### Доска на которой мы вели:
[Канбан доска](https://github.com/users/oruchkin/projects/7/views/1)

# Docker compose
## Profiles
Чтобы не поднимать всю вселенную разом, можно использовать профили, например:
```
docker compose --profile admin up
```
Доступные профили:
- admin - только то, что необходимо для работы Django
- admin-dev - база и хранилища файлов с высунутыми наружу портами
- etl - только etl часть
- fastapi - только окружение для fastapi
- all - admin, etl, fastapi, но без тестов


## External volumes
В docker-compose используются внешние статические зависимости, чтобы сделать управление данными более надежным. Чтобы инициализировать такую зависимость в docker, нужно выполнить команду:
```
docker volume create <volume name> --opt type=none --opt device=<path to volume> --opt o=bind
```

![screenshot](readme/make-admin.png) вот так можно удобно создавать админа make admin в терминале

![screenshot](readme/run-etl.png) чтобы перезапустить etl сервис и чтобы он снова прогнал все данные из постгри в эластик, нужно внутри контейнера удалить etl_state.json (на случай если тестами все почистишь)

![screenshot](readme/tests-failed.png) Тесты в моменте фэйлятся, но подключаются и к redis + elastic, и чистят эластик полностью (что плохо) пофикшу позже


```docker-compose --env-file .env up --build``` запуск если env слетают

# IDP
Check later: https://www.reddit.com/r/Python/comments/16pin4l/a_maintained_library_for_oidc_in_python/

JWT libraries: https://jwt.io/libraries?language=Python

## Keycloak

### Development
Setup all the environment variables and run
```
docker compose --profile idp-dev up --attach keycloak
```
1) руками создать в базе данных базу ```idp```

### Setup client
From https://medium.com/@imsanthiyag/introduction-to-keycloak-admin-api-44beb9011f7d
- Go to Clients, on the Clients list tab select admin-cli and in Capability config set `Client authentication` to On. 
- Also check `Service accounts roles`.
- After hitting Save you must see new Credentials tab on the top.
- Switch to that tab and copy Client secret value.


- Important step: To perform specific operations like create users client must have roles assigned. 
- Click on the `admin-cli` client, then open `Service accounts roles` tab
and assign `manage-users` role from the `master-realm`.
![screenshot](readme/keycloak/client-assign-role.png)

### Tips
Open Dev tab in browser to see what requests Keycloak UI is sending to the API
