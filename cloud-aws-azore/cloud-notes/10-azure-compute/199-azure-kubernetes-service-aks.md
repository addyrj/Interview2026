# 199. Azure Kubernetes Service (AKS)
# AWS: Amazon EKS
# Azure: Azure Kubernetes Service (AKS)
# हिंदी में: Azure की managed Kubernetes सेवा, control plane Azure संभालता है

---

## 🔵 Simple Definition
Managed Kubernetes: Azure runs the control plane; you manage node pools and workloads.
AKS में Kubernetes का control plane Azure चलाता है, आप सिर्फ nodes और ऐप संभालते हैं।

---

## 🔴 Why it Exists
Running many containerized services needs scheduling, scaling, rolling updates and service discovery without hand-building Kubernetes.

---

## 🟢 How it Works
```
Azure-managed Control Plane (API server, etcd)  [Free tier / Standard tier w/ SLA]
        |
Node pools (VMSS): system pool + user pools
        |
Pods <- Deployments/Services/Ingress ; Image from ACR (attach-acr)
Add-ons: Azure CNI, Workload Identity, Cluster autoscaler, Key Vault CSI driver
```

---

## 💻 Code / Config Example
```bash
az group create -n rg-aks -l centralindia
az acr create -g rg-aks -n myacr123 --sku Basic
az aks create -g rg-aks -n aks-demo --node-count 2 --node-vm-size Standard_B2s \
  --enable-managed-identity --attach-acr myacr123 \
  --enable-cluster-autoscaler --min-count 2 --max-count 4 --generate-ssh-keys
az aks get-credentials -g rg-aks -n aks-demo
kubectl apply -f deploy.yaml
```
```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  replicas: 2
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      containers:
        - name: api
          image: myacr123.azurecr.io/api:1.0
          ports: [{ containerPort: 3000 }]
          readinessProbe: { httpGet: { path: /health, port: 3000 } }
---
apiVersion: v1
kind: Service
metadata: { name: api }
spec:
  type: LoadBalancer
  selector: { app: api }
  ports: [{ port: 80, targetPort: 3000 }]
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | EKS | AKS |
| Control plane cost | Charged per cluster-hour | Free tier; paid tier with SLA (approximate - check docs) |
| Nodes | Managed node groups / Fargate | Node pools / virtual nodes |
| Registry | ECR | ACR |

---

## ⚠️ Common Mistakes
❌ Mistake: Single node, no requests/limits.
✅ Correct: 2+ nodes across zones, set resource requests/limits.

❌ Mistake: Service principal secrets for ACR pull.
✅ Correct: Managed identity with `--attach-acr`.

---

## ⚫ Interview Q&A
Q1: [Easy] Who manages the control plane?
A1: Azure.

Q2: [Medium] System vs user node pool?
A2: System pool runs critical add-ons (CoreDNS); user pools run your apps.

Q3: [Hard] When avoid AKS?
A3: For a few services on a small team; App Service or Container Apps costs less operational effort.

---

## ✅ Quick Checklist
□ Autoscaler and probes set
□ Workload Identity, no secrets
□ Upgrades planned

---

## ⚡ 1-Line Summary
AKS = managed Kubernetes on Azure. | AKS = Azure की managed Kubernetes।

## ➡️ Next: AKS vs EKS
