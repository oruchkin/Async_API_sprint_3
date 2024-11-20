# Hosts
127.0.0.1 	keycloak.local
127.0.0.1 	jaeger.local
127.0.0.1   mailhog.local
127.0.0.1   admin.local
127.0.0.1   fileapi.local
127.0.0.1   api.local
127.0.0.1   idp.local

# Полезные команды

Старт
```bash
minikube start
```

Удалить все целиком
```bash
minikube delete
```

Включить ingress
```bash
minikube addons enable ingress 
```

Чотбы пробросить роутинг до хостов обязательно сначала запустить туннель
```bash
minikube tunnel
```

Использовать внутрениий docker
```
minikube docker-env
```
и внимательно читаем, что там написано!


Посмотреть, что сейчас запущено
```bash
kubectl get all
```

If any errors use
```
kubectl descript pod {podname}
```
to see all the details and errors

Expose port
```bash
kubectl port-forward pod/postgres-statefulset-0 5432:5432
```

## Find service url
1. Connect to any pod:
```
kubectl exec -it podName -n namespace -- /bin/sh
```
Install util:
```
apt-get update && apt-get install dnsutils
```
Resolve ip-address (check service in kubectl get all):
```
nslookup ip-address
```
prometheus-service.default.svc.cluster.local

# TODO:
[x] postgres
[x] mongodb
[x] admin
[x] admin-nginx -> k8s-admin-nginx
[x] elasticsearch
[x] etl -> k8s-etl
[x] redis
[x] api -> k8s-api
[x] api-nginx
[x] minio
[x] fileapi -> k8s-fileapi
[x] idp-nginx
[x] idp -> k8s-idp
[x] keycloak -> k8s-keycloak
[x] jaeger
[x] rabbitmq
[ ] notify
[x] mailhog
[x] postgres-init -> k8s-pginit


1. Create db `keycloak` for keycloak