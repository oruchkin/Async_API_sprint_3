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

Useful Grafana metrics:
1. Service Uptime
    Chart Type: Single Stat or Gauge
    Query: avg_over_time(up{job="your_service"}[1h]) * 100
    Description: Displays the percentage uptime of a service over the past hour.

2. Request Rate
    Chart Type: Time Series
    Query: rate(http_requests_total{job="your_service"}[1m])
    Description: Tracks the rate of HTTP requests per second for a service.

3. Error Rate
    Chart Type: Bar Gauge or Time Series
    Query: rate(http_requests_total{job="your_service", status=~"5.."}[1m])
    Description: Displays the rate of HTTP 5xx errors over time.

4. CPU Usage
    Chart Type: Time Series
    Query: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
    Description: Monitors CPU utilization for service instances.

5. Memory Usage
    Chart Type: Time Series
    Query: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100
    Description: Tracks memory usage as a percentage.

6. Service Latency
    Chart Type: Time Series or Heatmap
    Query: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="your_service"}[5m])) by (le))
    Description: Shows the 95th percentile latency of HTTP requests.

7. Active Connections
    Chart Type: Time Series
    Query: sum(nginx_http_connections{job="your_service"})
    Description: Tracks the number of active connections for a service.

8. Service Restarts
    Chart Type: Table or Time Series
    Query: rate(process_start_time_seconds{job="your_service"}[1m])
    Description: Monitors unexpected service restarts.

9. Disk Space Usage
    Chart Type: Time Series or Gauge
    Query: (node_filesystem_size_bytes{fstype!="tmpfs"} - node_filesystem_avail_bytes{fstype!="tmpfs"}) / node_filesystem_size_bytes{fstype!="tmpfs"} * 100
    Description: Tracks disk space usage as a percentage.

10. Request Breakdown by Endpoint
    Chart Type: Pie Chart
    Query: sum(rate(http_requests_total{job="your_service"}[1m])) by (path)
    Description: Shows the distribution of requests by endpoint.

Пример настройки ![Grafana](readme/grafana.png)