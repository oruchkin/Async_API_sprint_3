#!/bin/bash

PROJECT_ROOT=$(dirname "$(dirname "$(pwd)")")
DOCKER_NAMESPACE="oruchkin"

echo "Собираем образ $DOCKER_NAMESPACE/k8s-keycloak"
docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_NAMESPACE/k8s-keycloak "$PROJECT_ROOT/idp/keycloak" --push

echo "Собираем образ $DOCKER_NAMESPACE/k8s-admin"
docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_NAMESPACE/k8s-admin "$PROJECT_ROOT/admin" --push

echo "Собираем образ $DOCKER_NAMESPACE/k8s-admin-nginx"
docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_NAMESPACE/k8s-admin-nginx -f "$PROJECT_ROOT/admin/nginx/Dockerfile" "$PROJECT_ROOT/admin" --push

echo "Собираем образ $DOCKER_NAMESPACE/k8s-idp"
docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_NAMESPACE/k8s-idp "$PROJECT_ROOT/idp" --push

echo "Собираем образ $DOCKER_NAMESPACE/k8s-pginit"
docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_NAMESPACE/k8s-pginit "$PROJECT_ROOT/postgres_init" --push

echo "Собираем образ $DOCKER_NAMESPACE/k8s-etl"
docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_NAMESPACE/k8s-etl "$PROJECT_ROOT/etl" --push

echo "Собираем образ $DOCKER_NAMESPACE/k8s-fileapi"
docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_NAMESPACE/k8s-fileapi "$PROJECT_ROOT/file_service" --push

echo "Собираем образ $DOCKER_NAMESPACE/k8s-api"
docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_NAMESPACE/k8s-api "$PROJECT_ROOT/api" --push

echo "Собираем образ $DOCKER_NAMESPACE/k8s-notifications"
docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_NAMESPACE/k8s-notifications "$PROJECT_ROOT/notifications" --push

echo "Сборка завершена!"
