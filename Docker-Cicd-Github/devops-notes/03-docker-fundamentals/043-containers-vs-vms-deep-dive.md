# 43. Containers vs VMs — Deep Dive
# हिंदी में: Containers बनाम VMs - गहराई से

---

## 🔵 Simple Definition (English)
Under the hood a container is just a normal Linux process wrapped with **namespaces** (isolated view of PIDs, network, mounts, hostname, users), limited by **cgroups** (CPU, memory, IO caps), and given a **layered root filesystem** (overlayfs). A VM instead emulates whole hardware, and a guest kernel runs on it. This note explains those building blocks and the real trade-offs.

## 🔵 सरल परिभाषा (Hindi)
अंदर से container एक सामान्य Linux process है जिसे **namespaces** (PID, network, mounts, hostname, users का अलग दृश्य) में लपेटा गया है, **cgroups** (CPU, memory, IO की सीमा) से बाँधा गया है, और **layered root filesystem** (overlayfs) दिया गया है। VM इसके उलट पूरा hardware emulate करती है और उस पर guest kernel चलता है। यह note इन building blocks और असली trade-offs को समझाता है।

---

## 🔴 Problem it Solves
Knowing only "containers are lighter" fails in interviews and in production incidents. Why can a container OOM-die while the host has free RAM? Why does `ps` inside show PID 1? Why can't I load a kernel module in a container? Why did a kernel CVE (security hole) affect all containers on a host but only one VM? Understanding the mechanisms answers all of these and guides secure, sized deployments.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ "containers हल्के हैं" जानना interviews और production incidents में काम नहीं आता। Host पर RAM खाली होते हुए container OOM से क्यों मरता है? अंदर `ps` में PID 1 क्यों दिखता है? Container में kernel module load क्यों नहीं होता? Kernel CVE (security hole) सारे containers पर असर क्यों डालता है पर VM में सिर्फ़ एक पर? Mechanisms समझने से इन सबका जवाब मिलता है और सुरक्षित, सही-sized deployments बनते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → runc/containerd calls clone() with flags: CLONE_NEWPID, NEWNET, NEWNS, NEWUTS, NEWIPC (+ NEWUSER)
Step 2 → Process gets its own PID tree (it is PID 1 inside), own network stack, own mount table
Step 3 → A cgroup is created: memory.max, cpu.max, pids.max written for that process
Step 4 → overlayfs mounts: lowerdir = read-only image layers, upperdir = writable layer
Step 5 → pivot_root switches root to that merged filesystem; capabilities + seccomp filter applied
Step 6 → exec() starts your app (node server.js). Same host kernel throughout.
Step 7 → VM comparison: hypervisor traps privileged instructions, guest kernel manages own memory
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → runc/containerd clone() को flags के साथ बुलाता है: CLONE_NEWPID, NEWNET, NEWNS, NEWUTS, NEWIPC (+ NEWUSER)
Step 2 → Process को अपना PID tree (अंदर वह PID 1 है), अपना network stack, अपनी mount table मिलती है
Step 3 → cgroup बनता है: उस process के लिए memory.max, cpu.max, pids.max लिखे जाते हैं
Step 4 → overlayfs mount होता है: lowerdir = read-only image layers, upperdir = writable layer
Step 5 → pivot_root से root उस merged filesystem पर बदलता है; capabilities + seccomp filter लगते हैं
Step 6 → exec() आपका app (node server.js) शुरू करता है। पूरे समय host kernel वही रहता है।
Step 7 → VM से तुलना: hypervisor privileged instructions trap करता है, guest kernel अपनी memory खुद चलाता है
```

---

## 🟡 Real World Example
**Incident on a VPS:** a Node.js container with no memory limit leaked memory; the Linux OOM killer on the *host* killed the Postgres container instead, because without cgroup limits all processes compete for the host RAM. After adding `mem_limit: 512m` per service, only the leaking API container is killed and auto-restarted. **Security story:** the 2019 `runc` vulnerability (CVE-2019-5736) let a malicious container overwrite the host runc binary - a container-only class of bug that cannot happen across a hypervisor boundary in the same way.

## 🟡 Real Example Hindi mein
**VPS पर incident:** बिना memory limit वाले Node.js container में memory leak हुआ; *host* के Linux OOM killer ने leak करने वाले की जगह Postgres container मार दिया, क्योंकि cgroup limits के बिना सारे processes host RAM के लिए लड़ते हैं। हर service पर `mem_limit: 512m` लगाने के बाद सिर्फ़ leak वाला API container मरता है और auto-restart हो जाता है। **Security कहानी:** 2019 की `runc` vulnerability (CVE-2019-5736) में malicious container host का runc binary overwrite कर सकता था - यह container-only तरह का bug है जो hypervisor सीमा के पार उसी तरह नहीं हो सकता।

---

## 💻 Code / Config Example — Basic
```bash
# Explore the kernel features behind containers (Linux host or inside a Linux VM; needs Docker)
docker run -d --name demo --memory=256m --cpus=0.5 nginx:1.27-alpine   # start a limited container

PID=$(docker inspect -f '{{.State.Pid}}' demo)   # host PID of the container's main process
echo "Container main process is HOST pid: $PID"  # proves it is just a host process
ls -l /proc/$PID/ns                              # lists namespaces (pid, net, mnt, uts, ipc, user, cgroup)
docker exec demo ps                              # inside, nginx master appears as PID 1
docker inspect -f '{{.HostConfig.Memory}}' demo  # memory limit in bytes (268435456)

# cgroup v2 limit file (path varies by distro/cgroup driver; may need root)
cat /sys/fs/cgroup/system.slice/docker-$(docker inspect -f '{{.Id}}' demo).scope/memory.max

docker stats --no-stream demo                    # live CPU / memory use against the limit
docker rm -f demo                                # cleanup
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - production hardening using the kernel features explained above
# (namespaces, cgroups, capabilities, seccomp). Image tags are examples.
services:
  fastapi:                                   # Python API
    image: myorg/fastapi:2.1.0               # pinned image
    user: "10001:10001"                      # non-root user; combine with userns-remap on host if possible
    init: true                               # tiny init (tini) as PID 1: reaps zombies, forwards signals
    read_only: true                          # immutable root fs (overlay upperdir not writable)
    tmpfs:
      - /tmp:size=64m,mode=1777              # small RAM-backed temp space
    cap_drop: [ALL]                          # remove all Linux capabilities
    cap_add: []                              # add nothing back (e.g. NET_BIND_SERVICE only if port <1024)
    security_opt:
      - no-new-privileges:true               # setuid binaries cannot raise privileges
      - seccomp=default                      # keep Docker's default syscall filter (explicit)
    mem_limit: 512m                          # cgroup memory.max
    memswap_limit: 512m                      # equal to mem_limit = no swap use
    cpus: 1.5                                # cgroup cpu.max quota
    pids_limit: 256                          # cgroup pids.max
    ulimits:
      nofile:
        soft: 4096                           # max open files (soft)
        hard: 8192                           # max open files (hard)
    stop_grace_period: 20s                   # time for SIGTERM handling before SIGKILL
    restart: unless-stopped                  # restart policy
    logging:
      driver: json-file                      # default local log driver
      options:
        max-size: "10m"                      # rotate at 10 MB
        max-file: "3"                        # keep 3 files, stops logs filling VPS disk
```

---

## 🟠 My Stack Integration
- **Node.js:** set `--max-old-space-size` below the container `mem_limit` (e.g. 384 MB heap for 512 MB limit), otherwise V8 ignores the cgroup and gets OOM-killed. Recent Node versions are container-aware for some defaults, but set it explicitly.
- **FastAPI:** choose uvicorn workers by CPU quota, not host cores (`--workers 2` for `cpus: 1.5`).
- **Nginx:** `worker_processes auto;` may count host CPUs; pin it in containers.
- **VPS/AWS:** EC2 instance size is the ceiling; sum of `mem_limit` must stay below it.

```yaml
# Node.js service sized for its cgroup limit
services:
  api:
    image: myorg/api:1.4.0                   # pinned image
    mem_limit: 512m                          # hard memory cap
    environment:
      NODE_OPTIONS: "--max-old-space-size=384"   # V8 heap below the cgroup cap (leave headroom for buffers)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No memory/CPU limits on containers sharing a VPS.
✅ Correct: Always set `mem_limit` and `cpus`; one runaway service should not kill others.

❌ Mistake 2: Mounting `/var/run/docker.sock` into a container.
✅ Correct: Avoid it; whoever controls that socket is effectively root on the host. Use a socket proxy or remote API with TLS if needed.

❌ Mistake 3: Running `--privileged` or `--pid=host` / `--network=host` casually.
✅ Correct: These disable namespace isolation. Use only for specific tools and document why.

❌ Mistake 4: Believing "root in container" is harmless.
✅ Correct: By default it is UID 0 on the host too (without user namespaces). Use `USER` non-root and consider rootless Docker.

---

## 🧠 Tricky Interview Question
"A container has `--memory=512m`, the app is a Node.js server that keeps getting `Killed` (exit code 137) while `free -m` inside the container shows 3 GB free. Why?"

Answer: `free`, `top` and `/proc/meminfo` inside a container (without lxcfs) report the **host** memory, not the cgroup limit. The real ceiling is the cgroup `memory.max`, so the kernel OOM-killed the process at 512 MB (exit 137 = 128 + SIGKILL 9). Check `docker inspect ... .State.OOMKilled`, read `/sys/fs/cgroup/memory.max`, lower V8's heap, or raise the limit.

---

## ⚫ Interview Questions + Answers

Q1: What are namespaces and cgroups?
A1: Namespaces limit what a process can *see* (PID, net, mount, UTS, IPC, user, cgroup). Cgroups limit what it can *use* (CPU, memory, IO, PIDs).

Q2: What is overlayfs / union filesystem?
A2: Stacks read-only image layers with one writable layer on top and shows a merged view. Copy-on-write: a file is copied up to the writable layer only when modified.

Q3: Why can't containers run a different OS kernel?
A3: They have no kernel of their own; they call the host kernel's syscalls. Only the userland (distro files) differs.

Q4: What is a microVM and why exists?
A4: Firecracker/Kata launch a tiny VM per workload (~125 ms boot) to get VM-grade isolation with container-like speed. AWS Lambda and Fargate use Firecracker.

Q5: Name container hardening measures.
A5: Non-root user, read-only fs, drop capabilities, seccomp/AppArmor, resource limits, no-new-privileges, image scanning, rootless mode, no docker.sock mount.

---

## 🔷 When to Use + When Not to Use
✅ Use containers when:
- Trusted code of one team/org, high density, fast scaling
- You can apply limits and hardening

❌ Avoid plain containers when:
- Running untrusted/customer code (use microVM/VM)
- You need kernel modules, custom kernel, or non-Linux OS

---

## 📊 Visual Diagram
```
 Process tree on HOST                       What the container sees
 ───────────────────                        ───────────────────────
 systemd(1)                                 
  └─ dockerd                                PID namespace:   node = PID 1
      └─ containerd                         NET namespace:   eth0 172.18.0.2
          └─ containerd-shim                MNT namespace:   / = overlayfs
              └─ node server.js (pid 4721)  UTS namespace:   hostname = a1b2c3
                       │
                       ├── cgroup: memory.max=512M  cpu.max=150000/100000  pids.max=256
                       └── overlayfs:  upper(rw)  +  lower: [layer3][layer2][layer1](ro)
 ONE host kernel for every container ← shared attack surface
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Namespace | Isolated view of a resource | resource का अलग दृश्य |
| cgroup | Usage limit and accounting | उपयोग की सीमा और हिसाब |
| overlayfs | Layered copy-on-write filesystem | परतों वाला filesystem |
| seccomp | Syscall filter | syscall छानने वाला filter |
| Capability | Fine-grained root power | root की छोटी-छोटी शक्तियाँ |
| OOM kill | Kernel kills process for memory | memory खत्म होने पर kill |
| runc | Low-level container runtime | निचले स्तर का container runtime |

---

## ⚡ 3-Line Summary
English: A container is a Linux process isolated by namespaces, limited by cgroups, running on an overlay filesystem.
English: All containers share one kernel, so limits and hardening matter much more than with VMs.
English: Size your Node.js/FastAPI settings to the cgroup limits, not to the host's resources.
Hindi: Container एक Linux process है जो namespaces से अलग, cgroups से सीमित, और overlay filesystem पर चलता है।
Hindi: सारे containers एक ही kernel share करते हैं, इसलिए limits और hardening VMs से ज़्यादा ज़रूरी हैं।
Hindi: Node.js/FastAPI की settings cgroup limits के हिसाब से रखो, host के resources के हिसाब से नहीं।

---

## ➡️ Next Topic
**44. Docker Architecture** - now that the kernel mechanics are clear, see the software layers (client, daemon, containerd, runc, registry) that use them.
