# 73. RUN Instruction
# हिंदी में: RUN Instruction (Build के समय commands चलाना)

---

## 🔵 Simple Definition (English)
`RUN` executes a command at image build time and commits the result as a new layer. It has two forms: shell form `RUN apt-get update` (runs via `/bin/sh -c`) and exec form `RUN ["executable","arg"]` (no shell).

## 🔵 सरल परिभाषा (Hindi)
`RUN` image build के समय एक command चलाता है और उसका नतीजा नई layer के रूप में commit करता है। दो forms हैं: shell form `RUN apt-get update` (`/bin/sh -c` से चलता है) और exec form `RUN ["executable","arg"]` (shell नहीं)।

---

## 🔴 Problem it Solves
An image needs software installed, code compiled and folders prepared before it ever runs. Doing that at container start makes startup slow and non-deterministic (network down, package changed). `RUN` does this once at build time and freezes the result in a cached layer, so every container starts instantly from the same prepared filesystem.

## 🔴 यह क्यों बना? (Hindi)
Image को चलने से पहले software install, code compile और folders तैयार चाहिए। यह सब container start पर करने से startup धीमा और अनिश्चित हो जाता है (network बंद, package बदला)। `RUN` यह काम build के समय एक बार करके नतीजा cached layer में जमा देता है, इसलिए हर container उसी तैयार filesystem से तुरंत start होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Builder starts a temporary container from the previous layer
Step 2 → Executes the command inside it (shell form: /bin/sh -c "cmd")
Step 3 → Non-zero exit code = build fails
Step 4 → Filesystem changes are saved as a new layer
Step 5 → Layer is cached by the instruction text; same text + same parent = cache hit
Step 6 → Files deleted in a LATER RUN do not shrink earlier layers
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Builder पिछली layer से एक temporary container शुरू करता है
Step 2 → उसके अंदर command चलाता है (shell form: /bin/sh -c "cmd")
Step 3 → Exit code non-zero हुआ तो build fail
Step 4 → Filesystem के बदलाव नई layer में save होते हैं
Step 5 → Layer instruction के text से cache होती है; वही text + वही parent = cache hit
Step 6 → बाद वाले RUN में delete की गई files पुरानी layers को छोटा नहीं करतीं
```

---

## 🟡 Real World Example
A FastAPI team had three lines: `RUN apt-get update`, `RUN apt-get install -y gcc`, `RUN pip install ...`. After a few months the cached `apt-get update` layer was stale, and `install` failed with 404 on package URLs in CI. Merging into one `RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*` fixed the staleness and cut 60 MB from the image. A Node team also moved `npm ci` into its own `RUN` after copying only `package*.json`, saving minutes per CI run.

## 🟡 Real Example Hindi mein
एक FastAPI team की तीन lines थीं: `RUN apt-get update`, `RUN apt-get install -y gcc`, `RUN pip install ...`। कुछ महीनों बाद cached `apt-get update` layer पुरानी हो गई और CI में `install` package URLs पर 404 देने लगा। सबको एक `RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*` में जोड़ने से staleness ठीक हुई और image 60 MB छोटी हुई। एक Node team ने सिर्फ `package*.json` copy करके `npm ci` को अलग `RUN` में रखा, जिससे हर CI run में मिनटों की बचत हुई।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Dockerfile -- basic RUN usage (example versions)
# Debian-based Python image
FROM python:3.12-slim
# set working dir
WORKDIR /app
# copy dependency list first for caching
COPY requirements.txt .
# install Python deps, no pip cache stored in layer
RUN pip install --no-cache-dir -r requirements.txt
# copy app code after deps
COPY . .
# optional: precompile bytecode at build time
RUN python -m compileall app
# start command (runtime, not RUN)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

## 💻 Code / Config Example — Advanced
```dockerfile
# syntax=docker/dockerfile:1.7
# Dockerfile -- RUN with cache mounts, secrets, heredoc, strict shell (BuildKit required)
# base image (example tag)
FROM python:3.12-slim
# make pipes fail the build; use bash for RUN
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# avoid interactive apt prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# one RUN: update+install, cached apt dirs
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates

# app dir
WORKDIR /app
# manifest first
COPY requirements.txt .
# pip cache kept outside the image, speeds rebuilds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Private package index: secret is mounted only during this RUN and never stored in a layer
# token not written to image history
RUN --mount=type=secret,id=pip_token \
    PIP_INDEX_URL="https://__token__:$(cat /run/secrets/pip_token)@pypi.example.com/simple" \
    pip install -r requirements-private.txt

RUN <<EOF
set -eux
useradd --system --uid 10001 app
mkdir -p /app/data && chown app:app /app/data
EOF
# drop root after setup
USER app
```
Build: `docker build --secret id=pip_token,src=./token.txt .` (BuildKit; not run locally). Heredoc `RUN <<EOF` and `--mount` need BuildKit/Dockerfile syntax 1.4+; version-dependent. Bash blocks were `bash -n` checked.

---

## 🟠 My Stack Integration
Group RUN steps by change frequency: OS packages, dependencies, then build. In GitHub Actions, add the BuildKit cache so those layers survive between runs.

```yaml
# .github/workflows/build.yml -- reuse RUN-layer cache in CI
name: build                                 # workflow name
on: [push]                                  # trigger
jobs:                                       # jobs
  build:                                    # job id
    runs-on: ubuntu-latest                  # runner
    steps:                                  # steps
      - uses: actions/checkout@v4           # code (example version)
      - uses: docker/setup-buildx-action@v3 # BuildKit builder
      - uses: docker/build-push-action@v6   # build image
        with:                               # inputs
          context: .                        # context dir
          secrets: |                        # pass build secret safely
            pip_token=${{ secrets.PIP_TOKEN }}
          cache-from: type=gha              # restore layers
          cache-to: type=gha,mode=max       # save layers
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Separate `RUN apt-get update` and `RUN apt-get install`.
✅ Correct: Chain with `&&` in one `RUN` so update and install share one layer.

❌ Mistake 2: Cleanup in a different `RUN` (`RUN rm -rf /var/lib/apt/lists/*` after install).
✅ Correct: Clean in the same `RUN`; otherwise earlier layer keeps the data.

❌ Mistake 3: `RUN curl ... | sh` without verifying, or `ARG TOKEN` for secrets.
✅ Correct: Verify checksums, use `--mount=type=secret`; ARG values show in `docker history`.

❌ Mistake 4: Piped commands hiding failures (`RUN cmd1 | cmd2`).
✅ Correct: `SHELL ["/bin/bash","-o","pipefail","-c"]` or `set -o pipefail`.

---

## 🧠 Tricky Interview Question
`RUN source venv/bin/activate` then next line `RUN pip install x` installs into the system Python, not the venv. Why?

Answer: Each `RUN` is a separate shell process; environment changes (activate, `cd`, `export`) vanish when it ends. Use `ENV PATH="/opt/venv/bin:$PATH"` (persists in image metadata), `WORKDIR` instead of `cd`, or call `/opt/venv/bin/pip` directly.

---

## ⚫ Interview Questions + Answers

Q1: Shell form vs exec form of RUN?
A1: Shell form runs through `/bin/sh -c` (supports `&&`, pipes, variable expansion). Exec form runs the binary directly with no shell processing; needed when the image has no shell.

Q2: Does RUN run when the container starts?
A2: No. It runs only during `docker build`. Start-time commands are `CMD`/`ENTRYPOINT`.

Q3: How do you reduce layers/size from RUN?
A3: Combine related commands, clean caches in the same layer, use `--no-install-recommends`, multi-stage builds, and cache mounts.

Q4: Why does a cached `RUN apt-get update` become dangerous?
A4: Docker caches by instruction text, not by the result, so the old package index can persist; use `--no-cache` or chain update+install.

Q5: How to pass secrets safely to RUN?
A5: BuildKit `RUN --mount=type=secret`, or SSH mounts for private Git; never `ARG`/`ENV`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Installing OS packages and app dependencies.
- Compiling/bundling (`npm run build`).
- Creating users, folders, permissions.

❌ Avoid when:
- Starting servers or migrations (belongs at runtime).
- Storing secrets in layers.
- Doing environment-specific config that differs per deploy.

---

## 📊 Visual Diagram
```
  RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
        |
        v
  [temp container] -> run cmd -> exit 0 -> snapshot diff -> NEW LAYER (cached)
        |
        +-- exit != 0  ->  BUILD FAILS
  Bad:  RUN install ...  (layer 5: +80MB)  RUN rm cache (layer 6: whiteout)  => still 80MB
  Good: install + rm in ONE RUN                                              => cache never stored
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Shell form | Runs via /bin/sh -c | Shell के ज़रिए चलना |
| Exec form | JSON array, no shell | Shell के बिना सीधा चलना |
| Cache mount | Persistent build cache dir | Build का स्थायी cache folder |
| Heredoc | Multi-line script in RUN | RUN में multi-line script |
| pipefail | Fail if any pipe stage fails | Pipe में कोई भी fail तो fail |
| Whiteout | Delete marker | Delete का marker |

---

## ⚡ 3-Line Summary
English: `RUN` executes commands at build time and stores the result in a layer. Chain update, install and cleanup in one RUN, and use BuildKit secrets and caches. Each RUN is a fresh shell.
Hindi: `RUN` build के समय commands चलाकर नतीजा layer में रखता है। Update, install और cleanup एक ही RUN में जोड़ो, और BuildKit secrets/caches इस्तेमाल करो। हर RUN एक नया shell है।

---

## ➡️ Next Topic
**74. CMD vs ENTRYPOINT** — build के बाद container start होने पर क्या चलेगा, यह तय करने वाली instructions।
