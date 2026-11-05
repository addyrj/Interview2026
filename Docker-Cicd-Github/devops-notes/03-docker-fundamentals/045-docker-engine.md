# 45. Docker Engine
# हिंदी में: Docker Engine (इंजन)

---

## 🔵 Simple Definition (English)
**Docker Engine** is the open-source container runtime product you install on a Linux server. It bundles the **daemon** (`dockerd`), the **REST API**, the **CLI** (`docker`), and the components underneath (containerd, runc, BuildKit). "Docker Engine" is what runs on your VPS; "Docker Desktop" is the laptop app that wraps an Engine inside a VM.

## 🔵 सरल परिभाषा (Hindi)
**Docker Engine** वह open-source container runtime product है जिसे आप Linux server पर install करते हैं। इसमें **daemon** (`dockerd`), **REST API**, **CLI** (`docker`), और नीचे के components (containerd, runc, BuildKit) शामिल हैं। "Docker Engine" आपके VPS पर चलता है; "Docker Desktop" laptop की app है जो VM के अंदर Engine चलाती है।

---

## 🔴 Problem it Solves
Without a packaged engine, you would compile and wire a runtime, storage driver, network plumbing, and image builder yourself, and keep them compatible. Docker Engine provides a tested, versioned bundle with one install command, an auto-start systemd service, sane defaults (bridge network, overlay2 storage), and an API for tooling.

## 🔴 यह क्यों बना? (Hindi)
Packaged engine के बिना आपको runtime, storage driver, network plumbing और image builder खुद compile करके जोड़ने पड़ते और उन्हें compatible रखना पड़ता। Docker Engine एक tested, versioned bundle देता है: एक install command, auto-start systemd service, समझदार defaults (bridge network, overlay2 storage), और tools के लिए API।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install Engine from Docker's apt repo (docker-ce, containerd.io, buildx, compose plugin)
Step 2 → systemd starts docker.service -> dockerd, which starts/attaches to containerd
Step 3 → dockerd opens /var/run/docker.sock (root:docker 660) for the API
Step 4 → Storage driver overlay2 keeps images/containers under /var/lib/docker
Step 5 → Networking: creates docker0 bridge, manages iptables NAT for published ports
Step 6 → BuildKit handles `docker build`; compose plugin handles `docker compose`
Step 7 → Reads /etc/docker/daemon.json at start for custom settings
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Docker के apt repo से Engine install करो (docker-ce, containerd.io, buildx, compose plugin)
Step 2 → systemd docker.service -> dockerd शुरू करता है, जो containerd शुरू/attach करता है
Step 3 → dockerd API के लिए /var/run/docker.sock (root:docker 660) खोलता है
Step 4 → Storage driver overlay2 images/containers को /var/lib/docker में रखता है
Step 5 → Networking: docker0 bridge बनाता है, published ports के लिए iptables NAT संभालता है
Step 6 → `docker build` को BuildKit और `docker compose` को compose plugin संभालता है
Step 7 → शुरू होते समय custom settings के लिए /etc/docker/daemon.json पढ़ता है
```

---

## 🟡 Real World Example
You rent a $6 Ubuntu VPS for your Node.js + FastAPI + React stack. You SSH in, install Docker Engine from the official repository, add a `deploy` user, enable the service, and within ten minutes the whole stack runs from one `docker-compose.yml`. On AWS you do the same on an EC2 instance, or use an ECS-optimized AMI that has Engine pre-installed.

## 🟡 Real Example Hindi mein
आप Node.js + FastAPI + React stack के लिए $6 का Ubuntu VPS लेते हैं। SSH करके official repository से Docker Engine install करते हैं, `deploy` user जोड़ते हैं, service enable करते हैं, और दस मिनट में पूरा stack एक `docker-compose.yml` से चलने लगता है। AWS पर यही EC2 instance पर करते हैं, या ECS-optimized AMI इस्तेमाल करते हैं जिसमें Engine पहले से होता है।

---

## 💻 Code / Config Example — Basic
```bash
#!/usr/bin/env bash
# install-docker.sh - Docker Engine on Ubuntu (follows Docker's documented apt method;
# commands/URLs can change, verify at docs.docker.com/engine/install/ubuntu before use)
set -euo pipefail                                   # stop on error, unset var, or pipe failure

sudo apt-get update                                 # refresh package lists
sudo apt-get install -y ca-certificates curl        # tools needed to fetch the GPG key
sudo install -m 0755 -d /etc/apt/keyrings           # directory for apt signing keys
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc   # Docker's signing key
sudo chmod a+r /etc/apt/keyrings/docker.asc         # make key readable by apt

# Add Docker's apt repository for this Ubuntu release and CPU architecture
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update                                 # read the new repository
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin   # the Engine bundle
sudo systemctl enable --now docker                  # start now and on every boot
sudo docker run --rm hello-world                    # smoke test: pulls and runs a tiny image
docker --version                                    # print installed client version
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# harden-docker-host.sh - post-install setup for a production VPS (run as a sudo user)
set -euo pipefail                                   # strict mode

sudo adduser --disabled-password --gecos "" deploy  # dedicated deploy user without password login
sudo usermod -aG docker deploy                      # docker group = root-equivalent: only for this user

# Write daemon config: rotate logs, keep containers alive on daemon restart
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "live-restore": true,
  "no-new-privileges": true
}
EOF

sudo systemctl restart docker                       # apply daemon.json
sudo systemctl status docker --no-pager             # confirm it is active (running)
docker info --format '{{.LoggingDriver}} {{.LiveRestoreEnabled}}'   # verify the settings took effect

# Firewall: Docker edits iptables itself and BYPASSES ufw for published ports.
# So publish only what you need and bind private ports to localhost, e.g. "127.0.0.1:5432:5432".
sudo ufw allow OpenSSH                              # keep SSH reachable
sudo ufw allow 80,443/tcp                           # web traffic only
sudo ufw --force enable                             # turn the firewall on

# Weekly cleanup of unused images/containers (dangling + stopped), as a cron entry
echo '0 3 * * 0 root docker system prune -af --filter "until=168h"' | sudo tee /etc/cron.d/docker-prune   # Sunday 03:00; /etc/cron.d lines need the user field (root)
```

---

## 🟠 My Stack Integration
```yaml
# /srv/myapp/docker-compose.yml on the VPS - bind internal ports to localhost so ufw is not bypassed
services:
  api:                                       # Node.js API
    image: ghcr.io/myorg/api:1.4.0           # image built by CI (example tag)
    ports:
      - "127.0.0.1:3000:3000"                # reachable only from the host (Nginx on host), not the internet
    restart: unless-stopped                  # survive reboots (Engine is enabled in systemd)
  fastapi:                                   # Python API
    image: ghcr.io/myorg/fastapi:2.1.0       # example tag
    ports:
      - "127.0.0.1:8000:8000"                # same pattern for FastAPI
    restart: unless-stopped                  # survive reboots
# Host Nginx (apt install nginx) proxies:  /api -> 127.0.0.1:3000,  /py -> 127.0.0.1:8000,  / -> React static files
```
**AWS:** on EC2, Engine + security groups (open 80/443 only). **React:** build in CI, copy `dist` to Nginx.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Installing `docker.io` from Ubuntu repos and expecting the newest features/compose plugin.
✅ Correct: Use Docker's official apt repo (`docker-ce`) and keep it updated for security fixes.

❌ Mistake 2: Publishing `-p 5432:5432` and trusting `ufw deny` to block it.
✅ Correct: Docker's iptables rules bypass ufw. Bind to `127.0.0.1`, use internal networks, and add rules in the `DOCKER-USER` chain.

❌ Mistake 3: Letting `/var/lib/docker` fill the disk (logs, old images).
✅ Correct: Log rotation in daemon.json, `docker system prune`, monitor disk.

❌ Mistake 4: Running `curl | sh` get-docker script in production without reading it.
✅ Correct: Prefer the apt repo method, and pin versions where stability matters.

---

## 🧠 Tricky Interview Question
"`docker ps` works but a teammate gets `permission denied while trying to connect to the Docker daemon socket`. You fix it with `sudo chmod 666 /var/run/docker.sock`. Is that right?"

Answer: It works but is a security hole: any local user or compromised process can now control Docker, which is root-equivalent. The socket is `root:docker 660` by design. Correct fix: add the trusted user to the `docker` group (they must log in again), or use `sudo`, or rootless Docker. The permission also resets when the daemon restarts, so it is not even a stable fix.

---

## ⚫ Interview Questions + Answers

Q1: Docker Engine vs Docker Desktop?
A1: Engine is the Linux server runtime (CLI + dockerd). Desktop is a GUI app for Mac/Windows that runs Engine in a lightweight VM and adds Kubernetes/extension features; it has licensing terms for larger companies.

Q2: Where does Docker store data?
A2: `/var/lib/docker` (images, containers, volumes, overlay2 layers). Config in `/etc/docker/daemon.json`.

Q3: What is the storage driver?
A3: The layer implementation (overlay2 is the default and recommended). `docker info` shows it.

Q4: How do you make containers survive reboot?
A4: `systemctl enable docker` plus `restart: unless-stopped` (or `always`) on containers.

Q5: What is rootless mode?
A5: Run dockerd and containers as a non-root user using user namespaces, so a container escape lands as an unprivileged user. Trade-offs: some features (low ports, some network modes) are limited.

---

## 🔷 When to Use + When Not to Use
✅ Use Docker Engine when:
- Single VPS or EC2 deployments with compose
- CI runners and build servers

❌ Avoid when:
- Large fleets needing scheduling and self-healing (use ECS/Kubernetes)
- Strict security posture without rootless/hardening effort

---

## 📊 Visual Diagram
```
                   Docker Engine (installed on VPS / EC2)
 +-------------------------------------------------------------------+
 |  docker CLI  ──API──>  dockerd  ──>  containerd  ──>  runc        |
 |                          |                                        |
 |                          +─ BuildKit (builds)                     |
 |                          +─ networking: docker0, iptables NAT     |
 |                          +─ storage: overlay2 in /var/lib/docker  |
 |  config: /etc/docker/daemon.json     socket: /var/run/docker.sock |
 +-------------------------------------------------------------------+
        systemd (docker.service) ── starts at boot
 Internet ─80/443─> [ufw/SG] ─> Nginx ─> 127.0.0.1:3000 (api container)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Docker Engine | Server runtime bundle | server पर चलने वाला runtime |
| Docker Desktop | Mac/Windows app | Mac/Windows ऐप |
| overlay2 | Default storage driver | डिफ़ॉल्ट storage driver |
| daemon.json | Daemon config file | daemon की config file |
| live-restore | Containers survive daemon restart | daemon restart पर containers चलते रहें |
| Rootless | Run without root | बिना root के चलाना |
| BuildKit | Modern image builder | आधुनिक image builder |

---

## ⚡ 3-Line Summary
English: Docker Engine = dockerd + containerd + runc + CLI, installed as a systemd service on Linux.
English: Configure it with daemon.json (log rotation, live-restore) and keep the docker group tiny.
English: Docker bypasses ufw for published ports, so bind private services to 127.0.0.1.
Hindi: Docker Engine = dockerd + containerd + runc + CLI, Linux पर systemd service की तरह।
Hindi: daemon.json से configure करो (log rotation, live-restore) और docker group छोटा रखो।
Hindi: Docker published ports पर ufw को bypass करता है, इसलिए private services को 127.0.0.1 पर bind करो।

---

## ➡️ Next Topic
**46. Docker Daemon** - a closer look at dockerd: what it manages, how to configure, debug, and secure it.
