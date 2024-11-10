# Kubernetes Dashboard Installation Guide

A step-by-step guide for installing and configuring the Kubernetes Dashboard with secure access. This guide is regularly maintained and tested with the latest Kubernetes versions.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Installation Steps](#detailed-installation-steps)
- [Access Configuration](#access-configuration)
- [Troubleshooting](#troubleshooting)
- [Cleanup](#cleanup)

## Prerequisites

Before starting the installation, ensure you have:

- [ ] Kubernetes cluster (v1.24+)
- [ ] kubectl installed and configured
- [ ] Administrative access to your cluster
- [ ] OpenSSL (for token generation/verification)

## Quick Start

```bash
# Deploy dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Create admin user and get token
kubectl apply -f admin-user.yaml
kubectl create token admin-user -n kubernetes-dashboard
```

## Detailed Installation Steps

### 1. Deploy Dashboard

```bash
# Deploy the official dashboard configuration
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Verify deployment
kubectl get pod -n kubernetes-dashboard
```

Expected output:
```
NAME                                         READY   STATUS    RESTARTS   AGE
dashboard-metrics-scraper-7bc864c59-prd2k   1/1     Running   0          45s
kubernetes-dashboard-6c7ccb5d84-g5kdg       1/1     Running   0          45s
```

### 2. Create Admin User

Create `admin-user.yaml`:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
```

Apply the configuration:
```bash
kubectl apply -f admin-user.yaml
```

### 3. Generate Access Token

For Kubernetes v1.24+:
```bash
kubectl create token admin-user -n kubernetes-dashboard
```

For older versions:
```bash
kubectl -n kubernetes-dashboard get secret $(kubectl -n kubernetes-dashboard get sa/admin-user -o jsonpath="{.secrets[0].name}") -o go-template="{{.data.token | base64decode}}"
```

Save the token output securely - you'll need it for dashboard login.

## Access Configuration

### Method 1: NodePort

```bash
kubectl edit service kubernetes-dashboard -n kubernetes-dashboard
```

Change `type: ClusterIP` to `type: NodePort`

```bash
kubectl get service kubernetes-dashboard -n kubernetes-dashboard
```

## Troubleshooting

### Common Issues

1. **Pending Pods**
```bash
kubectl describe pod  -n kubernetes-dashboard
kubectl get events -n kubernetes-dashboard
```

### Health Check

```bash
# Check all dashboard resources
kubectl get all -n kubernetes-dashboard

# View dashboard logs
kubectl logs -f $(kubectl get pods -n kubernetes-dashboard -l k8s-app=kubernetes-dashboard -o jsonpath="{.items[0].metadata.name}") -n kubernetes-dashboard
```

## Cleanup

Remove dashboard and associated resources:

```bash
# Remove admin user
kubectl delete -f admin-user.yaml

# Remove dashboard
kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Remove namespace (optional)
kubectl delete namespace kubernetes-dashboard
```
