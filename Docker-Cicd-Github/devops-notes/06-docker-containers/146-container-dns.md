---

# 146. Container DNS
# हिंदी में: Container DNS (नाम से Container ढूँढना)

---

## 🔵 Simple Definition (English)
Container DNS is how a container turns a **name** (like `db` or `api.example.com`) into an **IP address**. On user-defined networks Docker runs an **embedded DNS server at 127.0.0.11** that answers for container and service names, and forwards all other names to the host's upstream DNS.

## 🔵 सरल परिभाषा (Hindi)
Container DNS वह तरीका है जिससे container किसी **नाम** (जैसे `db` या `api.example.com`) को **IP address** में बदलता है। User-defined networks पर Docker **127.0.0.11 पर एक embedded DNS server** चलाता है जो container और service नामों का जवाब देता है और बाकी नाम host के upstream DNS को भेज देता है।

---

## 🔴 Problem it Solves
Container IPs change at every restart or redeploy. Hardcoding `172.18.0.3` in a connection string breaks the next time the DB container is recreated. Docker DNS lets you write `postgres://db:5432` and always reach the right container, and also lets several replicas share one name (round-robin).

## 🔴 यह क्यों बना? (Hindi)
Container के IP हर restart या redeploy पर बदलते हैं। Connection string में `172.18.0.3` लिख देने से अगली बार DB container दोबारा बनने पर सब टूट जाएगा। Docker DNS से आप `postgres://db:5432` लिखते हैं और हमेशा सही container मिलता है; साथ ही कई replicas एक नाम share कर सकते हैं (round-robin)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → App calls getaddrinfo("db")
Step 2 → Container /etc/resolv.conf says: nameserver 127.0.0.11
Step 3 → Docker's embedded DNS (inside daemon) receives the query
Step 4 → Name matches a container/service/alias on the SAME network? -> answer IP
Step 5 → No match (e.g. google.com) -> forward to host DNS (from host resolv.conf / --dns)
Step 6 → Answer returned; app connects to the IP
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → App `getaddrinfo("db")` call करता है।
Step 2 → Container की `/etc/resolv.conf` में लिखा है: `nameserver 127.0.0.11`।
Step 3 → Docker का embedded DNS (daemon के अंदर) query लेता है।
Step 4 → नाम **उसी network** के container/service/alias से match हुआ? तो IP लौटाता है।
Step 5 → Match नहीं (जैसे google.com) तो host के DNS को forward कर देता है (host resolv.conf / `--dns`)।
Step 6 → जवाब मिलने पर app उस IP से connect करता है।

Key rules: names resolve **only inside the same network**; default `bridge` has no name DNS; Compose also registers the **service name** and any `aliases`; with several containers sharing an alias, DNS returns multiple A records.

---

## 🟡 Real World Example
Your Node.js API reads `REDIS_HOST=redis`. During a deploy you recreate the redis container; it gets a new IP but the name `redis` still works. A real outage story: an API cached the DNS result forever (Node `net` keeps the socket, but some libraries cache lookups). After a DB container was recreated, the API still pointed to the old IP until it restarted. Know that DNS gives a name -> IP at lookup time only.

## 🟡 Real Example Hindi mein
आपका Node.js API `REDIS_HOST=redis` पढ़ता है। Deploy में redis container दोबारा बनता है, नया IP मिलता है पर नाम `redis` काम करता रहता है। एक असली outage: API ने DNS result हमेशा के लिए cache कर लिया। DB container दोबारा बनने के बाद भी API पुराने IP पर जाता रहा जब तक restart नहीं हुआ। याद रखें DNS सिर्फ lookup के समय नाम -> IP देता है।

---

## 💻 Code / Config Example — Basic
```bash
# Create network and two containers
docker network create appnet                           # user-defined bridge => embedded DNS on
docker run -d --name db --network appnet \
  -e POSTGRES_PASSWORD=example postgres:16-alpine      # example image tag

# See what a container uses as resolver
docker run --rm --network appnet alpine cat /etc/resolv.conf
# expected: nameserver 127.0.0.11   (plus options ndots:0)

# Resolve a container name from another container
docker run --rm --network appnet alpine nslookup db    # returns the db container IP

# Add a network alias (extra name for the same container)
docker network connect --alias database appnet db      # "database" now also resolves

# Use custom DNS servers for one container
docker run --rm --dns 1.1.1.1 --dns-search internal.example alpine cat /etc/resolv.conf
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - aliases, custom DNS, extra_hosts, replica round-robin
services:
  api:
    build: ./api                          # Node.js / FastAPI image
    networks:
      backend:
        aliases:
          - api.internal                  # extra DNS name inside backend network
    dns:
      - 10.0.0.2                          # example: AWS VPC resolver (VPC base IP + 2)
      - 1.1.1.1                           # fallback public resolver
    dns_search:
      - corp.internal                     # lets "payments" resolve as payments.corp.internal
    extra_hosts:
      - "legacy-erp.local:10.0.5.20"      # static entry written to /etc/hosts of this container
      - "host.docker.internal:host-gateway" # reach host services on Linux
    environment:
      DB_HOST: db                         # resolved by Docker DNS, not hardcoded IP
  worker:
    build: ./worker                       # background workers
    deploy:
      replicas: 3                         # 3 containers => name "worker" returns several IPs
    networks:
      - backend                           # same network, same service name
  db:
    image: postgres:16-alpine             # example tag
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}   # from .env
    networks:
      backend:
        aliases:
          - database                      # second name for the same DB
networks:
  backend:
    driver: bridge                        # user-defined => embedded DNS available
```
Daemon-wide DNS (applies to all containers) goes in `/etc/docker/daemon.json`:
```json
{
  "dns": ["10.0.0.2", "1.1.1.1"],
  "dns-search": ["corp.internal"]
}
```
Restart docker after editing (`systemctl restart docker`), which restarts containers unless live-restore is on. Compose `deploy.replicas` is honoured by `docker compose up` in recent Compose versions; verify on your version. Not run locally.

---

## 🟠 My Stack Integration
- **Nginx in front of Node.js/FastAPI**: Nginx resolves `api` **only once at startup** when you write `proxy_pass http://api:3000;`. If the api container is recreated with a new IP, Nginx keeps the stale IP and returns 502. Fix with Docker's resolver and a variable:

```nginx
# nginx.conf fragment - re-resolve names at runtime
server {
  listen 80;                                    # plain HTTP inside the container
  resolver 127.0.0.11 valid=10s ipv6=off;       # Docker embedded DNS, cache 10 s
  location /api/ {
    set $upstream http://api:3000;              # variable forces runtime DNS lookup
    proxy_pass $upstream;                       # use variable (no URI part with it)
  }
}
```
- **AWS**: on EC2 the host resolver is the VPC DNS (VPC CIDR base + 2). Containers inherit it, so private Route53 zones and RDS endpoints resolve inside containers too.
- **Security**: DNS names are not authentication. Any container on the same network can resolve and call `db`. Segment networks.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting name resolution on the default `bridge`.
✅ Correct: Use a user-defined network or Compose.

❌ Mistake 2: Containers on different networks trying to resolve each other.
✅ Correct: Attach both to a shared network (`networks:` in Compose).

❌ Mistake 3: Hardcoding container IPs in `.env` files.
✅ Correct: Use service names or aliases.

❌ Mistake 4: Editing `/etc/resolv.conf` inside a running container.
✅ Correct: Docker rewrites it on restart; use `--dns` / `dns:` instead.

❌ Mistake 5: Nginx static `proxy_pass` to a recreated container (502 after deploy).
✅ Correct: Use `resolver 127.0.0.11` with a variable, or reload Nginx after deploys.

---

## 🧠 Tricky Interview Question
`nslookup db` works from the `api` container but your app throws `EAI_AGAIN` randomly in production. What could be happening?

Answer: Intermittent `EAI_AGAIN` is a DNS timeout. Causes: the upstream DNS is overloaded or blocked (Security Group/firewall blocking UDP 53 to the VPC resolver), Alpine/musl resolver quirks with `search` domains and `ndots`, a burst of lookups per request (no connection pooling or caching), or conntrack table limits dropping UDP packets. Fix with keep-alive connections, a local caching resolver, reducing `search` domains, and checking `dmesg` for conntrack drops.

---

## ⚫ Interview Questions + Answers

Q1: What IP does Docker's embedded DNS listen on?
A1: 127.0.0.11 inside the container's network namespace on user-defined networks.

Q2: Why does `--link` still appear in old docs?
A2: It was the old way to get names on the default bridge. It is deprecated; use user-defined networks.

Q3: How do you make one container reachable by two names?
A3: Network aliases: `docker network connect --alias` or `aliases:` in Compose.

Q4: How do you point containers to a company DNS?
A4: `--dns` per container, `dns:` in Compose, or `"dns"` in `/etc/docker/daemon.json` for all.

Q5: What does a name with multiple containers return?
A5: Multiple A records in rotating order (DNS round-robin), a basic load balancing; it is not health-aware.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Services in one Compose project talk to each other.
- You want replicas behind one name for simple balancing.

❌ Avoid when:
- You need health-aware balancing (use Nginx upstream, ALB or Kubernetes Service).
- You need names across hosts without Swarm/Kubernetes (use Route53 private zone or Consul).

---

## 📊 Visual Diagram
```
  api container
  +--------------------------+
  | app: connect("db:5432")  |
  | resolv.conf -> 127.0.0.11|
  +------------+-------------+
               | UDP 53
               v
     +-------------------------+     name known on this network?
     | Docker embedded DNS     |---- yes --> returns 172.19.0.4
     | (inside dockerd)        |
     +-----------+-------------+
                 | no (e.g. rds.amazonaws.com)
                 v
        host / VPC resolver (10.0.0.2) --> internet DNS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedded DNS | DNS server built into Docker daemon | Docker daemon में built-in DNS server |
| 127.0.0.11 | Resolver address inside containers | Containers के अंदर resolver का address |
| Alias | Extra name for a container | Container का अतिरिक्त नाम |
| A record | DNS record mapping name to IPv4 | नाम को IPv4 से जोड़ने वाला DNS record |
| resolv.conf | File listing DNS servers | DNS servers की सूची वाली file |
| EAI_AGAIN | Temporary DNS lookup failure | DNS lookup की अस्थायी विफलता |

---

## ⚡ 3-Line Summary
English: User-defined networks give containers name resolution through 127.0.0.11.
Names work only inside the same network; other names are forwarded upstream.
Nginx caches IPs at start, so use a resolver and a variable for dynamic upstreams.
Hindi: User-defined networks में containers को 127.0.0.11 से नाम resolution मिलता है।
नाम सिर्फ उसी network के अंदर चलते हैं; बाकी नाम upstream को forward होते हैं।
Nginx start पर IP cache कर लेता है, इसलिए dynamic upstream में resolver और variable इस्तेमाल करो।

---

## ➡️ Next Topic
**147. Container vs Host Network** - what changes when a container skips the bridge and shares the host's network directly.
