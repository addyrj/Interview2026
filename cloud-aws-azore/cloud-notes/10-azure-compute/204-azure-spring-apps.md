---

# 204. Azure Spring Apps
# AWS: N/A (Azure-only concept); closest: AWS App Runner / Elastic Beanstalk / ECS for Spring Boot
# Azure: Azure Spring Apps (managed Spring Boot hosting)
# हिंदी में: Java Spring Boot apps के लिए managed platform

---

## 🔵 Simple Definition (2 lines)
Azure Spring Apps runs Spring Boot microservices with built-in service registry, config server and autoscaling.
हिंदी: Azure Spring Apps में Spring Boot microservices बिना cluster संभाले चलते हैं।

---

## 🔴 Why it Exists (2 lines)
Running Spring Cloud components (Eureka, Config Server) and Kubernetes yourself is heavy ops work.
The service manages them so Java teams only deploy JARs or source.

---

## 🟢 How it Works
```
Your JAR / source --az spring app deploy--> Service instance
   |-- App 1 (instances, CPU/mem, scale rules)
   |-- App 2
   |-- Managed service registry + config server (Git-backed)
   -> Public endpoint or VNet injection
```
Note: Microsoft has announced retirement of Azure Spring Apps (Standard/Basic/Enterprise plans); verify dates in current docs and consider Azure Container Apps instead.

---

## 💻 Code / Config Example
```bash
# Create service + app (Azure CLI "spring" extension)
az extension add --name spring
az spring create -n my-spring -g rg-demo -l centralindia
az spring app create -n orders -s my-spring -g rg-demo --assign-endpoint true

# Deploy a built JAR
az spring app deploy -n orders -s my-spring -g rg-demo \
  --artifact-path target/orders-0.0.1-SNAPSHOT.jar
```
```bash
# Modern alternative: same Spring Boot app as a container on Container Apps
az containerapp up -n orders --source . -g rg-demo --ingress external --target-port 8080
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | N/A (AWS-only gap); closest: App Runner / Elastic Beanstalk / ECS | Azure Spring Apps |
| Spring Cloud parts | Self-managed (or Spring Cloud AWS libs) | Managed registry, config server |
| Pricing | Per underlying compute | Per vCPU/memory hours by plan (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Starting a new project on a service that is being retired.
✅ Correct: Check the retirement notice; prefer Container Apps/AKS for new Spring workloads.

❌ Mistake: Hard-coding DB passwords in `application.properties`.
✅ Correct: Use Key Vault references / managed identity.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is Azure Spring Apps? A1: Managed hosting for Spring Boot microservices.
Q2: [Medium] How is it different from App Service? A2: It bundles Spring Cloud features (registry, config server, tracing) and app-level scaling.
Q3: [Hard] How would you migrate off it? A3: Containerize with a Dockerfile, push to ACR, deploy to Container Apps/AKS, replace registry/config with Kubernetes DNS and Azure App Configuration.

---

## ✅ Quick Checklist
□ Check service retirement status
□ Secrets in Key Vault
□ Health endpoint (Actuator) enabled
□ Plan migration path to containers

---

## ⚡ 1-Line Summary
Managed Spring Boot hosting, now being retired in favour of containers | Spring Boot के लिए managed hosting, अब containers की ओर migration बेहतर है।

## ➡️ Next: 205. Azure Virtual Network (VNet)

---
