---

# 055. Installing Docker
# हिंदी में: Docker Install करना

---

## 🔵 Simple Definition (English)
Installing Docker means setting up the Docker Engine (the `dockerd` daemon plus the `docker` CLI) on a machine, usually from Docker's official apt repository on a Linux VPS, or Docker Desktop on Mac/Windows. After install you add your user to the `docker` group and verify with `docker run hello-world`.

## 🔵 सरल परिभाषा (Hindi)
Docker install करने का मतलब किसी machine पर Docker Engine (`dockerd` daemon और `docker` CLI) set up करना है, आमतौर पर Linux VPS पर Docker की official apt repository से, या Mac/Windows पर Docker Desktop से। Install के बाद अपने user को `docker` group में जोड़ें और `docker run hello-world` से verify करें।

---

## 🔴 Problem it Solves
Ubuntu's own `docker.io` package and snap versions are often old or behave differently. Random `curl | sh` installs on production are hard to audit and reproduce. A correct install from the official repository gives you current, security-patched Engine, Compose v2 and Buildx plugins, and updates through normal `apt upgrade`.

## 🔴 यह क्यों बना? (Hindi)
Ubuntu का अपना `docker.io` package और snap versions अक्सर पुराने होते हैं या अलग behave करते हैं। Production पर random `curl | sh` install audit और reproduce करना मुश्किल है। Official repository से सही install करने पर आपको current, security-patched Engine, Compose v2 और Buildx plugins मिलते हैं, और updates सामान्य `apt upgrade` से आते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Remove old/conflicting packages (docker.io, docker-compose, podman-docker, containerd)
Step 2 → Install prerequisites: ca-certificates, curl
Step 3 → Add Docker's GPG key to /etc/apt/keyrings/docker.asc
Step 4 → Add the Docker apt repository (signed-by that key)
Step 5 → apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
Step 6 → systemd starts and enables docker.service
Step 7 → sudo usermod -aG docker $USER, log out/in, run docker run hello-world
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → पुराने/conflicting packages हटाएँ (docker.io, docker-compose, podman-docker, containerd)
Step 2 → Prerequisites install करें: ca-certificates, curl
Step 3 → Docker की GPG key /etc/apt/keyrings/docker.asc में डालें
Step 4 → Docker apt repository जोड़ें (उसी key से signed-by)
Step 5 → apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
Step 6 → systemd docker.service को start और enable करता है
Step 7 → sudo usermod -aG docker $USER, logout/login, फिर docker run hello-world चलाएँ
```

---

## 🟡 Real World Example
You buy a fresh Ubuntu 24.04 VPS (or an AWS EC2 `t3.small`) for your FastAPI + React app. Before the first GitHub Actions deploy, you SSH in once, run the install script below, create a `deploy` user in the docker group, and your pipeline can then `ssh deploy@vps "docker compose pull && docker compose up -d"`. Teams at product companies bake the same steps into an AMI or cloud-init so every server is identical.

## 🟡 Real Example Hindi mein
आप अपने FastAPI + React app के लिए नया Ubuntu 24.04 VPS (या AWS EC2 `t3.small`) लेते हैं। पहले GitHub Actions deploy से पहले, एक बार SSH करके नीचे की install script चलाते हैं, `deploy` user को docker group में डालते हैं, और फिर pipeline `ssh deploy@vps "docker compose pull && docker compose up -d"` चला सकती है। Product companies यही steps AMI या cloud-init में डाल देती हैं ताकि हर server एक जैसा रहे।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# install-docker-basic.sh - Ubuntu/Debian quick install using Docker's convenience script
# The convenience script is fine for dev/test; production should use the apt repository (advanced example).
set -euo pipefail                                # stop on any error, undefined var or failed pipe

curl -fsSL https://get.docker.com -o get-docker.sh   # download the official script to a file (inspect it before running)
sudo sh get-docker.sh                            # run it: adds repo and installs Engine, Compose, Buildx
sudo systemctl enable --now docker               # start Docker now and on every boot
sudo usermod -aG docker "$USER"                  # let your user run docker without sudo (log out/in after)
docker --version                                 # print client version (needs new login for group to apply)
sudo docker run --rm hello-world                 # pulls a tiny image and prints a success message
docker compose version                           # confirms the Compose v2 plugin is installed
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# install-docker-prod.sh - Docker Engine from the official apt repository (Ubuntu 22.04/24.04, Debian 12)
# Follows the steps in Docker's documentation; re-check docs.docker.com/engine/install for changes.
set -euo pipefail                                # fail fast

# 1. Remove unofficial/conflicting packages (ignore errors if not installed)
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do
  sudo apt-get remove -y "$pkg" || true          # "|| true" keeps going when package is absent
done

# 2. Prerequisites
sudo apt-get update                              # refresh package index
sudo apt-get install -y ca-certificates curl     # TLS roots and curl for downloading the key

# 3. Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings        # create keyring directory with safe permissions
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc  # download key (use .../linux/debian/gpg on Debian)
sudo chmod a+r /etc/apt/keyrings/docker.asc      # apt must be able to read it

# 4. Add the repository for your Ubuntu codename
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null   # write the apt source file

# 5. Install Engine, CLI, containerd and plugins
sudo apt-get update                              # read the new repository
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 6. Enable service
sudo systemctl enable --now docker               # start and enable on boot

# 7. Non-root access for the deploy user (gives root-equivalent power; see security note)
sudo groupadd -f docker                          # create group if missing
sudo usermod -aG docker "${SUDO_USER:-$USER}"    # add the invoking user

# 8. Production daemon settings: log rotation so disks never fill with container logs
sudo mkdir -p /etc/docker                        # config directory
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "live-restore": true
}
EOF
sudo systemctl restart docker                    # apply daemon.json

# 9. Verify
sudo docker run --rm hello-world                 # end-to-end test
docker compose version                           # plugin check
```

```json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "live-restore": true
}
```

---

## 🟠 My Stack Integration
- **VPS**: run the advanced script once, then keep updated with `sudo apt-get update && sudo apt-get upgrade`.
- **AWS EC2**: Amazon Linux 2023 uses `sudo dnf install -y docker` and `sudo systemctl enable --now docker`; Compose plugin is installed separately. Ubuntu AMIs use the script above.
- **GitHub Actions**: `ubuntu-latest` runners already have Docker; no install step needed. For SSH deploy, only the server needs it.
- **Nginx / Node.js / FastAPI / React**: all run as containers after this step, so nothing else to install on the host except UFW/Security Group rules.

```yaml
# .github/workflows/deploy.yml - uses the Docker you just installed on the VPS (example values)
name: deploy                                     # workflow name in the Actions tab
on:
  push:
    branches: [main]                             # deploy when main changes
jobs:
  deploy:
    runs-on: ubuntu-latest                       # GitHub-hosted runner
    steps:
      - name: Deploy over SSH                    # run commands on the VPS
        uses: appleboy/ssh-action@v1.0.3         # example version, check the latest
        with:
          host: ${{ secrets.VPS_HOST }}          # server IP stored as a secret
          username: deploy                       # user that is in the docker group
          key: ${{ secrets.VPS_SSH_KEY }}        # private key stored as a secret
          script: |                              # commands run on the VPS
            cd /srv/app
            docker compose pull
            docker compose up -d
```

Security: membership in the `docker` group equals root on that host (a user can mount `/` into a container). Give it only to trusted deploy users. Consider rootless Docker for stricter isolation. Always inspect scripts before running them with `sudo`, and verify GPG keys come over HTTPS from `download.docker.com`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Installing `docker.io` or the snap package and mixing it with `docker-ce`.
✅ Correct: Remove old packages first, then install `docker-ce` from Docker's repository.

❌ Mistake 2: Running `usermod -aG docker` and testing in the same shell; "permission denied" persists.
✅ Correct: Log out and back in (or `newgrp docker`) so new group membership applies.

❌ Mistake 3: Using the old `docker-compose` (v1, Python) command and old file `version:` key.
✅ Correct: Use `docker compose` (v2 plugin). The `version:` key is obsolete.

❌ Mistake 4: Leaving default logging; a chatty container fills the disk.
✅ Correct: Set `max-size`/`max-file` in `/etc/docker/daemon.json`.

---

## 🧠 Tricky Interview Question
Your CI job on a VPS fails with `permission denied while trying to connect to the Docker daemon socket`, but `sudo docker ps` works. You added the user to the docker group an hour ago. What is wrong?

Answer: Group membership is read at login. The SSH session or running service started before the change still has the old groups. Start a new session (or restart the service/agent). Also check `/var/run/docker.sock` is `root:docker` with mode `660`. Remember the security cost: the docker group is root-equivalent.

---

## ⚫ Interview Questions + Answers

Q1: Why not use `apt install docker.io`?
A1: It is Ubuntu's repackaged, usually older build and may lack the latest Compose/Buildx plugins. Docker's own repository provides `docker-ce` with timely security fixes.

Q2: What are the components installed?
A2: `docker-ce` (daemon), `docker-ce-cli` (client), `containerd.io` (container runtime), `docker-buildx-plugin` (BuildKit builds), `docker-compose-plugin` (`docker compose`).

Q3: How do you run Docker without sudo, and what is the risk?
A3: Add the user to the `docker` group. Risk: any member can control the daemon, which equals root on the host. Alternative is rootless mode.

Q4: How do you verify installation?
A4: `docker version` (client and server both appear), `docker info`, and `docker run --rm hello-world`.

Q5: How do you make containers restart after a VPS reboot?
A5: Enable the service (`systemctl enable docker`) and use `restart: unless-stopped` (or `always`) in compose or `--restart unless-stopped` in `docker run`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Setting up any VPS/EC2 that runs containers.
- You want reproducible, auditable server setup (apt repo, scripted).

❌ Avoid when:
- Using the convenience script on production without reading it.
- The host is a managed platform (ECS Fargate, Cloud Run) where you do not install Docker yourself.

---

## 📊 Visual Diagram
```
 apt repo (download.docker.com)
          |  signed by GPG key
          v
 +---------------------------+
 | apt-get install docker-ce |
 +-------------+-------------+
               v
 +-----------+   unix socket    +------------+     +------------+
 | docker CLI|----------------->|  dockerd   |---->| containerd |--> runc --> containers
 +-----------+ /var/run/docker.sock +--------+     +------------+
   ^ plugins: compose, buildx          ^ config: /etc/docker/daemon.json
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Docker Engine | Daemon + CLI that runs containers | Containers चलाने वाला daemon + CLI |
| dockerd | Background Docker daemon | Background में चलने वाला Docker daemon |
| containerd | Low-level container runtime | Low-level container runtime |
| docker group | Users allowed to use the socket | Socket use करने की अनुमति वाले users |
| daemon.json | Daemon configuration file | Daemon की configuration file |
| Rootless mode | Run Docker without root | बिना root के Docker चलाना |

---

## ⚡ 3-Line Summary
English: Install Docker Engine from Docker's official apt repository, not from random packages.
Add your deploy user to the docker group (root-equivalent) and verify with hello-world.
Configure log rotation in daemon.json so disks stay healthy.
Hindi: Docker Engine को Docker की official apt repository से install करें, random packages से नहीं।
Deploy user को docker group में जोड़ें (यह root के बराबर है) और hello-world से verify करें।
Disk भरने से बचने के लिए daemon.json में log rotation लगाएँ।

---

## ➡️ Next Topic
**056. Docker Desktop vs Docker Engine.** Understand which one to use on your laptop versus on the server, and what the licensing difference is.

---
