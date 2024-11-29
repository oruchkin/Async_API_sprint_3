docker build -t gdreyv/k8s-keycloak:latest ../../idp/keycloak

docker build -t gdreyv/k8s-admin:latest ../../admin

docker build -t gdreyv/k8s-admin-nginx:latest ../../admin -f ../../admin/nginx/Dockerfile

docker build -t gdreyv/k8s-idp:latest ../../idp

docker build -t gdreyv/k8s-pginit:latest ../../postgres_init

docker build -t gdreyv/k8s-etl:latest ../../etl

docker build -t gdreyv/k8s-fileapi:latest ../../file_service

docker build -t gdreyv/k8s-api:latest ../../api

docker build -t gdreyv/k8s-notifications:latest ../../notifications

docker push gdreyv/k8s-keycloak:latest
docker push gdreyv/k8s-admin:latest
docker push gdreyv/k8s-admin-nginx
docker push gdreyv/k8s-idp:latest
docker push gdreyv/k8s-pginit:latest
docker push gdreyv/k8s-etl:latest
docker push gdreyv/k8s-fileapi:latest
docker push gdreyv/k8s-api:latest
docker push gdreyv/k8s-notifications:latest