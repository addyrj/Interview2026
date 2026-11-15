# 200. AKS vs EKS
# AWS: Amazon EKS
# Azure: Azure Kubernetes Service (AKS)
# हिंदी में: दोनों managed Kubernetes हैं; फर्क integration, cost और setup में है

---

## 🔵 Simple Definition
Both run upstream Kubernetes with a managed control plane; they differ in networking, identity, defaults and pricing.
दोनों में Kubernetes वही है, अंतर cloud integration और डिफ़ॉल्ट सेटअप का है।

---

## 🔴 Why it Exists
Teams must pick (or migrate between) clouds; knowing the differences avoids surprises.

---

## 🟢 How it Works
```
            EKS                         AKS
Identity:   IRSA / Pod Identity         Entra Workload Identity
Network:    VPC CNI (pod = VPC IP)      Azure CNI / CNI Overlay / kubenet
LB:         ALB/NLB (controller)        Azure LB / App Gateway (AGIC) built-in
Registry:   ECR                         ACR
Autoscale:  Cluster Autoscaler/Karpenter Cluster autoscaler / Node Auto-provisioning (Karpenter-based)
Create:     eksctl / Terraform (more steps)  az aks create (one command)
```

---

## 💻 Code / Config Example
```bash
# Same app manifests work on both. Only the cluster creation differs.
# EKS
eksctl create cluster --name demo --region ap-south-1 --nodes 2 --node-type t3.medium
aws eks update-kubeconfig --name demo --region ap-south-1

# AKS
az aks create -g rg-aks -n demo --node-count 2 --node-vm-size Standard_B2s --generate-ssh-keys
az aks get-credentials -g rg-aks -n demo

kubectl get nodes   # identical from here
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | EKS | AKS |
|---------|-----|-----|
| Control plane price | Per cluster-hour | Free tier or paid Standard (approximate - check docs) |
| Setup effort | Higher (add-ons, IAM mapping) | Lower (integrated) |
| Serverless nodes | Fargate | Virtual nodes (ACI) |
| Upgrades | Manual/managed node groups | Auto-upgrade channels |
| Ingress | AWS LB Controller | App Routing add-on / AGIC |

---

## ⚠️ Common Mistakes
❌ Mistake: Using cloud-specific annotations everywhere.
✅ Correct: Keep manifests portable; isolate cloud bits in Helm values.

❌ Mistake: Assuming Kubernetes versions match.
✅ Correct: Check supported versions in each service.

---

## ⚫ Interview Q&A
Q1: [Easy] Is the Kubernetes API different?
A1: No, both are conformant Kubernetes.

Q2: [Medium] Pod IAM on each?
A2: EKS uses IRSA/Pod Identity; AKS uses Workload Identity federated with Entra.

Q3: [Hard] Migrate EKS to AKS?
A3: Containerize config, move images to ACR, re-map identity/storage classes/ingress, use Helm/Terraform, move data with replication, shift traffic with DNS weights.

---

## ✅ Quick Checklist
□ Portable manifests
□ Identity model understood
□ Cost of control plane compared

---

## ⚡ 1-Line Summary
Same Kubernetes, different cloud glue: AKS is simpler, EKS more AWS-native. | Kubernetes वही, cloud integration अलग: AKS आसान, EKS AWS-नेटिव।

## ➡️ Next: Azure Networking (VNet)
