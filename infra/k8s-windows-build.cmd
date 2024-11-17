SET DOCKER_TLS_VERIFY=1
SET DOCKER_HOST=tcp://127.0.0.1:51071
SET DOCKER_CERT_PATH=C:\Users\avgre\.minikube\certs
SET MINIKUBE_ACTIVE_DOCKERD=minikube
REM To point your shell to minikube's docker-daemon, run:
REM @FOR /f "tokens=*" %i IN ('minikube -p minikube docker-env --shell cmd') DO @%i

docker build -t k8s-keycloak ../idp/keycloak

docker build -t k8s-admin ../admin

docker build -t k8s-admin-nginx ../admin -f ../admin/nginx/Dockerfile

docker build -t k8s-idp ../idp

docker build -t k8s-pginit ../postgres_init

docker build -t k8s-etl ../etl

docker build -t k8s-fileapi ../file_service