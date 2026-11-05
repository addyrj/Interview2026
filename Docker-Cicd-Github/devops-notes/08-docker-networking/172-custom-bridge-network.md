# 172. Custom Bridge Network
# हिंदी में: Custom Bridge Network (अपना user-defined bridge)

---

## 🔵 Simple Definition (English)
A **custom (user-defined) bridge network** is a bridge you create yourself with `docker network create`. Unlike the default `bridge`, it has **automatic DNS by container name**, better isolation, and lets you choose the subnet. It is the standard network for single-host apps and every Compose project.

## 🔵 सरल परिभाषा (Hindi)
**Custom (user-defined) bridge network** वह bridge है जिसे आप खुद `docker network create` से बनाते हैं। Default `bridge` के उलट इसमें **container के नाम से automatic DNS**, बेहतर isolation और अपना subnet चुनने की सुविधा होती है। Single-host apps और हर Compose project में यही standard है।

---

## 🔴 Problem it Solves
On the default `bridge` network containers only see each other by IP, and IPs change on every restart. Legacy `--link` was needed for names and is deprecated. Also, every container on the default bridge can reach every other one, so a compromised frontend can scan your DB. Custom bridges give name resolution, per-app isolation, and on-the-fly attach/detach without restart.

## 🔴 यह क्यों बना? (Hindi)
Default `bridge` पर containers सिर्फ IP से एक-दूसरे को देखते हैं, और restart पर IP बदल जाता है। नाम के लिए पुराना `--link` चाहिए था जो deprecated है। साथ ही default bridge पर हर container हर दूसरे तक पहुँच सकता है, यानी hack हुआ frontend आपके DB को scan कर सकता है। Custom bridge name resolution, हर app के लिए अलग isolation और बिना restart के attach/detach देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker network create app-net  (Docker makes a Linux bridge br-<id> and a subnet, e.g. 172.20.0.0/16)
Step 2 → docker run --network app-net --name db ...  (veth pair connects container to the bridge)
Step 3 → Container's /etc/resolv.conf points to Docker's embedded DNS 127.0.0.11
Step 4 → api calls "db" -> embedded DNS answers with db's current IP on app-net
Step 5 → Traffic stays on the bridge; to the internet it is NAT-ed (MASQUERADE) via host iptables
Step 6 → Only containers on app-net see each other; other networks are isolated by iptables rules
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker network create app-net (Docker Linux bridge br-<id> और subnet बनाता है, जैसे 172.20.0.0/16)
Step 2 → docker run --network app-net --name db ... (veth pair container को bridge से जोड़ता है)
Step 3 → Container की /etc/resolv.conf Docker के embedded DNS 127.0.0.11 को point करती है
Step 4 → api "db" बुलाता है -> embedded DNS db का मौजूदा IP बताता है
Step 5 → Traffic bridge के अंदर रहता है; internet के लिए host iptables से NAT (MASQUERADE) होता है
Step 6 → सिर्फ app-net के containers आपस में दिखते हैं; दूसरे networks iptables से अलग रहते हैं
```

---

## 🟡 Real World Example
Your VPS runs two projects: an e-commerce app and a blog. Each gets its own bridge (`shop-net`, `blog-net`). The shop's Node.js API connects to `mongodb://mongo:27017` — the name `mongo` works only inside `shop-net`. Even if both projects have a container called `db`, there is no conflict and the blog can never reach the shop database.

## 🟡 Real Example Hindi mein
आपकी VPS पर दो projects चलते हैं: e-commerce और blog। हर एक का अपना bridge है (`shop-net`, `blog-net`)। Shop की Node.js API `mongodb://mongo:27017` से जुड़ती है; `mongo` नाम सिर्फ `shop-net` के अंदर चलता है। दोनों projects में `db` नाम का container हो तब भी टकराव नहीं, और blog कभी shop के database तक नहीं पहुँच सकता।

---

## 💻 Code / Config Example — Basic
```bash
# Create a user-defined bridge with default subnet
docker network create app-net

# Start MongoDB on it (no published port: only reachable inside app-net)
docker run -d --name mongo --network app-net mongo:7

# Start a Node.js API on the same network, connect using the container NAME
docker run -d --name api --network app-net \
  -e MONGO_URL=mongodb://mongo:27017/shop \
  -p 3000:3000 \
  myrepo/api:1.0.0

# Prove DNS works (alpine has nslookup / wget)
docker run --rm --network app-net alpine:3.20 nslookup mongo

# Attach a running container to a second network without restarting
docker network connect shop-admin api

# Detach it again
docker network disconnect shop-admin api
```

## 💻 Code / Config Example — Advanced
```bash
# Custom subnet, gateway, fixed IP range, MTU and ICC off, for tight production control
docker network create \
  --driver bridge \
  --subnet 172.28.0.0/24 \
  --gateway 172.28.0.1 \
  --ip-range 172.28.0.128/25 \
  --opt com.docker.network.bridge.name=br-shop \
  --opt com.docker.network.driver.mtu=1450 \
  --opt com.docker.network.bridge.enable_icc=false \
  --label env=prod \
  shop-net
# --subnet/--gateway : avoid clashing with your VPC/VPN ranges
# --ip-range         : Docker auto-assigns only from this slice (fixed IPs below .128)
# bridge.name        : readable interface name for tcpdump/iptables rules
# mtu                : match the cloud/VPN MTU
# enable_icc=false   : containers cannot talk to each other unless explicitly linked/allowed
```
```yaml
# docker-compose.yml - same idea declared in Compose
services:
  api:
    image: myrepo/api:1.0.0               # example image
    networks:
      shop-net:
        ipv4_address: 172.28.0.10         # fixed IP (must be inside subnet, outside ip_range)
    ports:
      - "127.0.0.1:3000:3000"             # bind to loopback only; Nginx on host proxies it
  mongo:
    image: mongo:7
    networks: [shop-net]                  # no ports: private
networks:
  shop-net:
    driver: bridge                        # explicit driver
    ipam:
      config:
        - subnet: 172.28.0.0/24           # custom subnet
          gateway: 172.28.0.1             # bridge IP
          ip_range: 172.28.0.128/25       # dynamic assignment pool
    driver_opts:
      com.docker.network.bridge.name: br-shop        # stable interface name
      com.docker.network.driver.mtu: "1450"          # MTU override (quoted string)
```

---

## 🟠 My Stack Integration
On your VPS: Nginx (host or container) → Node.js/FastAPI → DB/Redis, all on one custom bridge. React is built and copied into the Nginx image/volume, so no runtime network for it.

```yaml
services:
  nginx:
    image: nginx:1.27-alpine              # example tag
    ports: ["80:80", "443:443"]           # the ONLY published ports
    networks: [edge]                      # edge net: nginx + api
  api:
    image: myrepo/fastapi:1.0.0
    networks: [edge, data]                # api bridges the two nets
  postgres:
    image: postgres:16-alpine
    networks: [data]                      # unreachable from nginx
networks:
  edge: {}                                # default bridge driver
  data:
    internal: true                        # no internet egress for DB
```
In `nginx.conf` use `proxy_pass http://api:8000;` (service name, not IP). Security: never publish DB ports (`5432:5432`) on a public VPS; use `127.0.0.1:` bindings or none. AWS security group should only allow 80/443. Not run locally; syntax checked only.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using the default `bridge` and trying `ping db`.
✅ Correct: Create/join a user-defined bridge; names only resolve there.

❌ Mistake 2: Subnet overlapping with VPN/VPC (e.g. 10.0.0.0/16).
✅ Correct: Choose a free range like 172.28.0.0/24 or set `default-address-pools` in `daemon.json`.

❌ Mistake 3: Hard-coding container IPs in app config.
✅ Correct: Use names; reserve fixed IPs only for exceptional cases.

❌ Mistake 4: Publishing every service port "just in case".
✅ Correct: Publish only the edge; internal traffic needs no `-p`.

---

## 🧠 Tricky Interview Question
`api` and `db` are both attached to `app-net`, yet `curl http://db:5432` from the host machine says "could not resolve host". Why?

Answer: Container names are resolved by Docker's embedded DNS (127.0.0.11), which is only available **inside containers** on user-defined networks. The host uses its own resolver. From the host you need the container IP (`docker inspect`) or a published port on localhost. For testing use `docker run --rm --network app-net ...` or `docker exec`.

---

## ⚫ Interview Questions + Answers

Q1: Default bridge vs custom bridge?
A1: Custom bridge has automatic DNS by name, better isolation, configurable subnet, live connect/disconnect. Default bridge has IP-only access and legacy `--link`.

Q2: Can a container be on multiple bridges?
A2: Yes, with `docker network connect` or multiple entries under `networks:`; it gets one interface and IP per network.

Q3: How do containers reach the internet?
A3: Via the bridge gateway and iptables MASQUERADE NAT on the host; `internal: true` removes that route.

Q4: How do you avoid IP range conflicts?
A4: Set `--subnet`, or define `"default-address-pools"` in `/etc/docker/daemon.json`.

Q5: What does enable_icc=false do?
A5: Blocks container-to-container traffic on that bridge unless explicit rules/links allow it, hardening lateral movement.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single-host multi-container apps (almost always)
- You want name-based discovery and per-app isolation
- Compose projects (it is created automatically)

❌ Avoid when:
- Multi-host clusters (use overlay)
- You need max network speed with zero NAT (host network)
- Containers need LAN IPs (macvlan)

---

## 📊 Visual Diagram
```
 Internet --> :443 --> [ VPS host ]
                          |  iptables NAT / port publish
                 +--------+--------------------------+
                 |  bridge br-shop 172.28.0.1        |
                 +--+-------------+-------------+----+
                    |             |             |
              [nginx .2]     [api .10]     [mongo .11]
               DNS: nginx     DNS: api      DNS: mongo
   api -> "mongo:27017" -> embedded DNS 127.0.0.11 -> 172.28.0.11
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| User-defined bridge | Bridge you create | खुद बनाया हुआ bridge |
| Embedded DNS | Docker's 127.0.0.11 resolver | Docker का अपना DNS |
| veth | Virtual ethernet pair | Virtual ethernet जोड़ी |
| IPAM | IP address management | IP address प्रबंधन |
| ICC | Inter-container communication | Containers की आपसी बातचीत |
| MASQUERADE | Source NAT for outbound traffic | बाहर जाते traffic का NAT |

---

## ⚡ 3-Line Summary
English: Custom bridge = your own single-host network with DNS by name and isolation.
English: Create it with docker network create or Compose networks; control subnet and MTU.
English: Publish only edge ports; keep databases off public interfaces.

Hindi: Custom bridge = single-host पर आपका अपना network, नाम से DNS और isolation के साथ।
Hindi: docker network create या Compose networks से बनाओ; subnet और MTU खुद तय करो।
Hindi: सिर्फ edge ports publish करो; databases को public interface से दूर रखो।

---

## ➡️ Next Topic
**173. Container DNS Resolution** - exactly how the embedded DNS turns names into IPs and how to debug it.
