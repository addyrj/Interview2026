# 217. AppArmor in Docker
# हिंदी में: Docker में AppArmor

---

## 🔵 Simple Definition (English)
**AppArmor** is a Linux Security Module (LSM) that restricts what a program can do: which files it can read/write, which network operations it can use, and which capabilities it can hold. Docker loads a default profile called `docker-default` for every container on hosts where AppArmor is enabled (Ubuntu, Debian). You can write a custom profile to be stricter.

## 🔵 सरल परिभाषा (Hindi)
**AppArmor** एक Linux Security Module (LSM) है जो तय करता है कि program क्या कर सकता है: कौन-सी files पढ़/लिख सकता है, कौन-से network operations और कौन-सी capabilities use कर सकता है। जिन hosts पर AppArmor चालू है (Ubuntu, Debian) वहाँ Docker हर container पर `docker-default` नाम की default profile लगाता है। ज़्यादा सख्ती के लिए आप custom profile लिख सकते हो।

---

## 🔴 Problem it Solves
Even with a non-root user and dropped capabilities, a compromised process can still read sensitive paths like `/proc/sys`, `/sys/firmware`, or write to places it should never touch. Seccomp filters syscalls but cannot say "this program may write only to /app/uploads". AppArmor adds path-based mandatory access control: even if the attacker is root inside the container, the kernel denies access outside the profile. This limits damage from container-escape attempts and from bugs like path traversal.

## 🔴 यह क्यों बना? (Hindi)
Non-root user और dropped capabilities के बाद भी compromised process `/proc/sys`, `/sys/firmware` जैसे संवेदनशील paths पढ़ सकता है या ऐसी जगह लिख सकता है जहाँ उसे कभी नहीं लिखना चाहिए। Seccomp syscalls filter करता है पर यह नहीं कह सकता कि "यह program सिर्फ /app/uploads में लिखे"। AppArmor path-based mandatory access control जोड़ता है: container के अंदर root होने पर भी kernel profile के बाहर access deny करता है। इससे container-escape कोशिशों और path traversal जैसे bugs का नुकसान सीमित होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Host kernel has AppArmor enabled (check: `aa-status` or /sys/module/apparmor/parameters/enabled).
Step 2 → You write a profile (text file) with rules: file paths, network, capability.
Step 3 → Load it into the kernel:  sudo apparmor_parser -r -W /etc/apparmor.d/docker-api
Step 4 → Start the container:      docker run --security-opt apparmor=docker-api ...
Step 5 → Every file/network/capability request from the container is checked against the profile.
Step 6 → Allowed -> proceeds. Denied -> returns "Permission denied" and a line is logged (audit/dmesg).
         Modes: enforce (block + log) and complain (only log, good for building profiles).
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Host kernel में AppArmor चालू होना चाहिए (check: `aa-status`)।
Step 2 → आप एक profile (text file) लिखते हो जिसमें rules होते हैं: file paths, network, capability।
Step 3 → Kernel में load करो:  sudo apparmor_parser -r -W /etc/apparmor.d/docker-api
Step 4 → Container चलाओ:       docker run --security-opt apparmor=docker-api ...
Step 5 → Container की हर file/network/capability request profile से check होती है।
Step 6 → Allowed -> चलता है। Denied -> "Permission denied" मिलता है और log में line लिखी जाती है (audit/dmesg)।
         Modes: enforce (block + log) और complain (सिर्फ log, profile बनाने के लिए अच्छा)।
```

---

## 🟡 Real World Example
A SaaS company hosts a document-conversion service (user uploads a file, a Node.js worker runs a converter). An attacker uploads a crafted file that gets the worker to run shell commands. With `docker-default`, the attacker could still read `/etc/passwd` and the app source. The team wrote a custom profile: read-only on `/app`, write only on `/tmp` and `/data/uploads`, deny `/proc/*/mem`, deny network raw sockets. The exploit still ran code but could not read secrets or write a backdoor, and the logs showed `apparmor="DENIED"` entries that alerted the on-call engineer.

## 🟡 Real Example Hindi mein
एक SaaS company document-conversion service चलाती है (user file upload करता है, Node.js worker converter चलाता है)। Attacker ने crafted file भेजी जिससे worker ने shell commands चलाए। `docker-default` के साथ attacker फिर भी `/etc/passwd` और app source पढ़ सकता था। Team ने custom profile लिखी: `/app` read-only, सिर्फ `/tmp` और `/data/uploads` में write, `/proc/*/mem` deny, raw sockets deny। Exploit code तो चला पर secrets पढ़ नहीं पाया और backdoor नहीं लिख पाया, और logs में `apparmor="DENIED"` entries ने on-call engineer को alert कर दिया।

---

## 💻 Code / Config Example — Basic

```bash
# 1. Check AppArmor is active on the host (Ubuntu/Debian)
sudo aa-status | head -n 5                              # lists loaded profiles; docker-default should appear

# 2. Default behaviour: every container already uses docker-default
docker run -d --name web nginx:1.27-alpine              # AppArmor docker-default applied automatically

# 3. See which profile a running container uses
docker inspect --format '{{.AppArmorProfile}}' web      # prints: docker-default

# 4. Turn AppArmor off for one container (debug only, never production)
docker run --rm --security-opt apparmor=unconfined alpine:3.20 sh -c 'echo no apparmor'   # no MAC

# 5. Use a custom profile that is already loaded in the kernel
docker run -d --name api --security-opt apparmor=docker-api node:20-alpine sleep 3600      # custom profile
```

## 💻 Code / Config Example — Advanced

```bash
# /etc/apparmor.d/docker-api  - custom profile for a Node.js API container
# Save this text as the file above, then load it with the command at the bottom.
#
# profile docker-api flags=(attach_disconnected,mediate_deleted) {   # name used in --security-opt
#   #include <abstractions/base>               # standard safe basics (libc, locale, etc.)
#
#   network inet tcp,                          # allow IPv4 TCP (HTTP, Postgres, Redis)
#   network inet6 tcp,                         # allow IPv6 TCP
#   network inet udp,                          # allow UDP (DNS lookups)
#   deny network raw,                          # forbid raw sockets (packet sniffing)
#   deny network packet,                       # forbid packet sockets
#
#   /app/** r,                                 # app code: READ only
#   /app/node_modules/** mr,                   # node_modules: read + map executable (native addons)
#   /usr/local/bin/node ix,                    # allow running the node binary
#   /tmp/** rw,                                # temp files: read/write
#   /data/uploads/** rw,                       # upload dir: read/write
#
#   deny /proc/sys/** wklx,                    # no kernel tuning via /proc
#   deny /sys/** wklx,                         # no writing to /sys
#   deny /proc/*/mem rwklx,                    # no memory peeking
#   deny mount,                                # no mount calls
#   deny capability sys_admin,                 # never allow SYS_ADMIN
#   deny capability sys_ptrace,                # never allow ptrace capability
# }
```

```bash
#!/usr/bin/env bash
# load-and-run.sh - create, load and use the profile (Ubuntu host with AppArmor)
set -euo pipefail                                         # fail fast

sudo tee /etc/apparmor.d/docker-api >/dev/null <<'EOF'   # write the profile file
#include <tunables/global>
profile docker-api flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  network inet tcp,
  network inet6 tcp,
  network inet udp,
  deny network raw,
  deny network packet,
  /app/** r,
  /app/node_modules/** mr,
  /usr/local/bin/node ix,
  /tmp/** rw,
  /data/uploads/** rw,
  deny /proc/sys/** wklx,
  deny /sys/** wklx,
  deny /proc/*/mem rwklx,
  deny mount,
  deny capability sys_admin,
  deny capability sys_ptrace,
}
EOF

sudo apparmor_parser -r -W /etc/apparmor.d/docker-api     # load or reload profile into the kernel
sudo aa-status | grep docker-api                          # confirm it is loaded

docker run -d --name api \
  --security-opt apparmor=docker-api \
  --security-opt no-new-privileges:true \
  --cap-drop ALL \
  --read-only --tmpfs /tmp \
  -v uploads:/data/uploads \
  myorg/api:1.4.2                                         # example image; profile enforced at start

sudo dmesg | grep -i 'apparmor="DENIED"' | tail -n 5      # watch for blocked actions
```

Test notes: profile syntax shown follows AppArmor documentation but was not loaded here (no AppArmor on this machine). Run it first with `flags=(complain)` on a staging host. / इस machine पर AppArmor नहीं है, इसलिए profile load नहीं की गई; staging host पर पहले `flags=(complain)` से चलाओ।

---

## 🟠 My Stack Integration
On your Ubuntu VPS or EC2 (Ubuntu AMI) AppArmor is on by default, so `docker-default` already protects Node.js, FastAPI and Nginx. Add a custom profile for the public API only. On Amazon Linux 2023 AppArmor is not the default (SELinux/none), so this topic does not apply there; use seccomp and capabilities instead. In Compose use `security_opt`.

```yaml
# docker-compose.prod.yml
services:
  api:
    image: myorg/node-api:1.4.2             # example tag
    security_opt:
      - apparmor=docker-api                 # custom profile (must be loaded on host first)
      - no-new-privileges:true              # no setuid escalation
    cap_drop: [ALL]                         # drop every capability
    read_only: true                         # read-only filesystem
    tmpfs: [ /tmp ]                         # writable temp in memory
  fastapi:
    image: myorg/fastapi:2.0.1              # FastAPI service
    security_opt:
      - apparmor=docker-default             # explicit default profile (same as implicit)
```

Add the `apparmor_parser` step to your Ansible/cloud-init script so a rebuilt VPS loads the profile before containers start. / Ansible/cloud-init में `apparmor_parser` step जोड़ो ताकि नया VPS containers से पहले profile load करे।

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Starting a container with `apparmor=docker-api` when the profile is not loaded. Docker fails with "profile not found".
✅ Correct: Load it first (`apparmor_parser -r`) on every host, automate it.

❌ Mistake 2: Using `apparmor=unconfined` to "fix" a permission error.
✅ Correct: Read `dmesg`/`journalctl` for `DENIED` lines, add one narrow rule.

❌ Mistake 3: Going straight to enforce mode in production.
✅ Correct: Start in complain mode (`aa-complain`), run tests, then `aa-enforce`.

❌ Mistake 4: Assuming AppArmor works on every host.
✅ Correct: Check `aa-status`. RHEL, Amazon Linux and Fedora use SELinux; Docker ignores the AppArmor option there.

---

## 🧠 Tricky Interview Question
**Q:** The app is root inside the container, and AppArmor denies writing to `/etc/shadow`. Can root inside the container bypass it with `chmod`?

**Answer:** No. AppArmor is mandatory access control: it is checked in addition to normal Unix permissions and is enforced by the kernel based on the profile attached to the process, not on the user ID. Even root cannot change its own profile unless it has the right capability (`mac_admin`), and Docker drops that. So `chmod` does not help; access is still denied.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between AppArmor and seccomp?
A1: Seccomp filters syscalls (what calls can be made). AppArmor controls resources (which files, network, capabilities). Use both: they cover different attack paths.

Q2: What is docker-default?
A2: A profile Docker generates and loads automatically. It allows normal container behaviour but denies writes to `/proc/sys`, `/sys`, mounting, and ptrace of other profiles.

Q3: AppArmor vs SELinux?
A3: AppArmor is path-based, simpler, used on Ubuntu/Debian/SUSE. SELinux is label-based, more granular but more complex, used on RHEL/Fedora/Amazon Linux. Docker supports either, one at a time per host.

Q4: How do you debug a denied operation?
A4: Check `dmesg | grep DENIED` or `journalctl -k`, find the path and operation, then add a rule or use `aa-logprof` to generate rules from logs.

Q5: Does AppArmor work inside Docker Desktop on Mac?
A5: Docker Desktop runs a Linux VM with its own kernel; behaviour is limited and not representative of your Ubuntu server. Test on the same OS as production.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Host is Ubuntu/Debian (AppArmor available)
- Service handles untrusted input or file uploads
- Compliance asks for mandatory access control
- You can test in complain mode before enforcing

❌ Avoid when:
- Host uses SELinux (Amazon Linux, RHEL): use SELinux labels instead
- Managed runtime (Fargate) where you cannot set it
- You cannot maintain the profile; keep docker-default rather than a broken custom one

---

## 📊 Visual Diagram
```
   Container process (root inside, but confined)
        |
        |  open("/etc/shadow", write)
        v
  +------------------------------+
  | Unix permissions: allowed?   |  <- normal check
  +--------------+---------------+
                 v
  +------------------------------+
  | AppArmor profile docker-api  |  <- extra mandatory check
  |  /app/**   r                 |
  |  /tmp/**   rw                |
  |  /etc/shadow -> not listed   |
  +--------------+---------------+
                 v
          DENIED (EACCES) + audit log line
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LSM | Linux Security Module framework | Linux security module |
| Profile | Rules for one program/container | एक program के नियम |
| Enforce mode | Block and log | Block + log |
| Complain mode | Only log violations | सिर्फ log |
| MAC | Mandatory Access Control | अनिवार्य access control |
| docker-default | Docker's built-in profile | Docker की default profile |

---

## ⚡ 3-Line Summary
English: AppArmor restricts files, network and capabilities per container using kernel profiles.
Docker applies docker-default; write custom profiles for exposed services and test in complain mode.
Works on Ubuntu/Debian; on SELinux hosts use SELinux instead.

Hindi: AppArmor kernel profiles से हर container की files, network और capabilities सीमित करता है।
Docker docker-default लगाता है; exposed services के लिए custom profile लिखो और complain mode में test करो।
Ubuntu/Debian पर चलता है; SELinux वाले hosts पर SELinux use करो।

---

## ➡️ Next Topic
**218. Docker Bench Security** - after hardening with seccomp and AppArmor, how do you automatically audit your host and containers against the CIS Docker Benchmark?
