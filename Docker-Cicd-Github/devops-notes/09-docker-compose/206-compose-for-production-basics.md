# 206. Compose for Production (basics)
# हिंदी में: Production के लिए Compose (बुनियादी बातें)

---

## 🔵 Simple Definition (English)
Compose in production means running your stack on a single server (VPS or EC2) with pinned images, restart policies, healthchecks, resource limits, log rotation, secrets and only the necessary ports open. It suits small and medium apps; it is not a multi-node orchestrator.

## 🔵 सरल परिभाषा (Hindi)
Production में Compose का मतलब है अपना stack एक server (VPS या EC2) पर pinned images, restart policies, healthchecks, resource limits, log rotation, secrets और सिर्फ ज़रूरी खुले ports के साथ चलाना। यह छोटी और मध्यम apps के लिए ठीक है; यह multi-node orchestrator नहीं है।

---

## 🔴 Problem it Solves
A dev compose file in production is dangerous: `latest` tags change under you, source bind mounts expose the host, DB ports are open to the internet, logs fill the disk, and there is no recovery after a crash. A production profile of Compose closes those holes while keeping the simple workflow.

## 🔴 यह क्यों बना? (Hindi)
Production में dev compose file ख़तरनाक है: `latest` tags अपने-आप बदल जाते हैं, source bind mounts host को खोल देते हैं, DB ports internet पर खुले रहते हैं, logs disk भर देते हैं और crash के बाद recovery नहीं होती। Compose का production रूप इन छेदों को बंद करता है और workflow आसान रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CI builds the image, tags it with the git SHA, pushes to a registry (GHCR / ECR)
Step 2 → On the server, compose.prod.yaml references that exact tag via ${TAG}
Step 3 → Secrets live in files / .env.prod with chmod 600, not in git
Step 4 → `docker compose pull` fetches images; `up -d` recreates only changed services
Step 5 → Healthchecks + restart policies keep services alive
Step 6 → Nginx (container or host) terminates TLS and proxies to the API; only 80/443 are public
Step 7 → Rollback = set TAG to the previous SHA and run `up -d` again
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → CI image build करता है, git SHA से tag लगाता है, registry (GHCR / ECR) में push करता है
Step 2 → Server पर compose.prod.yaml ${TAG} से ठीक वही tag इस्तेमाल करती है
Step 3 → Secrets files / .env.prod में chmod 600 के साथ, git में नहीं
Step 4 → `docker compose pull` images लाता है; `up -d` सिर्फ बदली services दोबारा बनाता है
Step 5 → Healthchecks + restart policies services को ज़िंदा रखते हैं
Step 6 → Nginx (container या host) TLS संभालता है और API को proxy करता है; सिर्फ 80/443 public हैं
Step 7 → Rollback = TAG को पिछले SHA पर रखकर फिर `up -d`
```

---

## 🟡 Real World Example
A small SaaS (Node API + React + Postgres) serves 5,000 daily users from one t3.medium EC2 instance. GitHub Actions builds `ghcr.io/acme/api:<sha>`, SSHes into EC2 and runs the deploy script. A bad release is rolled back in 30 seconds by re-deploying the previous SHA. When traffic outgrows one box, the team moves to ECS or Kubernetes, but the images stay the same.

## 🟡 Real Example Hindi mein
एक छोटा SaaS (Node API + React + Postgres) एक t3.medium EC2 instance से रोज़ 5,000 users को serve करता है। GitHub Actions `ghcr.io/acme/api:<sha>` बनाता है, EC2 में SSH करके deploy script चलाता है। खराब release 30 सेकंड में पिछला SHA दोबारा deploy करके rollback हो जाता है। Traffic एक box से ज़्यादा हो तो team ECS या Kubernetes पर जाती है, पर images वही रहती हैं।

---

## 💻 Code / Config Example — Basic
```yaml
# compose.prod.yaml  (Basic production)
services:
  api:
    image: ghcr.io/acme/api:${TAG}        # pinned image built by CI (never :latest)
    restart: unless-stopped               # recover from crash and reboot
    env_file: .env.prod                   # secrets on the server only
    ports:
      - "127.0.0.1:3000:3000"             # reachable only by host Nginx
```

## 💻 Code / Config Example — Advanced
```yaml
# compose.prod.yaml  (Advanced production for one VPS)
name: myapp                               # stable project name
services:
  nginx:
    image: nginx:1.27-alpine              # example tag
    restart: unless-stopped
    ports:
      - "80:80"                           # HTTP (redirect to HTTPS)
      - "443:443"                         # HTTPS
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro  # config read-only
      - /etc/letsencrypt:/etc/letsencrypt:ro                    # certs from certbot on host
    depends_on:
      api: { condition: service_healthy } # start proxy after API is healthy
    networks: [public, internal]          # talks to outside and to api
    read_only: true                       # immutable filesystem
    tmpfs: ["/var/cache/nginx", "/var/run", "/tmp"]  # nginx needs these writable
    security_opt: ["no-new-privileges:true"]         # block privilege escalation
    deploy:
      resources: { limits: { cpus: "0.25", memory: 128M } }

  api:
    image: ghcr.io/acme/api:${TAG:?TAG is required}   # fail if TAG missing
    restart: unless-stopped
    env_file: .env.prod                   # NODE_ENV=production etc.
    user: "node"                          # non-root (image should also set USER)
    read_only: true
    tmpfs: ["/tmp"]
    cap_drop: ["ALL"]                     # drop all Linux capabilities
    security_opt: ["no-new-privileges:true"]
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://localhost:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]  # Node 18+ fetch
      interval: 15s
      timeout: 3s
      retries: 3
      start_period: 20s                   # grace time at boot
    networks: [internal]                  # NOT reachable from the internet directly
    deploy:
      resources: { limits: { cpus: "1.00", memory: 512M } }
    logging:
      driver: json-file
      options: { max-size: "10m", max-file: "5" }     # avoid filling disk

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: app
      POSTGRES_DB: app
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass    # secret as file
    secrets: [db_pass]
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks: [internal]                  # no published ports at all
    deploy:
      resources: { limits: { cpus: "1.00", memory: 1G } }

networks:
  public: {}                              # default bridge for outside traffic
  internal:
    internal: true                        # no outbound internet for these containers (remove if the API must call external APIs)

secrets:
  db_pass:
    file: ./secrets/db_pass.txt           # chmod 600, not in git

volumes:
  pgdata: {}
```
Note: with `internal: true` the API cannot reach the internet and Nginx must also be on `internal` to reach it (done above). If your API calls third parties, put it on a second normal network too.

```bash
# deploy.sh  (run on the server)
set -euo pipefail                                       # strict mode
export TAG="$1"                                         # image tag passed as argument
docker compose -f compose.prod.yaml pull                # download images
docker compose -f compose.prod.yaml up -d --remove-orphans   # apply changes
docker image prune -f                                   # delete dangling images
```

---

## 🟠 My Stack Integration
- **Node.js/FastAPI:** build in CI, push to GHCR/ECR, run by SHA tag. FastAPI healthcheck: `python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/health')"`.
- **React:** compile to static files in a build stage and serve via Nginx image; no Node at runtime.
- **Nginx + certbot:** host-level certbot renews certificates; mount read-only.
- **VPS/AWS:** security group allows only 22 (your IP), 80, 443. Back up `pgdata` to S3; or move to RDS.
- **Security:** non-root, read-only filesystem, dropped capabilities, no-new-privileges, secrets as files, no DB ports.

```yaml
# snippet: FastAPI service in production
  ml:
    image: ghcr.io/acme/ml:${TAG}           # pinned image
    restart: unless-stopped
    command: ["gunicorn","-k","uvicorn.workers.UvicornWorker","-w","2","-b","0.0.0.0:8000","main:app"]  # 2 workers
    networks: [internal]                    # only Nginx reaches it
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `:latest`. A redeploy silently changes versions; rollback is impossible.
✅ Correct: Tag by git SHA or semver.

❌ Mistake 2: Publishing `5432:5432` to the world. Bots find open Postgres within hours.
✅ Correct: No `ports` for the DB; use an internal network.

❌ Mistake 3: No log rotation. `json-file` logs grow until the disk is full.
✅ Correct: `max-size` and `max-file`.

❌ Mistake 4: Building images on the production server.
✅ Correct: Build in CI, pull in prod.

---

## 🧠 Tricky Interview Question
You run `docker compose up -d` on the server after pushing a new image under the same tag. Containers do not change. Why?

Answer: Compose compares the service config, not the remote image content. The tag is the same, and without `pull` the local cached image is reused. Run `docker compose pull` first (or `up -d --pull always`). Better still, use a unique tag per build so config changes and the container is recreated.

---

## ⚫ Interview Questions + Answers

Q1: Is Compose production-ready?
A1: For single-host deployments, yes, if hardened. It lacks multi-node scheduling, auto-scaling and rolling updates with health gates.

Q2: How do you do zero-downtime deploy with Compose?
A2: Not natively. Options: run two copies behind Nginx and switch (blue/green), use `docker rollout` plugin, or move to ECS/Kubernetes.

Q3: Where do secrets go?
A3: Files via Compose `secrets` or a manager (AWS Secrets Manager); not committed `.env`.

Q4: How do you roll back?
A4: Run the deploy with the previous tag; keep the last N images.

Q5: How are logs handled?
A5: Rotate with the logging driver; ship to CloudWatch/Loki for search.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- One server, small to medium traffic, small team.
- You want simple, readable deployments.

❌ Avoid when:
- You need high availability across nodes, autoscaling or strict zero-downtime SLAs.
- Compliance needs orchestrator-level policies.

---

## 📊 Visual Diagram
```
 Internet --443--> [ Nginx ] --internal net--> [ API ] --> [ Postgres ]
                      |                           |            |
                  TLS certs (ro)            healthcheck     volume pgdata
 CI --push--> Registry --pull--> Server: compose.prod.yaml (TAG=<sha>)
 Rollback: TAG=<previous sha> ; up -d
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pinned tag | Fixed image version | निश्चित image version |
| rollback | Return to previous release | पिछले release पर लौटना |
| read_only | Immutable root filesystem | बदला न जा सकने वाला filesystem |
| cap_drop | Remove Linux privileges | Linux अधिकार हटाना |
| internal network | Network without outside access | बाहरी पहुँच रहित network |
| log rotation | Limit log size/files | log का आकार सीमित करना |

---

## ⚡ 3-Line Summary
English: Production Compose = pinned images from CI, restart + healthchecks + limits, rotated logs, secrets as files, internal networks, only 80/443 public. Build in CI, pull on the server, rollback by tag.
Hindi: Production Compose = CI से pinned images, restart + healthchecks + limits, rotated logs, files में secrets, internal networks, सिर्फ 80/443 public। CI में build, server पर pull, tag से rollback।

---

## ➡️ Next Topic
**207. Node.js + PostgreSQL + Redis Compose Example**: a complete working stack built from these pieces.
