# 087. SHELL Instruction
# हिंदी में: SHELL इंस्ट्रक्शन (Default Shell बदलना)

---

## 🔵 Simple Definition (English)
`SHELL` changes the default shell used by the **shell form** of `RUN`, `CMD` and `ENTRYPOINT`. On Linux the default is `["/bin/sh", "-c"]`. You write it in JSON array form, for example `SHELL ["/bin/bash", "-o", "pipefail", "-c"]`.

## 🔵 सरल परिभाषा (Hindi)
`SHELL` `RUN`, `CMD` और `ENTRYPOINT` के **shell form** द्वारा इस्तेमाल होने वाला default shell बदलता है। Linux में default `["/bin/sh", "-c"]` है। इसे JSON array में लिखते हैं, जैसे `SHELL ["/bin/bash", "-o", "pipefail", "-c"]`।

---

## 🔴 Problem it Solves
`/bin/sh` (dash or busybox ash) lacks bash features such as `[[ ]]`, arrays, `set -o pipefail` and process substitution. Worse, in `RUN curl ... | tar xz`, if `curl` fails the pipe's exit status is `tar`'s status (0), so the build **silently succeeds with a broken file**. Changing the shell with `pipefail` makes the whole pipe fail. On Windows images, `SHELL` switches between `cmd` and `powershell`.

## 🔴 यह क्यों बना? (Hindi)
`/bin/sh` (dash या busybox ash) में bash के features नहीं होते जैसे `[[ ]]`, arrays, `set -o pipefail`, process substitution। इससे बुरा, `RUN curl ... | tar xz` में अगर `curl` fail हो तो pipe का exit status `tar` का (0) होता है, तो build **चुपचाप टूटी file के साथ सफल** हो जाता है। `pipefail` वाला shell बदलने से पूरा pipe fail होता है। Windows images में `SHELL` से `cmd` और `powershell` के बीच बदलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Default (Linux): RUN npm ci  is executed as  /bin/sh -c "npm ci"
Step 2 → Add:  SHELL ["/bin/bash", "-o", "pipefail", "-c"]
Step 3 → Every later shell-form RUN/CMD/ENTRYPOINT now runs as  /bin/bash -o pipefail -c "..."
Step 4 → Exec-form (JSON) commands are NOT affected, they run without any shell
Step 5 → SHELL can appear many times; each affects the lines after it
Step 6 → The shell binary must exist in the image (alpine: install bash first)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Default (Linux): RUN npm ci  असल में  /bin/sh -c "npm ci"  की तरह चलता है
Step 2 → जोड़ो:  SHELL ["/bin/bash", "-o", "pipefail", "-c"]
Step 3 → इसके बाद हर shell-form RUN/CMD/ENTRYPOINT  /bin/bash -o pipefail -c "..."  से चलता है
Step 4 → Exec-form (JSON) commands पर असर नहीं, वे बिना shell के चलते हैं
Step 5 → SHELL कई बार आ सकता है; हर बार अपनी बाद वाली lines पर असर करता है
Step 6 → Shell binary image में मौजूद होनी चाहिए (alpine में पहले bash install करो)
```

---

## 🟡 Real World Example
A CI build downloads a vendor binary: `RUN curl -sSL https://example.com/tool.tgz | tar -xz -C /usr/local/bin`. One day the vendor's server returns 503. `curl` fails, but `tar` just reads empty input and exits 0 (or prints an error that the default `sh` ignores since the last command status is used), and the image is built and deployed without the tool. The app then crashes in production with "tool: not found". After adding `SHELL ["/bin/bash","-o","pipefail","-c"]`, the same 503 fails the build immediately in CI, where it is cheap to fix.

## 🟡 Real Example Hindi mein
CI build vendor की एक binary download करता है: `RUN curl -sSL https://example.com/tool.tgz | tar -xz -C /usr/local/bin`। एक दिन vendor का server 503 देता है। `curl` fail होता है पर default `sh` आखिरी command का status देखता है, इसलिए image बन जाती है और tool के बिना deploy हो जाती है। फिर production में app "tool: not found" पर crash होती है। `SHELL ["/bin/bash","-o","pipefail","-c"]` जोड़ने के बाद वही 503 CI में ही build fail कर देता है, जहाँ ठीक करना सस्ता है।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Basic SHELL example: make pipes fail the build (Debian-based image has bash)
# Base image (example tag; debian based, includes /bin/bash)
FROM node:20-bookworm-slim
# Use bash with pipefail for all following shell-form instructions
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# Working directory
WORKDIR /app
# If curl fails, the whole RUN now fails (without pipefail it would pass silently)
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
# Pipe example: fails if either side fails
RUN curl -fsSL https://nodejs.org/dist/index.json | head -c 100 > /tmp/index-head.txt
# Bash-only feature [[ ]] works now
RUN [[ -f /tmp/index-head.txt ]] && echo "file exists"
# Start the app (exec form does not use SHELL at all)
CMD ["node", "server.js"]
```

```bash
# Build; add --progress=plain to read the full output
docker build --progress=plain -t shell-demo .
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Advanced: alpine needs bash installed first; switch SHELL only after installing it
# Alpine base (example tag; has only busybox ash by default)
FROM node:20-alpine
# Working directory
WORKDIR /app
# Step 1: still using the default /bin/sh here (bash is not installed yet)
RUN apk add --no-cache bash curl
# Step 2: now switch to bash with strict flags: e = exit on error, u = unset var is error, o pipefail
SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
# Multi-line script: runs as ONE bash process, so set -e semantics apply to every command
RUN echo "downloading checksum file" \
    && curl -fsSL https://example.com/tool.sha256 -o /tmp/tool.sha256 \
    && test -s /tmp/tool.sha256 \
    && echo "checksum downloaded"
# Heredoc (BuildKit syntax 1.4+): readable multi-line script in the selected shell
RUN <<EOF
set -x
mkdir -p /app/data
echo "ready" > /app/data/status.txt
EOF
# Copy manifests then install
COPY package*.json ./
# Install production dependencies
RUN npm ci --omit=dev
# Source code
COPY . .
# Non-root user
USER node
# Switching back is allowed too (affects only later shell-form lines)
SHELL ["/bin/sh", "-c"]
# Exec form is shell-free and handles signals properly (preferred)
CMD ["node", "server.js"]
```

Alternative without `SHELL`: per-line option.

```dockerfile
# Inline alternative: invoke bash only for the lines that need it
RUN ["/bin/bash", "-o", "pipefail", "-c", "curl -fsSL https://example.com/a | tar -xz -C /opt"]
```

```yaml
# .github/workflows/lint-dockerfile.yml: catch missing pipefail with hadolint (DL4006)
name: dockerfile-lint
# Run on pull requests
on: [pull_request]
jobs:
  hadolint:
    # GitHub hosted runner
    runs-on: ubuntu-latest
    steps:
      # Get the code
      - uses: actions/checkout@v4
      # Official hadolint action (example version, update to latest)
      - uses: hadolint/hadolint-action@v3.1.0
        with:
          # Which Dockerfile to lint
          dockerfile: Dockerfile
```

---

## 🟠 My Stack Integration
- **Node.js (alpine)**: either install bash first (as above) or write pipe-free `RUN` lines; avoid bash-only syntax on `sh`.
- **FastAPI (python:slim = Debian)**: bash is already present, so a simple `SHELL ["/bin/bash","-o","pipefail","-c"]` at the top works.
- **React / Nginx**: build stage is Node (see above); the final `nginx:alpine` stage needs no SHELL, since it is just `COPY`.
- **GitHub Actions**: lint with hadolint (rule DL4006 reminds you about pipefail). Its action is third party; pin the version.
- **VPS / AWS**: nothing special, but `SHELL` is Dockerfile only; it does not change what shell `docker exec` or your SSH session uses.
- **Security**: `curl | bash` installers in RUN are risky even with pipefail; download, verify checksum, then execute.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `SHELL ["/bin/bash", ...]` on alpine without installing bash. Build fails: "/bin/bash: no such file".
✅ Correct: `RUN apk add --no-cache bash` first, then SHELL.

❌ Mistake 2: Writing `SHELL /bin/bash -c` (not JSON).
✅ Correct: Must be JSON array: `SHELL ["/bin/bash", "-c"]`.

❌ Mistake 3: Expecting `CMD ["npm","start"]` (exec form) to use the new shell.
✅ Correct: Only shell form (`CMD npm start`) uses SHELL. Exec form is better for signals anyway.

❌ Mistake 4: Forgetting the trailing `-c`.
✅ Correct: The last array element must be the flag that takes a command string.

❌ Mistake 5: Assuming `SHELL` persists in the running container.
✅ Correct: It only affects how Dockerfile instructions are executed.

---

## 🧠 Tricky Interview Question
`RUN wget -qO- https://bad.example/x.sh | sh` fails to resolve DNS, yet the build passes. Later `RUN somecommand` fails at deploy. Why did the build pass, and how do you fix it without changing the line?

Answer: In a pipeline, the exit status is that of the last command (`sh`), which got empty input and returned 0. The failure of `wget` is lost. Without changing the line, add `SHELL ["/bin/bash","-o","pipefail","-c"]` above it (so a failure on any side fails the pipe). Better still, split into download, verify and run steps so failures are visible.

---

## ⚫ Interview Questions + Answers

Q1: What is the default shell on Linux and Windows images?
A1: Linux: `["/bin/sh", "-c"]`. Windows: `["cmd", "/S", "/C"]`.

Q2: Does SHELL affect exec form?
A2: No. Exec (JSON) form runs the binary directly without a shell.

Q3: Why use pipefail?
A3: So that a pipeline fails if any command in it fails, not only the last one.

Q4: Can SHELL be used more than once?
A4: Yes. Each instruction changes the shell for all later shell-form instructions until changed again.

Q5: How do you use bash on Alpine?
A5: Install it (`apk add --no-cache bash`) and then `SHELL ["/bin/bash","-c"]`. Or stick to POSIX sh syntax.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have pipes in `RUN` lines and want builds to fail correctly.
- You need bash features (arrays, `[[ ]]`).
- Windows containers switching to PowerShell.

❌ Avoid when:
- Your `RUN` lines are simple and POSIX compatible, and image size matters (installing bash on alpine adds size).
- You can instead chain with `&&` and avoid pipes.

---

## 📊 Visual Diagram

```
 Default                                After SHELL
 -------                                -----------
 RUN a | b                              SHELL ["/bin/bash","-o","pipefail","-c"]
   |                                    RUN a | b
   v                                      |
 /bin/sh -c "a | b"                       v
   |                                    /bin/bash -o pipefail -c "a | b"
   v                                      |
 status = status of b only                v
 (a failing is HIDDEN)                  status = non-zero if a OR b fails
                                        (build stops, bug caught in CI)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SHELL | Sets shell for shell-form commands | shell-form commands का shell तय करता है |
| Shell form | `RUN cmd args` (uses a shell) | shell के साथ चलने वाला रूप |
| Exec form | `RUN ["cmd","arg"]` (no shell) | बिना shell का JSON रूप |
| pipefail | Pipe fails if any part fails | pipe का कोई भाग fail तो fail |
| busybox ash | Small shell in Alpine | Alpine का छोटा shell |
| Heredoc | Multi-line script block | कई lines का script block |

---

## ⚡ 3-Line Summary
English: SHELL replaces the default `/bin/sh -c` used by shell-form instructions. Use it for `pipefail` and bash features, and install bash first on Alpine. Exec form ignores it.
Hindi: SHELL shell-form instructions के default `/bin/sh -c` को बदलता है। `pipefail` और bash features के लिए use करो, और Alpine में पहले bash install करो। Exec form इसे ignore करता है।

---

## ➡️ Next Topic
**088. .dockerignore File**: now that the Dockerfile is solid, control what even reaches the build, for speed and security.
