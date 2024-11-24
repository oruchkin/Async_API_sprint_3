@echo off
REM Set script to fail on error
setlocal enabledelayedexpansion

REM To point your shell to minikube's docker-daemon, run:
FOR /f "tokens=*" %%i IN ('minikube -p minikube docker-env --shell cmd') DO %%i

docker build -t k8s-keycloak ../../idp/keycloak

docker build -t k8s-admin ../../admin

docker build -t k8s-admin-nginx ../../admin -f ../../admin/nginx/Dockerfile

docker build -t k8s-idp ../../idp

docker build -t k8s-pginit ../../postgres_init

docker build -t k8s-etl ../../etl

docker build -t k8s-fileapi ../../file_service

docker build -t k8s-api ../../api

docker build -t k8s-notifications ../../notifications