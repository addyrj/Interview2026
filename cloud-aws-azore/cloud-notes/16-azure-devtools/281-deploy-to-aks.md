# 281. Deploy to AKS
# AWS: Amazon EKS
# Azure: Azure Kubernetes Service (AKS)
# हिंदी में: AKS पर Docker ऐप डिप्लॉय करना

---

## 🔵 Simple Definition
AKS is Azure's managed Kubernetes: Azure runs the control plane, you manage node pools and workloads (Deployment + Service + Ingress).
हिंदी: AKS Azure का मैनेज्ड Kubernetes है, कंट्रोल प्लेन Azure चलाता है और आप सिर्फ ऐप डिप्लॉय करते हैं।

---

## 🔴 Why it Exists
Running your own Kubernetes control plane (etcd, API server, upgrades) is heavy work.
AKS gives scaling, rolling updates and self-healing for containers without that ops burden.

---

## 🟢 How it Works
```
git push -> GitHub Actions -> docker build -> push to ACR
                                   |
                     az aks get-credentials (kubeconfig)
                                   |
                     kubectl apply -> Deployment (3 pods)
                                   |
        Service (ClusterIP) <- Ingress / LoadBalancer <- Users
```

---

## 💻 Code / Config Example
```yaml
# k8s/app.yaml - Node.js/NestJS API
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  replicas: 3
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      containers:
        - name: api
          image: myacr.azurecr.io/api:latest   # replace tag with git SHA in CI
          ports: [{ containerPort: 3000 }]
          readinessProbe: { httpGet: { path: /health, port: 3000 } }
          resources:
            requests: { cpu: 100m, memory: 128Mi }
            limits: { memory: 256Mi }
---
apiVersion: v1
kind: Service
metadata: { name: api }
spec:
  type: LoadBalancer
  selector: { app: api }
  ports: [{ port: 80, targetPort: 3000 }]
```
```bash
az group create -n rg-demo -l centralindia
az acr create -g rg-demo -n myacr --sku Basic
az aks create -g rg-demo -n demo-aks --node-count 2 --attach-acr myacr --generate-ssh-keys
az aks get-credentials -g rg-demo -n demo-aks
kubectl apply -f k8s/app.yaml
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | EKS | AKS |
| Registry | ECR | ACR |
| Control plane cost | Charged per cluster-hour | Free tier available; paid Standard tier (approximate - check current docs) |
| Pod identity | IRSA / Pod Identity | Workload Identity |

---

## ⚠️ Common Mistakes
❌ Mistake: Using the `latest` tag and no resource requests/probes.
✅ Correct: Tag with git SHA, set requests/limits and readiness probes.

❌ Mistake: Cluster cannot pull from ACR (ImagePullBackOff).
✅ Correct: Use `--attach-acr` or grant the kubelet identity the AcrPull role.

---

## ⚫ Interview Q&A
Q1: [Easy] What does AKS manage for you?
A1: The Kubernetes control plane (API server, etcd, upgrades); you manage node pools and workloads.

Q2: [Medium] How does AKS pull private images from ACR?
A2: Attach ACR to the cluster so the kubelet managed identity gets the AcrPull role.

Q3: [Hard] How do you do zero-downtime deploys on AKS?
A3: RollingUpdate strategy with readiness probes, PodDisruptionBudget, multiple replicas across zones, and HPA/cluster autoscaler for capacity.

---

## ✅ Quick Checklist
□ Image tagged with commit SHA, stored in ACR
□ Probes, requests/limits set
□ Workload Identity instead of stored secrets

---

## ⚡ 1-Line Summary
AKS = managed Kubernetes on Azure for containers at scale. | AKS = Azure पर स्केल के लिए मैनेज्ड Kubernetes।

## ➡️ Next: 282. Deploy React to Static Web Apps
