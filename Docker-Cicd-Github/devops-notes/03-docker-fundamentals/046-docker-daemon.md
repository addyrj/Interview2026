# 46. Docker Daemon
# हिंदी में: Docker Daemon (डेमन)

---

## 🔵 Simple Definition (English)
The **Docker daemon** (`dockerd`) is the long-running background service that does the real work: it listens for API requests, manages images, containers, networks and volumes, and delegates container execution to `containerd`. If the daemon is down, the `docker` CLI cannot do anything.

## 🔵 सरल परिभाषा (Hindi)
**Docker daemon** (`dockerd`) वह लगातार चलने वाली background service है जो असली काम करती है: API requests सुनती है, images, containers, networks और volumes संभालती है, और container चलाने का काम `containerd` को देती है। Daemon बंद हो तो `docker` CLI कुछ नहीं कर सकता।

---

## 🔴 Problem it Solves
Someone must own long-lived state: which containers run, their network ports, volumes, restart policies, log streams. A one-shot CLI process cannot do that. A central daemon gives one authority that restarts crashed containers, keeps networks consistent, serves many clients (CLI, compose, CI, Portainer), and exposes one API.

## 🔴 यह क्यों बना? (Hindi)
लंबे समय की state किसी को संभालनी होती है: कौन से containers चल रहे हैं, उनके ports, volumes, restart policies, log streams। एक बार चलने वाला CLI यह नहीं कर सकता। केंद्रीय daemon एक ही अधिकारी देता है जो crashed containers restart करता है, networks सुसंगत रखता है, कई clients (CLI, compose, CI, Portainer) को serve करता है, और एक ही API देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → systemd starts dockerd at boot (docker.service, depends on docker.socket / containerd.service)
Step 2 → dockerd reads /etc/docker/daemon.json + command-line flags
Step 3 → Restores its state from /var/lib/docker (containers, networks, volumes metadata)
Step 4 → Applies restart policies (starts containers marked always / unless-stopped)
Step 5 → Listens on unix:///var/run/docker.sock (and optionally tcp with TLS)
Step 6 → For each API call it validates, then delegates: image pulls itself, run -> containerd
Step 7 → Streams logs via the logging driver; emits events (docker events)
Step 8 → On SIGTERM: stops containers (unless live-restore), flushes state, exits
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → systemd boot पर dockerd शुरू करता है (docker.service, docker.socket / containerd.service पर निर्भर)
Step 2 → dockerd /etc/docker/daemon.json + command-line flags पढ़ता है
Step 3 → /var/lib/docker से अपनी state लौटाता है (containers, networks, volumes का metadata)
Step 4 → Restart policies लागू करता है (always / unless-stopped वाले containers चालू)
Step 5 → unix:///var/run/docker.sock पर सुनता है (और चाहें तो TLS के साथ tcp)
Step 6 → हर API call validate करके आगे देता है: image pull खुद, run -> containerd
Step 7 → Logging driver से logs stream करता है; events देता है (docker events)
Step 8 → SIGTERM पर: containers रोकता है (live-restore न हो तो), state flush करके बंद
```

---

## 🟡 Real World Example
**Production outage pattern:** a VPS ran out of disk because the daemon's default `json-file` logs for a chatty Node.js container grew to 40 GB; `dockerd` slowed, then `docker ps` hung and deploys failed. Fix: log rotation in `daemon.json`, `docker system df` monitoring, and a CloudWatch/Prometheus disk alert. Another: a CI runner's daemon cache grew until builds failed; a weekly `docker builder prune` solved it.

## 🟡 Real Example Hindi mein
**Production outage का आम पैटर्न:** VPS की disk भर गई क्योंकि बहुत बोलने वाले Node.js container के default `json-file` logs 40 GB हो गए; `dockerd` धीमा हुआ, फिर `docker ps` अटकने लगा और deploys fail हुए। Fix: `daemon.json` में log rotation, `docker system df` monitoring, और CloudWatch/Prometheus disk alert। दूसरा: CI runner के daemon का cache इतना बढ़ा कि builds fail हुए; साप्ताहिक `docker builder prune` से हल हुआ।

---

## 💻 Code / Config Example — Basic
```bash
# Manage and inspect the daemon (Linux, systemd; needs sudo)
sudo systemctl status docker --no-pager        # is dockerd running? shows last log lines
sudo systemctl restart docker                  # restart the daemon (containers stop unless live-restore is on)
sudo journalctl -u docker.service -n 100 --no-pager   # last 100 daemon log lines (errors on start-up appear here)
sudo dockerd --validate --config-file /etc/docker/daemon.json   # check the config file for errors (supported in modern versions)
docker info                                    # daemon facts: storage driver, root dir, cgroup, runtimes
docker events --since 10m                      # live stream of daemon events (start, die, oom, pull)
docker system df                               # disk used by images, containers, volumes, build cache
docker system prune -f                         # remove stopped containers, dangling images, unused networks
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# daemon-tls-and-limits.sh - configure dockerd with a systemd drop-in and TLS-secured remote API.
# Only needed if you must expose the API; SSH contexts (topic 44) are usually safer.
set -euo pipefail                                   # strict mode

# 1) systemd drop-in: raise limits and keep unit file untouched across upgrades
sudo mkdir -p /etc/systemd/system/docker.service.d  # drop-in directory
sudo tee /etc/systemd/system/docker.service.d/override.conf > /dev/null <<'EOF'
[Service]
LimitNOFILE=1048576
LimitNPROC=infinity
TasksMax=infinity
EOF

# 2) daemon.json: TLS API on 2376 (do NOT also pass -H on the ExecStart line, or dockerd fails with a conflict)
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2376"],
  "tlsverify": true,
  "tlscacert": "/etc/docker/certs/ca.pem",
  "tlscert": "/etc/docker/certs/server-cert.pem",
  "tlskey": "/etc/docker/certs/server-key.pem",
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "live-restore": true
}
EOF
# NOTE: with "hosts" in daemon.json on systemd distros, the stock unit passes -H fd://, which conflicts.
# Clear it in the drop-in by adding to override.conf:  ExecStart=  then  ExecStart=/usr/bin/dockerd
# (verify the ExecStart path with `systemctl cat docker`). Certificates are not generated here.

sudo systemctl daemon-reload                        # re-read unit/drop-in files
sudo systemctl restart docker                       # restart with new config
sudo ss -tlnp | grep dockerd || true                # confirm what the daemon listens on
```

---

## 🟠 My Stack Integration
- **VPS monitoring:** scrape daemon metrics (`"metrics-addr": "127.0.0.1:9323"` in daemon.json) with Prometheus; alert on disk and container restarts.
- **Node.js/FastAPI:** `restart: unless-stopped` relies on the daemon being enabled at boot.
- **Nginx:** if Nginx runs in a container, a daemon restart without live-restore means brief downtime of the whole site.
- **AWS:** CloudWatch agent can ship `journalctl -u docker` logs.

```yaml
# docker-compose.yml fragment: depends on the daemon's restart handling + log rotation per service
services:
  api:
    image: ghcr.io/myorg/api:1.4.0           # example image
    restart: unless-stopped                  # daemon restarts it after crash or reboot
    logging:
      driver: json-file                      # per-service override of daemon default
      options:
        max-size: "10m"                      # rotate at 10 MB
        max-file: "3"                        # keep 3 rotated files
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Opening the daemon on TCP 2375 without TLS.
✅ Correct: Unix socket locally; SSH context or `tlsverify` on 2376.

❌ Mistake 2: Setting `hosts` in daemon.json while systemd also passes `-H fd://`.
✅ Correct: Override ExecStart in a drop-in; otherwise dockerd fails with "directive 'hosts' ... conflicts".

❌ Mistake 3: Ignoring daemon logs when containers misbehave.
✅ Correct: `journalctl -u docker` and `docker events` show OOM kills, network failures, storage errors.

❌ Mistake 4: Never pruning; disk reaches 100 percent.
✅ Correct: Scheduled prune and log rotation; monitor `docker system df`.

---

## 🧠 Tricky Interview Question
"Your containers have `restart: always`, yet after a server reboot none came back. The daemon works when started manually. What did you forget?"

Answer: The daemon is not enabled in systemd (`systemctl enable docker`), so it did not start at boot and nobody applied the restart policies. (Also check: containers manually stopped before reboot are not restarted by `unless-stopped`; `always` restarts them.) The restart policy is enforced by the daemon, not by the kernel.

---

## ⚫ Interview Questions + Answers

Q1: What does dockerd do vs containerd?
A1: dockerd handles API, images, builds, networks, volumes, plugins. containerd manages container lifecycle and image storage at a lower level and calls runc.

Q2: Where are daemon logs?
A2: `journalctl -u docker` on systemd hosts (or `/var/log/syslog`). Container logs are separate: `docker logs`.

Q3: What is live-restore?
A3: Option that keeps containers running when dockerd stops/restarts; daemon re-attaches on start.

Q4: How can you debug a daemon that will not start?
A4: `journalctl -u docker -n 100`; validate daemon.json (invalid JSON or unknown keys are the top causes); run `dockerd -D` in the foreground for debug output.

Q5: How do you secure the daemon?
A5: Keep it on the unix socket, restrict the docker group, use TLS or SSH for remote, rootless mode, user-namespace remap, patch regularly.

---

## 🔷 When to Use + When Not to Use
✅ Tune the daemon when:
- Production VPS/CI hosts: log rotation, live-restore, metrics, ulimits

❌ Avoid when:
- Changing storage driver or data-root on a host with live data without migrating/backup

---

## 📊 Visual Diagram
```
  docker CLI ─┐
  compose  ───┼─> [ /var/run/docker.sock ]  or  tcp:2376 (TLS)
  CI / UI  ───┘               │
                       +------v-------+
                       |   dockerd    |  config: daemon.json
                       | - images     |  state:  /var/lib/docker
                       | - networks   |  logs:   journalctl -u docker
                       | - volumes    |  metrics: 127.0.0.1:9323
                       | - restart    |
                       +------+-------+
                              │ gRPC
                       +------v-------+      +-----------+
                       |  containerd  |─────>| runc/shim | ─> containers
                       +--------------+      +-----------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| dockerd | Docker daemon process | Docker का background process |
| daemon.json | Daemon settings | daemon की settings |
| live-restore | Keep containers during restart | restart के दौरान containers चालू |
| Restart policy | Auto-restart rule | अपने-आप restart का नियम |
| data-root | Where Docker stores data | Docker का data folder |
| TLS verify | Mutual cert authentication | दोनों तरफ certificate जाँच |
| systemd drop-in | Override unit settings | unit settings बदलने की फ़ाइल |

---

## ⚡ 3-Line Summary
English: dockerd is the background service that owns images, containers, networks, volumes and restart policies.
English: Enable it in systemd, rotate logs, monitor disk, and secure the API socket.
English: Debug with journalctl, docker events, and docker system df.
Hindi: dockerd वह background service है जो images, containers, networks, volumes और restart policies संभालती है।
Hindi: systemd में enable करो, logs rotate करो, disk monitor करो, API socket सुरक्षित रखो।
Hindi: Debug के लिए journalctl, docker events और docker system df इस्तेमाल करो।

---

## ➡️ Next Topic
**47. Docker Client** - the `docker` CLI that talks to this daemon: contexts, DOCKER_HOST, and how commands map to API calls.
