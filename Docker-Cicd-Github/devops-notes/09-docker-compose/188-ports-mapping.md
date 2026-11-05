# 188. ports Mapping
# हिंदी में: `ports` Mapping

---

## 🔵 Simple Definition (English)
`ports:` publishes a container port on the host machine so that outside clients can reach it. The format is `HOST:CONTAINER`. `expose:` only documents a port for other containers; it does not open anything on the host.

## 🔵 सरल परिभाषा (Hindi)
`ports:` container के port को host machine पर publish करता है ताकि बाहर के clients पहुँच सकें। Format है `HOST:CONTAINER`। `expose:` सिर्फ दूसरे containers के लिए port document करता है; host पर कुछ नहीं खोलता।

---

## 🔴 Problem it Solves
Containers live in their own network namespace; a browser on your laptop (or a user on the Internet) cannot reach `172.18.0.3:3000`. Without port publishing the app is invisible. But publishing too much is dangerous: a Postgres published as `5432:5432` on a public VPS is scanned and attacked within minutes. `ports` gives controlled exposure, including binding to `127.0.0.1` only.

## 🔴 यह क्यों बना? (Hindi)
Containers अपने network namespace में रहते हैं; आपके laptop का browser (या Internet का user) `172.18.0.3:3000` तक नहीं पहुँच सकता। Port publish न करो तो app दिखेगा ही नहीं। पर ज़रूरत से ज़्यादा publish करना खतरनाक है: public VPS पर `5432:5432` से Postgres कुछ ही मिनटों में scan और attack हो जाता है। `ports` नियंत्रित exposure देता है, जिसमें सिर्फ `127.0.0.1` पर bind करना भी शामिल है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write ports: ["8080:80"].
Step 2 → Docker adds iptables/nftables DNAT rule: host:8080 -> container:80.
Step 3 → A starter docker-proxy (or kernel NAT) forwards packets.
Step 4 → Client hits http://VPS_IP:8080 and reaches the container's port 80.
Step 5 → Container-to-container traffic ignores `ports` and uses the container port directly.
Step 6 → `docker compose port web 80` / `docker compose ps` shows actual mapping.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप लिखते हैं ports: ["8080:80"]।
Step 2 → Docker iptables/nftables में DNAT rule जोड़ता है: host:8080 -> container:80।
Step 3 → docker-proxy (या kernel NAT) packets आगे भेजता है।
Step 4 → Client http://VPS_IP:8080 मारता है और container के port 80 तक पहुँचता है।
Step 5 → Container-to-container traffic `ports` को ignore करके सीधे container port use करता है।
Step 6 → `docker compose port web 80` / `docker compose ps` असली mapping दिखाता है।
```

---

## 🟡 Real World Example
A developer published `"5432:5432"` and `"6379:6379"` on an EC2 box. UFW showed only ports 22/80/443 allowed, yet Redis was compromised: Docker inserts its own iptables rules that bypass UFW. After the incident the fix was `"127.0.0.1:5432:5432"` for local debugging via SSH tunnel and no publishing at all in production. Only nginx publishes 80 and 443.

## 🟡 Real Example Hindi mein
एक developer ने EC2 पर `"5432:5432"` और `"6379:6379"` publish किए। UFW में सिर्फ 22/80/443 allowed थे, फिर भी Redis hack हुआ: Docker अपने iptables rules डालता है जो UFW को bypass करते हैं। घटना के बाद fix: local debugging के लिए `"127.0.0.1:5432:5432"` (SSH tunnel से) और production में बिल्कुल publish नहीं। सिर्फ nginx 80 और 443 publish करता है।

---

## 💻 Code / Config Example — Basic

```yaml
services:                       # containers
  web:                          # nginx web server
    image: nginx:1.27-alpine    # example tag
    ports:                      # list of published ports
      - "8080:80"               # host 8080 -> container 80 (quote it!)
  api:                          # backend
    image: node:20-alpine       # example tag
    command: node -e "require('http').createServer((q,s)=>s.end('ok')).listen(3000)"  # tiny demo server
    expose:                     # not published to host, only for other containers
      - "3000"                  # documentation + inter-container access
```

## 💻 Code / Config Example — Advanced

```yaml
services:                             # containers
  nginx:                              # public reverse proxy
    image: nginx:1.27-alpine          # example tag
    ports:                            # published ports
      - "80:80"                       # HTTP on all interfaces
      - "443:443"                     # HTTPS on all interfaces
      - target: 443                   # long syntax: container port
        published: "8443"             # host port (quoted string/int)
        protocol: udp                 # HTTP/3 (QUIC) uses UDP
        mode: host                    # bind directly on host (vs swarm ingress)
  api:                                # FastAPI backend
    image: ghcr.io/addyrj/fastapi-app:1.4.2   # example image
    ports:                            # debugging port
      - "127.0.0.1:8000:8000"         # reachable ONLY from the VPS itself (SSH tunnel)
  db:                                 # PostgreSQL
    image: postgres:16-alpine         # example tag
    ports:                            # optional dev access
      - "127.0.0.1:5433:5432"         # local-only, host 5433 avoids clash with local postgres
    environment:                      # config
      POSTGRES_PASSWORD: ${DB_PASSWORD:?required}   # fail if unset
  metrics:                            # container with random host port
    image: prom/node-exporter:v1.8.1  # example tag
    ports:                            # published ports
      - "127.0.0.1::9100"             # Docker picks a random free host port on loopback
  ranges:                             # range example
    image: alpine:3.20                # example tag
    command: ["sleep", "infinity"]    # keep alive
    ports:                            # port range
      - "9000-9002:9000-9002"         # three consecutive ports
```

Access the db on a VPS safely: `ssh -L 5433:127.0.0.1:5433 user@vps` then connect to localhost:5433 from your laptop.

---

## 🟠 My Stack Integration
Only nginx publishes ports. FastAPI (8000), Node (3000), Redis, Postgres remain unpublished. React is served either by nginx directly or via a web container behind nginx.

```yaml
services:                            # VPS stack
  nginx:                             # only public service
    image: nginx:1.27-alpine         # example tag
    ports:                           # public ports
      - "80:80"                      # redirect to https
      - "443:443"                    # TLS
    depends_on: [api]                # start order
  api:                               # FastAPI behind nginx
    image: ghcr.io/addyrj/fastapi-app:1.4.2   # example image
    expose: ["8000"]                 # internal only; nginx uses proxy_pass http://api:8000
  # nginx location block example (conf file, not compose):
  #   location /api/ { proxy_pass http://api:8000/; }
```

Security: Docker publishes to `0.0.0.0` by default and bypasses UFW; bind to `127.0.0.1` when not needed externally, use the AWS Security Group as the real firewall, and consider the `DOCKER-USER` iptables chain for restrictions.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `ports: - 22:22` unquoted (YAML base-60 can parse `xx:yy` under 60 as a number).
✅ Correct: Always quote: `"22:22"`.

❌ Mistake 2: Publishing database ports on a public server.
✅ Correct: No `ports` or `127.0.0.1:` binding.

❌ Mistake 3: App listens on `127.0.0.1` inside the container, so the published port gives "connection reset".
✅ Correct: Bind to `0.0.0.0` in the app (uvicorn `--host 0.0.0.0`).

❌ Mistake 4: Reversing order: `"80:8080"` when the app listens on 80.
✅ Correct: It is HOST:CONTAINER.

❌ Mistake 5: Using `ports` to connect between containers via host port.
✅ Correct: Use `http://api:3000` (container port).

---

## 🧠 Tricky Interview Question
"UFW denies port 6379, yet an external scanner reaches your Redis container. Why?"

Answer: Docker writes its own rules into the `nat` and `FORWARD` iptables chains before UFW's rules are evaluated, so published ports are reachable even though UFW looks closed. Remove the publish, bind to 127.0.0.1, filter in the `DOCKER-USER` chain, and rely on cloud Security Groups.

---

## ⚫ Interview Questions + Answers

Q1: `ports` vs `expose`?
A1: `ports` publishes to the host; `expose` only documents/allows container-to-container access (which already works inside one network).

Q2: How to publish only on localhost?
A2: `"127.0.0.1:8080:80"`.

Q3: What happens when host port is taken?
A3: Compose fails with "port is already allocated". Change host port or stop the other process.

Q4: Why quote ports?
A4: YAML may interpret `22:22` as a sexagesimal number (1342).

Q5: Can you publish UDP?
A5: Yes: `"53:53/udp"` or long syntax `protocol: udp`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Only the entry point (nginx/ALB target) needs outside access.
- Local development access to api/db via localhost.

❌ Avoid when:
- Service is used only by other containers.
- Production databases, caches, admin panels.

---

## 📊 Visual Diagram
```
 Internet --> :443 [AWS SG] --> VPS eth0
                                   |  DNAT (Docker iptables)
                                   v
      +---------- docker bridge network ----------+
      | [nginx:443] --http://api:8000--> [api]    |
      |                                   |       |
      |                         [postgres :5432]  |  <- no `ports`, unreachable from outside
      +-------------------------------------------+
 ports: "443:443"  (nginx only)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| publish | Open container port on host | container port को host पर खोलना |
| expose | Mark internal port | internal port चिह्नित करना |
| DNAT | Address translation rule | address translation नियम |
| loopback bind | Listen on 127.0.0.1 only | सिर्फ 127.0.0.1 पर सुनना |
| DOCKER-USER | iptables chain for custom rules | custom rules की iptables chain |

---

## ⚡ 3-Line Summary
English: `ports: "HOST:CONTAINER"` makes a container reachable from outside.
English: Docker bypasses UFW, so publish only what is needed and bind to 127.0.0.1 otherwise.
English: Containers talk to each other on container ports, never through host ports.
Hindi: `ports: "HOST:CONTAINER"` container को बाहर से reachable बनाता है।
Hindi: Docker UFW को bypass करता है, इसलिए सिर्फ ज़रूरी publish करें और बाकी `127.0.0.1` पर bind करें।
Hindi: Containers आपस में container port पर बात करते हैं, host port से कभी नहीं।

---

## ➡️ Next Topic
189. environment Variables - configuration (DB URLs, secrets, modes) is passed into containers with `environment:`.
