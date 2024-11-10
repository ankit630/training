Kubernetes Dashboard Installation Guide 🚀

A step-by-step guide for installing and configuring the Kubernetes Dashboard with secure access. This guide is regularly maintained and tested with the latest Kubernetes versions.

Table of Contents
Prerequisites
Quick Start
Detailed Installation Steps
Security Setup
Access Configuration
Troubleshooting
Cleanup

Prerequisites
Before starting the installation, ensure you have:

 Kubernetes cluster (v1.24+)
 kubectl installed and configured
 Administrative access to your cluster
 OpenSSL (for token generation/verification)

Quick Start
bashCopy# Deploy dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Create admin user and get token
kubectl apply -f admin-user.yaml
kubectl create token admin-user -n kubernetes-dashboard
Detailed Installation Steps
1. Deploy Dashboard
bashCopy# Deploy the official dashboard configuration
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Verify deployment
kubectl get pod -n kubernetes-dashboard
Expected output:
CopyNAME                                         READY   STATUS    RESTARTS   AGE
dashboard-metrics-scraper-7bc864c59-prd2k   1/1     Running   0          45s
kubernetes-dashboard-6c7ccb5d84-g5kdg       1/1     Running   0          45s
2. Create Admin User
Create admin-user.yaml:
yamlCopyapiVersion: v1
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
Apply the configuration:
bashCopykubectl apply -f admin-user.yaml
3. Generate Access Token
For Kubernetes v1.24+:
bashCopykubectl create token admin-user -n kubernetes-dashboard
For older versions:
bashCopykubectl -n kubernetes-dashboard get secret $(kubectl -n kubernetes-dashboard get sa/admin-user -o jsonpath="{.secrets[0].name}") -o go-template="{{.data.token | base64decode}}"
Save the token output securely - you'll need it for dashboard login.
Security Setup
RBAC Configuration
The default setup uses cluster-admin role. For production, create custom roles:
yamlCopyapiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: dashboard-viewer
  namespace: kubernetes-dashboard
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
SSL/TLS Configuration
Generate self-signed certificates (for testing):
bashCopyopenssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout dashboard.key -out dashboard.crt \
  -subj "/CN=kubernetes-dashboard"

kubectl create secret generic kubernetes-dashboard-certs \
  --from-file=dashboard.key \
  --from-file=dashboard.crt \
  -n kubernetes-dashboard
Access Configuration
Method 1: kubectl proxy
bashCopykubectl proxy
Access URL: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
Method 2: NodePort
bashCopykubectl edit service kubernetes-dashboard -n kubernetes-dashboard
Change type: ClusterIP to type: NodePort
bashCopykubectl get service kubernetes-dashboard -n kubernetes-dashboard
Method 3: Port Forward
bashCopykubectl port-forward -n kubernetes-dashboard service/kubernetes-dashboard 8443:443
Access URL: https://localhost:8443
Troubleshooting
Common Issues

Pending Pods

bashCopykubectl describe pod <pod-name> -n kubernetes-dashboard
kubectl get events -n kubernetes-dashboard

Access Denied

bashCopy# Verify RBAC
kubectl auth can-i list pods -n kubernetes-dashboard --as system:serviceaccount:kubernetes-dashboard:admin-user

Certificate Issues

bashCopy# Check certificate validity
kubectl get secret kubernetes-dashboard-certs -n kubernetes-dashboard -o yaml
Health Check
bashCopy# Check all dashboard resources
kubectl get all -n kubernetes-dashboard

# View dashboard logs
kubectl logs -f $(kubectl get pods -n kubernetes-dashboard -l k8s-app=kubernetes-dashboard -o jsonpath="{.items[0].metadata.name}") -n kubernetes-dashboard
Cleanup
Remove dashboard and associated resources:
bashCopy# Remove admin user
kubectl delete -f admin-user.yaml

# Remove dashboard
kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Remove namespace (optional)
kubectl delete namespace kubernetes-dashboard
Contributing

Fork the repository
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

Support

📧 Create an Issue
📚 Official Kubernetes Dashboard Documentation

License
This project is licensed under the MIT License - see the LICENSE file for details.

⭐️ If this guide helped you, please consider giving it a star on GitHub!