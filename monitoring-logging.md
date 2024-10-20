# Мониторинг и логирование

В проекте **Secret Vault** реализованы механизмы мониторинга и логирования для отслеживания состояния системы, а также для оперативного реагирования на инциденты. Это позволяет поддерживать стабильную работу сервиса и предотвращать потенциальные сбои.

### 1. Мониторинг

Мониторинг системы обеспечивается с помощью стека **Prometheus** и **Grafana**. Эти инструменты позволяют собирать метрики со всех микросервисов, визуализировать их и настраивать уведомления о проблемах.

- **Prometheus**: Служит для сбора метрик, таких как загрузка CPU, использование памяти, состояние подов и количество запросов к API.
- **Grafana**: Предоставляет удобную визуализацию собранных метрик и позволяет настроить дашборды для отслеживания состояния системы.

#### Установка и настройка:

1. Установка Prometheus:
   ```bash
   helm install prometheus prometheus-community/prometheus
   ```

2. Установка Grafana:
   ```bash
   helm install grafana grafana/grafana
   ```

3. Настройка метрик для подов и сервисов через аннотации в манифестах Kubernetes:
   ```yaml
   metadata:
     annotations:
       prometheus.io/scrape: 'true'
       prometheus.io/port: '8000'
   ```

4. Проброс порта для доступа к Grafana:
   ```bash
   kubectl port-forward svc/grafana 3000:3000
   ```
   Перейдите на `http://localhost:3000`, чтобы получить доступ к дашбордам.

### 2. Логирование

Логирование реализовано с помощью **Fluentd** и **Elasticsearch**. Все логи микросервисов собираются через Fluentd и отправляются в Elasticsearch для анализа и хранения. Kibana используется для визуализации логов и проведения поисковых запросов по ним.

- **Fluentd**: Сбор и пересылка логов из подов и сервисов в Elasticsearch.
- **Elasticsearch**: Хранилище логов, в котором можно выполнять быстрый поиск и анализ данных.
- **Kibana**: Визуализация логов, настройка дашбордов и проведение аналитики по логам.

#### Установка и настройка:

1. Установка Elasticsearch:
   ```bash
   helm install elasticsearch elastic/elasticsearch
   ```

2. Установка Fluentd:
   ```bash
   kubectl apply -f fluentd-config.yaml
   ```

3. Установка Kibana:
   ```bash
   helm install kibana elastic/kibana
   ```

4. Проброс порта для доступа к Kibana:
   ```bash
   kubectl port-forward svc/kibana 5601:5601
   ```
   Перейдите на `http://localhost:5601` для доступа к интерфейсу Kibana.

### 3. Пример конфигурации Fluentd

**Файл манифеста**: `fluentd-config.yaml`

Конфигурация Fluentd для пересылки логов в Elasticsearch через порт 9200:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type forward
      port 24224
    </source>
    <match **>
      @type elasticsearch
      host elasticsearch
      port 9200
      logstash_format true
    </match>
```

### 4. Уведомления

Для оперативного реагирования на инциденты Grafana позволяет настроить оповещения. Например, можно настроить уведомления при превышении порога использования CPU или памяти.

Пример настройки уведомлений в Grafana:
- Уведомление при загрузке CPU выше 80%.
- Отправка уведомлений в Slack или на электронную почту.
