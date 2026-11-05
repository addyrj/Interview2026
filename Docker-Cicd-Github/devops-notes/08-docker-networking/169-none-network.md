# 169. None Network
# हिंदी में: None Network (बिना network का container)

---

## 🔵 Simple Definition (English)
**None network** (`--network none`) gives a container only a loopback interface (`lo`). It has no external connectivity: no internet, no other containers, no host. It is the strongest network isolation Docker offers.

## 🔵 सरल परिभाषा (Hindi)
**None network** (`--network none`) container को सिर्फ loopback interface (`lo`) देता है। बाहर से कोई connection नहीं: न internet, न दूसरे containers, न host। यह Docker का सबसे मज़बूत network isolation है।

---

## 🔴 Problem it Solves
Some jobs never need the network: converting a PDF from an untrusted user, running a code-judge submission, a batch job that processes files from a volume, or a cryptographic signing step. If such a container is compromised (malicious PDF exploit), a network would let it exfiltrate data or attack internal services. With `none`, there is nowhere to connect.

## 🔴 यह क्यों बना? (Hindi)
कुछ jobs को network की ज़रूरत ही नहीं: untrusted user की PDF convert करना, code-judge submission चलाना, volume की files process करने वाला batch job, या signing step। अगर ऐसा container compromise हो (malicious PDF exploit), तो network होने पर वो data चुरा सकता है या internal services पर हमला कर सकता है। `none` में connect करने की कोई जगह ही नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker run --network none myimage
Step 2 → Docker creates a network namespace for the container
Step 3 → Only the loopback interface lo (127.0.0.1) is configured
Step 4 → No veth pair, no bridge attachment, no IP, no DNS, no default route
Step 5 → Any outbound connect() fails: "Network is unreachable"
Step 6 → Data goes in/out only through volumes (or stdin/stdout)
Step 7 → -p publish is not possible (nothing to forward to)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker run --network none myimage
Step 2 → Docker container के लिए network namespace बनाता है
Step 3 → सिर्फ loopback interface lo (127.0.0.1) configure होता है
Step 4 → कोई veth pair नहीं, bridge नहीं, IP नहीं, DNS नहीं, default route नहीं
Step 5 → कोई भी outbound connect() fail: "Network is unreachable"
Step 6 → Data सिर्फ volumes (या stdin/stdout) से अंदर-बाहर जाता है
Step 7 → -p publish संभव नहीं (आगे भेजने को कुछ है ही नहीं)
```

---

## 🟡 Real World Example
An online-judge platform (like a coding contest site) runs each candidate's submitted code in a container with `--network none --read-only --memory 256m --cpus 0.5 --pids-limit 64`. The code reads input from a mounted file and writes the result to an output file. Even if a contestant writes code that tries to `curl` a server or scan the VPC, it fails instantly.

## 🟡 Real Example Hindi mein
एक online-judge platform (coding contest site जैसा) हर candidate का code `--network none --read-only --memory 256m --cpus 0.5 --pids-limit 64` वाले container में चलाता है। Code mounted file से input पढ़ता है और result output file में लिखता है। कोई contestant `curl` या VPC scan करने की कोशिश करे तो तुरंत fail हो जाता है।

---

## 💻 Code / Config Example — Basic
```bash
# run a container with no network
docker run --rm --network none alpine ip addr          # shows only lo (127.0.0.1)

# prove there is no internet
docker run --rm --network none alpine ping -c1 8.8.8.8 # fails: Network is unreachable

# prove loopback still works inside the container
docker run --rm --network none alpine sh -c 'ip addr show lo'   # lo is UP

# inspect mode on a running container
docker run -d --name iso --network none alpine sleep 600   # long running
docker inspect -f '{{.HostConfig.NetworkMode}}' iso        # prints: none
docker rm -f iso                                            # cleanup
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# run-untrusted.sh - sandbox for untrusted file conversion
set -euo pipefail                              # fail fast on errors

IN_DIR="$1"                                    # directory with the user's input file
OUT_DIR="$2"                                   # directory where result is written

docker run --rm \
  --network none \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --memory 256m --cpus 0.5 --pids-limit 64 \
  --user 65534:65534 \
  -v "$IN_DIR":/in:ro \
  -v "$OUT_DIR":/out:rw \
  myorg/pdf-converter:1.0 /in/input.pdf /out/output.txt
# --network none : no connectivity at all
# --read-only    : root filesystem cannot be modified
# --tmpfs /tmp   : small RAM scratch space, no exec
# --cap-drop ALL : remove every Linux capability
# no-new-privileges : block setuid privilege escalation
# --memory/--cpus/--pids-limit : stop resource bombs and fork bombs
# --user 65534   : run as "nobody"
# /in:ro , /out:rw : input read-only, only /out writable
```

```yaml
# docker-compose.yml - one-shot job with no network
services:
  converter:
    image: myorg/pdf-converter:1.0         # example image
    network_mode: none                     # Compose equivalent of --network none
    read_only: true                        # immutable filesystem
    cap_drop:
      - ALL                                # no Linux capabilities
    volumes:
      - ./in:/in:ro                        # input files, read-only
      - ./out:/out                         # output files
    profiles: ["jobs"]                     # run only with: docker compose --profile jobs run converter
```

---

## 🟠 My Stack Integration
- **Node.js:** a worker that resizes images or runs `ffmpeg` on uploaded files can use `none`; the main API (on a bridge) puts the file in a shared volume and spawns the sandbox via a job runner.
- **FastAPI + ML:** model inference on local files with no outbound calls prevents data leaks.
- **Nginx / React:** these need networking; never use `none`.
- **CI (GitHub Actions):** run untrusted test code or linting of third-party repos with `--network none` after dependencies are installed.
- **AWS:** complements IAM and security groups; `none` blocks even the EC2 metadata endpoint (169.254.169.254), protecting instance credentials from SSRF-style escapes.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `none` for a service that must install packages at start (`npm install`, `pip install`).
✅ Correct: Install dependencies at build time; the runtime container then needs no network.

❌ Mistake 2: Thinking `none` is a full sandbox.
✅ Correct: It only removes the network. Add `--read-only`, `--cap-drop ALL`, seccomp, memory/CPU limits and non-root user.

❌ Mistake 3: Trying `-p 8080:80` with `none`.
✅ Correct: Nothing can be published; use a bridge for services.

❌ Mistake 4: Combining `none` with other networks via Compose `networks:`.
✅ Correct: `network_mode: none` cannot be combined with `networks:`.

---

## 🧠 Tricky Interview Question
**Q:** A container runs with `--network none`. Can two such containers talk to each other through `localhost`?

**Answer:** No. Each container has its own network namespace, so each `lo` is private. Two `none` containers are completely separate. They can share data only through a shared volume or by sharing a namespace explicitly (`--network container:<name>`). Also, a process inside can still use Unix domain sockets on a shared volume, so a mounted `docker.sock` would be a serious escape path; never mount it into sandboxes.

---

## ⚫ Interview Questions + Answers

Q1: What does `--network none` provide?
A1: Only loopback; no external interfaces.

Q2: When would you use it?
A2: Untrusted code execution, offline batch processing, security-sensitive transforms.

Q3: How does a `none` container exchange data?
A3: Via volumes, stdin/stdout, or `docker cp`.

Q4: Is it enough to secure untrusted code?
A4: No; combine with dropped capabilities, seccomp/AppArmor, read-only FS, resource limits, non-root.

Q5: Can you attach a `none` container to another network later?
A5: `none` is meant to be exclusive and Docker restricts mixing it with other networks; the clean approach is to recreate the container with the network you want.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running untrusted or third-party code
- Offline processing of sensitive files
- Reducing blast radius of a risky component

❌ Avoid when:
- The app serves requests or calls APIs/DBs
- It needs DNS, package downloads or telemetry at runtime

---

## 📊 Visual Diagram
```
  bridge container               none container
 +------------------+          +------------------+
 | eth0 172.17.0.2  |          |   lo 127.0.0.1   |
 | lo               |          |   (nothing else) |
 +--------+---------+          +--------+---------+
          |                             X  no route
      docker0 --- NAT --- Internet      |
                                  [volume /in  /out]
                                   (only data path)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Loopback | Interface to talk to self | खुद से बात का interface |
| Sandbox | Restricted execution area | सीमित सुरक्षित क्षेत्र |
| Capability | Fine-grained root privilege | root के छोटे अधिकार |
| no-new-privileges | Block privilege escalation | अधिकार बढ़ने पर रोक |
| Exfiltration | Stealing data out | data चुराकर बाहर भेजना |
| Egress | Outbound traffic | बाहर जाने वाला traffic |

---

## ⚡ 3-Line Summary
English: `none` gives a container only loopback and no outside connectivity.
Ideal for untrusted or offline jobs, combined with other hardening flags.
Data moves through volumes only.
Hindi: `none` container को सिर्फ loopback देता है, बाहर कोई connectivity नहीं।
Untrusted या offline jobs के लिए आदर्श, बाकी hardening flags के साथ।
Data सिर्फ volumes से आता-जाता है।

---

## ➡️ Next Topic
**170. Overlay Network** - from the most isolated driver to the one that connects containers across multiple hosts.
