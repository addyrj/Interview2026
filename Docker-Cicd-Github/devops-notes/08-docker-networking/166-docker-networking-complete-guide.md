# 166. Docker Networking — Complete Guide
# हिंदी में: Docker Networking — पूरी गाइड

---

## 🔵 Simple Definition (English)
**Docker networking** is the system that lets containers talk to each other, to the host, and to the internet. Docker creates virtual networks (bridge, host, none, overlay, macvlan), gives each container a virtual network interface and IP, and provides built-in DNS so containers can find each other by name.

## 🔵 सरल परिभाषा (Hindi)
**Docker networking** वो system है जिससे containers आपस में, host से, और internet से बात करते हैं। Docker virtual networks (bridge, host, none, overlay, macvlan) बनाता है, हर container को virtual network interface और IP देता है, और built-in DNS देता है ताकि containers एक-दूसरे को नाम से ढूँढ सकें।

---

## 🔴 Problem it Solves
Containers are isolated: each has its own network namespace, so `localhost` inside the API container is NOT the database. Without Docker networking you would hard-code changing IPs, expose every service on the host, and have no isolation between unrelated apps. Docker networking gives stable names, controlled exposure, and isolation between stacks.

## 🔴 यह क्यों बना? (Hindi)
Containers isolated होते हैं: हर एक का अपना network namespace है, इसलिए API container के अंदर `localhost` database नहीं है। Docker networking के बिना तुम बदलते IPs hard-code करते, हर service host पर expose करते, और अलग apps में कोई isolation न होता। Docker networking stable names, नियंत्रित exposure और stacks के बीच isolation देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Docker daemon starts and creates 3 default networks: bridge, host, none
Step 2 → docker run attaches a container to a network (default: bridge "docker0")
Step 3 → Docker creates a veth pair: one end in the container (eth0), one on the host bridge
Step 4 → Container gets a private IP (e.g. 172.17.0.2) from the network's subnet
Step 5 → Outbound traffic: NAT (iptables MASQUERADE) translates it to the host IP
Step 6 → Inbound traffic: -p 8080:80 adds a DNAT rule host:8080 -> container:80
Step 7 → On USER-DEFINED networks an embedded DNS (127.0.0.11) resolves container names
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Docker daemon शुरू होते ही 3 default networks बनाता है: bridge, host, none
Step 2 → docker run container को network से जोड़ता है (default: bridge "docker0")
Step 3 → Docker veth pair बनाता है: एक सिरा container में (eth0), दूसरा host bridge पर
Step 4 → Container को network के subnet से private IP मिलती है (जैसे 172.17.0.2)
Step 5 → Outbound traffic: NAT (iptables MASQUERADE) उसे host IP में बदलता है
Step 6 → Inbound: -p 8080:80 एक DNAT rule जोड़ता है host:8080 -> container:80
Step 7 → USER-DEFINED networks पर embedded DNS (127.0.0.11) container names resolve करता है
```

---

## 🟡 Real World Example
Swiggy-like food app on one VPS: `nginx` (public), `api` (Node.js), `worker`, `postgres`, `redis`. Only nginx publishes port 443. api, worker, postgres and redis sit on a private network, so the internet cannot reach the database directly. The API connects with `postgres://db:5432` using the name `db`, not an IP.

## 🟡 Real Example Hindi mein
Swiggy जैसा food app एक VPS पर: `nginx` (public), `api` (Node.js), `worker`, `postgres`, `redis`। सिर्फ nginx port 443 publish करता है। बाकी सब private network पर हैं, इसलिए internet सीधे database तक नहीं पहुँच सकता। API `postgres://db:5432` से जुड़ता है, यानी IP नहीं बल्कि नाम `db`।

---

## 💻 Code / Config Example — Basic
```bash
# list default networks
docker network ls                                  # shows bridge, host, none

# create your own bridge network (gives DNS by name)
docker network create appnet                       # user-defined bridge

# run a db and an api on that network
docker run -d --name db --network appnet \
  -e POSTGRES_PASSWORD=secret postgres:16-alpine   # db reachable as "db" inside appnet

docker run -d --name api --network appnet \
  -p 3000:3000 myorg/api:1.0                       # only api is published to the host

# test name resolution from inside api (alpine/busybox images have nslookup)
docker exec api nslookup db                        # should print db container IP

# inspect a network: subnet, gateway, attached containers
docker network inspect appnet                      # JSON details
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - segmented networks: public edge + private backend
services:
  nginx:
    image: nginx:1.27-alpine               # example tag
    ports:
      - "80:80"                            # the ONLY published ports
      - "443:443"
    networks:
      - frontend                           # talks to the api
    depends_on:
      - api                                # start order only
  api:
    image: myorg/api:1.4.2                 # Node.js or FastAPI image
    environment:
      DATABASE_URL: postgres://app:${DB_PASSWORD}@db:5432/app  # "db" resolved by Docker DNS
      REDIS_URL: redis://cache:6379        # "cache" is the redis service name
    networks:
      - frontend                           # reachable from nginx
      - backend                            # can reach db and cache
  db:
    image: postgres:16-alpine              # example tag
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}    # from .env, not committed
    volumes:
      - pgdata:/var/lib/postgresql/data    # persistent data
    networks:
      - backend                            # NOT on frontend: nginx cannot reach it
  cache:
    image: redis:7-alpine                  # example tag
    networks:
      - backend                            # private only
networks:
  frontend: {}                             # edge network
  backend:
    internal: true                         # no outbound internet, no host access
volumes:
  pgdata: {}                               # named volume for db
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** use service names in connection strings (`mongodb://mongo:27017`), never `localhost` or a hard-coded IP.
- **React:** the browser runs on the user's machine, so React cannot call `http://api:3000`. Route via Nginx: `/api` proxied to `api:3000`.
- **Nginx:** `proxy_pass http://api:3000;` works because nginx and api share a network.
- **VPS:** open only 80/443 in the firewall/security group; Docker's published ports bypass UFW (it edits iptables), so bind admin ports to localhost: `127.0.0.1:5432:5432`.
- **AWS:** one EC2 = bridge networks; multi-node = ECS/EKS networking (awsvpc) replaces Docker overlay.

```nginx
# nginx/default.conf - proxy to the api container by name
server {
  listen 80;                              # public port
  location /api/ {
    proxy_pass http://api:3000/;          # "api" = compose service name (Docker DNS)
    proxy_set_header Host $host;          # keep original host header
    proxy_set_header X-Real-IP $remote_addr;  # pass client IP to Node/FastAPI
  }
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `localhost` in the API to reach the DB container.
✅ Correct: Use the service/container name (`db`). Localhost is the API container itself.

❌ Mistake 2: Using the default `bridge` network and expecting name resolution.
✅ Correct: The default bridge has no DNS by name; create a user-defined network (Compose does this automatically).

❌ Mistake 3: Publishing `5432:5432` or `27017:27017` on a public VPS.
✅ Correct: Do not publish DB ports, or bind to `127.0.0.1`.

❌ Mistake 4: Assuming UFW blocks Docker published ports.
✅ Correct: Docker inserts its own iptables rules; control exposure with `127.0.0.1:` binding or the `DOCKER-USER` chain.

---

## 🧠 Tricky Interview Question
**Q:** Two containers are on the default bridge. `ping 172.17.0.3` works but `ping db` fails. Why, and what is the minimal fix?

**Answer:** The default `bridge` network does not provide automatic DNS-based name resolution (only legacy `--link`). IP connectivity works because both sit on the same bridge. Fix: create a user-defined bridge (`docker network create appnet`) and attach both containers to it; the embedded DNS at 127.0.0.11 then resolves names. Compose does this by default.

---

## ⚫ Interview Questions + Answers

Q1: What network drivers does Docker have?
A1: bridge (default, single host), host, none, overlay (multi-host/Swarm), macvlan (container gets a LAN MAC/IP), and ipvlan.

Q2: How do containers on one network find each other?
A2: Embedded DNS server at 127.0.0.11 on user-defined networks resolves container names and network aliases.

Q3: What does `-p 8080:80` do?
A3: Publishes container port 80 on host port 8080 using an iptables DNAT rule.

Q4: What is `internal: true`?
A4: A network with no route to the outside; containers can talk to each other but not the internet.

Q5: Difference between EXPOSE and -p?
A5: `EXPOSE` is documentation only; `-p` actually publishes the port.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running multi-container apps (API + DB + cache)
- You need isolation between projects or tiers
- You want service discovery by name

❌ Avoid when:
- A single container needs raw max network speed (consider host mode)
- Multi-host clusters: use orchestrator networking (Swarm overlay, Kubernetes CNI)

---

## 📊 Visual Diagram
```
 Internet
    |  :80/:443
 +--v--------------------------------------------+
 | Host (VPS)  iptables DNAT / MASQUERADE        |
 |                                               |
 |  [frontend net 172.20.0.0/16]                 |
 |     nginx ---------- api                      |
 |                       |                       |
 |  [backend net 172.21.0.0/16, internal]        |
 |                  api--+--db     cache         |
 |         (names resolved by DNS 127.0.0.11)    |
 +-----------------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Network namespace | Isolated network stack per container | अलग network stack |
| veth pair | Virtual cable connecting container and host | virtual तार |
| Bridge | Virtual switch on host | virtual switch |
| NAT | Rewrites IPs between private and public | IP बदलने की तकनीक |
| Embedded DNS | Docker's built-in name server | built-in नाम सर्वर |
| Published port | Container port exposed on host | host पर खुला port |

---

## ⚡ 3-Line Summary
English: Docker gives each container a virtual network, IP and DNS name.
Use user-defined networks, publish only what is public, and keep databases private.
Learn the drivers: bridge, host, none, overlay, macvlan.
Hindi: Docker हर container को virtual network, IP और DNS नाम देता है।
User-defined networks use करो, सिर्फ public चीज़ें publish करो, database private रखो।
Drivers सीखो: bridge, host, none, overlay, macvlan।

---

## ➡️ Next Topic
**167. Bridge Network (default)** - the most common driver; we will see exactly how docker0 and user-defined bridges differ.
