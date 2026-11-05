# 216. Seccomp Profiles
# हिंदी में: Seccomp Profiles (System Call Filter)

---

## 🔵 Simple Definition (English)
**Seccomp** (secure computing mode) is a Linux kernel feature that filters which **system calls** a process may make. A **seccomp profile** is a JSON allow/deny list. Docker applies a built-in default profile to every container that blocks about 44 dangerous syscalls (for example `reboot`, `mount`, `kexec_load`). You can supply a stricter custom profile for sensitive services.

## 🔵 सरल परिभाषा (Hindi)
**Seccomp** (secure computing mode) Linux kernel का feature है जो तय करता है कि कोई process कौन-से **system calls** कर सकता है। **Seccomp profile** एक JSON allow/deny list होती है। Docker हर container पर एक default profile लगाता है जो लगभग 44 खतरनाक syscalls (जैसे `reboot`, `mount`, `kexec_load`) block करती है। संवेदनशील services के लिए आप ज़्यादा सख्त custom profile दे सकते हो।

---

## 🔴 Problem it Solves
A container shares the host kernel. If an attacker gets code execution inside your Node.js container (through a vulnerable npm package, for instance), the next step is to attack the kernel through syscalls. Kernel bugs such as Dirty COW or container-escape CVEs are reached through syscalls that a web app never needs. Without a filter, the attacker has the full syscall surface (more than 300 calls) to try. Seccomp shrinks that surface, so even a compromised app cannot call what it does not need.

## 🔴 यह क्यों बना? (Hindi)
Container host का kernel share करता है। अगर attacker आपके Node.js container के अंदर code चला लेता है (जैसे किसी vulnerable npm package से), तो अगला कदम syscalls के ज़रिए kernel पर हमला होता है। Dirty COW या container-escape जैसे kernel bugs उन syscalls से पहुँचे जाते हैं जिनकी web app को कभी ज़रूरत नहीं होती। Filter के बिना attacker के पास 300 से ज़्यादा syscalls आज़माने को होते हैं। Seccomp यह surface घटा देता है, इसलिए compromised app भी वह call नहीं कर पाता जिसकी उसे ज़रूरत नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Container process calls a syscall (e.g. open, read, mount, ptrace).
Step 2 → The kernel checks the seccomp filter attached to that process before executing.
Step 3 → The profile has a defaultAction (e.g. SCMP_ACT_ERRNO = deny) and a list of rules.
Step 4 → Syscall is in the allow list  -> kernel runs it normally.
Step 5 → Syscall is NOT allowed        -> kernel returns EPERM (or kills the process, per action).
Step 6 → Filter is set when the container starts (--security-opt seccomp=...) and cannot be removed
         from inside; children inherit it.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Container process कोई syscall करता है (जैसे open, read, mount, ptrace)।
Step 2 → Kernel execute करने से पहले उस process से जुड़ा seccomp filter check करता है।
Step 3 → Profile में defaultAction (जैसे SCMP_ACT_ERRNO = deny) और rules की list होती है।
Step 4 → Syscall allow list में है  -> kernel normal चलाता है।
Step 5 → Syscall allowed नहीं है     -> kernel EPERM लौटाता है (या action के हिसाब से process मार देता है)।
Step 6 → Filter container start पर लगता है (--security-opt seccomp=...) और अंदर से हटाया नहीं जा सकता; child processes भी इसे inherit करते हैं।
```

---

## 🟡 Real World Example
A fintech team runs a Node.js payments API on an AWS EC2 host. A pentest found that a malicious dependency could call `ptrace` and `process_vm_readv` to read memory of other processes. Docker's default profile already blocks `ptrace` on older kernels, but the team went further: they generated a custom profile by recording the syscalls their app really uses, and allowed only those. Result: the exploit failed with "Operation not permitted", and the audit item was closed. Netflix, Google (gVisor) and Kubernetes (`RuntimeDefault` profile) follow the same idea.

## 🟡 Real Example Hindi mein
एक fintech team AWS EC2 host पर Node.js payments API चलाती है। Pentest में पता चला कि एक malicious dependency `ptrace` और `process_vm_readv` call करके दूसरे processes की memory पढ़ सकती थी। Docker की default profile पुराने kernels पर `ptrace` block करती है, पर team ने आगे बढ़कर custom profile बनाई: app जो syscalls सच में use करता है उन्हें record किया और सिर्फ वही allow किए। नतीजा: exploit "Operation not permitted" से fail हुआ और audit item बंद हो गया। Netflix, Google (gVisor) और Kubernetes (`RuntimeDefault`) भी यही सोच अपनाते हैं।

---

## 💻 Code / Config Example — Basic

```bash
# Run with Docker's DEFAULT seccomp profile (this is already on, no flag needed)
docker run -d --name api-default node:20-alpine sleep 3600   # default profile applied automatically

# Prove it: 'unshare' creates new namespaces, the default profile blocks it for non-root-cap containers
docker run --rm alpine:3.20 unshare --user /bin/sh -c 'echo ok'   # fails: Operation not permitted

# Explicitly point to a custom profile file on the host
docker run -d --name api-custom \
  --security-opt seccomp=./my-profile.json \
  node:20-alpine sleep 3600                                       # use custom allow-list

# DANGEROUS: disable seccomp completely (only for debugging, never in production)
docker run --rm --security-opt seccomp=unconfined alpine:3.20 sh -c 'echo no filter'  # no syscall filter
```

```json
{
  "defaultAction": "SCMP_ACT_ALLOW",
  "architectures": ["SCMP_ARCH_X86_64", "SCMP_ARCH_AARCH64"],
  "syscalls": [
    {
      "names": ["mount", "umount2", "reboot", "kexec_load", "ptrace", "swapon", "swapoff"],
      "action": "SCMP_ACT_ERRNO"
    }
  ]
}
```

The JSON above is a small **deny-list** profile (allow everything, deny a few). / ऊपर वाला JSON छोटी **deny-list** profile है (सब allow, कुछ deny)।

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# build-seccomp.sh - create an allow-list (default deny) profile for a Node.js API
# NOTE: the syscall list is an EXAMPLE. Always test against your own app, syscalls vary by Node version.
set -euo pipefail                                    # stop on error, unset var, pipe failure

cat > seccomp-node.json <<'EOF'
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "defaultErrnoRet": 1,
  "architectures": ["SCMP_ARCH_X86_64", "SCMP_ARCH_AARCH64"],
  "syscalls": [
    {
      "names": [
        "accept4", "bind", "brk", "clone", "clone3", "close", "connect", "dup", "dup2", "dup3",
        "epoll_create1", "epoll_ctl", "epoll_pwait", "epoll_wait", "eventfd2", "execve", "exit",
        "exit_group", "fcntl", "fstat", "futex", "getcwd", "getdents64", "getpid", "getrandom",
        "getsockname", "getsockopt", "ioctl", "listen", "lseek", "madvise", "mmap", "mprotect",
        "munmap", "newfstatat", "openat", "pipe2", "poll", "prctl", "pread64", "read", "readlink",
        "recvfrom", "recvmsg", "rt_sigaction", "rt_sigprocmask", "rt_sigreturn", "sched_yield",
        "sendmsg", "sendto", "set_robust_list", "setsockopt", "socket", "statx", "uname", "write",
        "writev", "getuid", "getgid", "geteuid", "getegid", "sigaltstack", "arch_prctl",
        "set_tid_address", "rseq", "prlimit64", "clock_gettime", "clock_nanosleep", "nanosleep",
        "gettid", "tgkill", "kill", "umask", "unlink", "rename", "mkdir", "ftruncate", "fsync",
        "pwrite64", "socketpair", "shutdown", "capget", "membarrier", "sched_getaffinity",
        "sysinfo", "statfs", "fstatfs", "access", "faccessat2", "getppid", "wait4", "readv",
        "pselect6", "timerfd_create", "timerfd_settime", "io_uring_setup", "io_uring_enter"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
EOF

python3 -c "import json; json.load(open('seccomp-node.json')); print('valid JSON')"   # syntax check
```

```yaml
# docker-compose.yml - run the API with the custom seccomp profile
services:
  api:
    image: myorg/api:1.4.2                 # pinned image tag (example)
    read_only: true                        # read-only root filesystem
    cap_drop: [ALL]                        # drop all Linux capabilities
    security_opt:
      - no-new-privileges:true             # block setuid privilege escalation
      - seccomp=./seccomp-node.json        # custom syscall allow-list (path relative to compose file)
    ports:
      - "127.0.0.1:3000:3000"              # bind only to localhost, Nginx proxies it
    restart: unless-stopped                # restart on crash
```

---

## 🟠 My Stack Integration
For your VPS / EC2 setup: keep Docker's **default** profile on for all services (Node.js, FastAPI, Nginx, Redis). Add a custom profile only for the most exposed service, usually the public API. FastAPI with uvicorn needs a similar syscall set to Node.js. React is just static files served by Nginx, so default profile is enough. On AWS ECS Fargate you cannot set a custom profile (managed), but on ECS on EC2 you can via `dockerSecurityOptions`.

```yaml
# docker-compose.prod.yml - stack-wide hardening with seccomp
services:
  nginx:
    image: nginx:1.27-alpine               # example tag, update regularly
    security_opt: [ "no-new-privileges:true" ]   # default seccomp stays ON (no override)
    ports: [ "80:80", "443:443" ]          # only Nginx is public
  api:
    image: myorg/node-api:1.4.2            # Node.js service
    security_opt:
      - no-new-privileges:true
      - seccomp=./seccomp-node.json        # strict allow-list for the exposed API
  ml-service:
    image: myorg/fastapi:2.0.1             # FastAPI service
    security_opt:
      - no-new-privileges:true             # default profile is good enough here
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `--security-opt seccomp=unconfined` "because the app didn't start".
✅ Correct: Find the blocked syscall (`strace`, `dmesg | grep audit`, `journalctl`) and add only that one to your profile.

❌ Mistake 2: Using `--privileged` and thinking seccomp is still on. `--privileged` disables seccomp.
✅ Correct: Never use `--privileged` in production; add the exact capability needed with `--cap-add`.

❌ Mistake 3: Writing an allow-list once and never retesting after a Node.js or base image upgrade.
✅ Correct: Run the profile in CI integration tests; new Node versions may use new syscalls (`io_uring`, `clone3`).

❌ Mistake 4: Copying a profile from a blog without validating the JSON and the architectures.
✅ Correct: Validate JSON, include all architectures you deploy (amd64 and arm64 Graviton).

---

## 🧠 Tricky Interview Question
**Q:** Your container works on your laptop but crashes on the production server with "Operation not permitted" after you added a custom seccomp profile. CPU architecture differs (Mac M1 vs EC2 x86). What do you check?

**Answer:** Syscall names and numbers differ by architecture, and some syscalls exist on one but not the other (for example `open` exists on x86_64 but arm64 only has `openat`). If the profile lists only one architecture in `architectures`, calls on the other are denied by `defaultAction`. Check `architectures`, use the `openat` family, and look at `dmesg` / audit log to see which syscall number was denied. Test the profile on the same architecture as production.

---

## ⚫ Interview Questions + Answers

Q1: What is seccomp and how is it different from capabilities?
A1: Capabilities split root's powers into pieces (e.g. NET_ADMIN). Seccomp filters individual system calls. They work together: capabilities say "what privileged things you may do", seccomp says "which syscalls you may call at all".

Q2: Does Docker apply seccomp by default?
A2: Yes. Since Docker 1.10 a default profile is applied to every container, blocking about 44 syscalls. It is disabled only by `seccomp=unconfined` or `--privileged`.

Q3: How would you create a minimal profile for your app?
A3: Run the app with a tracing tool (`strace -c -f`, or the OCI `oci-seccomp-bpf-hook`) during tests, collect all syscalls used, generate an allow-list with `defaultAction: SCMP_ACT_ERRNO`, and test in CI.

Q4: What is the difference between SCMP_ACT_ERRNO and SCMP_ACT_KILL?
A4: ERRNO makes the syscall return an error and the process continues (easier to debug). KILL terminates the process immediately. LOG only logs. Use ERRNO or LOG while learning, KILL for strict cases.

Q5: How does Kubernetes use seccomp?
A5: Set `securityContext.seccompProfile.type: RuntimeDefault` (runtime's default) or `Localhost` (custom file). Since v1.27 `--seccomp-default` can make RuntimeDefault the cluster default.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Service is internet-facing (public API, webhook receiver)
- You run untrusted or user-supplied code (CI runners, code playgrounds)
- Compliance requires defense in depth (PCI-DSS, SOC 2)
- You can test the profile in CI before deploy

❌ Avoid when:
- You are debugging (temporarily use LOG mode, not unconfined in prod)
- App uses exotic syscalls and you lack time to maintain a custom list (stay on default profile)
- You are on a managed platform (Fargate) that does not allow custom profiles

---

## 📊 Visual Diagram
```
   +----------------------- Container --------------------+
   |  Node.js app  --- syscall: openat() --+               |
   |               --- syscall: mount()  --+               |
   +---------------------------------------|---------------+
                                           v
                              +---------------------------+
                              |  Seccomp filter (profile) |
                              |  openat -> ALLOW          |
                              |  mount  -> ERRNO (EPERM)  |
                              +-----------|---------------+
                                          v
                              +---------------------------+
                              |        Linux Kernel       |
                              +---------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Syscall | Request from program to kernel | Program से kernel को request |
| Seccomp | Kernel syscall filter | Syscall filter |
| Profile | JSON list of allowed/denied calls | Allow/deny की JSON list |
| SCMP_ACT_ERRNO | Return error to caller | Caller को error लौटाओ |
| unconfined | Seccomp turned off | Seccomp बंद |
| Allow-list | Deny everything except listed | सिर्फ listed allow |

---

## ⚡ 3-Line Summary
English: Seccomp filters which syscalls a container process can make.
Docker applies a default profile; a custom allow-list is stricter for exposed services.
Never use `unconfined` or `--privileged` in production; test profiles in CI.

Hindi: Seccomp तय करता है कि container process कौन-से syscalls कर सकता है।
Docker default profile लगाता है; exposed services के लिए custom allow-list ज़्यादा सख्त है।
Production में `unconfined` या `--privileged` कभी नहीं; profile को CI में test करो।

---

## ➡️ Next Topic
**217. AppArmor in Docker** - seccomp limits syscalls; AppArmor limits which files, network and capabilities a container can touch. Together they form the kernel-level safety net.
