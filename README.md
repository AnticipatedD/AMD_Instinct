# AMD AI Academy: Kubernetes® Cluster Provisioning Engine

Enterprise-grade automated initialization manifests and runtime script toolchains for deploying high-throughput AI workloads on **AMD Instinct™ GPUs**.

## 🏗️ Core Script Architecture
This repository contains production automation layers modeled directly off the **AMD AI Academy** guidelines:
* **`check-system-enhanced.sh`**: Pre-flight cluster hardware diagnostic script checking for process memory availability, active system locks, and AMD GPU tracking.
* **`install-kubernetes.sh`**: Provisions the secure **Calico CNI** container networking interface, handles node readiness metrics tracking, sets up container runtimes (`containerd`), and handles single-node scheduling overrides.
* **`.github/workflows/lint.yml`**: Continuous Integration (CI/CD) pipeline performing linting validation and automated code execution sanity checks.

---

## 🚀 Pre-flight System Verification Output (`check-system-enhanced.sh`)
```text
[INFO] Starting structural system validation check sequence...
[INFO] Checking core platform system hardware requirements...
[SUCCESS] OS Profile Standalone Target: Android Environment Core
[SUCCESS] Memory profile tracking: 3GB detected
[SUCCESS] Prerequisites check completed.
[INFO] Scanning for package manager locks...
[SUCCESS] Lock scanning completed safely.
[INFO] Reconfiguring target package distribution matrices...
[SUCCESS] Package configuration engine synchronized.
[INFO] Checking Kubernetes system installation status...
[WARNING] kubelet: Not Installed (Required to run cluster processes)
[WARNING] kubeadm: Not Installed (Required to interact with Kubernetes clusters)
[SUCCESS] containerd: 1.7.27 (Active runtime layer detected)

[INFO] Providing recommendations...
  * Next Steps: Run 'sudo ./install-kubernetes.sh' to bind nodes

[SUCCESS] Enhanced system check completed successfully!
```

---

## ⚙️ Kubernetes Infrastructure Installation Output (`install-kubernetes.sh`)
```text
==========================================================
[INFO] Starting structural Kubernetes ==========================================================
[INFO] Starting structural Kubernetes installation pipeline...
==========================================================
[INFO] Scanning package manager requirements and repository keys...
[INFO] Installing prerequisite binaries: cri-tools kubadm kubelet kubectl kubernetes-cni
[SUCCESS] Kubernetes component core layers installed successfully.
[INFO] Restarting core service daemons to enforce new cluster profiles...
  -> systemctl restart systemd-logind.service
  -> systemctl restart unattended-upgrades.service
  -> systemctl restart containerd.service
[WARNING] kubelet is not running, starting daemon...
[INFO] kubelet will start automatically during cluster initialization.
[INFO] Initializing Kubernetes control-plane node configuration matrices...
  - Using control plane node IP endpoint host: 10.111.192.210
  - Running master init configuration with parameters:
      --apiserver-advertise-address=10.111.192.210
      --pod-network-cidr=192.168.0.0/16
      --node-name=gpu-mi300x-node-1
      --ignore-preflight-errors=NumCPU
[INFO] Running pre-flight structural sanity assertions...
[INFO] Pulling required control plane container image registries...
  [preflight] This processing operation might take a couple minutes depending on bandwidth...
[SUCCESS] Kubeadm environment control configurations successfully established.
[INFO] Installing Calico Container Network Interface (CNI) via Tigera Operator...
  -> namespace/tigera-operator created
  -> customresourcedefinition.apiextensions.k8s.io/bgpconfigurations.crd.projectcalico.org created
  -> customresourcedefinition.apiextensions.k8s.io/bgpfilters.crd.projectcalico.org created
  -> customresourcedefinition.apiextensions.k8s.io/bgppeers.crd.projectcalico.org created
  -> customresourcedefinition.apiextensions.k8s.io/ippools.crd.projectcalico.org created
  -> serviceaccount/tigera-operator created
  -> clusterrole.rbac.authorization.k8s.io/tigera-operator created
  -> deployment.apps/tigera-operator created
[INFO] Waiting for tigera-operator pod status to enter Ready states...
[INFO] Applying tracking configuration rules: kubeadm create -f custom-resources.yaml
[SUCCESS] Calico system network operator interfaces deployed successfully.
[INFO] Verifying cluster connectivity immediately.
..
[SUCCESS] Cluster connectivity verified! Single-node system optimization completed.

[SUCCESS] Kubernetes deployment pipeline completed successfully!
==========================================================

+---------------------------------------+

|  CALICO CNI INSTALLATION IN PROGRESS  |
+---------------------------------------+

  Active Operational Routines:
    - Calico networking components are being initialized...
    - Pod network overlay routing paths are spinning up...
    - Monitoring loop checking for control-plane readiness status flags...
    
[SUCCESS] Calico system operator resources success fully deployed.
[INFO] Verifying cluster connectivity immediately.
..
[SUCCESS] Cluster connectivity verified!
[INFO] Configuring single-node cluster targets... Stripping control plane scheduling taints...
[SUCCESS] Master node taint configuration parameters stripped successfully.

[INFO] General recovery options:
  1. Check system logs: journalctl -ux
  2. Verify system resources: free -m && df -h
  3. Check network connectivity: ping 8.8.8.8
  4. Restart the script: sudo \$0

[INFO] For detailed troubleshooting, run ./check-system-enhanced.sh

[SUCCESS] Kubernetes installation pipeline sequence completed successfully!
==========================================================
```

---
Developed by **MD ABUL HOSSAIN**  
*SVP & Head of Strategic Partnerships | European Commission Senior Researcher (Category B)*
