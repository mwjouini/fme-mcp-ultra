# Kubernetes Deployment Guide

This guide describes how to deploy `fme-mcp-ultra` in production Kubernetes clusters (EKS, GKE, AKS, OpenShift, or on-premises k8s).

## Manifest Architecture

The `k8s/` folder contains production-ready manifests:

- `namespace.yaml`: Isolated namespace `fme-mcp`.
- `configmap.yaml`: Non-sensitive application configuration and allowed paths.
- `secret.yaml`: Encrypted FME Flow tokens and MCP API keys.
- `deployment.yaml`: Replicated Deployment with resource requests/limits, health probes, and security contexts.
- `service.yaml`: ClusterIP service exposing port 8000.
- `networkpolicy.yaml`: Zero-trust network policy restricting ingress and egress traffic.

## Quick Installation

Deploy using `kubectl`:

```bash
# 1. Create the dedicated namespace
kubectl apply -f k8s/namespace.yaml

# 2. Deploy ConfigMap and Secrets
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# 3. Deploy Workload & Networking
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/networkpolicy.yaml
```

## Pod Hardening & Security Context

Every container runs under strict non-root policies:

```yaml
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 10001
  capabilities:
    drop:
      - ALL
  seccompProfile:
    type: RuntimeDefault
```

## Scaling & High Availability

Because `fme-mcp-ultra` is stateless in Streamable HTTP transport mode, horizontal pod autoscaling (HPA) can be enabled based on CPU utilisation or JSON-RPC request volume:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fme-mcp-ultra-hpa
  namespace: fme-mcp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fme-mcp-ultra
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 75
```

