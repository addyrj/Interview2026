# 224. Docker Swarm Basics
# हिंदी में: Docker Swarm की बुनियादी बातें

---

## 🔵 Simple Definition (English)
**Docker Swarm** (swarm mode) is Docker's built-in orchestrator. You join several Docker hosts into one cluster of **manager** and **worker** nodes, then deploy **services** (a image + replicas + ports). Swarm schedules tasks (containers), load-balances traffic with a routing mesh, restarts failures, and does rolling updates. Commands are plain `docker` commands.

## 🔵 सरल परिभाषा (Hindi)
**Docker Swarm** (swarm mode) Docker का built-in orchestrator है। आप कई Docker hosts को **manager** और **worker** nodes वाले एक cluster में जोड़ते हो, फिर **services** (image + replicas + ports) deploy करते हो। Swarm tasks (containers) schedule करता है, routing mesh से traffic load-balance करता है, failures restart करता है और rolling updates करता है। Commands सामान्य `docker` commands ही हैं।

---

## 🔴 Problem it Solves
You outgrew a single VPS with Compose: you want 2-3 servers, automatic failover and rolling deploys, but Kubernetes feels like too much (control plane, YAML sprawl, networking plugins, steep learning curve). Swarm gives the core orchestration features with almost no extra setup: `docker swarm init`, `docker stack deploy`, and you reuse your Compose file.

## 🔴 यह क्यों बना? (Hindi)
आपका एक VPS + Compose छोटा पड़ गया: आपको 2-3 servers, automatic failover और rolling deploys चाहिए, लेकिन Kubernetes बहुत भारी लगता है (control plane, ढेर सारा YAML, networking plugins, ऊँची learning curve)। Swarm लगभग बिना extra setup के core orchestration features देता है: `docker swarm init`, `docker stack deploy`, और आप अपनी Compose file ही दोबारा इस्तेमाल करते हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → On server 1: `docker swarm init --advertise-addr <IP>` -> it becomes a manager (Raft leader).
Step 2 → It prints a join token. On servers 2 and 3: `docker swarm join --token ... <IP>:2377`.
Step 3 → Create/describe a stack in docker-compose.yml with a `deploy:` section (replicas, update_config...).
Step 4 → `docker stack deploy -c docker-compose.yml myapp` -> managers store desired state (Raft log).
Step 5 → Scheduler spreads TASKS (containers) across nodes; each service gets a virtual IP + DNS name.
Step 6 → Ingress routing mesh: any node's published port forwards to a healthy task anywhere.
Step 7 → Node fails -> tasks are rescheduled; `docker service update --image ...` does a rolling update.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Server 1 पर: `docker swarm init --advertise-addr <IP>` -> यह manager (Raft leader) बन जाता है।
Step 2 → यह join token देता है। Server 2 और 3 पर: `docker swarm join --token ... <IP>:2377`।
Step 3 → docker-compose.yml में `deploy:` section (replicas, update_config...) के साथ stack लिखो।
Step 4 → `docker stack deploy -c docker-compose.yml myapp` -> managers desired state (Raft log) सहेजते हैं।
Step 5 → Scheduler TASKS (containers) को nodes में बाँटता है; हर service को virtual IP + DNS नाम मिलता है।
Step 6 → Ingress routing mesh: किसी भी node का published port किसी भी जगह के healthy task तक पहुँचाता है।
Step 7 → Node fail -> tasks दोबारा schedule; `docker service update --image ...` से rolling update।
```

Key objects: **Node** (a Docker host), **Service** (desired state), **Task** (one container of a service), **Stack** (group of services from one Compose file), **Overlay network** (multi-host network), **Secret/Config** (encrypted data distributed to tasks).

---

## 🟡 Real World Example
A small Indian e-learning startup runs 3 cheap VPS (Hetzner / DigitalOcean / AWS EC2). One is a manager, two are workers. Services: `web` (Nginx + React), `api` (Node.js, 3 replicas), `ml` (FastAPI, 2 replicas). When a worker VPS is rebooted for kernel patching, Swarm moves its tasks to the other nodes in seconds and students notice nothing. Releases are `docker service update` rolling one replica at a time.

## 🟡 Real Example Hindi mein
एक छोटा Indian e-learning startup 3 सस्ते VPS (Hetzner / DigitalOcean / AWS EC2) चलाता है। एक manager है, दो workers। Services: `web` (Nginx + React), `api` (Node.js, 3 replicas), `ml` (FastAPI, 2 replicas)। Kernel patching के लिए जब कोई worker VPS reboot होता है, Swarm उसके tasks कुछ सेकंड में बाकी nodes पर ले जाता है और students को पता भी नहीं चलता। Release में `docker service update` एक-एक replica बदलता है।

---

## 💻 Code / Config Example — Basic

```bash
# --- On the FIRST server (becomes manager) ---
docker swarm init --advertise-addr 10.0.0.10   # create the swarm; use the PRIVATE IP of this host
# Output prints: docker swarm join --token SWMTKN-1-xxxx 10.0.0.10:2377

# --- On the OTHER servers (workers) ---
docker swarm join --token SWMTKN-1-xxxx 10.0.0.10:2377  # token copied from the init output

# --- Back on the manager ---
docker node ls                                  # list nodes and their status (Ready / Active / Leader)

# Create a simple service with 3 replicas and a published port
docker service create \
  --name web \
  --replicas 3 \
  --publish published=8080,target=80 \
  nginx:1.27-alpine
# --name: service name (also DNS name)  --replicas: desired copies
# --publish: routing mesh, port 8080 on EVERY node -> container port 80

docker service ls                               # services and replica counts (3/3)
docker service ps web                           # which node runs each task
docker service scale web=5                      # scale up to 5 replicas
docker service rm web                           # remove the service
```

(Commands are standard Swarm CLI; not executed on this machine because no Docker daemon is available.)

## 💻 Code / Config Example — Advanced

```yaml
# stack.yml (production-style): deploy with `docker stack deploy -c stack.yml myapp`
# Compose file format; `deploy:` is honoured only in Swarm (docker stack deploy)
services:
  api:
    image: registry.example.com/myorg/api:1.5.0   # pinned image from your private registry (example)
    networks:
      - backend                       # overlay network shared with other services
    secrets:
      - db_password                   # encrypted secret, mounted at /run/secrets/db_password
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password   # app reads password from file, not env
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]  # swarm waits for healthy tasks
      interval: 10s                   # probe interval
      timeout: 3s                     # probe timeout
      retries: 3                      # failures before unhealthy
    stop_grace_period: 30s            # time to finish requests on SIGTERM
    deploy:
      replicas: 3                     # desired number of tasks
      update_config:
        parallelism: 1                # update one task at a time
        delay: 10s                    # wait 10s between tasks
        order: start-first            # start new task before stopping old (zero downtime)
        failure_action: rollback      # auto-rollback if new tasks fail
      rollback_config:
        parallelism: 1                # rollback one at a time
      restart_policy:
        condition: on-failure         # restart only on failure
        max_attempts: 3               # give up after 3 attempts
      resources:
        limits:
          cpus: "0.50"                # max half a CPU
          memory: 512M                # max 512 MB RAM
      placement:
        constraints:
          - node.role == worker       # run only on worker nodes
  nginx:
    image: nginx:1.27-alpine          # reverse proxy
    ports:
      - target: 80                    # container port
        published: 80                 # host port on every node (routing mesh)
        mode: ingress                 # load-balanced across nodes
    networks:
      - backend                       # reach api by name `api`
    deploy:
      replicas: 2                     # two proxies
networks:
  backend:
    driver: overlay                   # multi-host network
secrets:
  db_password:
    external: true                    # created beforehand: printf 'S3cret' | docker secret create db_password -
```

```bash
# Deploy and operate the stack (run on a manager node)
printf 'S3cretPassw0rd' | docker secret create db_password -   # create the secret from stdin (not stored in shell history file if you type interactively)
docker stack deploy -c stack.yml myapp       # create / update all services
docker stack services myapp                  # status of services
docker service logs -f myapp_api             # follow logs of the api service
docker service update --image registry.example.com/myorg/api:1.5.1 myapp_api  # rolling update
docker service rollback myapp_api            # manual rollback to previous spec
```

---

## 🟠 My Stack Integration
- **Node.js + FastAPI:** each becomes a Swarm service; use service names (`api`, `fastapi`) in Nginx `proxy_pass http://api:3000;` - Swarm DNS returns the virtual IP and balances tasks.
- **React:** build static files in CI, bake into an Nginx image, run as a 2-replica service.
- **Nginx:** published on 80/443 with the routing mesh; any node's public IP works, put a cloud load balancer or DNS round-robin in front.
- **VPS:** open only the Swarm ports between nodes (private network/firewall): TCP 2377 (cluster management), TCP/UDP 7946 (node gossip), UDP 4789 (overlay VXLAN). Never open these to the internet.
- **AWS:** EC2 instances in one VPC, security group allowing those ports within the group; use ALB in front for TLS.

```yaml
# Minimal stack for your stack: nginx + node api + fastapi
services:
  nginx:
    image: nginx:1.27-alpine          # entry point
    ports:
      - "80:80"                       # public HTTP
    deploy:
      replicas: 2                     # HA proxy
  api:
    image: myorg/node-api:1.0.0       # Node.js API (example)
    deploy:
      replicas: 3                     # three copies
  fastapi:
    image: myorg/fastapi:1.0.0        # FastAPI service (example)
    deploy:
      replicas: 2                     # two copies
```

**Security aspects:** Swarm encrypts the control plane (mTLS between nodes) and supports `--opt encrypted` for overlay data traffic. Rotate join tokens (`docker swarm join-token --rotate worker`). Use secrets instead of env vars. Use an odd number of managers (3 or 5) for Raft quorum, keep managers off public traffic, and enable autolock (`docker swarm init --autolock`) to protect the Raft keys at rest.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Only one manager node, so losing it loses control of the cluster.
✅ Correct: 3 managers (tolerates 1 failure) or 5 (tolerates 2); never an even number.

❌ Mistake 2: Using `build:` in a stack file and expecting `docker stack deploy` to build images.
✅ Correct: Build and push to a registry in CI, reference `image:` only.

❌ Mistake 3: Opening 2377/7946/4789 to the internet.
✅ Correct: Restrict to private network / security group of the nodes.

❌ Mistake 4: Stateful database with a local volume on a replicated service; the task moves and data is gone.
✅ Correct: Pin with placement constraints, use a managed DB, or a volume driver with shared storage.

---

## 🧠 Tricky Interview Question
**Q:** You published port 80 for service `web` which has 2 replicas running only on node A and B. A request hits node C's public IP. Does it work?

**Answer:** Yes. The **ingress routing mesh** listens on the published port on every node in the swarm. Node C forwards the request (IPVS) to a healthy task on A or B over the overlay network. Use `mode: host` publishing if you want the port only on nodes that run the task (and then you lose mesh balancing and must handle client IP preservation differently).

---

## ⚫ Interview Questions + Answers

Q1: Difference between a service, a task and a stack?
A1: A service is the desired state of one image with replicas; a task is one running container (plus its scheduling slot) of that service; a stack is a group of services deployed from one Compose file.

Q2: How does Swarm keep manager state consistent?
A2: Managers use the Raft consensus algorithm; the leader writes changes, a majority (quorum) must agree. With N managers you tolerate (N-1)/2 failures, so use 3 or 5.

Q3: What are Swarm's rolling update options?
A3: `update_config`: `parallelism`, `delay`, `order` (start-first / stop-first), `failure_action` (pause / continue / rollback), `monitor`, `max_failure_ratio`.

Q4: How do you manage secrets in Swarm?
A4: `docker secret create`, referenced in the service's `secrets:`. They are encrypted in the Raft log and mounted as in-memory files at `/run/secrets/<name>` only on nodes running that service.

Q5: What is the routing mesh?
A5: Ingress load balancing: published ports are open on all nodes and traffic is forwarded to any healthy task, regardless of which node it is on.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Small teams, 2-10 nodes, you already use Compose and want HA + rolling updates cheaply.
- Simple self-hosted deployments on VPS or EC2.

❌ Avoid when:
- You need advanced autoscaling, CRDs, service mesh, large ecosystem, managed cloud offering (Kubernetes/EKS wins).
- You need long-term vendor/community momentum: Swarm is maintained but Kubernetes dominates industry adoption.

---

## 📊 Visual Diagram
```
              docker stack deploy -c stack.yml myapp
                              |
                              v
        +------------------ MANAGERS (Raft quorum) ------------------+
        |   Manager 1 (Leader)   Manager 2        Manager 3          |
        +------------------------------+-----------------------------+
                                       | schedules tasks
              +------------------------+------------------------+
              v                        v                        v
        +-----------+            +-----------+            +-----------+
        | Worker A  |            | Worker B  |            | Worker C  |
        | api.1     |            | api.2     |            | api.3     |
        | nginx.1   |            | fastapi.1 |            | nginx.2   |
        +-----------+            +-----------+            +-----------+
   ingress routing mesh: :80 on ANY node -> healthy nginx task
   overlay network "backend": api <-> fastapi by service name
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Swarm | Docker's native clustering | Docker की native clustering |
| Manager | Node that holds cluster state | cluster की state रखने वाला node |
| Worker | Node that runs tasks | tasks चलाने वाला node |
| Service | Desired state for an image | image की desired state |
| Task | One container of a service | Service का एक container |
| Stack | Services from one Compose file | एक Compose file की services |
| Routing mesh | Ingress load balancing on all nodes | सभी nodes पर ingress load balancing |
| Raft | Consensus algorithm for managers | Managers की सहमति का algorithm |

---

## ⚡ 3-Line Summary
English: Swarm turns several Docker hosts into one cluster with `docker swarm init` and `join`.
English: You deploy stacks (Compose + `deploy:`) and Swarm handles scheduling, healing, routing mesh and rolling updates.
English: Easy and light, ideal for small clusters; use 3 managers, private ports and secrets.

Hindi: Swarm `docker swarm init` और `join` से कई Docker hosts को एक cluster बना देता है।
Hindi: आप stacks (Compose + `deploy:`) deploy करते हो और Swarm scheduling, healing, routing mesh व rolling updates संभालता है।
Hindi: आसान और हल्का, छोटे clusters के लिए बढ़िया; 3 managers, private ports और secrets रखो।

---

## ➡️ Next Topic
**225. Docker Swarm vs Kubernetes** - now that you know Swarm, compare it honestly with Kubernetes to decide which to learn and use.
