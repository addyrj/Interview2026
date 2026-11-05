# 173. Container DNS Resolution
# हिंदी में: Container DNS Resolution (नाम से IP कैसे मिलता है)

---

## 🔵 Simple Definition (English)
**Container DNS resolution** is how a container turns a name like `db` or `google.com` into an IP. On user-defined networks Docker runs an **embedded DNS server at 127.0.0.11** inside each container's network namespace: it answers container/service/alias names itself and forwards everything else to the host's upstream DNS.

## 🔵 सरल परिभाषा (Hindi)
**Container DNS resolution** वह तरीका है जिससे container `db` या `google.com` जैसे नाम को IP में बदलता है। User-defined networks पर Docker हर container के network namespace में **127.0.0.11 पर embedded DNS server** चलाता है: container/service/alias के नाम वह खुद बताता है और बाकी सब host के upstream DNS को भेज देता है।

---

## 🔴 Problem it Solves
Container IPs are dynamic - they change at every restart or redeploy. Hard-coding IPs breaks apps, and editing `/etc/hosts` by hand is unmanageable. Embedded DNS gives stable names, handles scaling (several replicas under one name) and keeps each network's name space separate.

## 🔴 यह क्यों बना? (Hindi)
Container के IP dynamic होते हैं - हर restart या redeploy पर बदलते हैं। IP hard-code करने से app टूटती है और `/etc/hosts` हाथ से बदलना असंभव है। Embedded DNS स्थिर नाम देता है, scaling (एक नाम के पीछे कई replicas) सँभालता है और हर network का name space अलग रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Container starts on a user-defined network; Docker writes /etc/resolv.conf: nameserver 127.0.0.11
Step 2 → App calls getaddrinfo("db"); libc reads resolv.conf and asks 127.0.0.11
Step 3 → Docker daemon checks the network(s) of the asking container for name/alias "db"
Step 4 → Match found -> returns container IP (or service VIP / all replica IPs for round-robin DNS)
Step 5 → No match -> daemon forwards the query to the host's DNS (from /etc/resolv.conf or --dns)
Step 6 → Answer returns; the app connects. Names are visible only inside shared networks
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Container user-defined network पर चलता है; Docker /etc/resolv.conf में nameserver 127.0.0.11 लिखता है
Step 2 → App getaddrinfo("db") बुलाती है; libc resolv.conf पढ़कर 127.0.0.11 से पूछता है
Step 3 → Docker daemon पूछने वाले container के network(s) में नाम/alias "db" खोजता है
Step 4 → मिला -> container IP (या service VIP / सभी replica IPs round-robin के लिए) देता है
Step 5 → नहीं मिला -> query host के DNS (/etc/resolv.conf या --dns) को forward होती है
Step 6 → जवाब लौटता है; app connect करती है। नाम सिर्फ साझा networks में दिखते हैं
```

---

## 🟡 Real World Example
After a deploy on your VPS, the FastAPI container randomly returns 502 for external API calls (Razorpay) but internal DB calls work. Cause: the host's `/etc/resolv.conf` points to `127.0.0.53` (systemd-resolved), unusable from inside the container, so upstream forwarding fails intermittently. Setting `"dns": ["1.1.1.1","8.8.8.8"]` in `daemon.json` (or the Compose `dns:` key) fixes it.

## 🟡 Real Example Hindi mein
VPS पर deploy के बाद FastAPI container बाहरी API calls (Razorpay) पर कभी-कभी 502 देता है पर internal DB calls चलती हैं। कारण: host की `/etc/resolv.conf` `127.0.0.53` (systemd-resolved) को point करती है जो container के अंदर बेकार है, इसलिए upstream forwarding बीच-बीच में fail होती है। `daemon.json` में `"dns": ["1.1.1.1","8.8.8.8"]` (या Compose का `dns:`) लगाने से ठीक हो जाता है।

---

## 💻 Code / Config Example — Basic
```bash
# Network + two containers
docker network create app-net                                   # user-defined bridge (DNS enabled)
docker run -d --name db --network app-net redis:7-alpine        # name "db" is registered in DNS

# Look at the resolver config inside a container
docker run --rm --network app-net alpine:3.20 cat /etc/resolv.conf
# expected: nameserver 127.0.0.11 and options ndots:0

# Resolve a container name
docker run --rm --network app-net alpine:3.20 nslookup db       # shows db's IP via 127.0.0.11

# Resolve an external name (forwarded to host DNS)
docker run --rm --network app-net alpine:3.20 nslookup example.com

# Same lookup on the DEFAULT bridge fails for names (no embedded DNS there)
docker run --rm alpine:3.20 nslookup db                         # NXDOMAIN
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - custom DNS, search domain, extra_hosts and round-robin replicas
services:
  api:
    image: myrepo/api:1.0.0               # example image
    dns:
      - 1.1.1.1                           # upstream resolver for external names
      - 8.8.8.8                           # fallback upstream
    dns_search:
      - internal.example.com              # lets "billing" resolve as billing.internal.example.com
    dns_opt:
      - ndots:2                           # names with <2 dots get search domains tried first
    extra_hosts:
      - "legacy-erp:10.0.5.20"            # static entry written to /etc/hosts
      - "host.docker.internal:host-gateway"   # reach host services (Linux needs host-gateway)
    networks: [app-net]
    depends_on:
      worker:
        condition: service_started        # worker must exist so its name resolves

  worker:
    image: myrepo/worker:1.0.0
    deploy:
      replicas: 3                         # honoured by "docker compose up" in Compose v2
    networks:
      app-net:
        aliases:
          - jobs                          # extra DNS name; all replicas answer to it (round robin)

networks:
  app-net: {}                             # user-defined bridge
```
```json
{
  "dns": ["1.1.1.1", "8.8.8.8"],
  "dns-search": ["internal.example.com"]
}
```
Save the JSON as `/etc/docker/daemon.json`, then `sudo systemctl restart docker` (restarts containers unless live-restore is on).

---

## 🟠 My Stack Integration
- **Node.js**: Node caches nothing by default but `dns.lookup` uses a threadpool; a failing resolver shows as `EAI_AGAIN`. Use service names (`mongo`, `redis`) in connection strings.
- **FastAPI/uvicorn**: same; with `httpx` set sensible timeouts so DNS stalls do not hang workers.
- **Nginx**: it resolves upstream names **once at startup**. If `api` is recreated with a new IP, Nginx keeps the stale one. Fix with Docker's resolver and a variable:

```nginx
# nginx.conf fragment (inside server { } block)
resolver 127.0.0.11 valid=10s ipv6=off;   # Docker embedded DNS, re-check every 10 s
set $api_upstream http://api:8000;        # variable forces runtime resolution
location /api/ {
    proxy_pass $api_upstream;             # note: no URI part when using a variable
}
```
Security: DNS is service discovery, not access control; anyone on the same network can resolve names. Use separate networks. Block outbound port 53 to unknown resolvers in hardened setups. Nginx config not tested (`nginx` not installed here).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using container names on the default bridge.
✅ Correct: Use a user-defined network.

❌ Mistake 2: Nginx upstream breaks after `docker compose up -d` recreates the API.
✅ Correct: Use `resolver 127.0.0.11` with a variable, or restart Nginx on deploy.

❌ Mistake 3: Resolving names from the host shell (`ping api`).
✅ Correct: Test from a container: `docker exec web getent hosts api`.

❌ Mistake 4: Host DNS is `127.0.0.53`, containers can't resolve externally.
✅ Correct: Set `dns` in `daemon.json` or Compose.

---

## 🧠 Tricky Interview Question
You scale `worker` to 3 replicas and `nslookup worker` shows 3 IPs in changing order, but your Node client always hits the same one. Why?

Answer: Compose/bridge DNS uses **DNS round-robin**: it returns all IPs with order rotated, but clients typically use the first or cache the result (Node HTTP agents keep-alive sockets, libc caches in-process). Load balancing is therefore uneven. Use a real load balancer (Nginx, Traefik), Swarm VIP (`endpoint_mode: vip`), or disable keep-alive/re-resolve per request.

---

## ⚫ Interview Questions + Answers

Q1: What is 127.0.0.11?
A1: The address of Docker's embedded DNS server inside containers on user-defined networks.

Q2: Why doesn't the default bridge resolve names?
A2: It doesn't use the embedded DNS; it copies the host's resolv.conf. Only `--link` (deprecated) added names.

Q3: How do you give a container custom DNS servers?
A3: `docker run --dns 1.1.1.1`, Compose `dns:`, or `daemon.json`.

Q4: How can containers have multiple names?
A4: Network aliases, service names, and container names all resolve.

Q5: How does DNS differ in Swarm?
A5: A service name resolves to a VIP by default; `tasks.<service>` returns task IPs; `endpoint_mode: dnsrr` returns task IPs directly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Services discover each other by name (always on user-defined networks)
- Replicas share one logical name
- You must route external lookups to a corporate resolver

❌ Avoid when:
- You rely on DNS for strict load balancing (use an LB)
- You need security boundaries (DNS names are not authentication)
- You depend on very short TTL failover without re-resolving clients

---

## 📊 Visual Diagram
```
 +--------------------- container "api" ----------------------+
 |  app: connect("db:5432")                                    |
 |     |                                                       |
 |  /etc/resolv.conf -> nameserver 127.0.0.11                  |
 +---------|---------------------------------------------------+
           v
   Docker embedded DNS (in dockerd)
      |-- "db" in shared network?  yes -> 172.20.0.3 ----> app
      |-- no (e.g. example.com)    -> forward to host DNS (8.8.8.8) -> answer
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedded DNS | Docker's built-in resolver | Docker का अपना DNS |
| resolv.conf | Resolver config file | Resolver की config फ़ाइल |
| Round-robin DNS | Rotating list of IPs | घूमती IP सूची |
| ndots | Dots needed before treating name as absolute | नाम को absolute मानने की dots संख्या |
| extra_hosts | Static /etc/hosts entries | स्थिर hosts entries |
| EAI_AGAIN | Temporary DNS failure error | DNS की अस्थायी विफलता |

---

## ⚡ 3-Line Summary
English: Containers on user-defined networks ask Docker's DNS at 127.0.0.11.
English: It resolves container, service and alias names and forwards the rest upstream.
English: Watch Nginx's startup-time resolution and set upstream DNS explicitly.

Hindi: User-defined networks के containers Docker के DNS (127.0.0.11) से पूछते हैं।
Hindi: वह container, service, alias नाम बताता है और बाकी upstream को भेजता है।
Hindi: Nginx की startup-time resolution पर ध्यान दो और upstream DNS साफ़ सेट करो।

---

## ➡️ Next Topic
**174. Network Aliases** - give one container several DNS names, or share one name across containers.
