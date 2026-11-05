# 215. Dropping Linux Capabilities
# हिंदी में: Linux Capabilities हटाना (cap_drop)

---

## 🔵 Simple Definition (English)
Linux splits root's power into about 40 separate permissions called capabilities (for example `NET_BIND_SERVICE`, `CHOWN`, `SYS_ADMIN`). Docker gives containers a default subset. Dropping capabilities (`cap_drop: [ALL]`) removes them, and you add back only the few the app truly needs (`cap_add`).

## 🔵 सरल परिभाषा (Hindi)
Linux root की ताकत को लगभग 40 अलग permissions में बाँटता है जिन्हें capabilities कहते हैं (जैसे `NET_BIND_SERVICE`, `CHOWN`, `SYS_ADMIN`)। Docker containers को इनका एक default हिस्सा देता है। Capabilities हटाना (`cap_drop: [ALL]`) इन्हें निकाल देता है, और आप सिर्फ वही वापस जोड़ते हैं (`cap_add`) जो app को सच में चाहिए।

---

## 🔴 Problem it Solves
Even a process running as UID 0 in a container, or a non-root process that finds a setuid binary, can use powers like changing file owners, opening raw sockets (`NET_RAW`, used for ARP spoofing), changing UIDs (`SETUID`) or mounting filesystems. Most web apps need none of these. Leaving them gives attackers extra steps for privilege escalation and lateral movement.

## 🔴 यह क्यों बना? (Hindi)
Container में UID 0 का process, या setuid binary पाने वाला non-root process भी file owners बदलने, raw sockets खोलने (`NET_RAW`, ARP spoofing में काम आता है), UID बदलने (`SETUID`) या filesystems mount करने जैसी ताकतें इस्तेमाल कर सकता है। ज़्यादातर web apps को इनमें से कुछ नहीं चाहिए। इन्हें छोड़ देने से attackers को privilege escalation और lateral movement के अतिरिक्त रास्ते मिलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → The kernel checks a capability bit (not "is root?") for each privileged action
Step 2 → Docker starts containers with a default set (CHOWN, SETUID, NET_BIND_SERVICE, KILL, ...)
Step 3 → You set cap_drop: [ALL] so the process has an empty set
Step 4 → Run the app; if an action needs a capability, it fails with EPERM ("Operation not permitted")
Step 5 → Identify the missing one (logs, strace, capsh --print) and add only it with cap_add
Step 6 → Add no-new-privileges so setuid binaries cannot regain powers
Step 7 → Never use --privileged (it grants all capabilities and device access)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Kernel हर privileged काम के लिए capability bit जाँचता है ("क्या root है?" नहीं)
Step 2 → Docker containers को default set (CHOWN, SETUID, NET_BIND_SERVICE, KILL, ...) के साथ चालू करता है
Step 3 → आप cap_drop: [ALL] रखते हैं ताकि process का set खाली हो
Step 4 → App चलाएँ; किसी काम के लिए capability चाहिए तो वह EPERM ("Operation not permitted") से fail होगा
Step 5 → छूटी हुई capability पहचानें (logs, strace, capsh --print) और सिर्फ वही cap_add करें
Step 6 → no-new-privileges जोड़ें ताकि setuid binaries ताकत वापस न पा सकें
Step 7 → --privileged कभी इस्तेमाल न करें (यह सारी capabilities और device access देता है)
```

---

## 🟡 Real World Example
A hosting company runs customer Node apps in containers. One customer's dependency is compromised and the attacker tries ARP spoofing to sniff traffic of other containers on the same bridge network. The default capability `NET_RAW` allows crafting raw packets, so it could work. After the platform team sets `cap_drop: [ALL]` the raw-socket call returns EPERM and the attack fails. Only the nginx front proxy keeps `NET_BIND_SERVICE` (to bind port 80 without root tricks).

## 🟡 Real Example Hindi mein
एक hosting कंपनी customers की Node apps containers में चलाती है। एक customer की dependency compromise हो जाती है और attacker उसी bridge network के दूसरे containers का traffic sniff करने के लिए ARP spoofing आज़माता है। Default capability `NET_RAW` raw packets बनाने देती है, इसलिए यह चल सकता था। Platform team `cap_drop: [ALL]` लगाती है तो raw-socket call EPERM देता है और attack fail होता है। सिर्फ nginx front proxy के पास `NET_BIND_SERVICE` रहता है (port 80 के लिए)।

---

## 💻 Code / Config Example — Basic
```bash
# See the default vs dropped capabilities (comments per line)
docker run --rm alpine sh -c 'apk add -q libcap && capsh --print | grep Current'   # default set (needs internet; example)
docker run --rm --cap-drop ALL alpine sh -c 'chown nobody /tmp'                     # EPERM: CHOWN was dropped
docker run --rm --cap-drop ALL --cap-add CHOWN alpine sh -c 'chown nobody /tmp && echo ok'  # works after adding back only CHOWN
```
```yaml
# compose.yaml  (Basic: drop everything for a Node API)
services:
  api:
    image: node:20-alpine            # example tag
    command: ["node", "server.js"]   # app needs no special powers on port 3000
    cap_drop:
      - ALL                          # remove every capability
    security_opt:
      - no-new-privileges:true       # setuid binaries cannot add privileges
```

## 💻 Code / Config Example — Advanced
```yaml
# compose.prod.yaml  (Advanced: per-service minimal capabilities)
services:
  api:                                   # Node.js on port 3000, runs as non-root
    image: ghcr.io/acme/api:${TAG}       # pinned image
    user: "10001:10001"                  # non-root (topic 213)
    read_only: true                      # topic 214
    tmpfs: ["/tmp"]
    cap_drop: ["ALL"]                    # needs no capabilities
    security_opt: ["no-new-privileges:true"]
    pids_limit: 200                      # fork-bomb guard
  fastapi:                               # Python on port 8000
    image: ghcr.io/acme/ml:${TAG}
    user: "10001:10001"
    read_only: true
    cap_drop: ["ALL"]
    security_opt: ["no-new-privileges:true"]
  nginx:                                 # edge proxy, official image starts as root then drops to nginx user
    image: nginx:1.27-alpine
    ports: ["80:80", "443:443"]
    cap_drop: ["ALL"]                    # drop everything...
    cap_add:                             # ...then add back what the official image needs at startup
      - CHOWN                            # entrypoint/cache dirs chown
      - SETUID                           # master switches worker user
      - SETGID                           # master switches worker group
      - NET_BIND_SERVICE                 # bind 80/443 (also default in Docker)
    security_opt: ["no-new-privileges:true"]
    tmpfs: ["/var/cache/nginx", "/var/run", "/tmp"]
    read_only: true
  postgres:                              # official image needs a few to chown data dir and switch user
    image: postgres:16-alpine
    cap_drop: ["ALL"]
    cap_add: ["CHOWN", "SETUID", "SETGID", "DAC_OVERRIDE", "FOWNER"]   # typical set; verify for your image/version
    security_opt: ["no-new-privileges:true"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes:
  pgdata: {}
```
Verify on a running container: `docker exec api cat /proc/1/status | grep Cap` (CapEff `0000000000000000` means none). Capability lists above are typical starting points, not guaranteed for every image version; not run here, so test each service and read errors.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** non-root + high port = zero capabilities needed; use `cap_drop: [ALL]`.
- **Nginx:** use `nginx-unprivileged` (port 8080) and drop ALL, or the official image with the four capabilities above.
- **React:** static files only, same as Nginx.
- **Postgres/Redis:** prefer managed RDS/ElastiCache on AWS; if self-hosted, use the minimal add-back list, or run as the data-owning user so `CHOWN`/`SETUID` are unnecessary.
- **Debug tools:** `ping` needs `NET_RAW`; do not add it permanently, use a separate debug container.
- **Security:** never `privileged: true`, never `cap_add: [SYS_ADMIN]` or `ALL`, avoid mounting `/var/run/docker.sock`.

```bash
# audit a running container's capabilities (comments per line)
docker inspect api --format '{{.HostConfig.CapDrop}} {{.HostConfig.CapAdd}} privileged={{.HostConfig.Privileged}}'  # what is configured
docker exec api sh -c 'grep Cap /proc/1/status'    # hex capability sets of PID 1
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `privileged: true` "because something failed".
✅ Correct: Find the one missing capability with the error message and `cap_add` just that.

❌ Mistake 2: `cap_add` without `cap_drop: [ALL]` first, so extra defaults remain.
✅ Correct: Drop ALL, then add the minimum.

❌ Mistake 3: Believing a non-root user makes capabilities irrelevant. Setuid binaries and file capabilities can still elevate.
✅ Correct: Also set `no-new-privileges:true`.

❌ Mistake 4: Giving `SYS_ADMIN` to fix a mount problem. It is nearly root.
✅ Correct: Redesign (volumes) instead of granting it.

---

## 🧠 Tricky Interview Question
A container has `cap_drop: [ALL]`, but the Nginx image still starts and binds port 80. How, if `NET_BIND_SERVICE` was dropped?

Answer: Binding to ports below 1024 normally needs `NET_BIND_SERVICE` in the container's network namespace. If it truly were dropped, bind to 80 would fail with EPERM. Two realistic explanations: the Compose file also re-added it with `cap_add`, or the image is `nginx-unprivileged` listening on 8080 and the host port map (`80:8080`) is done by Docker's proxy outside the container. Also note that modern Docker sets `net.ipv4.ip_unprivileged_port_start=0` inside containers in recent versions, which lets any process bind low ports in the container namespace; so the capability may not be required at all there. (Version-dependent: check `docker exec c cat /proc/sys/net/ipv4/ip_unprivileged_port_start`.)

---

## ⚫ Interview Questions + Answers

Q1: What is a capability?
A1: A fine-grained slice of root privilege, checked by the kernel for each privileged operation.

Q2: Which dangerous capabilities should never be granted?
A2: `SYS_ADMIN`, `SYS_PTRACE`, `SYS_MODULE`, `NET_ADMIN` (unless required), `DAC_READ_SEARCH`; and the `--privileged` flag grants all.

Q3: How do you find the capabilities an app needs?
A3: Start with drop ALL, read EPERM errors, use `strace -f` or run in a test environment, and add back one at a time.

Q4: What does `no-new-privileges` do?
A4: It sets a kernel flag so execve cannot gain extra privileges via setuid/setgid binaries or file capabilities.

Q5: How does this relate to seccomp?
A5: Capabilities restrict which privileged actions are allowed; seccomp restricts which system calls can be made at all. They are complementary (next topic).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every production container, starting from `cap_drop: [ALL]`.

❌ Avoid when:
- Network tools/VPN/monitoring agents that genuinely need `NET_ADMIN`/`NET_RAW`; grant them minimally in isolated containers.
- Docker-in-Docker or low-level system containers (rethink the design first).

---

## 📊 Visual Diagram
```
 root power ->  [CHOWN][SETUID][NET_RAW][SYS_ADMIN][NET_BIND_SERVICE] ... (~40)
 Docker default:  [CHOWN][SETUID][SETGID][KILL][NET_BIND_SERVICE][NET_RAW] ... (~14)
 cap_drop ALL  :  [ ]                                  (empty)
 cap_add       :  [NET_BIND_SERVICE]   <- only what the app proves it needs
 + no-new-privileges  -> setuid cannot bring powers back
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| capability | One slice of root power | root की ताकत का एक हिस्सा |
| cap_drop / cap_add | Remove / add capabilities | capabilities हटाना / जोड़ना |
| NET_BIND_SERVICE | Bind ports under 1024 | 1024 से नीचे के ports bind करना |
| NET_RAW | Raw sockets (ping, spoofing) | raw sockets |
| SYS_ADMIN | Huge catch-all power | बहुत बड़ी सर्वव्यापी ताकत |
| privileged | Container with almost host powers | लगभग host जैसी ताकत वाला container |
| EPERM | Operation not permitted | अनुमति नहीं |

---

## ⚡ 3-Line Summary
English: Capabilities split root into small powers. Use `cap_drop: [ALL]`, add back only what errors prove necessary, and set `no-new-privileges`. Never use `privileged`.
Hindi: Capabilities root को छोटी ताकतों में बाँटती हैं। `cap_drop: [ALL]` रखें, errors से साबित ज़रूरी चीज़ें ही वापस जोड़ें और `no-new-privileges` लगाएँ। `privileged` कभी न करें।

---

## ➡️ Next Topic
**216. Seccomp Profiles**: after limiting powers, we filter which system calls a container may make.
