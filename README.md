# AMD Instinct™ Orchestrating vLLM # AMD Instinct™ Inference Routing & Infrastructure Framework

A focused Python and Kubernetes reference framework for routing inference workloads and orchestrating service verification over AMD ROCm and Instinct™ hardware environments.

<div align="center">
  
![AMD](https://img.shields.io/badge/AMD-Skills-ED1C24?logo=amd&logoColor=white)
![ROCm](https://img.shields.io/badge/ROCm-Enabled-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## ⚡ Quickstart & Installation

Ensure your system has Python and pip available, then clone and install the pinned dependencies:

```bash
# Clone the repository
git clone [https://github.com/AnticipatedD/AMD_Instinct.git](https://github.com/AnticipatedD/AMD_Instinct.git)
cd AMD_Instinct

# Install project dependencies
`pip install -r requirements-lock.txt`

# Run the complete test suite locally
`pytest -v tests/`
```

## 🗺️ Reference System Architecture

[ Client API Tunnels ] ──► [ Secure SSH Port Forward: 5000 ]
                               │
                               ▼
               ┌──────────────────────────────┐
               │     MetalLB LoadBalancer     │
               └──────────────────────────────┘
                               │
                               ▼
               ┌──────────────────────────────┐
               │      vLLM Inference Pod      │
               │  (Qwen3-Coder-30B-Instruct)  │
               └──────────────────────────────┘
                               │
                               ▼
            [ AMD GPU Operator / ROCm Device Plugin ]


## 🛠️ Production Monitoring & Troubleshooting Runbook

| Tracked System Symptom | Primary Diagnostic Verification | Infrastructure Resolution Strategy |
| :--- | :--- | :--- |
| **Pod Stuck in Pending State** | `kubectl describe pod -l app=vllm-engine` | Inspect logs for `Insufficient ://amd.com`. Verify the health of the NFD (Node Feature Discovery) daemonset. |
| **Inference Service Unreachable** | `kubectl get svc -A` | Validate Layer-2 address pooling metrics. Ensure external routing allocations do not conflict with active gateways. |
| **Model Loading Disconnects** | `kubectl get pvc --all-namespaces` | Ensure storage volume paths match local directories (/mnt/data/ai-models) and access permissions are configured. |
| **OOM Killed Containers / Crashes** | `kubectl node-shell <node>` | Cluster hardware hitting RAM ceiling limits. Downscale runtime flags or upgrade limits inside container boundary resources. |

---

# AMD Instinct GPU Orchestration & Inference Routing Framework

An enterprise production environment for running optimized inference workloads with the `Qwen3-Coder-30B-A3B-Instruct` model across AMD Instinct hardware footprints (CDNA modules, including the MI300X series) via AMD ROCm software environments.


## 🏗️ Repository Module Breakdown:

- `​lemonade_router.py`: Core routing engine utilizing structured OpenAI-compatible tool-calling pipelines and runtime parameter validation.
- `​chatbot_backend.py`: Session context builder and inference parameter configuration profile.
- ​`manage_infra.py`: System automation script for checking local ROCm environments (`rocm-smi`) and validating Kubernetes cluster connection states.
- ​`manifests/`: Cloud-native deployment manifests:
- `​metallb-config.yaml`: Network routing and cluster load balancing configuration.
- `​model-storage.yaml`: Persistent volume configurations for model asset storage.
- ​`vllm-deployment.yaml`: Deployment profiles allocating parameters to active GPU devices.
- ​`tests/`: Unit test specifications covering routing logic, configuration boundaries, and infrastructure simulations.

## ​🔐 Environment Matrix Parameters
​Configure your system variables by copying `.env.example` to `.env`:
- ​`ROCM_API_KEY`: Authorization token used for runtime API validation.
- `​ROCM_ENGINE_URL`: Endpoint path pointing to active vLLM tensor serving instances (defaults to http://localhost:8000/v1).
- `​ROCM_MODEL_NAME`: Target model deployment designation (defaults to `Qwen3-Coder-30B-A3B-Instruct`).

## ​⚠️ Known Limitations
​- **Infrastructure Manifests**: The Kubernetes manifests and deployment scripts in this repository provide structural reference templates; full multi-node MetalLB layer-2 load balancing requires specific underlying host network configurations.
