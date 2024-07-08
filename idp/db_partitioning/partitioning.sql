-- Переименование существующей таблицы
ALTER TABLE user_entity RENAME TO user_entity_old;

-- Создание новой основной таблицы с партиционированием
CREATE TABLE user_entity (
    id                          varchar(36)           not null,
    email                       varchar(255),
    email_constraint            varchar(255),
    email_verified              boolean default false not null,
    enabled                     boolean default false not null,
    federation_link             varchar(255),
    first_name                  varchar(255),
    last_name                   varchar(255),
    realm_id                    varchar(255),
    username                    varchar(255),
    created_timestamp           bigint,
    service_account_client_link varchar(255),
    not_before                  integer default 0     not null,
    PRIMARY KEY (id, created_timestamp),
    UNIQUE (realm_id, email_constraint, created_timestamp),
    UNIQUE (realm_id, username, created_timestamp)
) PARTITION BY RANGE (created_timestamp);

-- Назначение владельца таблицы
ALTER TABLE user_entity OWNER TO app;

-- Создание партиций
CREATE TABLE user_entity_2022 PARTITION OF user_entity
    FOR VALUES FROM (1640995200) TO (1672531199);  -- Unix timestamp for 2022

CREATE TABLE user_entity_2023 PARTITION OF user_entity
    FOR VALUES FROM (1672531200) TO (1704067199);  -- Unix timestamp for 2023

CREATE TABLE user_entity_2024 PARTITION OF user_entity
    FOR VALUES FROM (1704067200) TO (1735603199);  -- Unix timestamp for 2024

CREATE TABLE user_entity_2025 PARTITION OF user_entity
    FOR VALUES FROM (1735603200) TO (1767139199);  -- Unix timestamp for 2025

CREATE TABLE user_entity_2026 PARTITION OF user_entity
    FOR VALUES FROM (1767139200) TO (1798675199);  -- Unix timestamp for 2026

-- Перенос данных в партиции
INSERT INTO user_entity SELECT * FROM user_entity_old WHERE created_timestamp BETWEEN 1640995200 AND 1672531199;
INSERT INTO user_entity SELECT * FROM user_entity_old WHERE created_timestamp BETWEEN 1672531200 AND 1704067199;
INSERT INTO user_entity SELECT * FROM user_entity_old WHERE created_timestamp BETWEEN 1704067200 AND 1735603199;
INSERT INTO user_entity SELECT * FROM user_entity_old WHERE created_timestamp BETWEEN 1735603200 AND 1767139199;
INSERT INTO user_entity SELECT * FROM user_entity_old WHERE created_timestamp BETWEEN 1767139200 AND 1798675199;

-- Воссоздание индексов
CREATE INDEX idx_user_email ON user_entity (email);
CREATE INDEX idx_user_service_account ON user_entity (realm_id, service_account_client_link);

-- Удаление старой таблицы вместе с зависимостями
DROP TABLE user_entity_old CASCADE;
