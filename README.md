
![screenshot](readme/make-admin.png) вот так можно удобно создавать админа make admin в терминале

![screenshot](readme/run-etl.png) чтобы перезапустить etl сервис и чтобы он снова прогнал все данные из постгри в эластик, нужно внутри контейнера удалить etl_state.json (на случай если тестами все почистишь)

![screenshot](readme/tests-failed.png) Тесты в моменте фэйлятся, но подключаются и к redis + elastic, и чистят эластик полностью (что плохо) пофикшу позже

обрати внимание что fastapi сейчас на порту 8001 джанго админка на 8000

![screenshot](readme/common-env.png) сделал общую папку под .env

```docker-compose --env-file ./envs/.env up --build``` запуск если env слетают
