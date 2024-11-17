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



# TODO:
[x] postgres
[x] mongodb
[x] admin
[ ] admin-nginx
[x] elasticsearch
[ ] etl
[x] redis
[ ] api
[ ] api-nginx
[x] minio
[ ] fileapi
[ ] idp-nginx
[x] idp -> k8s-idp
[x] keycloak -> k8s-keycloak
[x] jaeger
[x] rabbitmq
[ ] notify
[x] mailhog
[x] postgres-init -> k8s-pginit


1. Create db `keycloak` for keycloak