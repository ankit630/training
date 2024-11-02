# Kubernetes Cluster Setup Guide

A comprehensive guide for setting up a production-ready Kubernetes cluster using kubeadm and containerd.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Pre-installation Steps](#pre-installation-steps)
- [Installing containerd](#installing-containerd)
- [Installing Kubernetes Components](#installing-kubernetes-components)
- [Initializing the Cluster](#initializing-the-cluster)
- [Adding Worker Nodes](#adding-worker-nodes)
- [Troubleshooting](#troubleshooting)
- [Version Information](#version-information)

## Prerequisites

Before beginning the installation, ensure you have:

✅ Ubuntu/Debian Linux systems  
✅ Root or sudo access  
✅ Minimum system requirements per node:
   * 2 CPUs
   * 2GB RAM
   * 20GB disk space
✅ Multiple machines for master and worker nodes

## Pre-installation Steps

### 1. System Updates

Update the package lists on all nodes:

    sudo apt update

### 2. Disable Swap

Kubernetes requires swap to be turned off:

    sudo swapoff -a
    sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

### 3. Load Kernel Modules

Create and load necessary kernel modules:

    # Create a configuration file for containerd modules
    sudo tee /etc/modules-load.d/containerd.conf <<EOF
    overlay
    br_netfilter
    EOF

    # Load the modules
    sudo modprobe overlay
    sudo modprobe br_netfilter

### 4. Configure Kernel Parameters

Set up required kernel parameters:

    # Create kubernetes.conf with necessary settings
    sudo tee /etc/sysctl.d/kubernetes.conf <<EOF
    net.bridge.bridge-nf-call-ip6tables = 1
    net.bridge.bridge-nf-call-iptables = 1
    net.ipv4.ip_forward = 1
    EOF

    # Apply settings
    sysctl --system

## Installing containerd

### 1. Install Dependencies

    apt-get update
    sudo apt-get install -y libseccomp2

### 2. Install containerd

    # Download containerd
    wget https://github.com/containerd/containerd/releases/download/v1.7.12/containerd-1.7.12-linux-amd64.tar.gz

    # Extract to /usr/local
    sudo tar -C /usr/local -xzf containerd-1.7.12-linux-amd64.tar.gz

### 3. Configure containerd

    # Create config directory
    mkdir -p /etc/containerd

    # Generate default config
    containerd config default | sudo tee /etc/containerd/config.toml

    # Enable SystemdCgroup
    sudo sed -i 's/SystemdCgroup \= false/SystemdCgroup \= true/g' /etc/containerd/config.toml

    # Set up containerd service
    sudo curl -L https://raw.githubusercontent.com/containerd/containerd/main/containerd.service -o /etc/systemd/system/containerd.service

    # Reload daemon and start containerd
    sudo systemctl daemon-reload
    sudo systemctl start containerd
    sudo systemctl enable --now containerd

    # Verify containerd status
    systemctl status containerd

## Installing Kubernetes Components

### 1. Install Required Packages

    apt-get update && apt-get install -y apt-transport-https curl runc

### 2. Add Kubernetes Repository

    # Add GPG key
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

    # Add Kubernetes repository
    apt install software-properties-common -y
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

### 3. Install Kubernetes Tools

    # Update package list
    apt-get update

    # Install specific versions of kubernetes components
    apt-get install -y kubelet=1.31.2-1.1 kubeadm=1.31.2-1.1 kubectl=1.31.2-1.1

    # Prevent automatic updates
    apt-mark hold kubelet kubeadm kubectl

### 4. Disable Firewall

    ufw disable

## Initializing the Cluster

### 1. Initialize Master Node

    kubeadm init --apiserver-advertise-address=<MASTER_IP> --pod-network-cidr 192.168.0.0/16 --kubernetes-version 1.28.2

> Note: Replace `<MASTER_IP>` with your master node's IP address.

### 2. Configure kubectl

For regular user:

    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config

For root user (not recommended):

    export KUBECONFIG=/etc/kubernetes/admin.conf

### 3. Install Network Plugin (Calico)

    kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

### 4. Verify Node Status

    kubectl get nodes

## Adding Worker Nodes

### 1. Generate Join Command
On the master node:

    kubeadm token create --print-join-command

### 2. Join Worker Nodes
Copy the output from the previous command and run it on each worker node:

    kubeadm join <MASTER_IP>:6443 --token <TOKEN> --discovery-token-ca-cert-hash <HASH>

### 3. Verify Cluster Status
On the master node:

    kubectl get nodes

## Troubleshooting

Common issues and solutions:

1. **Nodes Not Ready**
   - Wait a few minutes for all pods to initialize
   - Check pod status: `kubectl get pods --all-namespaces`
   - View logs: `kubectl logs <pod-name> -n <namespace>`

2. **Network Issues**
   - Verify network plugin installation
   - Check node connectivity
   - Ensure firewall rules are correct

3. **Pod Scheduling Issues**
   - Check node resources
   - Verify node labels and taints
   - Review pod specifications

## Notes

⚠️ Important considerations:

- Ensure all nodes have unique hostnames
- All nodes should have proper network connectivity
- The same kubernetes version should be used across all nodes
- Regular backups of etcd are recommended

## Version Information

Current tested versions:

Component    | Version
------------|----------
Kubernetes  | v1.28.2
containerd  | v1.7.12
Calico      | Latest stable
