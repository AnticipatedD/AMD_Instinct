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
[INFO] Starting structural Kubernetes installation pipeline...
==========================================================
[INFO] Evaluating core platform system execution limits...
[SUCCESS] OS Profile Tracked: Termux Shell Environment Base
[SUCCESS] Requirement verified: curl utility found
[SUCCESS] Requirement verified: wget utility found
[SUCCESS] Requirement verified: apt-get utility found
[SUCCESS] Memory scan complete: 3GB detected on node
[SUCCESS] System architecture prerequisites audit finished.
[INFO] Scanning system layer files for package manager locks...
[SUCCESS] Checking for package manager locks... No locks detected
[INFO] Configuring container runtime environment bounds...
[INFO] Installing containerd container runtime...
[INFO] Writing default configuration path layout file: /etc/containerd/config.toml
[INFO] Setting SystemdCgroup = true matching Kubernetes best practices...
[SUCCESS] containerd engine configured and running successfully.
[INFO] Orchestrating Calico CNI overlay components...
[INFO] Executing local tracking manifest: kubectl create -f custom-resources.yaml

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
