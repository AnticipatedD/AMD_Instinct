#!/usr/bin/env bash
set -euo pipefail

echo "Deploying high-performance vLLM configurations down into target Kubernetes namespace..."
kubectl apply -f manifests/vllm-deployment.yaml
echo "Successfully tracked instantiation of inference engine components configurations pipeline."
