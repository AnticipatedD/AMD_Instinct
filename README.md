# Orchestrating vLLM Inference Services on AMD Instinct™ GPUs with Kubernetes

An enterprise-grade reference architecture for automated multi-node cluster provisioning, Layer-2 networking load-balancing, and high-throughput LLM serving (`vLLM`) optimized over **AMD Instinct™ MI300X CDNA3** acceleration systems.

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
### Architected & Maintained by:
**MD ABUL HOSSAIN**  
*SVP & Head of Strategic Partnerships | Taru Global Access*  
* **IBM Business Partner Plus** | **Microsoft Official Business Partner**
* **European Commission Designated Category B Senior Researcher** (Designated F&T Expert)
* **AlphaNova Tech Global Leaderboard Rank #28** | Individual Rank 57/873
* *Credentials Framework Summary:*
