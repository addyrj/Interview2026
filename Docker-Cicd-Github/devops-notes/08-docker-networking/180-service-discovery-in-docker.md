# 180. Service Discovery in Docker
# हिंदी में: Docker में Service Discovery

---

## 🔵 Simple Definition (English)
**Service discovery** is how one container finds another without knowing its IP. On user-defined networks Docker runs an embedded DNS server (127.0.0.11) that resolves container names, Compose service names and network aliases to the current container IPs.

## 🔵 सरल परिभाषा (Hindi)
**Service discovery** वो तरीका है जिससे एक container दूसरे को उसकी IP जाने बिना ढूँढता है। User-defined networks पर Docker एक embedded DNS server (127.0.0.11) चलाता है जो container names, Compose service names और network aliases को मौजूदा container IPs में resolve करता है।

---

## 🔴 Problem it Solves
Container IPs are dynamic: they change on every restart or redeploy. Hard-coding `172.18.0.5` in `.env` breaks the app each time. In scaled setups there may be several containers behind one service name and the list changes continuously. Service discovery gives stable names and (for Swarm/Compose scale) basic round-robin load balancing.

## 🔴 यह क्यों बना? (Hindi)
Container IPs dynamic होती हैं: हर restart या redeploy पर बदल जाती हैं। `.env` में `172.18.0.5` hard-code करो तो हर बार app टूटेगा। Scaled setups में एक service नाम के पीछे कई containers हो सकते हैं और list लगातार बदलती है। Service discovery stable names और (Swarm/Compose scale में) basic round-robin load balancing देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Compose creates a user-defined network and starts services api, db
Step 2 → Each container's /etc/resolv.conf points to the embedded DNS 127.0.0.11
Step 3 → api runs getaddrinfo("db") -> request goes to Docker's DNS
Step 4 → Docker DNS looks up "db" in the networks api shares with db
Step 5 → It answers with the db container's CURRENT IP (A record)
Step 6 → If db is scaled to 3, DNS returns all 3 IPs (round-robin DNS)
Step 7 → Unknown names are forwarded to the host's upstream DNS (e.g. google.com)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Compose user-defined network बनाता है और services api, db चालू करता है
Step 2 → हर container की /etc/resolv.conf embedded DNS 127.0.0.11 की ओर इशारा करती है
Step 3 → api getaddrinfo("db") चलाता है -> request Docker के DNS को जाती है
Step 4 → Docker DNS उन networks में "db" ढूँढता है जो api और db दोनों में हैं
Step 5 → वह db container की मौजूदा IP (A record) लौटाता है
Step 6 → db को 3 scale करो तो DNS तीनों IPs लौटाता है (round-robin DNS)
Step 7 → अनजाने नाम host के upstream DNS को forward होते हैं (जैसे google.com)
```

---

## 🟡 Real World Example
A SaaS runs three replicas of its Node.js API with `docker compose up --scale api=3`. Nginx uses `proxy_pass http://api:3000;`. When a replica is replaced during a rolling restart, its IP changes, but nobody edits any config. The catch: Nginx resolves `api` once at startup and caches the IPs; the team adds `resolver 127.0.0.11 valid=10s;` plus a variable in `proxy_pass` so nginx re-resolves, and replacement replicas receive traffic automatically.

## 🟡 Real Example Hindi mein
एक SaaS अपने Node.js API की तीन replicas `docker compose up --scale api=3` से चलाता है। Nginx `proxy_pass http://api:3000;` use करता है। Rolling restart में replica बदलने पर IP बदल जाती है, पर कोई config edit नहीं करता। पेच: Nginx `api` को startup पर एक बार resolve करके IPs cache कर लेता है; टीम ने `resolver 127.0.0.11 valid=10s;` और `proxy_pass` में variable जोड़ा ताकि nginx दोबारा resolve करे और नई replicas को traffic अपने-आप मिले।

---

## 💻 Code / Config Example — Basic
```yaml
# docker-compose.yml - service discovery by name
services:
  api:
    image: myorg/api:1.4.2                   # example tag
    environment:
      DB_HOST: db                            # use the SERVICE NAME as hostname
      DB_PORT: "5432"                        # container port (not a published host port)
    depends_on:
      - db                                   # start db first (does not wait for readiness)
  db:
    image: postgres:16-alpine                # example tag
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}      # from .env
```

```bash
docker compose up -d                                   # start the stack
docker compose exec api getent hosts db                # shows: 172.x.x.x  db
docker compose exec api cat /etc/resolv.conf           # shows: nameserver 127.0.0.11
docker compose up -d --scale api=3                     # three replicas share one DNS name
docker compose exec db getent hosts api                # returns multiple IPs (round robin)
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - aliases + replicas + nginx re-resolving
services:
  nginx:
    image: nginx:1.27-alpine                 # example tag
    ports: ["80:80"]                         # public entry point
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro   # config below
    networks: [edge]                         # shares network with api
    depends_on: [api]                        # start after api containers exist
  api:
    image: myorg/api:1.4.2
    deploy:
      replicas: 3                            # honoured by recent Compose versions (docker compose up)
    networks:
      edge:
        aliases:
          - backend.internal                 # extra DNS name usable by nginx
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]  # busybox wget in alpine image
      interval: 10s                          # probe every 10 seconds
      timeout: 3s                            # fail if no answer in 3 seconds
      retries: 3                             # unhealthy after 3 failures
networks:
  edge: {}                                   # shared user-defined bridge
```

```nginx
# nginx.conf - re-resolve Docker DNS so replaced replicas get traffic
server {
  listen 80;                                        # public HTTP
  resolver 127.0.0.11 valid=10s ipv6=off;           # use Docker's DNS, cache 10 seconds
  location / {
    set $upstream http://api:3000;                  # variable forces runtime DNS lookup
    proxy_pass $upstream;                           # without variable, nginx resolves ONLY at startup
    proxy_set_header Host $host;                    # preserve host header
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  # client IP chain
  }
}
```
(nginx config not tested with `nginx -t` on this machine; verify in your environment.)

---

## 🟠 My Stack Integration
- **Node.js:** `mongoose.connect('mongodb://mongo:27017/app')`. Driver reconnects and re-resolves on failure, so restarts heal automatically.
- **FastAPI:** `DATABASE_URL=postgresql://app:pw@db:5432/app`; SQLAlchemy pool recycles connections (`pool_pre_ping=True`) so stale IPs are dropped.
- **React:** discovery is for server-side only; the browser must hit a public URL (`/api` through Nginx).
- **Nginx:** use the resolver trick above for scaled upstreams, or define `upstream` with a service that has a fixed IP.
- **VPS/AWS:** Docker DNS works on a single host. Across multiple EC2 hosts use AWS Cloud Map, ECS Service Connect, Kubernetes DNS or Consul.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `localhost` or a published host port (`db:5433`) inside the network.
✅ Correct: Use `service-name:container-port`, e.g. `db:5432`.

❌ Mistake 2: Expecting service names to resolve on the default bridge.
✅ Correct: Use a user-defined network (Compose does it for you).

❌ Mistake 3: Nginx caching old IPs and returning 502 after the upstream restarts.
✅ Correct: Use `resolver 127.0.0.11` with a variable in `proxy_pass`, or restart nginx after deploys.

❌ Mistake 4: Assuming `depends_on` waits until the service is ready.
✅ Correct: Combine with healthchecks and `condition: service_healthy` (see 191 and 192).

❌ Mistake 5: Using container names across different Compose projects without a shared network.
✅ Correct: Create an external network and attach both projects.

---

## 🧠 Tricky Interview Question
**Q:** After `docker compose up --scale api=3`, `curl api:3000` from a worker container always seems to hit the same replica. Is Docker DNS round-robin broken?

**Answer:** Not broken: DNS returns all three IPs, but many clients (and libc resolvers) pick the first address and reuse a keep-alive connection, or cache the answer. Round-robin DNS is a coarse load-balancing method, not a real load balancer. For fair balancing use Nginx/HAProxy/Traefik with health checks, or a client library with its own balancing. In Swarm, VIP-based routing gives real balancing per connection.

---

## ⚫ Interview Questions + Answers

Q1: What is Docker's embedded DNS address?
A1: 127.0.0.11 inside containers on user-defined networks.

Q2: What names resolve?
A2: Container names, Compose service names, and network aliases within a shared network.

Q3: Why doesn't service-name DNS work on the default bridge?
A3: The default bridge uses legacy linking and has no embedded DNS for names.

Q4: How can several containers share one name?
A4: Give them the same network alias or scale one service; DNS returns multiple A records.

Q5: What replaces this in Kubernetes?
A5: CoreDNS with Service objects (`svc.namespace.svc.cluster.local`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single-host multi-container apps
- You want zero hard-coded IPs
- Local development and small production setups

❌ Avoid when:
- Multi-host fleets needing health-aware discovery (use Consul, Cloud Map, Kubernetes)
- Real load balancing with sticky sessions is needed

---

## 📊 Visual Diagram
```
  [api container]
     | 1. lookup "db"
     v
  127.0.0.11  (Docker embedded DNS)
     | 2. checks shared networks
     v
  +------------------------+
  | name table (live)      |
  | db      -> 172.20.0.3  |
  | api     -> 172.20.0.2, .4, .5  (scaled x3)
  | backend.internal -> api|
  +------------------------+
     | 3. answers IP(s)
     v
  [api] connects to 172.20.0.3:5432
  (db restarts -> new IP -> DNS table updates automatically)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Service discovery | Finding services by name | नाम से service ढूँढना |
| Embedded DNS | Docker's built-in resolver | built-in DNS |
| A record | DNS name to IPv4 mapping | नाम से IP का मैप |
| Alias | Extra name for a container | अतिरिक्त नाम |
| Round-robin DNS | Rotate through multiple IPs | बारी-बारी IP देना |
| Resolver (nginx) | Directive to set DNS server | nginx का DNS server |

---

## ⚡ 3-Line Summary
English: Docker's embedded DNS resolves service names to current container IPs on user-defined networks.
Always use names and container ports, never IPs or localhost.
Fix nginx caching with `resolver 127.0.0.11` and a variable.
Hindi: Docker का embedded DNS user-defined networks पर service names को मौजूदा IPs में बदलता है।
हमेशा नाम और container port use करो, IP या localhost नहीं।
nginx caching को `resolver 127.0.0.11` और variable से ठीक करो।

---

## ➡️ Next Topic
**181. Docker Compose — Complete Guide** - tie networking, volumes and services together in one file.
