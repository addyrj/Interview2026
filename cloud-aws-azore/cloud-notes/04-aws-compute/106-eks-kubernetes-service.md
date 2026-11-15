# 106. EKS - Kubernetes Service
# AWS: Amazon EKS
# Azure: Azure Kubernetes Service (AKS)
# हिंदी में: AWS का managed Kubernetes - control plane AWS चलाता है

---

## 🔵 Simple Definition
EKS runs the Kubernetes control plane (API server, etcd) for you; you provide worker nodes (managed node groups, Fargate profiles) and deploy standard Kubernetes manifests.
Kubernetes का दिमाग AWS संभालता है, workers और apps आप।

---

## 🔴 Why it Exists
Running Kubernetes yourself means patching and HA-ing etcd and masters. Teams that need the K8s ecosystem (Helm, operators, portability) want it managed.

---

## 🟢 How it Works
```
kubectl / CI --> EKS API endpoint (AWS-managed control plane, multi-AZ)
                      |
          Managed Node Group (EC2 in your VPC)  or  Fargate profile
                      |
   Pods <- Service (type LoadBalancer / Ingress via AWS Load Balancer Controller)
Auth: IAM -> access entries / aws-auth; Pod AWS access: IRSA or EKS Pod Identity.
```

---

## 💻 Code / Config Example
```yaml
# eksctl cluster.yaml (create with: eksctl create cluster -f cluster.yaml)
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: demo
  region: ap-south-1
managedNodeGroups:
  - name: ng-1
    instanceType: t3.medium
    desiredCapacity: 2
    minSize: 2
    maxSize: 4
---
# deployment.yaml - FastAPI app
apiVersion: apps/v1
kind: Deployment
metadata: { name: fastapi }
spec:
  replicas: 2
  selector: { matchLabels: { app: fastapi } }
  template:
    metadata: { labels: { app: fastapi } }
    spec:
      containers:
        - name: app
          image: 123456789012.dkr.ecr.ap-south-1.amazonaws.com/fastapi:v1
          ports: [{ containerPort: 8000 }]
          readinessProbe: { httpGet: { path: /health, port: 8000 } }
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Managed K8s | EKS | AKS |
| Control plane cost | Charged per cluster-hour (approximate - check current docs) | Free tier; paid uptime-SLA tier (check docs) |
| Pod identity | IRSA / Pod Identity | Workload Identity |
| Ingress | AWS Load Balancer Controller | AGIC / NGINX |

---

## ⚠️ Common Mistakes
❌ Mistake: Using EKS for one small API.
✅ Correct: Use ECS/App Runner unless you need Kubernetes features.

❌ Mistake: Giving all pods the node IAM role.
✅ Correct: Per-service-account roles (IRSA / Pod Identity).

---

## ⚫ Interview Q&A
Q1: [Easy] What does AWS manage in EKS?
A1: The control plane; you manage nodes (unless Fargate/Auto Mode).
Q2: [Medium] How do pods get AWS permissions?
A2: IRSA (OIDC-based service account roles) or EKS Pod Identity.
Q3: [Hard] Pods can't get IPs - why?
A3: VPC CNI assigns VPC IPs from subnets/ENIs; subnet or instance ENI/IP limits exhausted. Use prefix delegation or bigger subnets.

---

## ✅ Quick Checklist
□ Nodes in private subnets across 2+ AZs
□ Pod-level IAM, not node role
□ Plan Kubernetes version upgrades

---

## ⚡ 1-Line Summary
EKS = AWS-run Kubernetes control plane | EKS में Kubernetes का control plane AWS चलाता है।

## ➡️ Next: 107. EKS vs ECS
