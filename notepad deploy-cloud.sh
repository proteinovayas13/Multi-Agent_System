#!/bin/bash
# Скрипт для деплоя в облако

# Сборка образа
docker build -t your-dockerhub/langgraph-agent:latest .

# Пуш в Docker Hub
docker push your-dockerhub/langgraph-agent:latest

# Применение конфигураций
kubectl apply -f k8s/deployment.yaml -n langgraph
kubectl apply -f k8s/service.yaml -n langgraph
kubectl apply -f k8s/ingress.yaml -n langgraph

# Проверка статуса
kubectl get pods -n langgraph -w