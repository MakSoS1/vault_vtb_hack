# Установка

В этом разделе описаны шаги по клонированию репозитория, сборке Docker-контейнеров и развертыванию проекта в Kubernetes.

### 1. Клонирование репозитория

Сначала клонируйте проект на локальную машину:
```bash
git clone https://github.com/yourusername/secret-vault.git
cd secret-vault
```

### 2. Сборка Docker-контейнеров

Для каждого микросервиса в проекте имеется свой `Dockerfile`. Сначала убедитесь, что Docker установлен, а затем выполните сборку всех контейнеров.

Сборка основного API:
```bash
cd Docker/api
docker build -t secret-app-api:latest .
```

Сборка конфигурационного сервиса:
```bash
cd ../config
docker build -t secret-app-config:latest .
```

Сборка сервиса шифрования:
```bash
cd ../encryption
docker build -t secret-app-encryption:latest .
```

Сборка остальных сервисов (если требуется):
```bash
# Повторите команды для других папок (models, seal и т.д.)
```

### 3. Настройка Kubernetes

Перед развертыванием убедитесь, что ваш Kubernetes-кластер запущен и настроен.

Проверьте статус кластера:
```bash
kubectl cluster-info
```

### 4. Развёртывание компонентов в Kubernetes

1. Примените манифесты деплойментов и сервисов для каждого микросервиса:
```bash
kubectl apply -f api-deployment.yaml
kubectl apply -f config-deployment.yaml
kubectl apply -f encryption-deployment.yaml
kubectl apply -f models-deployment.yaml
kubectl apply -f seal-deployment.yaml
```

2. Настройте PersistentVolumeClaim для шаблонов и ключей:
```bash
kubectl apply -f templates-pvc.yaml
kubectl apply -f key-pvc.yaml
```

3. Примените манифест для Ingress и настройку TLS:
```bash
kubectl apply -f ingress.yaml
kubectl apply -f certificate.yaml
```

### 5. Горизонтальное масштабирование (опционально)

Если требуется автоматическое масштабирование, примените манифест HPA:
```bash
kubectl apply -f hpa.yaml
```

### 6. Проверка состояния

После развертывания проверьте статус подов и сервисов:
```bash
kubectl get pods
kubectl get services
```

Для проверки Ingress:
```bash
kubectl get ingress
```

Если всё запущено правильно, вы сможете получить доступ к приложению через IP-адрес кластера или домен, настроенный в `ingress.yaml`.
