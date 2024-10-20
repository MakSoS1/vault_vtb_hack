# Масштабируемость и отказоустойчивость

Проект **Secret Vault** разработан с учётом требований к горизонтальной масштабируемости и высокой отказоустойчивости. Эти параметры обеспечивают стабильную работу системы при увеличении нагрузки, а также минимизируют простои в случае сбоев.

### 1. Горизонтальная масштабируемость

Система поддерживает горизонтальное масштабирование с использованием механизма **Horizontal Pod Autoscaler (HPA)** в Kubernetes. HPA автоматически увеличивает или уменьшает количество реплик подов в зависимости от загрузки процессора.

#### Основные настройки:

- **Минимальное количество реплик**: 2
- **Максимальное количество реплик**: 10
- **Порог загрузки CPU**: 80%

**Файл манифеста**: `hpa.yaml`

#### Как это работает:
Когда нагрузка на процессор превышает 80%, Kubernetes автоматически увеличивает количество подов, что позволяет системе справляться с увеличением трафика. Как только нагрузка снижается, количество подов возвращается к минимальному значению.

### 2. Балансировка нагрузки

Балансировка нагрузки между репликами подов осуществляется с помощью **Kubernetes Service** с типом **LoadBalancer**. Это обеспечивает равномерное распределение трафика между всеми активными репликами, что улучшает производительность системы и снижает риски перегрузки отдельных подов.

**Файл манифеста**: `api-deployment.yaml` (секция Service)

Пример конфигурации LoadBalancer:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: secret-app-api-service
spec:
  selector:
    app: secret-app-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### 3. Реплики для отказоустойчивости

Для обеспечения высокой доступности каждый микросервис в системе развёртывается с несколькими репликами (кроме тех сервисов, где отказоустойчивость не критична). Это позволяет системе автоматически перенаправлять трафик на рабочие реплики в случае сбоя одной из них.

Пример конфигурации для деплоймента:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secret-app-api
spec:
  replicas: 3  # 3 реплики для отказоустойчивости
  ...
```

#### Преимущества использования реплик:
- Если одна реплика выходит из строя, Kubernetes автоматически перенаправляет трафик на другие рабочие реплики.
- Количество реплик можно легко изменять с помощью HPA в зависимости от нагрузки.

### 4. PersistentVolume для хранения данных

Для хранения данных, таких как HTML-шаблоны или ключи шифрования, используются **PersistentVolumeClaims (PVC)**. Это позволяет сохранять данные даже при перезапуске подов, обеспечивая их доступность в любое время.

- **Файл манифеста для хранения шаблонов**: `templates-pvc.yaml`
- **Файл манифеста для хранения ключей**: `key-pvc.yaml`

Пример конфигурации PVC:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: templates-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
```

### 5. Кластеризация базы данных

База данных, используемая в проекте (например, **Cassandra**), развёрнута в кластерном режиме, что обеспечивает отказоустойчивость и высокую доступность данных. Это позволяет системе продолжать работу, даже если один из узлов базы данных выходит из строя.

Пример конфигурации для подключения к кластеру Cassandra:
```yaml
env:
  - name: CASSANDRA_HOST
    value: "cassandra.default.svc.cluster.local"
```

### 6. Восстановление после сбоев

Для повышения устойчивости к сбоям система поддерживает автоматическое восстановление сервисов в случае отказа:

- **Auto-Healing**: Kubernetes автоматически перезапускает поды, которые вышли из строя.
- **Rolling Updates**: Обновления сервисов производятся без простоев за счёт использования Rolling Updates, что позволяет обновлять контейнеры постепенно.

Пример конфигурации для Rolling Updates:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1
    maxSurge: 1
```
