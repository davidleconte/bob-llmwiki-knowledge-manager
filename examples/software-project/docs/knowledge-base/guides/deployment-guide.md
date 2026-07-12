# Deployment Guide

## Overview
This guide covers deploying the e-commerce platform to Kubernetes on AWS.

## Prerequisites
- AWS account with appropriate permissions
- kubectl configured
- Docker Hub account
- Helm 3.x installed

## Step 1: Build Docker Images

```bash
# Build all service images
./scripts/build-images.sh

# Tag images
docker tag user-service:latest company/user-service:v1.0.0
docker tag product-service:latest company/product-service:v1.0.0
docker tag order-service:latest company/order-service:v1.0.0

# Push to registry
docker push company/user-service:v1.0.0
docker push company/product-service:v1.0.0
docker push company/order-service:v1.0.0
```

## Step 2: Configure Kubernetes

```bash
# Create namespace
kubectl create namespace ecommerce

# Create secrets
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password=secure-password \
  -n ecommerce

# Create configmaps
kubectl create configmap app-config \
  --from-file=config/production.yaml \
  -n ecommerce
```

## Step 3: Deploy Infrastructure

```bash
# Deploy PostgreSQL
helm install postgres bitnami/postgresql \
  --namespace ecommerce \
  --set auth.username=admin \
  --set auth.password=secure-password

# Deploy Redis
helm install redis bitnami/redis \
  --namespace ecommerce

# Deploy RabbitMQ
helm install rabbitmq bitnami/rabbitmq \
  --namespace ecommerce
```

## Step 4: Deploy Services

```bash
# Deploy all services
kubectl apply -f k8s/deployments/ -n ecommerce

# Verify deployments
kubectl get deployments -n ecommerce
kubectl get pods -n ecommerce
```

## Step 5: Configure Ingress

```bash
# Deploy ingress controller
kubectl apply -f k8s/ingress.yaml -n ecommerce

# Get load balancer URL
kubectl get ingress -n ecommerce
```

## Step 6: Verify Deployment

```bash
# Check service health
curl https://api.example.com/user-service/health
curl https://api.example.com/product-service/health
curl https://api.example.com/order-service/health

# Check logs
kubectl logs -f deployment/user-service -n ecommerce
```

## Monitoring

```bash
# Deploy Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring

# Deploy Grafana
helm install grafana grafana/grafana \
  --namespace monitoring
```

## Rollback

```bash
# Rollback deployment
kubectl rollout undo deployment/user-service -n ecommerce

# Check rollout status
kubectl rollout status deployment/user-service -n ecommerce
```

## Related Documents
- [Microservices Architecture](../concepts/microservices.md)
- [Setup Guide](./setup-guide.md)
