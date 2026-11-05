# 225. Docker Swarm vs Kubernetes
# हिंदी में: Docker Swarm बनाम Kubernetes

---

## 🔵 Simple Definition (English)
Both are **container orchestrators**: they run many containers across many servers, restart failed ones, scale them and route traffic. **Docker Swarm** is built into Docker: simple, small, quick to learn. **Kubernetes (K8s)** is a much larger, more powerful platform with a big ecosystem (Helm, operators, autoscaling, cloud-managed services like EKS), but with a steeper learning curve and more operating cost.

## 🔵 सरल परिभाषा (Hindi)
दोनों **container orchestrators** हैं: कई servers पर कई containers चलाते हैं, fail हुए को restart करते हैं, scale करते हैं और traffic route करते हैं। **Docker Swarm** Docker में ही built-in है: सरल, छोटा, जल्दी सीखा जाता है। **Kubernetes (K8s)** कहीं बड़ा और शक्तिशाली platform है जिसका बड़ा ecosystem है (Helm, operators, autoscaling, EKS जैसी managed services), पर सीखना कठिन और चलाने का खर्च ज़्यादा है।

---

## 🔴 Problem it Solves
Teams must choose an orchestrator and often choose wrongly: a 3-person startup adopts Kubernetes and spends months on YAML, networking and upgrades instead of features; or a growing company stays on Swarm and hits limits (no native autoscaling, small ecosystem, uncertain future). Knowing the real differences lets you pick the right tool for the size of your team, traffic and budget.

## 🔴 यह क्यों बना? (Hindi)
Teams को orchestrator चुनना पड़ता है और अक्सर गलत चुनते हैं: 3 लोगों की startup Kubernetes ले लेती है और features की जगह महीनों YAML, networking और upgrades में लगाती है; या बढ़ती company Swarm पर रहकर limits से टकराती है (native autoscaling नहीं, छोटा ecosystem, भविष्य अनिश्चित)। असली फर्क जानने से आप अपनी team, traffic और budget के हिसाब से सही tool चुन पाते हो।

---

## 🟢 How it Works — Step by Step

```
Swarm:
Step 1 → `docker swarm init` on a manager; `docker swarm join` on workers.
Step 2 → `docker stack deploy -c stack.yml app` (a Compose file with a `deploy:` section).
Step 3 → Managers (Raft) schedule tasks onto workers; ingress routing mesh publishes ports on every node.

Kubernetes:
Step 1 → Create a cluster (kubeadm, k3s, or managed EKS/GKE/AKS). Control plane = API server, etcd, scheduler, controllers.
Step 2 → `kubectl apply -f deployment.yaml service.yaml ingress.yaml` (desired state).
Step 3 → Controllers continuously compare desired vs actual state and fix the difference (self-healing).
Step 4 → Ingress controller / Service load-balances; HPA scales pods on CPU or custom metrics.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Swarm:
Step 1 → Manager पर `docker swarm init`; workers पर `docker swarm join`।
Step 2 → `docker stack deploy -c stack.yml app` (Compose file जिसमें `deploy:` section हो)।
Step 3 → Managers (Raft) tasks को workers पर schedule करते हैं; ingress routing mesh हर node पर ports publish करता है।

Kubernetes:
Step 1 → Cluster बनाओ (kubeadm, k3s, या managed EKS/GKE/AKS)। Control plane = API server, etcd, scheduler, controllers।
Step 2 → `kubectl apply -f deployment.yaml service.yaml ingress.yaml` (desired state)।
Step 3 → Controllers लगातार desired और actual state की तुलना करके फर्क ठीक करते हैं (self-healing)।
Step 4 → Ingress controller / Service load-balance करता है; HPA CPU या custom metrics पर pods scale करता है।
```

Comparison / तुलना:

| Feature | Docker Swarm | Kubernetes |
|---------|--------------|------------|
| Setup | 1 command, minutes | Hours/days (or managed service) |
| Learning curve | Low (Compose syntax) | High (many objects) |
| Config format | Compose YAML | Many manifests / Helm charts |
| Autoscaling | No built-in | HPA, VPA, Cluster Autoscaler, KEDA |
| Rolling update | Yes (`update_config`) | Yes, plus strategies, probes, PDB |
| Storage | Volumes, limited plugins | PV/PVC, CSI drivers |
| Ecosystem | Small | Huge (Helm, Argo CD, Istio, Prometheus operator) |
| Cloud managed | None | EKS, GKE, AKS |
| Min. overhead | Very light | Control plane needs resources (k3s is lighter) |
| Community / jobs | Declining | Industry standard |

---

## 🟡 Real World Example
Company A: a 4-person agency running 6 client apps on 3 VPS nodes. They use Swarm: a stack file per app, Traefik for TLS, rolling updates, and secrets via `docker secret`. Setup took an afternoon. Company B: a Flipkart-like marketplace with 80 microservices, traffic spikes on sale days, multiple teams. They use EKS with HPA, Argo CD for GitOps, and Prometheus for monitoring. The spike scales pods from 10 to 200 automatically. Both choices are right for their size.

## 🟡 Real Example Hindi mein
Company A: 4 लोगों की agency, 3 VPS nodes पर 6 client apps। वे Swarm use करते हैं: हर app का एक stack file, TLS के लिए Traefik, rolling updates, और `docker secret` से secrets। Setup में एक दोपहर लगी। Company B: Flipkart जैसा marketplace, 80 microservices, sale के दिन traffic spikes, कई teams। वे HPA, GitOps के लिए Argo CD और monitoring के लिए Prometheus के साथ EKS use करते हैं। Spike में pods 10 से 200 अपने-आप हो जाते हैं। दोनों चुनाव अपने size के लिए सही हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# stack.yml - Docker Swarm version of a Node.js API
# Deploy with: docker stack deploy -c stack.yml shop
version: "3.8"                              # Compose file format used by `docker stack`
services:
  api:
    image: myorg/node-api:1.4.2             # image (example tag)
    ports:
      - "3000:3000"                         # published through the routing mesh on every node
    deploy:
      replicas: 3                           # run 3 copies
      update_config:
        parallelism: 1                      # update one task at a time
        delay: 10s                          # wait 10s between updates
        order: start-first                  # start new before stopping old
      restart_policy:
        condition: on-failure               # restart failed tasks
      resources:
        limits:
          cpus: "0.5"                       # CPU cap
          memory: 256M                      # memory cap
```

```yaml
# k8s-api.yaml - Kubernetes version of the same service (Deployment + Service)
apiVersion: apps/v1                         # API group for Deployment
kind: Deployment                            # desired-state controller
metadata:
  name: api                                 # object name
spec:
  replicas: 3                               # run 3 pods
  selector:
    matchLabels:
      app: api                              # which pods this Deployment manages
  strategy:
    type: RollingUpdate                     # rolling update strategy
    rollingUpdate:
      maxSurge: 1                           # 1 extra pod during update
      maxUnavailable: 0                     # never go below desired count
  template:
    metadata:
      labels:
        app: api                            # pod label
    spec:
      containers:
        - name: api                         # container name
          image: myorg/node-api:1.4.2       # same image (example tag)
          ports:
            - containerPort: 3000           # app port
          resources:
            limits: { cpu: "500m", memory: 256Mi }   # same caps as Swarm example
          readinessProbe:
            httpGet: { path: /readyz, port: 3000 }   # traffic only when ready
---
apiVersion: v1
kind: Service                               # stable virtual IP + load balancing
metadata:
  name: api
spec:
  selector:
    app: api                                # route to pods with this label
  ports:
    - port: 80                              # service port
      targetPort: 3000                      # container port
```

## 💻 Code / Config Example — Advanced

```yaml
# k8s-hpa.yaml - autoscaling: something Swarm cannot do natively
apiVersion: autoscaling/v2                  # stable HPA API
kind: HorizontalPodAutoscaler               # scales pod count automatically
metadata:
  name: api-hpa                             # name
spec:
  scaleTargetRef:
    apiVersion: apps/v1                     # what to scale
    kind: Deployment
    name: api                               # the Deployment from above
  minReplicas: 3                            # never fewer than 3
  maxReplicas: 30                           # never more than 30
  metrics:
    - type: Resource
      resource:
        name: cpu                           # scale on CPU
        target:
          type: Utilization
          averageUtilization: 65            # keep average CPU near 65% of requests
```

```bash
# Decision helper script (rule of thumb, adjust to your situation)
#!/usr/bin/env bash
# usage: ./choose.sh <services> <engineers> <needs_autoscaling yes|no>
svc=$1; eng=$2; scale=$3                       # read arguments
if [ "$scale" = "yes" ] || [ "$svc" -gt 15 ] || [ "$eng" -gt 8 ]; then   # big or auto-scaling need
  echo "Kubernetes (managed: EKS/GKE) - ecosystem and autoscaling pay off"
elif [ "$svc" -le 5 ] && [ "$eng" -le 4 ]; then                          # small
  echo "Single host Docker Compose, or Swarm if you need 2-3 nodes"
else
  echo "k3s or Swarm - middle path; re-evaluate every 6 months"
fi
```

Both YAML files parse; neither was applied to a real cluster (no Docker/kubectl here). The `version:` key is ignored by modern Compose but still used by older `docker stack` tooling. / दोनों YAML parse हुए; असली cluster पर apply नहीं किए।

---

## 🟠 My Stack Integration
For your stack (Node.js, FastAPI, React, Nginx on VPS/AWS) the practical path:
1. **Now (1 VPS)**: Docker Compose + Nginx. No orchestrator needed.
2. **2-5 VPS nodes, small team**: Swarm is fine; stack files reuse your Compose knowledge.
3. **AWS, growing**: ECS on Fargate is a simpler AWS-native alternative; EKS if you want portability/ecosystem; k3s on EC2 if you want K8s cheaply.
4. **Interviews**: you must know Kubernetes basics (Pod, Deployment, Service, Ingress, ConfigMap, Secret, HPA) even if you run Swarm or Compose.

```yaml
# Swarm: secrets and configs for your Nginx + API stack
services:
  nginx:
    image: nginx:1.27-alpine                 # example tag
    ports: ["80:80", "443:443"]              # public
    configs:
      - source: nginx_conf                   # mounted config
        target: /etc/nginx/nginx.conf
  api:
    image: myorg/node-api:1.4.2
    secrets: [db_url]                        # file at /run/secrets/db_url
configs:
  nginx_conf:
    file: ./nginx.conf                       # source file on the manager
secrets:
  db_url:
    external: true                           # created with `docker secret create`
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Choosing Kubernetes because it is trendy, for 2 services on 1 server.
✅ Correct: Choose by team size, number of services and need for autoscaling.

❌ Mistake 2: Saying "Swarm is dead" in interviews.
✅ Correct: Swarm is maintained and works fine for small clusters, but its ecosystem is small and most hiring demand is for Kubernetes. Say it precisely.

❌ Mistake 3: Running a single Swarm manager in production.
✅ Correct: Use 3 managers (odd number for Raft quorum) for HA.

❌ Mistake 4: Assuming Compose files run unchanged on Kubernetes.
✅ Correct: Convert deliberately (Helm/Kustomize, or `kompose` as a starting point only).

❌ Mistake 5: Self-hosting the K8s control plane without need.
✅ Correct: Prefer managed (EKS/GKE) or k3s; upgrades and etcd backups are real work.

---

## 🧠 Tricky Interview Question
**Q:** Your company runs 4 services on 3 nodes with Swarm and the CTO says "move to Kubernetes". What do you ask before answering?

**Answer:** Ask what problem we have. Do we need autoscaling, multiple teams with RBAC and namespaces, GitOps, service mesh, or cloud integration? Are current deploys unreliable? What is the operating cost (people and money for EKS control plane about $73/month plus nodes)? If the answer is "no concrete pain", migrating adds risk without benefit; a measured plan could be: containerize cleanly, adopt health checks and 12-factor config (portable to both), pilot one service on k3s/EKS, then decide. Migration should follow a business need.

---

## ⚫ Interview Questions + Answers

Q1: Main architectural difference?
A1: Swarm: managers with Raft, tasks/services, simple model, Compose-based. Kubernetes: API server + etcd + controllers, many object types (Pod, ReplicaSet, Deployment, Service, Ingress...), declarative reconciliation loops.

Q2: How does service discovery differ?
A2: Swarm: DNS by service name plus a VIP and routing mesh. Kubernetes: CoreDNS with Services (ClusterIP, NodePort, LoadBalancer) and Ingress for HTTP routing.

Q3: Autoscaling?
A3: Swarm has none built-in (scale manually or with custom scripts). Kubernetes has HPA (pods), VPA (resources), Cluster Autoscaler or Karpenter (nodes).

Q4: Which is easier for stateful apps (DB)?
A4: Kubernetes has StatefulSets, PVCs and operators, but running databases in either is risky. On AWS prefer RDS and treat the cluster as stateless.

Q5: What are lighter Kubernetes options?
A5: k3s (single binary, great for VPS/edge), kind/minikube for local, managed EKS/GKE/AKS for production.

---

## 🔷 When to Use + When Not to Use
✅ Use Swarm when:
- Small team, few services, 2-5 nodes, already on Compose
- You want orchestration without a learning cliff

✅ Use Kubernetes when:
- Many services/teams, autoscaling, multi-cloud or managed cloud
- You need ecosystem tools (Argo CD, Prometheus operator, cert-manager)

❌ Avoid when:
- Kubernetes for a single small app on one VPS
- Swarm if your roadmap needs autoscaling, advanced rollout (canary via service mesh), or many third-party operators

---

## 📊 Visual Diagram
```
   Docker Swarm                         Kubernetes
 +-------------------+          +--------------------------------+
 | Manager (Raft) x3 |          | Control plane: API | etcd |     |
 +---------+---------+          |   scheduler | controllers      |
           |                    +---------------+----------------+
   +-------+-------+                            |
   | Worker | Worker |                  +--------+--------+
   | tasks  | tasks  |                  | Node  | Node    |
   +--------+--------+                 | Pods  | Pods    |
 routing mesh :3000                     +-------+---------+
 stack.yml (Compose)                   Deployment/Service/Ingress/HPA
 Simple, small                         Powerful, large ecosystem
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Orchestrator | Manages many containers | कई containers का manager |
| Stack | Group of Swarm services | Swarm services का group |
| Pod | Smallest K8s unit | K8s की सबसे छोटी इकाई |
| Deployment | Desired state for pods | Pods की desired state |
| HPA | Horizontal Pod Autoscaler | Pods अपने-आप घटाने/बढ़ाने वाला |
| Control plane | Brain of the cluster | Cluster का दिमाग |

---

## ⚡ 3-Line Summary
English: Swarm is simple and built-in; Kubernetes is powerful with a huge ecosystem but heavier.
Choose by team size, service count and autoscaling needs, not by trend.
Learn Kubernetes basics for interviews even if you run Compose or Swarm.

Hindi: Swarm सरल और built-in है; Kubernetes शक्तिशाली और बड़े ecosystem वाला पर भारी है।
Team size, services की संख्या और autoscaling की ज़रूरत से चुनो, trend से नहीं।
Interviews के लिए Kubernetes basics सीखो, चाहे आप Compose या Swarm चलाओ।

---

## ➡️ Next Topic
**226. Container Registry in Production** - whichever orchestrator you pick, it pulls images from a registry; next is how to run and secure one (ECR, GHCR, Docker Hub).
