# 176. Port Mapping Strategies
# हिंदी में: Port Mapping की रणनीतियाँ

---

## 🔵 Simple Definition (English)
**Port mapping strategy** is the plan for which container ports you publish, on which host interface and which host port numbers. Choices include fixed, random, loopback-only, per-environment variable ports, and "one public port with a reverse proxy in front of many apps".

## 🔵 सरल परिभाषा (Hindi)
**Port mapping strategy** वह योजना है कि कौन-से container ports, किस host interface और किन host port नंबरों पर publish करने हैं। विकल्प हैं: fixed, random, सिर्फ loopback, environment-variable वाले ports, और "एक public port + सामने reverse proxy जो कई apps सँभाले"।

---

## 🔴 Problem it Solves
On one VPS you may run 10 apps that all listen on 3000 or 8000 inside their containers. Two cannot both bind host port 3000. Hard-coded ports clash between dev, staging and prod; random ports are unpredictable; opening too many ports expands the attack surface. A deliberate strategy avoids conflicts, keeps configs portable and the firewall rules short.

## 🔴 यह क्यों बना? (Hindi)
एक VPS पर 10 apps हो सकती हैं जो सब container के अंदर 3000 या 8000 पर सुनती हैं। दो apps host port 3000 नहीं ले सकतीं। Hard-coded ports dev, staging और prod में टकराते हैं; random ports का अनुमान नहीं लगता; बहुत ports खोलने से attack surface बढ़ता है। सोची-समझी strategy conflicts रोकती है, configs portable रखती है और firewall rules छोटे रखती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List every service and decide: public, host-only, or internal-only
Step 2 → Internal-only: no mapping at all, use network + service name
Step 3 → Host-only (reverse proxy on host / debugging): map to 127.0.0.1:<hostport>:<containerport>
Step 4 → Public: only the proxy (80/443) is mapped; apps are reached by hostname/path routing
Step 5 → Make host ports variables (${API_PORT:-3000}) so each environment/project picks its own
Step 6 → Document a port table; verify with docker ps and ss -tlnp; allow only 80/443/22 in firewall
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर service की सूची बनाओ और तय करो: public, host-only या internal-only
Step 2 → Internal-only: कोई mapping नहीं, network + service name इस्तेमाल करो
Step 3 → Host-only (host का reverse proxy / debug): 127.0.0.1:<hostport>:<containerport> से map करो
Step 4 → Public: सिर्फ proxy (80/443) map हो; apps hostname/path routing से पहुँचती हैं
Step 5 → Host ports को variables बनाओ (${API_PORT:-3000}) ताकि हर environment/project अपना port चुने
Step 6 → Port table लिखो; docker ps और ss -tlnp से जाँचो; firewall में सिर्फ 80/443/22 खोलो
```

---

## 🟡 Real World Example
Your VPS hosts `shop.example.com`, `admin.example.com` and `blog.example.com`. Each stack's API listens on 3000 internally. Host mapping: shop `127.0.0.1:3101`, admin `127.0.0.1:3102`, blog `127.0.0.1:3103`. A host-level Nginx listens on 80/443 and routes by `server_name` to those loopback ports. Result: one public entry point, no port clashes, trivial firewall.

## 🟡 Real Example Hindi mein
आपकी VPS पर `shop.example.com`, `admin.example.com` और `blog.example.com` हैं। हर stack की API अंदर 3000 पर सुनती है। Host mapping: shop `127.0.0.1:3101`, admin `127.0.0.1:3102`, blog `127.0.0.1:3103`। Host का Nginx 80/443 पर सुनता है और `server_name` से इन loopback ports पर भेजता है। नतीजा: एक public entry, कोई port टकराव नहीं, और firewall आसान।

---

## 💻 Code / Config Example — Basic
```bash
# 1) Fixed mapping: host 8080 -> container 3000 (simple, predictable)
docker run -d --name app1 -p 8080:3000 myrepo/api:1.0.0

# 2) Same container port reused by a second app with a different host port
docker run -d --name app2 -p 8081:3000 myrepo/api:1.0.0

# 3) Loopback only: reachable from the VPS itself (e.g. host Nginx), not the internet
docker run -d --name app3 -p 127.0.0.1:3103:3000 myrepo/api:1.0.0

# 4) Let Docker choose a free host port (good for tests / CI)
docker run -d --name ci-test -p 3000 myrepo/api:1.0.0      # only container port given
docker port ci-test 3000                                    # discover the random host port

# 5) Range mapping
docker run -d --name multi -p 7000-7002:7000-7002 myrepo/ws:1.0.0   # three consecutive ports

# See all mappings
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - parameterised ports, per-environment via .env
# .env (not committed with secrets) example:
#   BIND_ADDR=127.0.0.1
#   API_PORT=3101
#   WEB_PORT=8101
services:
  api:
    image: myrepo/api:${API_TAG:-1.0.0}     # image tag from env, default 1.0.0
    ports:
      - "${BIND_ADDR:-127.0.0.1}:${API_PORT:-3000}:3000"   # safe default = loopback
    restart: unless-stopped                 # recover after reboot

  web:
    image: myrepo/web:${WEB_TAG:-1.0.0}     # nginx image serving React build
    ports:
      - target: 80                          # long syntax: container port
        host_ip: ${BIND_ADDR:-127.0.0.1}    # bind interface
        published: "${WEB_PORT:-8080}"      # host port (string allowed for ranges)
        protocol: tcp                       # protocol
        mode: host                          # host mode: no routing mesh (Swarm)
    restart: unless-stopped
```
```nginx
# /etc/nginx/conf.d/shop.conf on the HOST - one public entry routes to loopback ports
server {
    listen 80;                               # public HTTP (redirect to 443 in real life)
    server_name shop.example.com;            # route by hostname
    location /api/ {
        proxy_pass http://127.0.0.1:3101;    # shop API (compose published on loopback)
        proxy_set_header Host $host;         # preserve host header
        proxy_set_header X-Real-IP $remote_addr;   # pass client IP
    }
    location / {
        proxy_pass http://127.0.0.1:8101;    # shop web (nginx with React build)
    }
}
server {
    listen 80;
    server_name admin.example.com;           # second app
    location / { proxy_pass http://127.0.0.1:3102; }   # admin stack
}
```

---

## 🟠 My Stack Integration
Recommended table for one VPS:

| Service | Container port | Host mapping | Public? |
|---|---|---|---|
| host Nginx | 80/443 | 0.0.0.0:80/443 | Yes |
| Node API (shop) | 3000 | 127.0.0.1:3101 | Via Nginx |
| FastAPI (ml) | 8000 | 127.0.0.1:8101 | Via Nginx |
| React (static) | 80 | 127.0.0.1:8201 | Via Nginx |
| Postgres/Mongo/Redis | 5432/27017/6379 | none | No |

```bash
# AWS: security group inbound = 22 (your IP), 80, 443 only. Verify nothing else listens publicly:
sudo ss -tlnp | awk '$4 ~ /^0\.0\.0\.0|^\[::\]/'      # anything here is world-reachable on the host
```
Security: loopback bindings keep apps invisible to scanners; Nginx adds TLS, rate limiting and headers. Remember Docker bypasses UFW for published ports. Nginx config is not tested with `nginx -t` (nginx not installed here).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Two containers mapped to the same host port.
✅ Correct: Unique host ports (or a proxy); Docker errors "port is already allocated".

❌ Mistake 2: Publishing `3000:3000` for every app and opening them in the security group.
✅ Correct: Loopback + reverse proxy; open only 80/443.

❌ Mistake 3: Hard-coding host ports in Compose for all environments.
✅ Correct: `${API_PORT:-3000}` with per-env `.env`.

❌ Mistake 4: Using random ports in prod without service discovery.
✅ Correct: Random only for CI/tests; prod uses fixed documented ports.

---

## 🧠 Tricky Interview Question
`docker compose up` fails with "bind: address already in use" for port 80, but `docker ps` shows nothing on 80. What do you check?

Answer: Something outside Docker holds the port: host Nginx/Apache, another compose project that is stopped but a `docker-proxy` remains, or systemd socket activation. Run `sudo ss -tlnp | grep :80` or `lsof -i :80`, stop/disable the other service, or change the mapping. Also check IPv6 (`[::]:80`) since the conflict can be on the v6 listener.

---

## ⚫ Interview Questions + Answers

Q1: Syntax of port mapping?
A1: `-p [hostIP:]hostPort:containerPort[/proto]`.

Q2: Why bind to 127.0.0.1?
A2: Keeps the port off the public interface; only local processes (host reverse proxy) can connect.

Q3: How do you run many apps that use port 3000?
A3: Same container port, different host ports (or no host port with a containerised proxy on a shared network).

Q4: Host mode vs ingress mode (Swarm)?
A4: Ingress uses routing mesh on all nodes; host mode binds only on the node running the task.

Q5: How to find a random port?
A5: `docker port <container>` or `docker inspect`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Fixed ports: stable public edge and documented infra
- Loopback: host-level reverse proxy
- Random: parallel CI test runs

❌ Avoid when:
- Mapping internal services at all
- Hard-coding ports in shared images/compose files
- Using privileged ports below 1024 inside the app without need (use host mapping instead)

---

## 📊 Visual Diagram
```
 Internet :443
     |
 [host Nginx 0.0.0.0:80/443]
     |-- shop.example.com  -> 127.0.0.1:3101 -> [shop-api  :3000]
     |-- admin.example.com -> 127.0.0.1:3102 -> [admin-api :3000]
     |-- ml.example.com    -> 127.0.0.1:8101 -> [fastapi   :8000]
 (databases: no mapping, internal docker networks only)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Host port | Port on the server | Server का port |
| Container port | Port inside container | Container के अंदर का port |
| Loopback binding | 127.0.0.1 only | सिर्फ local binding |
| Reverse proxy | Front server routing to apps | आगे बैठा routing server |
| Ephemeral port | Random high port | Random ऊँचा port |
| docker-proxy | Userland proxy process | Userland proxy process |

---

## ⚡ 3-Line Summary
English: Plan ports: internal none, debug on loopback, one public proxy on 80/443.
English: Parameterise host ports with env vars to avoid clashes across projects.
English: Verify with docker ps and ss, and lock the cloud firewall to 22/80/443.

Hindi: Ports की योजना बनाओ: internal पर कुछ नहीं, debug loopback पर, एक public proxy 80/443 पर।
Hindi: Host ports को env variables से तय करो ताकि projects में टकराव न हो।
Hindi: docker ps और ss से जाँचो, और cloud firewall में सिर्फ 22/80/443 रखो।

---

## ➡️ Next Topic
**177. Network Security** - hardening Docker networks: firewalls, TLS, internal networks and least privilege.
