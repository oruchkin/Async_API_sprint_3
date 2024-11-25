## Проектная работа 13 и 14 спринтов

В этом спринте наша команда:
- Описала манифесты для всех сервисов кинотеатра
- Задеплоила все сервисы кинотеатра в Managed Service Kubernetis yandex.cloud
- Организала сбор метрик в prometeus
- Визуализировала метрики в графана
- Настроила алертинг на email / telegram


### Доска на которой мы вели задачи:
[Канбан доска](https://github.com/users/oruchkin/projects/15)

---

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
   Query: (node_filesystem_size_bytes{fstype!="tmpfs"} - node_filesystem_avail_bytes{fstype!="tmpfs"}) /
   node_filesystem_size_bytes{fstype!="tmpfs"} * 100
   Description: Tracks disk space usage as a percentage.


10. Request Breakdown by Endpoint
    Chart Type: Pie Chart
    Query: sum(rate(http_requests_total{job="your_service"}[1m])) by (path)
    Description: Shows the distribution of requests by endpoint.

Пример настройки ![Grafana](readme/grafana.png)

---
Алерты:

- Зарегестрированые алерты ![Alerts](readme/alerts.png)
- телеграм / email ![notification](readme/notifications.png)

---
Prometheus:
Добавили прометеус для сбора метрик Nodes, собирает информацию по:
- диску
- памяти
- процессорному времени

---
Сервисы в yandex.cloud

- сервисы залитые в managed service K8S: ![services](readme/services.png)

