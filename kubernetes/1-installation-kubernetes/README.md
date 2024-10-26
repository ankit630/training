Kubernetes Cluster Setup Guide
This guide provides step-by-step instructions for setting up a Kubernetes cluster using kubeadm with containerd as the container runtime.
Prerequisites

Ubuntu/Debian Linux systems
Root or sudo access
Minimum requirements:

2 CPUs
2GB RAM
20GB disk space


Multiple machines for master and worker nodes

Pre-installation Steps
1. System Updates
Update the package lists on all nodes:
bashCopysudo apt update
2. Disable Swap
Kubernetes requires swap to be turned off:
bashCopysudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
3. Load Kernel Modules
Create and load necessary kernel modules:
bashCopy# Create a configuration file for containerd modules
sudo tee /etc/modules-load.d/containerd.conf <<EOF
overlay
br_netfilter
EOF

# Load the modules
sudo modprobe overlay
sudo modprobe br_netfilter
4. Configure Kernel Parameters
Set up required kernel parameters:
bashCopy# Create kubernetes.conf with necessary settings
sudo tee /etc/sysctl.d/kubernetes.conf <<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF

# Apply settings
sysctl --system
Installing containerd
1. Install Dependencies
bashCopyapt-get update
sudo apt-get install -y libseccomp2
2. Install containerd
bashCopy# Download containerd
wget https://github.com/containerd/containerd/releases/download/v1.7.12/containerd-1.7.12-linux-amd64.tar.gz

# Extract to /usr/local
sudo tar -C /usr/local -xzf containerd-1.7.12-linux-amd64.tar.gz
3. Configure containerd
bashCopy# Create config directory
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
Installing Kubernetes Components
1. Install Required Packages
bashCopyapt-get update && apt-get install -y apt-transport-https curl runc
2. Add Kubernetes Repository
bashCopy# Add GPG key
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmour -o /etc/apt/trusted.gpg.d/kubernetes-xenial.gpg

# Add Kubernetes repository
sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
3. Install Kubernetes Tools
bashCopy# Update package list
apt-get update

# Install specific versions of kubernetes components
apt-get install -y kubelet=1.28.2-00 kubeadm=1.28.2-00 kubectl=1.28.2-00

# Prevent automatic updates
apt-mark hold kubelet kubeadm kubectl
4. Disable Firewall
bashCopyufw disable
Initializing the Cluster
1. Initialize Master Node
bashCopykubeadm init --apiserver-advertise-address=<MASTER_IP> --pod-network-cidr 192.168.0.0/16 --kubernetes-version 1.28.2
Replace <MASTER_IP> with your master node's IP address.
2. Configure kubectl
For regular user:
bashCopymkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
For root user (not recommended):
bashCopyexport KUBECONFIG=/etc/kubernetes/admin.conf
3. Install Network Plugin (Calico)
bashCopykubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
4. Verify Node Status
bashCopykubectl get nodes
Adding Worker Nodes
1. Generate Join Command
On the master node:
bashCopykubeadm token create --print-join-command
2. Join Worker Nodes
Copy the output from the previous command and run it on each worker node:
bashCopykubeadm join <MASTER_IP>:6443 --token <TOKEN> --discovery-token-ca-cert-hash <HASH>
3. Verify Cluster Status
On the master node:
bashCopykubectl get nodes
Troubleshooting

If nodes are not showing as Ready, wait a few minutes for all pods to initialize
Check pod status: kubectl get pods --all-namespaces
View logs: kubectl logs <pod-name> -n <namespace>