---

# 130. Image Pull Policy
# हिंदी में: Image Pull Policy (Image कब दोबारा खींची जाए)

---

## 🔵 Simple Definition (English)
**Image pull policy** decides whether the runtime downloads an image again before starting a container. Docker Compose has `pull_policy` (`always`, `missing`, `never`, `build`, `daily`, `weekly`), `docker run` has `--pull` (`always`, `missing`, `never`), and Kubernetes has `imagePullPolicy` (`Always`, `IfNotPresent`, `Never`).

## 🔵 सरल परिभाषा (Hindi)
**Image pull policy** तय करती है कि container शुरू करने से पहले runtime image दोबारा download करेगा या नहीं। Docker Compose में `pull_policy` (`always`, `missing`, `never`, `build`, `daily`, `weekly`), `docker run` में `--pull` (`always`, `missing`, `never`), और Kubernetes में `imagePullPolicy` (`Always`, `IfNotPresent`, `Never`) होती है।

---

## 🔴 Problem it Solves
A mutable tag like `myapp:latest` or `myapp:staging` can point to a new image tomorrow. If the host already has an old copy, `docker run` happily starts the stale one, so you deploy "new code" and still run old code. Pulling always wastes time and hits rate limits; never pulling breaks fresh servers. A clear policy gives predictable, repeatable deployments.

## 🔴 यह क्यों बना? (Hindi)
`myapp:latest` या `myapp:staging` जैसा mutable tag कल किसी नई image पर point कर सकता है। Host पर पुरानी copy हो तो `docker run` उसी stale image को चला देता है, यानी आप "नया code" deploy करते हैं पर पुराना code चलता है। हमेशा pull करना समय और rate limit खाता है; कभी pull न करना नए servers पर चलता ही नहीं। साफ़ policy से deployments predictable और repeatable बनते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run: docker run / compose up / kubectl apply with an image reference
Step 2 → Runtime reads the policy (flag, compose key or pod spec)
Step 3 → always   : contact registry, compare manifest digest, download only changed layers
Step 4 → missing / IfNotPresent : pull only if the tag is not in the local image store
Step 5 → never    : use local image; fail with "No such image" if absent
Step 6 → Kubernetes default: tag :latest or no tag -> Always ; any other tag -> IfNotPresent ;
         digest reference (image@sha256:...) -> IfNotPresent
Step 7 → Container starts from the resolved image ID
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप image reference के साथ docker run / compose up / kubectl apply चलाते हैं
Step 2 → Runtime policy पढ़ता है (flag, compose key या pod spec से)
Step 3 → always   : registry से संपर्क, manifest digest की तुलना, सिर्फ़ बदली layers download
Step 4 → missing / IfNotPresent : tag local store में न हो तभी pull
Step 5 → never    : local image इस्तेमाल; न हो तो "No such image" error
Step 6 → Kubernetes default: tag :latest या बिना tag -> Always ; कोई और tag -> IfNotPresent ;
         digest reference (image@sha256:...) -> IfNotPresent
Step 7 → Container resolved image ID से शुरू होता है
```

---

## 🟡 Real World Example
A food-delivery team pushed `api:prod` every release. One night a hotfix was pushed, the deploy script ran `docker compose up -d`, and nothing changed: the VPS already had an `api:prod` image, and Compose's default `pull_policy: missing` reused it. Orders kept failing for 40 minutes until someone ran `docker compose pull`. Afterwards they switched to immutable tags (`api:1.8.3` and the git SHA), added `docker compose pull` to the deploy script, and used `imagePullPolicy: IfNotPresent` on Kubernetes staging.

## 🟡 Real Example Hindi mein
एक food-delivery team हर release पर `api:prod` push करती थी। एक रात hotfix push हुआ, deploy script ने `docker compose up -d` चलाया, और कुछ नहीं बदला: VPS पर पहले से `api:prod` image थी और Compose का default `pull_policy: missing` उसी को चलाता रहा। Orders 40 मिनट तक fail होते रहे जब तक किसी ने `docker compose pull` नहीं चलाया। बाद में उन्होंने immutable tags (`api:1.8.3` और git SHA) अपनाए, deploy script में `docker compose pull` जोड़ा, और Kubernetes staging पर `imagePullPolicy: IfNotPresent` रखा।

---

## 💻 Code / Config Example — Basic

```bash
# docker run --pull controls pulling for a single container (Docker 20.10+)

# Default: pull only if image is missing locally
docker run --rm --pull missing alpine:3.20 echo "hello"
# --rm removes the container after exit; "missing" is the default behaviour

# Always check the registry first (fresh code for mutable tags)
docker run --rm --pull always alpine:3.20 echo "fresh"
# always compares digests; unchanged layers are not downloaded again

# Never pull: use only local images (offline or air-gapped server)
docker run --rm --pull never alpine:3.20 echo "offline"
# fails with "Unable to find image" if alpine:3.20 is not already present

# Pull manually without running anything
docker pull alpine:3.20
# updates the local tag to the latest digest in the registry

# See which digest the local tag points to
docker image inspect alpine:3.20 --format '{{index .RepoDigests 0}}'
# RepoDigests shows the immutable sha256 reference of the pulled image
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml: per-service pull policy (Compose Specification, v2.x)
services:
  api:
    image: ghcr.io/acme/node-api:1.8.3     # immutable version tag, safest in production
    pull_policy: if_not_present            # reuse local copy if same tag exists (alias of missing)
    restart: unless-stopped                # restart after crash or reboot
    environment:
      NODE_ENV: production                 # production mode for Node.js
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]  # app health endpoint
      interval: 30s                        # probe every 30 seconds
      timeout: 3s                          # fail if slower than 3 seconds
      retries: 3                           # unhealthy after 3 failures

  web:
    image: ghcr.io/acme/react-nginx:staging   # mutable tag: needs always
    pull_policy: always                    # check registry on every compose up
    ports:
      - "80:80"                            # publish HTTP

  worker:
    build: ./worker                        # image built from local source
    image: acme/worker:dev                 # name given to the built image
    pull_policy: build                     # always rebuild instead of pulling

  cache:
    image: redis:7.4-alpine                # third-party image rarely changes
    pull_policy: weekly                    # re-check the registry at most once a week
```

```yaml
# k8s-deployment.yaml: Kubernetes imagePullPolicy with private registry
apiVersion: apps/v1                        # Deployment API group
kind: Deployment                           # workload type
metadata:
  name: node-api                           # deployment name
spec:
  replicas: 2                              # two pods for availability
  selector:
    matchLabels:
      app: node-api                        # which pods this deployment owns
  template:
    metadata:
      labels:
        app: node-api                      # pod label matched by selector
    spec:
      imagePullSecrets:
        - name: regcred                    # secret created with kubectl create secret docker-registry
      containers:
        - name: api                        # container name
          image: registry.example.com/node-api@sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef  # example digest, replace
          imagePullPolicy: IfNotPresent    # digest is immutable, so reuse is safe
          ports:
            - containerPort: 3000          # port the Node.js app listens on
```

All three YAML documents were parsed locally; none were applied to a cluster or Docker daemon. `pull_policy` values `daily` and `weekly` require a recent Compose v2 release (version-dependent, check `docker compose version`).

---

## 🟠 My Stack Integration
For your VPS deploy: CI tags images with the git SHA, pushes, then SSH runs `docker compose pull && docker compose up -d`. Because the tag changes every release, the policy hardly matters, which is the point of immutable tags. Use `always` only on environments that keep a moving tag (staging).

```yaml
# deploy step in GitHub Actions (excerpt)
- name: Deploy over SSH                              # step label
  uses: appleboy/ssh-action@v1.0.3                   # example third-party SSH action, pin and review it
  with:
    host: ${{ secrets.VPS_HOST }}                    # server address from secrets
    username: deploy                                 # non-root deploy user
    key: ${{ secrets.VPS_SSH_KEY }}                  # private key stored as secret
    script: |                                        # commands run on the VPS
      cd /srv/app                                    # project folder with compose file
      export IMAGE_TAG=${{ github.sha }}             # tag built by this run
      docker compose pull                            # fetch exact tag, no stale image
      docker compose up -d --remove-orphans          # recreate only changed services
      docker image prune -f                          # clean dangling layers
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deploying `app:latest` and trusting `docker compose up -d` to fetch the newest image.
✅ Correct: Use unique tags (version or SHA) and run `docker compose pull`, or set `pull_policy: always`.

❌ Mistake 2: Setting `imagePullPolicy: Never` on a Kubernetes cluster with several nodes.
✅ Correct: `Never` works only if the image was preloaded on every node (e.g. kind/minikube). Use `IfNotPresent` or `Always` with a registry.

❌ Mistake 3: Using `Always` for every service in production, so one Docker Hub outage blocks restarts.
✅ Correct: Pin versions or digests and use `IfNotPresent`; keep a mirror or private registry.

❌ Mistake 4: Forgetting `imagePullSecrets` for a private registry and getting `ImagePullBackOff`.
✅ Correct: Create the registry secret in the same namespace and reference it in the pod or service account.

---

## 🧠 Tricky Interview Question
A pod uses `image: myapp:v2` with `imagePullPolicy: IfNotPresent`. You rebuild and push a fixed `myapp:v2` (same tag). After `kubectl rollout restart`, some pods run the fix and some do not. Why?

Answer: With `IfNotPresent`, each node reuses its cached `myapp:v2`. Nodes that had never pulled `v2` (or that evicted the old layers) downloaded the new image; nodes that already cached the old one kept it. Mutable tags plus `IfNotPresent` give non-deterministic rollouts. Fix: never reuse a tag; release `v3` or reference the image by digest. `Always` would also work but still allows two different digests to run during a rolling update.

---

## ⚫ Interview Questions + Answers

Q1: What is the Kubernetes default pull policy?
A1: If the tag is `:latest` or missing, `Always`. If another tag or a digest, `IfNotPresent`. (Admission controller `AlwaysPullImages` can force `Always` cluster-wide.)

Q2: Does `Always` re-download the whole image every time?
A2: No. The runtime asks the registry for the manifest digest; if it equals the local one, no layers are downloaded. Only changed layers transfer.

Q3: Why is `AlwaysPullImages` a security feature in multi-tenant clusters?
A3: With `IfNotPresent`, a pod without credentials can use a private image just because another tenant already pulled it to the node. `Always` forces each pod to prove access to the registry.

Q4: What does Compose `pull_policy: build` do?
A4: Always builds the image from the `build:` section, never pulls it. Useful for locally built services.

Q5: How do you guarantee the exact image bytes?
A5: Reference by digest (`repo@sha256:...`). A digest cannot change, so the pull policy then has no effect on content.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `always`: mutable tags like `staging`, `latest` in test environments
- `missing` / `IfNotPresent`: immutable version tags in production
- `never`: air-gapped hosts or preloaded images in local clusters

❌ Avoid when:
- Using `always` on a high-churn cluster without a mirror (rate limits)
- Using `never` anywhere images are not preloaded
- Relying on any policy instead of fixing mutable tag practice

---

## 📊 Visual Diagram
```
 docker run / compose up / kubectl apply
                 │
         read pull policy
     ┌───────────┼─────────────┐
   always     missing /      never
     │        IfNotPresent     │
     ▼            │            ▼
 ask registry     ▼        local image?
 digest same?  local tag?    yes -> run
  │yes │no       │yes │no    no  -> ERROR
  ▼    ▼         ▼    ▼
 run  pull      run  pull -> run
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pull_policy | Compose key controlling pulls | Compose की pull नियंत्रण key |
| imagePullPolicy | Kubernetes container field | Kubernetes container का field |
| Mutable tag | Tag that can be repointed | बदला जा सकने वाला tag |
| Digest | sha256 content hash of an image | Image का sha256 hash |
| ImagePullBackOff | Pod cannot pull, retries with delay | Pull fail, delay के साथ retry |
| imagePullSecrets | Registry credentials for pods | Pods के लिए registry credentials |

---

## ⚡ 3-Line Summary
English: Pull policy decides if an image is downloaded again before a container starts. Use immutable tags or digests with `missing`/`IfNotPresent`, and `always` only for moving tags. Remember Kubernetes defaults: `:latest` means Always, other tags mean IfNotPresent.
Hindi: Pull policy तय करती है कि container शुरू होने से पहले image दोबारा download होगी या नहीं। Immutable tags या digests के साथ `missing`/`IfNotPresent` रखो, और `always` सिर्फ़ बदलने वाले tags के लिए। Kubernetes defaults याद रखो: `:latest` यानी Always, बाकी tags यानी IfNotPresent।

---

## ➡️ Next Topic
**131. Container Lifecycle**: with images covered, the next step is what happens after the pull: create, start, pause, stop and remove.

---
