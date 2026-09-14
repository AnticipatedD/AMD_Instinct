# AMD AI Academy: Kubernetes® Cluster Provisioning Engine

Enterprise-grade automated initialization manifests and runtime script toolchains for deploying high-throughput AI workloads on **AMD Instinct™ GPUs**.

## 🏗️ Reference Core Script Architecture
This repository contains production automation layers modeled directly off the **AMD AI Academy** guidelines:
* **`check-system-enhanced.sh`**: Pre-flight cluster hardware diagnostic script checking for process memory availability, active system locks, and AMD GPU tracking.
* **`install-kubernetes.sh`**: Provisions the secure **Calico CNI** container networking interface, handles node readiness metrics tracking, and sets up single-node scheduling overrides.

## 🚀 Deployment Runtime Output Log
The cluster execution script ran successfully and captured the following infrastructure system footprints:

```text
==========================================================
[INFO] Starting structural Kubernetes installation pipeline...
==========================================================
[INFO] Validating administrative local access configuration metrics...
[INFO] Default configuration mapping layer established under ~/.kube/config
[INFO] Verifying control plane connectivity matrices...
[INFO] Initiating Calico container network interface provisioning...
[INFO] kubectl create -f custom-resources.yaml

+-------------------------------------+

| CALICO CNI INSTALLATION IN PROGRESS |
+-------------------------------------+

  What's happening now:
    - Calico networking components are being initialized.
    - Pod network overlay routing paths are spinning up.
    - Monitoring loop checking for control-plane readiness status flags...
    
[SUCCESS] Calico system operator resources successfully deployed.
[INFO] Verifying cluster connectivity immediately...
[SUCCESS] Cluster connectivity verified!

[INFO] System State Summary Snapshot:
  - Node Name: localhost
  - Runtime Context Version: Kubernetes v1.28.2 (Target Virtual Mode)
  - Network Layer Interface: Calico Core Engine active

[INFO] Configuring single-node cluster target settings...
[INFO] Removing control-plane scheduling taints from master node...
[SUCCESS] Master node taint configuration parameters stripped successfully.

[SUCCESS] Kubernetes deployment pipeline completed successfully!
==========================================================
```

---
Developed by **MD ABUL HOSSAIN**  
*SVP & Head of Strategic Partnerships | European Commission Senior Researcher (Category B)*
