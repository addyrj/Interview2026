---

# 134. Port Mapping (-p)
# हिंदी में: Port Mapping (-p)

---

## 🔵 Simple Definition (English)
Port mapping publishes a container's internal port on the host machine: `-p HOST_PORT:CONTAINER_PORT`. Without it, a container's ports are reachable only from inside Docker networks, not from your browser or the internet.

## 🔵 सरल परिभाषा (Hindi)
Port mapping container के अंदर वाले port को host machine पर publish करता है: `-p HOST_PORT:CONTAINER_PORT`। इसके बिना container के ports सिर्फ़ Docker networks के अंदर से पहुँच में होते हैं, browser या internet से नहीं।

---

## 🔴 Problem it Solves
Each container has its own network namespace and private IP (like 172.17.0.2). Your laptop or the internet cannot reach that IP directly. Also ten containers may all listen on port 3000 internally, which would clash on one host. Port mapping gives each container a unique host port (or interface) and forwards traffic to the right one.

## 🔴 यह क्यों बना? (Hindi)
हर container का अपना network namespace और private IP (जैसे 172.17.0.2) होता है। आपका laptop या internet उसे सीधे नहीं पहुँच सकता। साथ ही दस containers अंदर से port 3000 सुन सकते हैं, जो एक host पर टकराएगा। Port mapping हर container को unique host port (या interface) देता है और traffic सही जगह forward करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run: docker run -p 8080:3000 app   (host 8080 -> container 3000)
Step 2 → dockerd adds iptables NAT rules (DNAT in the DOCKER chain) for host port 8080
Step 3 → dockerd also starts docker-proxy for some cases (e.g. localhost/IPv6 hairpin)
Step 4 → Packet arrives at host:8080 -> rewritten to 172.17.0.2:3000 -> reaches your app
Step 5 → Reply goes back through connection tracking to the client
```
Important: the app must listen on `0.0.0.0` inside, not `127.0.0.1`.

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप चलाते हैं: docker run -p 8080:3000 app   (host 8080 -> container 3000)
Step 2 → dockerd DOCKER chain में iptables NAT (DNAT) rules जोड़ता है
Step 3 → कुछ cases (localhost/IPv6) के लिए docker-proxy भी चलता है
Step 4 → Packet host:8080 पर आता है -> 172.17.0.2:3000 में बदलता है -> app तक पहुँचता है
Step 5 → जवाब connection tracking से वापस client को जाता है
```
ज़रूरी: app को अंदर `0.0.0.0` पर listen करना चाहिए, `127.0.0.1` पर नहीं।

---

## 🟡 Real World Example
On your EC2 VPS you run three Node.js services, all listening on 3000 inside. Map them to host ports 127.0.0.1:3001, 3002, 3003. Host Nginx routes `api.site.com` to 3001, `admin.site.com` to 3002. Only Nginx (80/443) is open in the AWS Security Group; the app ports are never public. A team that wrote `-p 3001:3001` (all interfaces) once exposed an admin panel to the internet, because Docker edits iptables directly and bypasses UFW rules.

## 🟡 Real Example Hindi mein
EC2 VPS पर तीन Node.js services, सब अंदर 3000 पर। उन्हें host पर 127.0.0.1:3001, 3002, 3003 से map करो। Host Nginx `api.site.com` को 3001 और `admin.site.com` को 3002 पर भेजता है। AWS Security Group में सिर्फ़ Nginx (80/443) खुला है; app ports कभी public नहीं। एक team ने `-p 3001:3001` (सभी interfaces) लिखा और admin panel internet पर खुल गया, क्योंकि Docker सीधे iptables बदलता है और UFW rules को bypass करता है।

---

## 💻 Code / Config Example — Basic
```bash
#!/usr/bin/env bash
# port-basic.sh - port mapping forms
docker run -d --name p1 -p 8080:80 nginx:1.27-alpine                # host 8080 -> container 80 (all interfaces)
docker run -d --name p2 -p 127.0.0.1:8081:80 nginx:1.27-alpine      # only reachable from the host itself
docker run -d --name p3 -p 80 nginx:1.27-alpine                     # random free host port -> container 80
docker run -d --name p4 -P nginx:1.27-alpine                        # -P publishes ALL EXPOSEd ports on random ports
docker run -d --name p5 -p 5353:53/udp alpine:3.20 sleep 600        # UDP mapping (default is tcp)
docker run -d --name p6 -p 8000-8002:8000-8002 alpine:3.20 sleep 600 # port range

docker port p1                      # list mappings: 80/tcp -> 0.0.0.0:8080
docker port p3 80                   # which host port did Docker pick for 80?
docker ps --format '{{.Names}} {{.Ports}}'   # mappings in table form
curl -s -o /dev/null -w '%{http_code}\n' localhost:8080   # expect 200
docker rm -f p1 p2 p3 p4 p5 p6      # cleanup
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - safe port publishing for a full stack
services:
  nginx:
    image: nginx:1.27-alpine               # example tag
    ports:
      - "80:80"                            # public HTTP, the ONLY intentionally public ports
      - "443:443"                          # public HTTPS
    depends_on:
      - api                                # start api before nginx
    networks: [frontend]                   # talks to api over internal network

  api:
    image: myorg/orders-api:1.4.2          # example pinned image
    expose:
      - "3000"                             # documents port; reachable by containers on same network only
    ports:
      - "127.0.0.1:3000:3000"              # optional: also reachable from host for debugging
    networks: [frontend, backend]          # bridges web tier and db tier

  db:
    image: postgres:16-alpine              # example tag
    # NO ports: section at all - the database is never published
    networks: [backend]                    # only api can reach it by hostname "db"

networks:
  frontend: {}                             # nginx <-> api
  backend:
    internal: true                         # no outside connectivity at all for this network
```
```bash
# Debug mapping problems
sudo iptables -t nat -L DOCKER -n          # see DNAT rules Docker added (Linux host)
ss -ltnp | grep -E ':80|:3000'             # who is listening on host ports?
docker inspect -f '{{json .NetworkSettings.Ports}}' orders-api   # mappings as JSON
```

---

## 🟠 My Stack Integration
**Node.js**: `app.listen(3000, '0.0.0.0')` (Express default already listens on all interfaces; check frameworks that default to localhost).
**FastAPI**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`; the default `127.0.0.1` makes `-p` look broken.
**React**: Nginx image listens on 80; map `127.0.0.1:8081:80` and proxy from the host Nginx, or let it own 80/443.
**VPS/AWS**: Security Group opens only 22 (your IP), 80, 443. Do not rely on UFW for Docker-published ports; bind to 127.0.0.1 or add rules in the `DOCKER-USER` iptables chain.

```nginx
# host Nginx: two apps, each published on localhost only (not tested here)
upstream orders { server 127.0.0.1:3001; }      # container 1 published on 127.0.0.1:3001
upstream admin  { server 127.0.0.1:3002; }      # container 2 published on 127.0.0.1:3002
server {
  listen 80;                                    # HTTP entry (add TLS in real use)
  server_name api.example.com;                  # domain for app 1
  location / { proxy_pass http://orders; }      # forward to container
}
server {
  listen 80;                                    # same port, different server_name
  server_name admin.example.com;                # domain for app 2
  location / { proxy_pass http://admin; }       # forward to container
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Swapping order: `-p 3000:8080` when the app listens on 3000.
✅ Correct: it is always HOST:CONTAINER. Container port must match what the app listens on.

❌ Mistake 2: Publishing databases (`-p 5432:5432`, `-p 27017:27017`) on a public server.
✅ Correct: no `-p`; let the app reach the DB over a Docker network, or bind to 127.0.0.1.

❌ Mistake 3: Trusting UFW to block Docker ports.
✅ Correct: Docker's iptables rules come first. Bind to 127.0.0.1 or use the `DOCKER-USER` chain, plus the cloud Security Group.

❌ Mistake 4: App listens on 127.0.0.1 inside the container.
✅ Correct: use `0.0.0.0` inside.

❌ Mistake 5: Thinking `EXPOSE` in a Dockerfile publishes the port.
✅ Correct: `EXPOSE` is documentation only; `-p` or `-P` actually publishes.

---

## 🧠 Tricky Interview Question
Container A calls container B on the same user-defined network. Do you need `-p` on B?

Answer: No. Containers on the same network reach each other directly via `B_name:CONTAINER_PORT`, no publishing needed. `-p` is only for traffic from the host or outside. Publishing B anyway would needlessly expose it. Also note: use the container port, not the host port, in A's connection URL.

---

## ⚫ Interview Questions + Answers

Q1: What does `-p 8080:80` mean?
A1: Traffic to host port 8080 is forwarded to port 80 in the container.

Q2: Difference between `-p` and `-P`?
A2: `-p` maps specific ports; `-P` maps all EXPOSEd ports to random high host ports.

Q3: What does `EXPOSE` do?
A3: Metadata/documentation only (and used by `-P`); it does not open ports.

Q4: How do you make a port reachable only from the host?
A4: Bind to the loopback: `-p 127.0.0.1:8080:80`.

Q5: Why can Docker ports ignore UFW?
A5: Docker inserts its own iptables rules (nat and filter) ahead of UFW's chains, so published ports can be open even if UFW denies them.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Edge services (Nginx, one API) must be reached from outside.
- Local development and debugging.

❌ Avoid when:
- Container-to-container traffic: use networks and service names.
- Databases, caches, queues: keep unpublished.

---

## 📊 Visual Diagram
```
 Internet --> AWS Security Group (80,443 only)
                    |
            [ VPS host ]
   :80/:443 --> Nginx --> 127.0.0.1:3001 ==DNAT==> [api container 172.18.0.3:3000]
                                                         |  network "backend"
                                                         v
                                                  [db 172.19.0.2:5432]  (no -p)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Publish | Open container port on host | Host पर port खोलना |
| DNAT | Rewrites destination address | Destination address बदलना |
| EXPOSE | Documents a port, does not open it | सिर्फ़ दस्तावेज़ |
| Loopback | 127.0.0.1, host-only interface | सिर्फ़ host का interface |
| Security Group | AWS virtual firewall | AWS का firewall |

---

## ⚡ 3-Line Summary
English: `-p HOST:CONTAINER` forwards host traffic into the container via iptables NAT.
Publish only edge ports, bind to 127.0.0.1 behind Nginx, never publish databases.
EXPOSE does not publish, and Docker can bypass UFW.

Hindi: `-p HOST:CONTAINER` iptables NAT से host का traffic container में भेजता है।
सिर्फ़ edge ports publish करें, Nginx के पीछे 127.0.0.1 पर bind करें, database कभी publish न करें।
EXPOSE publish नहीं करता, और Docker UFW को bypass कर सकता है।

---

## ➡️ Next Topic
**135. Environment Variables in Container**: ports tell the app where to listen; environment variables tell it how to behave and where its database is.
