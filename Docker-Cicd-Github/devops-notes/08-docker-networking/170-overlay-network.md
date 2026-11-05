# 170. Overlay Network
# हिंदी में: Overlay Network (कई servers के बीच container network)

---

## 🔵 Simple Definition (English)
An **overlay network** is a virtual Docker network that spans **multiple Docker hosts**. Containers on different servers join the same overlay and talk to each other by name, as if they were on one LAN. Docker wraps their traffic in **VXLAN** tunnels (UDP 4789) over the real network.

## 🔵 सरल परिभाषा (Hindi)
**Overlay network** एक virtual Docker network है जो **कई Docker hosts** में फैला होता है। अलग-अलग servers के containers एक ही overlay में जुड़ते हैं और नाम से एक-दूसरे से बात करते हैं, जैसे सब एक ही LAN पर हों। Docker उनका traffic **VXLAN** tunnel (UDP 4789) में लपेटकर असली network पर भेजता है।

---

## 🔴 Problem it Solves
A bridge network only works inside **one** host. The moment you run your API on VPS-1 and your database or worker on VPS-2, containers cannot reach each other by container name or private IP. Without overlay you must publish ports on the public IP, hard-code server IPs and punch firewall holes. Overlay gives one flat, encrypted-optionally, name-resolvable network across all nodes of a Swarm.

## 🔴 यह क्यों बना? (Hindi)
Bridge network सिर्फ **एक** host के अंदर काम करता है। जैसे ही API VPS-1 पर और DB/worker VPS-2 पर चला, containers नाम या private IP से एक-दूसरे तक नहीं पहुँच पाते। Overlay के बिना public IP पर ports खोलने पड़ते, server IPs hard-code करने पड़ते और firewall में छेद करने पड़ते। Overlay सभी Swarm nodes पर एक flat, (चाहें तो) encrypted, name से resolve होने वाला network देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker swarm init on manager; workers join with the token (ports 2377/tcp, 7946/tcp+udp, 4789/udp open)
Step 2 → docker network create -d overlay app-net  (created on manager, appears on a node only when a task needs it)
Step 3 → A service/container attaches to app-net; Docker gives it an IP from the overlay subnet (e.g. 10.0.1.x)
Step 4 → Container A (node-1) calls "db:5432"; embedded DNS resolves "db" to a virtual IP (VIP) or task IPs
Step 5 → Packet leaves node-1 wrapped in a VXLAN/UDP packet addressed to node-2's real IP
Step 6 → node-2 unwraps VXLAN, delivers original packet to container B -> reply follows the same path
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Manager पर docker swarm init; workers token से join करते हैं (ports 2377/tcp, 7946/tcp+udp, 4789/udp खुले हों)
Step 2 → docker network create -d overlay app-net (manager पर बनता है, node पर तभी दिखता है जब वहाँ task चले)
Step 3 → Service app-net से जुड़ती है; Docker उसे overlay subnet से IP देता है (जैसे 10.0.1.x)
Step 4 → node-1 का container "db:5432" बुलाता है; embedded DNS "db" को VIP या task IPs में बदलता है
Step 5 → Packet VXLAN/UDP में लपेटकर node-2 के असली IP पर जाता है
Step 6 → node-2 उसे खोलकर container B को देता है; जवाब उसी रास्ते लौटता है
```

---

## 🟡 Real World Example
Swiggy-style order platform on 3 EC2 instances: `api` replicas run on all nodes, `redis` on node-3, `worker` on node-2. All attach to overlay `backend`. The API calls `redis:6379` and never knows which server holds Redis. When node-3 dies, Swarm reschedules Redis on node-2 and the name `redis` still works because the overlay DNS updates. Only `nginx` publishes port 443 to the internet; the DB network is `--internal`.

## 🟡 Real Example Hindi mein
Swiggy जैसा order platform 3 EC2 instances पर: `api` replicas सब nodes पर, `redis` node-3 पर, `worker` node-2 पर। सब overlay `backend` से जुड़े हैं। API `redis:6379` बुलाती है और उसे पता नहीं Redis किस server पर है। node-3 मरे तो Swarm Redis को node-2 पर चला देता है और `redis` नाम फिर भी चलता है। सिर्फ `nginx` port 443 बाहर खोलता है; DB network `--internal` है।

---

## 💻 Code / Config Example — Basic
```bash
# --- run on the MANAGER node (EC2 / VPS-1) ---
# Initialise swarm; --advertise-addr is the private IP other nodes can reach
docker swarm init --advertise-addr 10.0.0.10

# Create an overlay network named app-net
docker network create --driver overlay app-net

# Attachable lets plain `docker run` containers (not only services) join it
docker network create --driver overlay --attachable debug-net

# Verify: scope must say "swarm"
docker network ls --filter driver=overlay

# Inspect subnet, peers and attached containers
docker network inspect app-net

# Start two replicas of a web service on that network
docker service create --name web --replicas 2 --network app-net nginx:1.27-alpine

# From any node, test name resolution using a throwaway container
docker run --rm --network debug-net alpine:3.20 nslookup tasks.web
```

## 💻 Code / Config Example — Advanced
```yaml
# stack.yml  ->  docker stack deploy -c stack.yml shop
# Production overlay setup: encrypted data plane, separate frontend/backend, internal DB net
services:
  nginx:                                  # public edge proxy
    image: nginx:1.27-alpine              # example tag, update to current
    ports:
      - target: 80                        # container port
        published: 80                     # port exposed on every swarm node (routing mesh)
        protocol: tcp                     # tcp is default, explicit for clarity
        mode: ingress                     # use the swarm routing mesh
    networks: [frontend]                  # only talks to the API tier
    deploy:
      replicas: 2                         # two edge copies for availability

  api:                                    # Node.js / FastAPI service
    image: myrepo/api:1.0.0               # your image (example name)
    environment:
      DB_HOST: db                         # overlay DNS name of the db service
      REDIS_URL: redis://redis:6379       # same, resolved across nodes
    networks: [frontend, backend]         # bridge between public and private tier
    deploy:
      replicas: 4                         # spread over nodes
      update_config:
        parallelism: 1                    # rolling update one task at a time
        order: start-first                # start new before stopping old (zero downtime)

  db:
    image: postgres:16-alpine             # example tag
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pw   # read password from swarm secret, not env
    secrets: [db_pw]                      # mount the secret
    networks: [backend]                   # NOT on frontend -> unreachable from nginx
    deploy:
      placement:
        constraints: ["node.labels.role == db"]    # pin DB to a labelled node (has the volume)

  redis:
    image: redis:7-alpine
    networks: [backend]

networks:
  frontend:
    driver: overlay                       # spans all swarm nodes
  backend:
    driver: overlay
    driver_opts:
      encrypted: "true"                   # IPsec ESP encryption of VXLAN data plane
    internal: true                        # no route to the internet / outside

secrets:
  db_pw:
    external: true                        # created earlier: printf 'S3cret' | docker secret create db_pw -
```

---

## 🟠 My Stack Integration
Your single VPS needs **no overlay** - Compose bridge networks are enough. Overlay matters when you grow to 2+ EC2 instances behind an ALB: Nginx, Node.js/FastAPI and Redis become Swarm services. React is built statically and served by Nginx, so it needs no network of its own.

```bash
# AWS security group for swarm nodes (allow only from the same SG, never 0.0.0.0/0)
# 2377/tcp  cluster management (managers only)
# 7946/tcp+udp  node gossip / discovery
# 4789/udp  VXLAN overlay data
aws ec2 authorize-security-group-ingress --group-id sg-0abc1234 \
  --protocol udp --port 4789 --source-group sg-0abc1234   # example IDs
```

Security: use `encrypted: "true"` for sensitive networks (adds CPU cost and slightly lower throughput), restrict 4789/udp to node-to-node, and mark the DB overlay `internal`. Not built/run locally; validated syntax only.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Opening 4789/udp, 7946 and 2377 to the whole internet.
✅ Correct: Allow them only between swarm nodes (same security group / private subnet).

❌ Mistake 2: Trying `docker run --network app-net` and getting "not manually attachable".
✅ Correct: Create the network with `--attachable` or use `docker service create`.

❌ Mistake 3: Assuming overlay traffic is encrypted by default.
✅ Correct: Only the control plane is encrypted; add `--opt encrypted` for the data plane.

❌ Mistake 4: Running overlay on a single host "for production" without Swarm.
✅ Correct: Overlay needs swarm mode (or a key-value store); use bridge for one host.

---

## 🧠 Tricky Interview Question
Two containers are on the same overlay network on different nodes. Ping by name works, but TCP connections to a big payload hang while small requests succeed. Why?

Answer: VXLAN adds ~50 bytes of header, so the effective MTU drops (1500 to about 1450). If the underlying network (cloud, VPN) has a smaller MTU or blocks ICMP fragmentation-needed, large packets are dropped silently while small ones pass. Fix: set the overlay MTU (`--opt com.docker.network.driver.mtu=1400`), allow ICMP, and check that UDP 4789 is not rate limited.

---

## ⚫ Interview Questions + Answers

Q1: What is an overlay network?
A1: A multi-host virtual network created with the overlay driver. Containers on different Docker hosts communicate privately using VXLAN encapsulation; requires swarm mode.

Q2: Which ports must be open for Swarm overlay?
A2: 2377/tcp (management), 7946/tcp and udp (gossip), 4789/udp (VXLAN data).

Q3: How is DNS handled on overlay?
A3: Docker's embedded DNS (127.0.0.11) resolves service name to a virtual IP (default `vip` mode) or, with `endpoint_mode: dnsrr`, to all task IPs; `tasks.<service>` always returns task IPs.

Q4: Overlay vs bridge?
A4: Bridge = one host, simple, fast. Overlay = many hosts, VXLAN overhead, needs Swarm. Both give name-based discovery on user-defined networks.

Q5: What is the ingress network?
A5: A special overlay created by Swarm for the routing mesh; published ports on any node are load-balanced to service tasks on any node.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Services run on multiple hosts (Swarm) and must talk privately
- You want name-based discovery regardless of where tasks run
- You need encrypted node-to-node container traffic

❌ Avoid when:
- Everything is on one VPS (use a custom bridge)
- You use Kubernetes (it has its own CNI plugins instead)
- Ultra low latency is required and network is already trusted (use host/macvlan)

---

## 📊 Visual Diagram
```
 Node-1 (10.0.0.10)                       Node-2 (10.0.0.11)
+--------------------------+            +--------------------------+
| [api 10.0.1.5]           |            | [db 10.0.1.9]            |
|      |  eth0             |            |      |  eth0             |
|   overlay bridge (br0)   |            |   overlay bridge (br0)   |
|   VXLAN VTEP             |            |   VXLAN VTEP             |
+-----------|--------------+            +-----------|--------------+
            |   UDP 4789 (VXLAN tunnel over real network)  |
            +----------------------------------------------+
   api -> "db:5432"  -> DNS -> 10.0.1.9 -> encapsulated -> node-2 -> db
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Overlay | Multi-host virtual network | कई hosts में फैला virtual network |
| VXLAN | L2-over-UDP tunnelling (port 4789) | UDP में L2 packet लपेटने की तकनीक |
| Swarm | Docker's native orchestrator | Docker का अपना cluster manager |
| Ingress | Overlay for routing mesh | बाहरी traffic बाँटने वाला overlay |
| VIP | Virtual IP load-balancing a service | Service का virtual IP |
| Attachable | Lets standalone containers join | अलग containers को जुड़ने देता है |

---

## ⚡ 3-Line Summary
English: Overlay connects containers across many Docker hosts using VXLAN tunnels.
English: It needs Swarm, ports 2377/7946/4789 between nodes, and optional encryption.
English: Use it for multi-node production; on one VPS a bridge is enough.

Hindi: Overlay कई Docker hosts के containers को VXLAN tunnel से जोड़ता है।
Hindi: इसे Swarm और nodes के बीच ports 2377/7946/4789 चाहिए; encryption optional है।
Hindi: Multi-node production में इस्तेमाल करो; एक VPS पर bridge काफी है।

---

## ➡️ Next Topic
**171. Macvlan Network** - when a container needs its own real LAN IP/MAC instead of NAT or tunnels.
