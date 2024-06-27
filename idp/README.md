Проектная работа 7 спринта

В этом спринте наша команда: 
- Развернула сервис ```keycloak``` 
- Написала сервис ```ipd``` для взаимодействия с ```keycloak``` через API

### Доска на которой мы вели задачи:
https://github.com/users/oruchkin/projects/8/ - Канбан доска 


### Как запустить
### 1. Создать `.env` файл скопировав содержимое из `.env.example`
### 2. Запустить запустить docker-compose.yml
```
docker compose up
```

#### Запущеные сервисы - ссылки:
- http://localhost:8080/ - keycloak 
- http://localhost:8000/api/openapi - документация `swagger` для `idp` 

### 3. Логинимся в админку - заходим в `keycloak`:
- username - `admin` (данные из `.env.example`)
- password - `admin` 

### 4. Настраиваем keycloak 
- Идем в `clients` -> выбираем `admin-cli` проваливаемся внутрь
- Внутри доходим до `Capability config`
- Нажать тумблер включить `Client authentication`
- Нажать галочку включить `Service accounts roles`
- Жмем `Save`
- Наверху появился раздел `Credentials`, идем туда
- Копируем `Client secret`
- Скопированные `client secret` вставляем в `.env` проекта сюда `IDP_KEYCLOAK_SECRET=Check_readme_IDP_section`
- перезапускаем `docker-compose up`

### 5. Накидываем базовые роли
- на главной странице кейклока выбираем раздел `clients`
- выбираем клиент `admin-cli`
- выбираем вкладку `service accounts roles`
- жмем кнопку `Assign role`
- здесь несколько страниц, выбери чтобы показовало все роли на одной странице
- добавь роли, нажми галочку на (удобно нажать CTRL + F): 
- `manage-users` - чтобы создавать юзеров 
- `view-clients` - чтобы получить id текущего клиента
- `manage-clients` - чтобы управлять ролями текущего клиента
- Нажми кнопку `Assign`

### Сервис уже работает
для дебага можно увеличить время жизни токена
- идем в `Realm settings`
- Вкладка `Tokens`
- `Access Token Lifespan` поставить сколько нужно, по умолчанию 1 минута

Создайте пользователя, API `Create user`, и авторизуйтесь получите токен в `Authenticate user`
В swagger можно авторизоваться справа сверху полученый токен прикрепить к хедеру кнопка `Authorize`
