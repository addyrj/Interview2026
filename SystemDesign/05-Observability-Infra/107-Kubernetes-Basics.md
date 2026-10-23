# 107. Kubernetes Basics
# हिंदी में: Kubernetes — containers को कई मशीनों पर अपने आप चलाने, स्केल करने, ठीक करने (restart) और नेटवर्क से जोड़ने वाला सिस्टम (container orchestrator)

---

## 🔵 Simple Definition (English)
**Kubernetes (K8s)** is an open-source **container orchestration platform**. You declare the **desired state** ("run 4 replicas of order-api:1.9 with 512 MB RAM, expose it on port 80, scale between 2 and 20 based on CPU"), and Kubernetes **continuously makes reality match**: scheduling containers onto machines (**nodes**), restarting failed ones, replacing them during deploys, load-balancing traffic, mounting config/secrets/storage, and autoscaling.
Managed versions: **EKS (AWS), GKE (Google), AKS (Azure)**. Lighter local ones: kind, minikube, k3s.

## 🔵 सरल परिभाषा (Hindi)
Kubernetes containers को कई मशीनों पर चलाने का "मैनेजर" है। आप बताते हो कि क्या चाहिए (order-api के 4 copies, इतनी memory, यह port), और Kubernetes हमेशा वैसा ही बनाए रखता है।
Container गिरे तो फिर चलाता है, deploy पर धीरे-धीरे बदलता है, ट्रैफ़िक बाँटता है, और भीड़ में copies बढ़ाता है।

---

## 🔴 Problem it Solves
Running containers with `docker run` on a few servers breaks down at scale:
- Which server has free CPU/RAM for the next container? (**scheduling**)
- A container crashes at 3 AM → who restarts it? A server dies → who moves its containers? (**self-healing**)
- Deploy v2 without downtime and roll back if broken. (**rolling updates**)
- 50 instances of a service with changing IPs → how do others find them? (**service discovery + load balancing**)
- Scale up for traffic spikes, down at night. (**autoscaling**)
- Inject config and secrets per environment. (**config management**)

Kubernetes gives a **standard, declarative API** for all of this, across clouds and on-prem.

## 🔴 यह क्यों बना? (Hindi)
कुछ सर्वरों पर `docker run` से containers चलाना बड़े स्केल पर टूट जाता है — किस मशीन पर जगह है? रात 3 बजे container गिरा तो कौन चलाएगा? बिना downtime नया version कैसे? 50 copies के बदलते IP कौन ढूँढेगा? भीड़ में scale कौन करेगा?
Kubernetes यह सब एक मानक, declarative API से करता है — किसी भी cloud पर।

---

## 🟢 How it Works — Step by Step

### Architecture

```
                         ┌──────────────────────── CONTROL PLANE ────────────────────────┐
  kubectl / CI ─────────►│ kube-apiserver ── etcd (cluster state, Raft)                  │
  (YAML: desired state)  │ scheduler (places pods on nodes)                              │
                         │ controller-manager (deployments, replicas, nodes, endpoints)  │
                         └───────────────────────────┬───────────────────────────────────┘
                                                     │ watches / instructions
            ┌────────────────────────────────┬───────┴────────────────────────┐
     ┌──────▼──────┐                  ┌──────▼──────┐                  ┌──────▼──────┐
     │  Node 1     │                  │  Node 2     │                  │  Node 3     │
     │ kubelet     │                  │ kubelet     │                  │ kubelet     │
     │ kube-proxy  │                  │ kube-proxy  │                  │ kube-proxy  │
     │ [pod][pod]  │                  │ [pod][pod]  │                  │ [pod]       │
     └─────────────┘                  └─────────────┘                  └─────────────┘
Reconciliation loop: controllers constantly compare desired vs actual state and fix differences.
```

### Core objects (must know)

```
Pod          → smallest unit: 1+ containers sharing network/IP & volumes (usually 1 app container
               + optional sidecars). Ephemeral — don't rely on pod IPs.
Deployment   → manages ReplicaSets → N identical stateless pods; rolling updates & rollbacks
Service      → stable virtual IP + DNS name load-balancing to pods matching labels
               (ClusterIP internal, NodePort, LoadBalancer → cloud LB)
Ingress      → L7 HTTP routing from outside (host/path → service), TLS; via an ingress controller
               (NGINX, AWS Load Balancer Controller). Gateway API is the newer replacement.
ConfigMap    → non-secret config (env vars / files)
Secret       → sensitive config (base64, encrypt at rest; better: external secrets from Vault/AWS SM)
Namespace    → logical isolation (dev/staging/prod, or per team) + quotas
StatefulSet  → stable identity & storage per pod (db-0, db-1) for stateful apps
DaemonSet    → one pod per node (log collectors, monitoring agents)
Job / CronJob→ run-to-completion tasks / scheduled tasks
PersistentVolume(Claim) → durable storage (EBS) attached to pods
HPA          → Horizontal Pod Autoscaler (scale replicas by CPU/memory/custom metrics)
```

### Request path into the cluster

```
User → DNS → Cloud LB → Ingress controller (NGINX/ALB) → Service (ClusterIP) → Pod (container :3000)
Inside: order pod → http://payment-service.prod.svc.cluster.local → kube-proxy/iptables → payment pods
```

### Deployments: rolling update

```
replicas: 4, maxSurge: 1, maxUnavailable: 0
v1 v1 v1 v1  → start v2 (readiness probe passes) → kill one v1 → repeat
v2 v1 v1 v1 … v2 v2 v2 v2     zero downtime if probes + graceful shutdown are correct
kubectl rollout undo deployment/order-api   → instant rollback to previous ReplicaSet
```

### Resources & scheduling

```
requests: guaranteed minimum used for SCHEDULING (cpu: 250m, memory: 256Mi)
limits:   max allowed (memory over limit → OOMKilled; CPU over limit → throttled)
Set requests realistically; set memory limit; be careful with CPU limits (throttling hurts latency).
Node autoscaling: Cluster Autoscaler / Karpenter adds nodes when pods can't be scheduled.
```

### Health probes (Topic 80)
```
startupProbe → readinessProbe (traffic) → livenessProbe (restart); graceful SIGTERM handling
```

### Is Kubernetes always the answer?
```
✅ Many services, teams, need for portability, autoscaling, platform team
❌ Small team / few services → ECS Fargate, Cloud Run, App Runner, Render, Railway, Fly.io, or a VPS
   with Docker Compose are simpler and cheaper. K8s has a real learning & ops cost.
```

## 🟢 कैसे काम करता है? (Hindi)
1. आप YAML में "चाहिए क्या" लिखते हो (Deployment: 4 copies, image, memory); API server इसे etcd में सेव करता है।
2. Scheduler pods को ख़ाली जगह वाली nodes पर रखता है; हर node का kubelet containers चलाता है।
3. Controllers लगातार जाँचते हैं — pod गिरा तो नया, node गिरा तो pods दूसरी जगह।
4. Service एक स्थिर नाम/IP देती है जो सही pods में ट्रैफ़िक बाँटती है; Ingress बाहर से HTTP routing (domain, path, TLS)।
5. Rolling update से बिना downtime नया version, गड़बड़ी हो तो `rollout undo`; HPA भीड़ में pods बढ़ाता है। छोटी टीम के लिए ECS/Cloud Run अक्सर आसान है।

---

## 🟡 Real World Example

**Google Borg → Kubernetes (2014)** — Kubernetes was inspired by Borg, Google's internal cluster manager that has run nearly everything at Google for over a decade. Google open-sourced the ideas as Kubernetes, which is now governed by the CNCF.

**Spotify, Airbnb, Pinterest, Shopify** — migrated to Kubernetes to standardize deployments across hundreds of services. Shopify runs Black Friday traffic on GKE.

**Indian companies (Swiggy, Zomato, Flipkart, PhonePe, Razorpay)** — run large fleets on EKS, GKE or self-managed Kubernetes, using HPA for dinner-time peaks and sale events, plus Karpenter or Cluster Autoscaler for node scaling.

**Pokémon GO (2016)** — ran on GKE and scaled to 50× its expected traffic within days of launch, a famous early Kubernetes scaling story.

## 🟡 Real Example Hindi में
Kubernetes Google के अंदरूनी Borg से प्रेरित है, जो Google की लगभग हर सेवा चलाता था। Pokémon GO लॉन्च के समय GKE पर अनुमान से 50 गुना ट्रैफ़िक तक स्केल हुआ।
Swiggy, Flipkart, PhonePe जैसी कंपनियाँ EKS/GKE पर बड़े clusters चलाती हैं — रात के खाने और सेल के समय HPA से pods बढ़ते हैं।

---

## 🟠 My Stack Example

### Deployment + Service + HPA for a Node.js API
```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: order-api, namespace: prod, labels: { app: order-api } }
spec:
  replicas: 3
  strategy: { type: RollingUpdate, rollingUpdate: { maxSurge: 1, maxUnavailable: 0 } }
  selector: { matchLabels: { app: order-api } }
  template:
    metadata: { labels: { app: order-api, version: "1.9.2" } }
    spec:
      terminationGracePeriodSeconds: 30
      containers:
        - name: api
          image: 123456789.dkr.ecr.ap-south-1.amazonaws.com/order-api:1.9.2   # immutable tag, never :latest
          ports: [{ containerPort: 3000 }]
          envFrom:
            - configMapRef: { name: order-api-config }
            - secretRef: { name: order-api-secrets }
          resources:
            requests: { cpu: 250m, memory: 256Mi }
            limits:   { memory: 512Mi }
          startupProbe:   { httpGet: { path: /health/live, port: 3000 }, periodSeconds: 5, failureThreshold: 24 }
          readinessProbe: { httpGet: { path: /health/ready, port: 3000 }, periodSeconds: 5 }
          livenessProbe:  { httpGet: { path: /health/live, port: 3000 }, periodSeconds: 10, failureThreshold: 3 }
          lifecycle: { preStop: { exec: { command: ["sh", "-c", "sleep 5"] } } }
      topologySpreadConstraints:                     # spread pods across AZs
        - { maxSkew: 1, topologyKey: topology.kubernetes.io/zone, whenUnsatisfiable: ScheduleAnyway,
            labelSelector: { matchLabels: { app: order-api } } }
---
apiVersion: v1
kind: Service
metadata: { name: order-api, namespace: prod }
spec: { selector: { app: order-api }, ports: [{ port: 80, targetPort: 3000 }] }
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: order-api, namespace: prod }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: order-api }
  minReplicas: 3
  maxReplicas: 30
  metrics: [{ type: Resource, resource: { name: cpu, target: { type: Utilization, averageUtilization: 60 } } }]
---
apiVersion: policy/v1
kind: PodDisruptionBudget                           # keep ≥2 pods during node drains/upgrades
metadata: { name: order-api, namespace: prod }
spec: { minAvailable: 2, selector: { matchLabels: { app: order-api } } }
```

### Ingress (NGINX or AWS ALB controller)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  namespace: prod
  annotations: { cert-manager.io/cluster-issuer: letsencrypt }
spec:
  ingressClassName: nginx
  tls: [{ hosts: [api.myapp.com], secretName: api-tls }]
  rules:
    - host: api.myapp.com
      http:
        paths:
          - { path: /api/v1/orders,   pathType: Prefix, backend: { service: { name: order-api,   port: { number: 80 } } } }
          - { path: /api/v1/payments, pathType: Prefix, backend: { service: { name: payment-api, port: { number: 80 } } } }
```

### CronJob (runs once, no duplicate cron across replicas)
```yaml
apiVersion: batch/v1
kind: CronJob
metadata: { name: daily-settlement, namespace: prod }
spec:
  schedule: "30 2 * * *"
  concurrencyPolicy: Forbid
  jobTemplate: { spec: { backoffLimit: 2, template: { spec: { restartPolicy: OnFailure,
    containers: [{ name: job, image: order-api:1.9.2, command: ["node", "dist/jobs/settlement.js"] }] } } } }
```

### Everyday kubectl
```bash
kubectl get pods -n prod -o wide
kubectl describe pod order-api-7c9f -n prod        # events: OOMKilled? probe failures? image pull?
kubectl logs -f deploy/order-api -n prod
kubectl rollout status deploy/order-api -n prod
kubectl rollout undo deploy/order-api -n prod
kubectl top pods -n prod                           # needs metrics-server
kubectl port-forward svc/order-api 3000:80 -n prod
kubectl exec -it deploy/order-api -n prod -- sh
```

### FastAPI image (multi-stage, small, non-root)
```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m app && chown -R app /app
USER app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
```

### Packaging & GitOps
```
Helm charts / Kustomize overlays per env; Argo CD or Flux syncs Git → cluster (GitOps)
Secrets: External Secrets Operator ← AWS Secrets Manager; images scanned in CI (Trivy)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is Kubernetes and what problems does it solve?**
A1: A container orchestration platform with a declarative API. You specify the desired state, and controllers continuously reconcile actual state to match it. It handles scheduling containers onto nodes, self-healing (restarting and rescheduling failed pods), rolling updates and rollbacks, service discovery and load balancing, config and secret injection, storage attachment, and horizontal autoscaling, portably across clouds.

**Q2: Explain Pod, Deployment and Service.**
A2: A Pod is the smallest deployable unit: one or more containers sharing a network namespace (IP) and volumes, and it's ephemeral. A Deployment manages a ReplicaSet to keep N identical pods running and performs rolling updates and rollbacks for stateless apps. A Service gives a stable virtual IP and DNS name that load-balances to the current set of healthy pods matching its label selector, decoupling clients from changing pod IPs.

**Q3: What's the difference between resource requests and limits?**
A3: Requests are the guaranteed CPU and memory the scheduler reserves when placing a pod on a node, and they affect scheduling and HPA percentages. Limits are hard caps: exceeding the memory limit gets the container OOM-killed, and exceeding the CPU limit gets it throttled. Set realistic requests from observed usage, always set memory limits, and be cautious with tight CPU limits, which can cause latency spikes from throttling.

**Q4: How does Kubernetes achieve zero-downtime deployments?**
A4: A Deployment's rolling update creates new pods (maxSurge) before removing old ones (maxUnavailable 0). New pods receive traffic only after the readiness probe passes. Old pods are removed from Service endpoints, get SIGTERM, and have a grace period (plus a preStop hook) to finish in-flight requests. PodDisruptionBudgets protect availability during node maintenance. If the new version is bad, `kubectl rollout undo` or automated canaries (Argo Rollouts) revert it.

**Q5: When would you NOT use Kubernetes?**
A5: For small teams or a few services where operational overhead outweighs the benefits: cluster upgrades, networking, security, observability and YAML sprawl. Simpler managed options (AWS ECS/Fargate, App Runner, Google Cloud Run, Render, Fly.io, Heroku-like platforms, or Docker Compose on a VPS for tiny apps) provide deploys, scaling and health checks with much less complexity. Adopt Kubernetes when scale, team count, portability or customization needs justify a platform team.

---

## 🔷 Trade-offs
✅ Advantages:
- Self-healing, autoscaling, rolling deploys, service discovery, portable & huge ecosystem (Helm, Argo, Istio).

❌ Disadvantages:
- Steep learning curve, operational complexity (upgrades, networking, security), YAML sprawl.
- Cost overhead for small workloads; misconfigured probes/limits cause outages.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Kubernetes | Container orchestration platform | containers का प्रबंधक |
| Node | Machine running pods | pods चलाने वाली मशीन |
| Pod | Smallest unit, 1+ containers | सबसे छोटी इकाई |
| Deployment | Manages replicated stateless pods | एक जैसे pods का प्रबंधन |
| Service | Stable name/IP + load balancing | स्थिर नाम और ट्रैफ़िक बँटवारा |
| Ingress | External HTTP routing | बाहर से HTTP routing |
| ConfigMap / Secret | Config / sensitive config | सेटिंग / गुप्त सेटिंग |
| HPA | Horizontal Pod Autoscaler | pods अपने आप बढ़ाना-घटाना |
| Control plane | API server, scheduler, etcd | cluster का दिमाग़ |
| Reconciliation | Matching actual to desired state | असली हालत को चाही हालत जैसा करना |

---

## ⚡ 3-Line Summary
**English:**
1. Kubernetes reconciles declared desired state: schedules pods on nodes, self-heals, rolls out updates, discovers & load-balances services, autoscales.
2. Core objects: Pod, Deployment, Service, Ingress, ConfigMap/Secret, StatefulSet, CronJob, HPA; set requests/limits and probes correctly.
3. Powerful but complex — use managed (EKS/GKE) or simpler platforms (ECS/Cloud Run) when the team is small.

**Hindi:**
1. Kubernetes = चाही हालत बनाए रखना: pods चलाना, ख़ुद ठीक होना, rolling update, service discovery, autoscaling।
2. मुख्य चीज़ें: Pod, Deployment, Service, Ingress, ConfigMap/Secret, CronJob, HPA; requests/limits और probes सही रखो।
3. ताक़तवर पर जटिल — छोटी टीम के लिए ECS/Cloud Run जैसे आसान विकल्प।

---

## ➡️ Next Topic Suggestion
**108. Chaos Engineering** — With self-healing infrastructure, prove it actually heals. Next: chaos engineering, deliberately injecting failures (kill pods, add latency, drop regions) to find weaknesses before real outages do.
