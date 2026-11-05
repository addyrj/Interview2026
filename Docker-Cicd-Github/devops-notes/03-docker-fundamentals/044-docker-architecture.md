# 44. Docker Architecture
# हिंदी में: Docker का Architecture (ढाँचा)

---

## 🔵 Simple Definition (English)
Docker uses a **client-server architecture**. The **Docker client** (`docker` CLI) sends commands over a REST API to the **Docker daemon** (`dockerd`), which builds images, runs containers (through `containerd` and `runc`), and talks to **registries** like Docker Hub to pull and push images.

## 🔵 सरल परिभाषा (Hindi)
Docker **client-server architecture** इस्तेमाल करता है। **Docker client** (`docker` CLI) REST API के ज़रिये आदेश **Docker daemon** (`dockerd`) को भेजता है, जो images बनाता है, containers चलाता है (`containerd` और `runc` के माध्यम से), और images pull/push करने के लिए Docker Hub जैसे **registries** से बात करता है।

---

## 🔴 Problem it Solves
Early container tools (LXC) were low-level: you handled namespaces, cgroups, and filesystems by hand. Docker separated concerns into layers: a friendly CLI, a long-running manager, a standard runtime, and a registry protocol. This lets you control a remote server's Docker from your laptop, swap runtimes (Kubernetes uses containerd without dockerd), and keep each component replaceable and standard (OCI specs).

## 🔴 यह क्यों बना? (Hindi)
शुरुआती container tools (LXC) low-level थे: namespaces, cgroups, filesystems हाथ से संभालने पड़ते थे। Docker ने काम layers में बाँट दिया: आसान CLI, हमेशा चलने वाला manager, standard runtime, और registry protocol। इससे आप laptop से दूर server का Docker चला सकते हैं, runtime बदल सकते हैं (Kubernetes dockerd के बिना containerd इस्तेमाल करता है), और हर component बदला जा सकता है (OCI standards)।

---

## 🟢 How it Works — Step by Step

```
You type: docker run -d -p 80:80 nginx

Step 1 → docker CLI (client) parses the command, builds an API request
Step 2 → Sends it via /var/run/docker.sock (unix socket) or tcp://host:2376 (TLS)
Step 3 → dockerd checks if image "nginx" exists locally
Step 4 → If not: dockerd pulls it from the registry (Docker Hub) layer by layer
Step 5 → dockerd asks containerd to create the container
Step 6 → containerd starts a shim + runc; runc sets namespaces/cgroups and execs nginx
Step 7 → dockerd sets up network (bridge, iptables port map) and volumes
Step 8 → Client prints the container ID; the container keeps running without the client
```

## 🟢 कैसे काम करता है? (Hindi)
```
आप टाइप करते हैं: docker run -d -p 80:80 nginx

Step 1 → docker CLI (client) command parse करके API request बनाता है
Step 2 → उसे /var/run/docker.sock (unix socket) या tcp://host:2376 (TLS) से भेजता है
Step 3 → dockerd देखता है कि image "nginx" local में है या नहीं
Step 4 → नहीं हो तो dockerd registry (Docker Hub) से layer-by-layer pull करता है
Step 5 → dockerd, containerd से container बनाने को कहता है
Step 6 → containerd shim + runc शुरू करता है; runc namespaces/cgroups लगाकर nginx चलाता है
Step 7 → dockerd network (bridge, iptables port map) और volumes सेट करता है
Step 8 → Client container ID दिखाता है; client बंद हो जाए तब भी container चलता रहता है
```

---

## 🟡 Real World Example
**GitHub Actions deploying to your VPS:** the runner is the *client*; it uses `DOCKER_HOST=ssh://deploy@vps` so the commands execute against the VPS's *daemon* without running a build on the VPS. **Kubernetes on AWS EKS:** the kubelet talks to containerd directly through CRI, bypassing dockerd, but images are still the same OCI images built by your Docker CLI.

## 🟡 Real Example Hindi mein
**आपके VPS पर GitHub Actions से deploy:** runner *client* है; वह `DOCKER_HOST=ssh://deploy@vps` इस्तेमाल करता है ताकि commands VPS के *daemon* पर चलें, build VPS पर नहीं करना पड़ता। **AWS EKS पर Kubernetes:** kubelet CRI के ज़रिये सीधे containerd से बात करता है, dockerd को छोड़कर, पर images वही OCI images हैं जो आपके Docker CLI ने बनाईं।

---

## 💻 Code / Config Example — Basic
```bash
# See the architecture pieces on any machine with Docker (needs a daemon)
docker version                      # prints Client and Server (Engine, containerd, runc) versions separately
docker info                         # daemon details: storage driver, cgroup driver, runtimes, registry mirrors
docker context ls                   # list targets (daemons) the client can talk to
ls -l /var/run/docker.sock          # the unix socket the client uses by default

# Talk to the daemon API directly, no CLI (proves it is a REST API)
curl --unix-socket /var/run/docker.sock http://localhost/version   # JSON version info
curl --unix-socket /var/run/docker.sock http://localhost/containers/json   # same as `docker ps`
```

## 💻 Code / Config Example — Advanced
(JSON cannot hold comments, so notes are here: this is `/etc/docker/daemon.json` on the VPS; `log-opts` rotates logs, `live-restore` keeps containers alive while dockerd restarts, `userland-proxy:false` uses iptables instead of a proxy process, `no-new-privileges` is the default for new containers, `default-ulimits` raises open-file limits. Restart docker after editing; dockerd refuses to start on unknown keys.)
```json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "default-ulimits": { "nofile": { "Name": "nofile", "Hard": 65536, "Soft": 65536 } },
  "registry-mirrors": []
}
```

```bash
# Remote control over SSH: client on laptop/CI, daemon on VPS (no TCP port opened)
docker context create vps --docker "host=ssh://deploy@203.0.113.10"   # define the remote target (example IP)
docker --context vps ps                                               # runs `ps` against the VPS daemon
docker --context vps compose -f docker-compose.yml up -d              # deploy remotely using the local compose file
docker context use vps                                                # make it the default for this shell
# Never expose tcp://0.0.0.0:2375 (unauthenticated = remote root). Use SSH or TLS on 2376.
```

---

## 🟠 My Stack Integration
- **Laptop:** Docker Desktop = client + a hidden Linux VM daemon.
- **VPS:** install Docker Engine (daemon + containerd + runc); add only a trusted deploy user to the `docker` group (it equals root).
- **CI:** the GitHub runner has its own daemon; build there, push to GHCR/ECR, then the VPS pulls.
- **Nginx/Node/FastAPI:** are just containers started by that daemon.

```yaml
# GitHub Actions: build on runner daemon, deploy through a remote context over SSH
steps:
  - uses: actions/checkout@v4                                  # get code
  - name: Add SSH key                                          # let the client reach the VPS daemon
    run: |
      mkdir -p ~/.ssh && chmod 700 ~/.ssh                      # create ssh dir, restrictive perms
      echo "${{ secrets.VPS_SSH_KEY }}" > ~/.ssh/id_ed25519    # private key from secrets
      chmod 600 ~/.ssh/id_ed25519                              # ssh requires strict key perms
      ssh-keyscan -H ${{ secrets.VPS_HOST }} >> ~/.ssh/known_hosts   # trust host (better: pin the fingerprint)
  - name: Deploy remotely                                      # run compose against the VPS daemon
    run: |
      docker context create vps --docker "host=ssh://deploy@${{ secrets.VPS_HOST }}"   # remote target
      docker --context vps compose up -d --pull always         # pull new images and restart changed services
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Exposing the daemon on `tcp://0.0.0.0:2375` without TLS.
✅ Correct: Use the local socket, SSH contexts, or TLS (2376) with client certs. Open 2375 = anyone can own your server (cryptominers love it).

❌ Mistake 2: Adding many users to the `docker` group.
✅ Correct: Group membership equals root. Keep it to a dedicated deploy user, or use rootless Docker.

❌ Mistake 3: Thinking containers die when the client exits or the terminal closes.
✅ Correct: The daemon owns containers. Use `-d`; for daemon restarts enable `live-restore`.

❌ Mistake 4: Assuming Docker is one binary.
✅ Correct: docker CLI + dockerd + containerd + runc (+ buildx/BuildKit, compose plugins).

---

## 🧠 Tricky Interview Question
"You run `docker stop` on the VPS and the `dockerd` service crashes/restarts. Do your running containers stop? How would you avoid downtime during Docker upgrades?"

Answer: By default restarting dockerd stops containers (without `live-restore`). With `"live-restore": true` in `daemon.json`, containers keep running while the daemon is down or being upgraded, since containerd-shim owns the processes. (Not all changes are supported with live-restore, e.g. major version upgrades might still require a restart.) Also use `restart: unless-stopped` so containers return after reboot.

---

## ⚫ Interview Questions + Answers

Q1: Describe Docker's architecture.
A1: Client (CLI) -> REST API -> daemon (dockerd) -> containerd -> runc -> container; images in registries; objects: images, containers, networks, volumes.

Q2: What is containerd and runc?
A2: containerd is the high-level runtime managing container lifecycle and images; runc is the low-level OCI runtime that actually creates the container via kernel features.

Q3: What is the OCI?
A3: Open Container Initiative: open specs for image format and runtime so tools (Docker, Podman, Kubernetes) interoperate.

Q4: Can client and daemon be on different machines?
A4: Yes: `DOCKER_HOST` or `docker context` with ssh:// or tcp:// (TLS).

Q5: What is the docker.sock and why is it dangerous?
A5: Unix socket for the daemon API. Mounting it into a container lets that container start privileged containers and mount the host disk = full host takeover.

---

## 🔷 When to Use + When Not to Use
✅ Use remote contexts/daemon knowledge when:
- Deploying from CI to a VPS, debugging "cannot connect to the Docker daemon"

❌ Avoid when:
- Using Kubernetes only (you interact with kubectl; dockerd may not even exist on nodes)
- Exposing the API publicly (never)

---

## 📊 Visual Diagram
```
 +--------+   REST API    +-----------+   gRPC   +------------+   +------+
 | docker |-------------->|  dockerd  |--------->| containerd |-->| runc |--> container
 |  CLI   |  unix socket  | (daemon)  |          +------------+   +------+    (nginx, node)
 +--------+  or ssh/TLS   +-----------+                |
  (client)        |  build (BuildKit) | networks | volumes
                  |
                  | pull / push (HTTPS, OCI registry API)
                  v
            +-------------------------+
            | Registry: Docker Hub /  |
            |  GHCR / AWS ECR         |
            +-------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Client | `docker` CLI | आदेश देने वाला CLI |
| Daemon (dockerd) | Background manager | पृष्ठभूमि में चलने वाला प्रबंधक |
| containerd | High-level runtime | उच्च-स्तरीय runtime |
| runc | Low-level OCI runtime | निम्न-स्तरीय runtime |
| OCI | Open container standards | खुले container मानक |
| Context | Saved daemon target | सहेजा हुआ daemon पता |
| docker.sock | Daemon unix socket | daemon का socket |

---

## ⚡ 3-Line Summary
English: Docker is client -> dockerd -> containerd -> runc, with registries storing images.
English: The client and daemon can be on different machines over the REST API.
English: Protect the socket and the docker group; they are effectively root access.
Hindi: Docker है client -> dockerd -> containerd -> runc, और images registries में रहती हैं।
Hindi: Client और daemon REST API के ज़रिये अलग machines पर हो सकते हैं।
Hindi: Socket और docker group की सुरक्षा करो; ये असल में root access हैं।

---

## ➡️ Next Topic
**45. Docker Engine** - the packaged server-side product (dockerd + containerd + runc + CLI) that you install on your VPS.
