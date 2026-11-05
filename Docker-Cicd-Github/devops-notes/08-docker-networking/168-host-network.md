# 168. Host Network
# हिंदी में: Host Network

---

## 🔵 Simple Definition (English)
In **host network mode** (`--network host`) the container does not get its own network namespace. It shares the host's network stack directly: same IP, same ports, same interfaces. No NAT, no port mapping, no isolation.

## 🔵 सरल परिभाषा (Hindi)
**Host network mode** (`--network host`) में container का अपना network namespace नहीं होता। वो host का network stack सीधे share करता है: वही IP, वही ports, वही interfaces। NAT नहीं, port mapping नहीं, isolation नहीं।

---

## 🔴 Problem it Solves
Bridge networking adds NAT and a virtual switch, which costs a little latency and CPU and makes some workloads awkward: apps that open thousands of ports (VoIP/RTP, game servers), tools that need to see real host interfaces (packet capture, network monitoring, DHCP), or apps that must see the real client IP. Host mode removes the layer.

## 🔴 यह क्यों बना? (Hindi)
Bridge networking में NAT और virtual switch होता है जो थोड़ा latency और CPU खाता है, और कुछ workloads के लिए असुविधाजनक है: हज़ारों ports खोलने वाले apps (VoIP/RTP, game servers), real host interfaces देखने वाले tools (packet capture, monitoring, DHCP), या जिन्हें real client IP चाहिए। Host mode वो extra layer हटा देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker run --network host myimage
Step 2 → Docker skips creating a new network namespace for the container
Step 3 → The container process sees host interfaces (eth0, lo, docker0...)
Step 4 → If the app listens on :3000, it listens on the HOST's :3000 directly
Step 5 → -p / ports: mappings are IGNORED (Docker warns about it)
Step 6 → Two containers cannot both bind the same port - conflicts like on a normal OS
Step 7 → Container name DNS does not apply; talk to others via localhost:port
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker run --network host myimage
Step 2 → Docker container के लिए नया network namespace नहीं बनाता
Step 3 → Container process को host के interfaces (eth0, lo, docker0...) दिखते हैं
Step 4 → App :3000 पर सुने तो वो सीधे HOST के :3000 पर सुनता है
Step 5 → -p / ports: mappings IGNORE होते हैं (Docker warning देता है)
Step 6 → दो containers एक ही port bind नहीं कर सकते - normal OS जैसा conflict
Step 7 → Container name वाला DNS लागू नहीं; दूसरों से localhost:port से बात करो
```

---

## 🟡 Real World Example
A company runs Prometheus **node_exporter** in Docker to monitor the VPS. It needs the host's real network interfaces and metrics, so it runs with `--network host --pid host`. Another example: a high-throughput WebSocket gateway on a dedicated EC2 instance uses host networking to avoid NAT overhead for 50k connections.

## 🟡 Real Example Hindi mein
एक company VPS monitor करने के लिए Docker में Prometheus **node_exporter** चलाती है। उसे host के real network interfaces और metrics चाहिए, इसलिए `--network host --pid host` से चलता है। दूसरा उदाहरण: dedicated EC2 पर high-throughput WebSocket gateway 50k connections के लिए NAT overhead बचाने को host networking use करता है।

---

## 💻 Code / Config Example — Basic
```bash
# run nginx directly on the host's network
docker run -d --name web --network host nginx:1.27-alpine   # example tag
# nginx now listens on host port 80; there is NO -p flag

curl -I http://localhost:80                  # works from the host itself
docker port web                              # prints nothing: no mappings exist
docker inspect -f '{{.HostConfig.NetworkMode}}' web   # prints: host

docker rm -f web                             # cleanup
```

Note: on Docker Desktop (Mac/Windows) host mode runs inside a VM, so behaviour differs (newer Docker Desktop versions added limited support). Treat host mode as a Linux feature and test on your server.

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - node_exporter in host mode for VPS monitoring
services:
  node-exporter:
    image: prom/node-exporter:v1.8.2        # example tag; update to current
    container_name: node-exporter           # fixed name for easy logs
    network_mode: host                      # share host network (no 'networks:' allowed with this)
    pid: host                               # see host processes for process metrics
    restart: unless-stopped                 # survive reboot
    read_only: true                         # immutable container filesystem
    volumes:
      - /:/host:ro,rslave                   # read-only view of host root for metrics
    command:
      - '--path.rootfs=/host'               # tell exporter where host root is mounted
      - '--web.listen-address=127.0.0.1:9100'  # listen on loopback only, not the public IP
```

```bash
# firewall: with host mode UFW DOES apply (no Docker iptables magic for this container)
sudo ufw allow from 10.0.0.5 to any port 9100 proto tcp   # only the Prometheus server (example IP)
sudo ufw deny 9100/tcp                                    # everyone else blocked
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** do not use host mode for normal APIs; bridge + published port is safer and portable.
- **Nginx:** a containerized Nginx in host mode can bind 80/443 and see real client IPs (`$remote_addr`) without proxy-protocol hacks. On a bridge, client IP is usually preserved for published ports on Linux, but userland-proxy cases can mask it for IPv6.
- **Monitoring:** node_exporter, cAdvisor sidecars, Netdata work well in host mode.
- **VPS/AWS:** security groups still apply at the EC2 level; any port the container opens is instantly on the host's public IP, so bind to `127.0.0.1` when possible.

```yaml
# Nginx container in host mode proxying to a Node app that is also host-mode
services:
  nginx:
    image: nginx:1.27-alpine                # example tag
    network_mode: host                      # nginx binds host :80 directly
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro   # config (proxy_pass http://127.0.0.1:3000)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Adding `ports: ["8080:80"]` together with `network_mode: host` and wondering why it is ignored.
✅ Correct: In host mode the app's own listen port is the host port; change the app config instead.

❌ Mistake 2: Running several host-mode containers that use the same port.
✅ Correct: Assign unique ports per app or use bridge mode.

❌ Mistake 3: Using host mode for convenience and exposing a DB publicly (Mongo on 0.0.0.0:27017).
✅ Correct: Bind to `127.0.0.1` or use bridge networks with no published port.

❌ Mistake 4: Expecting `http://api:3000` DNS names to work.
✅ Correct: Use `localhost:3000` or the host IP.

---

## 🧠 Tricky Interview Question
**Q:** You switched your Node.js container to `network_mode: host` for speed. Now `docker compose up` shows your `db` service unreachable at `db:5432`. Why?

**Answer:** A host-mode container is outside Docker's user-defined networks, so Docker's embedded DNS (127.0.0.11) does not resolve service names for it. It must reach the DB through the host: either publish the DB on `127.0.0.1:5432` and connect to `localhost:5432`, or move everything back to a bridge network. Mixed setups are a common source of confusion.

---

## ⚫ Interview Questions + Answers

Q1: What is host networking?
A1: The container shares the host's network namespace; same IP, interfaces and ports; no NAT.

Q2: Main benefits?
A2: Lower latency/overhead, no port mapping, access to real host interfaces, huge port ranges.

Q3: Main risks?
A3: No network isolation, port conflicts, any listening port is directly exposed, bigger blast radius if compromised.

Q4: Does `-p` work with host mode?
A4: No; it is ignored with a warning.

Q5: Does host mode work on Docker Desktop?
A5: Historically no (runs inside a VM); recent versions have optional support. Always verify on Linux servers.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Monitoring/network tools that need host interfaces
- Very high port counts or performance-critical networking
- Single-purpose dedicated hosts

❌ Avoid when:
- Multi-tenant or multi-app hosts needing isolation
- Typical web APIs (use bridge)
- You rely on Docker DNS service discovery

---

## 📊 Visual Diagram
```
 BRIDGE MODE                         HOST MODE
 +--------------------+              +----------------------------+
 | Host  eth0:80      |              | Host  eth0 (public IP)     |
 |   |  DNAT          |              |                            |
 |  docker0           |              |  [container process]       |
 |   |                |              |   listens directly on :80  |
 | [ctr 172.17.0.2:80]|              |   same IP, same ports      |
 +--------------------+              +----------------------------+
  NAT + isolation                      no NAT, no isolation
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Host mode | Share host network stack | host का network share |
| Network namespace | Isolated network view | अलग network दृश्य |
| network_mode | Compose key to choose mode | Compose में mode चुनना |
| Port conflict | Two apps want same port | एक port, दो दावेदार |
| Blast radius | Damage if compromised | नुकसान का दायरा |
| node_exporter | Host metrics exporter | host metrics देने वाला tool |

---

## ⚡ 3-Line Summary
English: Host mode removes the network layer: container uses the host's IP and ports directly.
It is fast and flexible but gives zero isolation and no Docker DNS.
Use it for monitoring/special cases, not ordinary APIs.
Hindi: Host mode network layer हटा देता है: container host का IP और ports सीधे use करता है।
यह तेज़ और flexible है लेकिन isolation और Docker DNS नहीं मिलता।
Monitoring/खास मामलों में use करो, साधारण APIs में नहीं।

---

## ➡️ Next Topic
**169. None Network** - the opposite extreme: a container with no network at all, for maximum isolation.
