# 345. Deploy to Kubernetes
# हिंदी में: Kubernetes पर Deploy करना

---

## 🔵 Simple Definition (English)
Deploying to Kubernetes means telling the cluster the desired state (a **Deployment** with a new image tag) and letting it roll pods over gradually. From CI you authenticate to the cluster, apply manifests (`kubectl apply`, `kustomize`, or `helm upgrade`) and wait with `kubectl rollout status`.

## 🔵 सरल परिभाषा (Hindi)
Kubernetes पर deploy का मतलब cluster को desired state बताना है (नए image tag वाला **Deployment**) और उसे pods धीरे-धीरे बदलने देना। CI से आप cluster में authenticate करते हैं, manifests apply करते हैं (`kubectl apply`, `kustomize` या `helm upgrade`) और `kubectl rollout status` से इंतज़ार करते हैं।

---

## 🔴 Problem it Solves
Many containers across many machines need scheduling, self-healing, rolling updates, service discovery and scaling. Doing this with scripts and SSH is brittle. Kubernetes reconciles reality to the declared state and keeps revision history for `rollout undo`.

## 🔴 यह क्यों बना? (Hindi)
कई machines पर कई containers को scheduling, self-healing, rolling updates, service discovery और scaling चाहिए। यह SSH scripts से नाज़ुक रहता है। Kubernetes असली स्थिति को declared state से मिलाता रहता है और `rollout undo` के लिए revision history रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build and push image: registry/api:<sha>
Step 2 → CI gets cluster credentials (EKS via OIDC role / kubeconfig secret)
Step 3 → Manifests stored in git (k8s/ or Helm chart)
Step 4 → kubectl set image / kustomize edit / helm upgrade --set image.tag
Step 5 → Deployment creates a new ReplicaSet, scales it up gradually
Step 6 → readinessProbe gates traffic; maxUnavailable limits downtime
Step 7 → kubectl rollout status --timeout; on failure rollout undo
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Image build और push: `registry/api:<sha>`।
Step 2 → CI को cluster credentials मिलते हैं (EKS में OIDC role / kubeconfig secret)।
Step 3 → Manifests git में (`k8s/` या Helm chart)।
Step 4 → `kubectl set image` / `kustomize edit` / `helm upgrade --set image.tag`।
Step 5 → Deployment नया ReplicaSet बनाकर धीरे-धीरे scale up करता है।
Step 6 → `readinessProbe` traffic रोकती/देती है; `maxUnavailable` downtime सीमित करता है।
Step 7 → `rollout status --timeout`; fail हो तो `rollout undo`।

---

## 🟡 Real World Example
A product company runs 12 microservices on EKS. A merge to `main` pushes `orders:sha-ab12cd3`, then the pipeline runs `kubectl set image deployment/orders orders=...`. Kubernetes replaces pods one at a time, only moving traffic once the readiness probe passes. A bad build never gets traffic; the job fails and `rollout undo` restores the previous ReplicaSet.

## 🟡 Real Example Hindi mein
एक product company के EKS पर 12 microservices हैं। `main` पर merge से `orders:sha-ab12cd3` push होता है और pipeline `kubectl set image deployment/orders orders=...` चलाती है। Kubernetes एक-एक pod बदलता है और readiness probe pass होने पर ही traffic देता है। खराब build को traffic नहीं मिलता; job fail होता है और `rollout undo` पिछला ReplicaSet लौटा देता है।

---

## 💻 Code / Config Example — Basic

```yaml
# k8s/deployment.yaml (basic Deployment + Service)
apiVersion: apps/v1                    # API group for Deployment
kind: Deployment                       # desired-state controller for pods
metadata:
  name: api                            # deployment name
spec:
  replicas: 2                          # run two pods
  selector:
    matchLabels:
      app: api                         # pods this deployment manages
  template:
    metadata:
      labels:
        app: api                       # label applied to each pod
    spec:
      containers:
        - name: api                    # container name
          image: ghcr.io/myorg/api:latest   # replaced by CI with a SHA tag
          ports:
            - containerPort: 3000      # port the app listens on
---
apiVersion: v1
kind: Service                          # stable internal address
metadata:
  name: api
spec:
  selector:
    app: api                           # route to pods with this label
  ports:
    - port: 80                         # service port
      targetPort: 3000                 # pod port
```

## 💻 Code / Config Example — Advanced

```yaml
# k8s/deployment-prod.yaml (probes, resources, rolling update, security)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
spec:
  replicas: 3
  revisionHistoryLimit: 5              # keep 5 old ReplicaSets for rollback
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1                      # one extra pod during update
      maxUnavailable: 0                # never drop below desired count
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      securityContext:
        runAsNonRoot: true             # refuse to run as root
        runAsUser: 1000                # numeric non-root user
      containers:
        - name: api
          image: ghcr.io/myorg/api:sha-ab12cd3     # example, set by CI
          ports:
            - containerPort: 3000
          envFrom:
            - secretRef:
                name: api-secrets      # DB URL etc. from a Kubernetes Secret
          readinessProbe:              # gate traffic
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
          livenessProbe:               # restart if stuck
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 15
            periodSeconds: 10
          resources:
            requests:
              cpu: 100m                # guaranteed share
              memory: 128Mi
            limits:
              cpu: 500m                # hard cap
              memory: 256Mi
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true   # needs writable volumes if app writes files
            capabilities:
              drop: ["ALL"]
```

```yaml
# .github/workflows/deploy-k8s.yml
name: deploy-k8s
on:
  push:
    branches: [main]
permissions:
  id-token: write                      # OIDC to AWS (EKS example)
  contents: read
env:
  CLUSTER: prod-eks                    # EKS cluster name
  AWS_REGION: ap-south-1
  NAMESPACE: production
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE }}
          aws-region: ${{ env.AWS_REGION }}
      - name: Get kubeconfig           # writes ~/.kube/config for EKS
        run: aws eks update-kubeconfig --name "$CLUSTER" --region "$AWS_REGION"
      - name: Apply manifests and set image
        run: |
          kubectl apply -n "$NAMESPACE" -f k8s/                        # sync manifests
          kubectl set image -n "$NAMESPACE" deployment/api api=ghcr.io/myorg/api:sha-${GITHUB_SHA::7}
      - name: Wait for rollout or undo
        run: |
          kubectl rollout status -n "$NAMESPACE" deployment/api --timeout=180s || {
            kubectl rollout undo -n "$NAMESPACE" deployment/api         # rollback
            exit 1
          }
```

The manifests were written for this note but not applied to a real cluster (no kubectl here); validate with `kubectl apply --dry-run=server` or `kubeconform` before relying on them.

---

## 🟠 My Stack Integration
Node.js and FastAPI become two Deployments with Services. An Ingress (nginx-ingress or AWS ALB controller) replaces the standalone Nginx; React is an Nginx-based image or S3/CloudFront.

```yaml
# k8s/ingress.yaml - path routing to Node.js and FastAPI
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"   # upload limit
spec:
  ingressClassName: nginx              # requires ingress-nginx installed
  tls:
    - hosts: ["app.example.com"]
      secretName: app-tls              # cert (e.g. from cert-manager)
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend: {service: {name: api, port: {number: 80}}}
          - path: /ml
            pathType: Prefix
            backend: {service: {name: ml-api, port: {number: 80}}}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deploying `:latest` with `imagePullPolicy: IfNotPresent`; nodes keep the old image.
✅ Correct: Use unique SHA tags or digests.

❌ Mistake 2: No readiness probe, so traffic hits pods that are still starting.
✅ Correct: Always define readiness and (carefully) liveness probes.

❌ Mistake 3: Cluster-admin kubeconfig stored in GitHub secrets.
✅ Correct: Namespace-scoped RBAC for CI, short-lived OIDC credentials.

❌ Mistake 4: No resource requests/limits.
✅ Correct: Set both to avoid noisy-neighbor and OOM surprises.

---

## 🧠 Tricky Interview Question
`kubectl rollout status` says success but users get 502 errors. How?

Answer: Rollout success only means pods are Ready per the readiness probe. If the probe is weak (e.g. TCP only) or points to a path that does not exercise dependencies, pods can be "ready" yet broken. Other causes: Ingress/Service selector mismatch, targetPort wrong, or connection draining missing (no `preStop` sleep) so in-flight requests die on termination.

---

## ⚫ Interview Questions + Answers

Q1: Deployment vs StatefulSet?
A1: Deployment for stateless interchangeable pods; StatefulSet for stable identity and storage (databases).

Q2: How does a rolling update work?
A2: A new ReplicaSet scales up while the old scales down within `maxSurge`/`maxUnavailable`.

Q3: Push vs pull (GitOps) deploys?
A3: Push: CI runs kubectl. Pull: Argo CD/Flux inside the cluster sync from git; CI only commits the new tag. Pull avoids giving CI cluster credentials.

Q4: How to roll back?
A4: `kubectl rollout undo deployment/api` (or `--to-revision=N`), or revert the git commit in GitOps.

Q5: Helm vs Kustomize?
A5: Helm templates plus releases and values; Kustomize patches plain YAML overlays without templating.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many services, autoscaling, multi-team platform.
- You need portability across clouds.

❌ Avoid when:
- One or two services on a single VPS.
- No one can operate and upgrade the cluster.

---

## 📊 Visual Diagram
```
 git push ─► CI: build/push image ghcr.io/myorg/api:sha-ab12cd3
                    │ kubectl set image (or git commit for GitOps)
                    ▼
 ┌──────────────────── Cluster ─────────────────────┐
 │ Deployment api                                   │
 │   ReplicaSet v41 (3→0 pods)   old                │
 │   ReplicaSet v42 (0→3 pods)   new, readiness OK  │
 │ Service api ──► Ingress ──► users                │
 └──────────────────────────────────────────────────┘
        rollout fails → rollout undo → v41
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pod | Smallest runnable unit | सबसे छोटी चलने वाली इकाई |
| Deployment | Manages replicated pods | pods की देखरेख |
| ReplicaSet | Keeps N pods of one version | एक version के N pods |
| Readiness probe | Is pod ready for traffic | traffic के लिए तैयार? |
| Ingress | HTTP routing into cluster | cluster में HTTP routing |
| GitOps | Cluster syncs from git | git से cluster sync |

---

## ⚡ 3-Line Summary
English: Update the Deployment image, let readiness probes gate the rolling update, and verify with rollout status. Undo on failure. Prefer OIDC or GitOps over static kubeconfig secrets.
Hindi: Deployment की image बदलो, readiness probes से rolling update चलने दो, rollout status से जाँचो। फेल पर undo करो। Static kubeconfig की जगह OIDC या GitOps चुनो।

---

## ➡️ Next Topic
**346. Deploy to Vercel** - the easiest path for frontends like React and Next.js.
