# AMD Instinct™ Orchestrating vLLM Inference Services on GPUs with Kubernetes

An enterprise-grade reference architecture for automated multi-node cluster provisioning, Layer-2 networking load-balancing, and high-throughput LLM serving (`vLLM`) optimized over **AMD Instinct™ MI300X CDNA3** acceleration systems.

<div align="center">
  
![AMD](https://img.shields.io/badge/AMD-Skills-ED1C24?logo=amd&logoColor=white)
![ROCm](https://img.shields.io/badge/ROCm-Enabled-green)
![Ryzen AI](https://img.shields.io/badge/Ryzen_AI-Ready-1F6FEB)
![Agent Skills](https://img.shields.io/badge/Agent_Skills-Standard-7B2D8E)
[![Cursor](https://img.shields.io/badge/Cursor-Compatible-000000?logo=cursor&logoColor=white)](https://cursor.com)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-F07535?logo=claude&logoColor=white)](https://www.anthropic.com/claude-code)
[![Gemini CLI](https://img.shields.io/badge/Gemini_CLI-Compatible-4285F4?logo=googlegemini&logoColor=white)](https://ai.google.dev/gemini-api/docs)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<img src="assets/banner.gif" alt="AMD Skills"/>

## 🗺️ Reference System Architecture

[ Client API Tunnels ] ──► [ Secure SSH Port Forward: 5000 ]│▼┌──────────────────────────┐│   MetalLB LoadBalancer   │└──────────────────────────┘│▼┌──────────────────────────┐│    vLLM Inference Pod    ││   (Qwen2.5-1.5B-Instruct)│└──────────────────────────┘│▼[AMD GPU Operator](ROCm / Device Node Plugin)
## 🏗️ Repository Module Breakdown
* **`check-system-enhanced.sh`**: Automatic environment verification tool checking process logs, lock bounds, and PCIe GPU links.
* **`install-kubernetes.sh`**: Automated provisioning loop initializing `kubeadm control-plane` nodes and installing **Calico operators**.
* **`deploy-vllm-inference.sh`**: Orchestrates Layer-2 IP pools (`MetalLB`) and deploys vLLM serving pods backed by persistent volume storage claims.
* **`run-web-demo.sh`**: Launches automated service monitors, mock web interfaces, secure port-forwarding setups, and troubleshooting matrices.
* **`manifests/`**: Cloud-native deployment metrics exposing raw hardware accelerators directly onto upstream schedulers.

---

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

## ⚡ Quickstart & Installation

Ensure you have mapped your core devices (`/dev/kfd` and `/dev/dri`) before bootstrapping local application clusters.

```bash
# Clone the repository
git clone https://github.com
cd AMD_Instinct

# Install project dependencies with exact lockfile values
pip install -r requirements.txt

# Run the complete automated verification test suite locally
pytest -v tests/
```

## 🏗️ Repository Module Breakdown

* `manifests/`: High-performance Kubernetes blueprints managing state configurations natively without runtime construction mutations.
  * `metallb-config.yaml`: Network routing and cluster load balancing configuration.
  * `model-storage.yaml`: Persistent volume configuration targeting high-performance storage blocks.
  * `vllm-deployment.yaml`: Deployment profile allocating model parameters to active GPU devices.
* `lemonade_router.py`: Core intent router module utilizing structured tool-calling pipelines.
* `chatbot_backend.py`: Session context builder and inference parameter configuration profile.
* `tests/`: High-impact verification test matrices managing cluster state simulations and software layers in isolation.

## 🔐 Environment Matrix Parameters

Configure your system variables by creating a `.env` file based on `.env.example`. Do not commit credentials directly to the repository history.

* `ROCM_API_KEY`: The authorization token used for local runtime validation checking.
* `ROCM_ENGINE_URL`: The endpoint path pointing to your active vLLM tensor compilation server instances (defaults to `http://localhost:8000/v1`).

---
### Architected & Maintained by:
**MD ABUL HOSSAIN**  
*SVP & Head of Strategic Partnerships | Taru Global Access*  
* **IBM Business Partner Plus** | **Microsoft Official Business Partner**
* **European Commission Designated Category B Senior Researcher** (Designated F&T Expert)
* **AlphaNova Tech Global Leaderboard Rank #28** | Individual Rank 57/873
* *Credentials Framework Summary:*
