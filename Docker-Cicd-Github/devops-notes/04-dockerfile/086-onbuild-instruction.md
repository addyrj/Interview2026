# 086. ONBUILD Instruction
# हिंदी में: ONBUILD इंस्ट्रक्शन (Child Build पर चलने वाला Trigger)

---

## 🔵 Simple Definition (English)
`ONBUILD` registers an instruction as a **trigger** that does not run when you build the current image. It runs later, right after the `FROM` line, when another Dockerfile uses this image as its base. It is for building reusable "base builder" images.

## 🔵 सरल परिभाषा (Hindi)
`ONBUILD` एक instruction को **trigger** के रूप में register करता है जो मौजूदा image बनाते समय नहीं चलती। वह बाद में, जब कोई दूसरी Dockerfile इस image को base बनाती है, तब `FROM` लाइन के ठीक बाद चलती है। यह reusable "base builder" images बनाने के लिए है।

---

## 🔴 Problem it Solves
An organisation has 30 Node.js microservices, and every Dockerfile repeats the same steps: copy `package.json`, run `npm ci`, copy the source. Copy-paste drifts. The platform team wanted a base image that already knows "when someone builds on me, copy their package files and install". ONBUILD provided that: child Dockerfiles become two lines. Historically, language stack images (`node:onbuild`, `python:onbuild`) did exactly this, but they were deprecated because the hidden behaviour surprised people.

## 🔴 यह क्यों बना? (Hindi)
एक organisation के 30 Node.js microservices हैं और हर Dockerfile में वही steps दोहराए जाते हैं: `package.json` copy करो, `npm ci` चलाओ, source copy करो। Copy-paste में फर्क आ जाता है। Platform team को ऐसी base image चाहिए थी जो जाने कि "जब कोई मुझ पर build करे तो उसकी package files copy करके install कर दो"। ONBUILD यही देता है: child Dockerfile सिर्फ दो लाइन की हो जाती है। इतिहास में `node:onbuild`, `python:onbuild` जैसी images यही करती थीं, लेकिन छिपे व्यवहार से लोग चौंकते थे इसलिए उन्हें deprecate किया गया।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parent Dockerfile contains:  ONBUILD COPY . /app   (NOT executed now)
Step 2 → Parent build finishes; trigger is stored in image config (OnBuild list)
Step 3 → docker inspect parent --format '{{.Config.OnBuild}}' shows stored triggers
Step 4 → Child Dockerfile: FROM parent
Step 5 → Builder runs triggers IMMEDIATELY after FROM, in the order registered
Step 6 → Triggers are NOT inherited by grandchildren (executed once, then cleared)
```

Rules: `ONBUILD ONBUILD` and `ONBUILD FROM`/`MAINTAINER` are not allowed. Triggers run in the child's build context, so `COPY` copies from the child's folder.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Parent Dockerfile में:  ONBUILD COPY . /app   (अभी नहीं चलती)
Step 2 → Parent build खत्म; trigger image config (OnBuild list) में store होता है
Step 3 → docker inspect parent --format '{{.Config.OnBuild}}' से stored triggers दिखते हैं
Step 4 → Child Dockerfile: FROM parent
Step 5 → Builder triggers को FROM के तुरंत बाद, register होने के क्रम में चलाता है
Step 6 → Triggers grandchild को inherit नहीं होते (एक बार चलकर साफ हो जाते हैं)
```

नियम: `ONBUILD ONBUILD` और `ONBUILD FROM`/`MAINTAINER` मना हैं। Triggers child के build context में चलते हैं, इसलिए `COPY` child के folder से copy करती है।

---

## 🟡 Real World Example
A platform team in a company with many Node.js services publishes `registry.example.com/base/node-service:20`. It has `ONBUILD COPY package*.json ./`, `ONBUILD RUN npm ci --omit=dev`, `ONBUILD COPY . .`. A service team writes `FROM registry.example.com/base/node-service:20` + `CMD ["node","server.js"]`. When the platform team bumps the Node patch version or the install flags, all services get it at their next build. The downside showed up when one service had a private npm registry and the hidden `npm ci` failed with no visible reason in their Dockerfile, so the team had to read the base image to debug.

## 🟡 Real Example Hindi mein
कई Node.js services वाली कंपनी की platform team `registry.example.com/base/node-service:20` publish करती है। इसमें `ONBUILD COPY package*.json ./`, `ONBUILD RUN npm ci --omit=dev`, `ONBUILD COPY . .` हैं। Service team सिर्फ `FROM registry.example.com/base/node-service:20` + `CMD ["node","server.js"]` लिखती है। Platform team Node patch version या install flags बदलती है तो सभी services अगले build में पा लेती हैं। नुकसान तब दिखा जब एक service में private npm registry थी और छिपा हुआ `npm ci` बिना किसी दिखने वाली वजह के fail हुआ; debug के लिए base image पढ़नी पड़ी।

---

## 💻 Code / Config Example — Basic

Parent (base) Dockerfile:

```dockerfile
# Parent image: base/node-service (build once, e.g. docker build -t node-service:20 .)
# Base image (example tag)
FROM node:20-alpine
# Working directory used by children
WORKDIR /app
# TRIGGER: runs in the child's build, copies the child's package files
ONBUILD COPY package*.json ./
# TRIGGER: install production dependencies in the child
ONBUILD RUN npm ci --omit=dev
# TRIGGER: copy the child's source code
ONBUILD COPY . .
# Normal instruction: runs now and for every child
USER node
```

Child Dockerfile (this is the whole file):

```dockerfile
# Child service Dockerfile: the ONBUILD triggers run right after this FROM
FROM node-service:20
# Only the start command is service specific
CMD ["node", "server.js"]
```

```bash
# Build the parent first
docker build -t node-service:20 -f Dockerfile.base .
# Show stored triggers
docker inspect --format '{{json .Config.OnBuild}}' node-service:20
# Build a child; build output shows "Executing 3 build triggers" on the classic builder
docker build -t orders-api .
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Advanced parent: a Python/FastAPI service base with guarded triggers and normal hardening
# Python slim base (example tag)
FROM python:3.12-slim
# Runtime flags for all children
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
# Shared working directory
WORKDIR /app
# Non-root user created once in the base
RUN useradd --system --uid 10001 --no-create-home appuser
# TRIGGER: child must provide requirements.txt (the build fails clearly if it is missing)
ONBUILD COPY requirements.txt ./
# TRIGGER: install with a pip cache mount (BuildKit) so rebuilds are fast
ONBUILD RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
# TRIGGER: copy the application package from the child
ONBUILD COPY app ./app
# Document the usual port
EXPOSE 8000
# Run unprivileged in every child
USER 10001
# Default command; children may override
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Label explaining the hidden behaviour so people can find it via docker inspect
LABEL com.example.base.note="Has ONBUILD triggers: copies requirements.txt and app/, runs pip install"
```

```dockerfile
# Child: complete FastAPI service Dockerfile (triggers perform the rest)
FROM registry.example.com/base/fastapi-service:3.12
```

An explicit alternative with no hidden magic (recommended today) is a shared multi-stage template or a reusable CI workflow:

```yaml
# .github/workflows/build.yml: reusable workflow call instead of ONBUILD magic
name: build
# Run on pull requests
on: [pull_request]
jobs:
  call-shared-build:
    # Call a shared workflow stored in a platform repo (example path, update)
    uses: your-org/platform-workflows/.github/workflows/docker-build.yml@main
    # Pass only non-secret inputs
    with:
      image-name: orders-api
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: for a few services in one repo, do not bother. Use a normal multi-stage Dockerfile; it is explicit and easy to debug.
- **React + Nginx**: no value; a standard two-stage build (node build -> nginx) is clearer.
- **GitHub Actions**: shared logic belongs in reusable workflows or composite actions, which are visible and versioned. ONBUILD images are a Docker-level alternative.
- **VPS / AWS**: if you publish a base image to ECR/GHCR, you must publish both the base and the children in an order, and rebuild children when the base changes (CI trigger on base update, e.g. Renovate/Dependabot).
- **Security**: hidden `ONBUILD RUN` executes arbitrary commands in the builds of anyone who uses your image. Only use ONBUILD base images from sources you trust, and pin by digest (`FROM image@sha256:...`).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using ONBUILD for logic that is not obviously visible, and then nobody understands the build.
✅ Correct: Prefer explicit Dockerfiles. Use ONBUILD only for a small documented platform base image.

❌ Mistake 2: Expecting triggers to run when building the parent itself.
✅ Correct: They run only in the child build. Test them by actually building a child.

❌ Mistake 3: Expecting grandchildren to run the triggers again.
✅ Correct: Triggers execute once in the direct child's build and are not inherited further.

❌ Mistake 4: Pulling an unknown ONBUILD base image.
✅ Correct: Inspect first: `docker inspect --format '{{.Config.OnBuild}}' IMAGE`.

❌ Mistake 5: `ONBUILD ADD . /app` (an ADD with a URL/tar) hidden in bases.
✅ Correct: Use `COPY`; keep triggers minimal.

---

## 🧠 Tricky Interview Question
Image A has `ONBUILD RUN echo A`. Image B is `FROM A` and has `ONBUILD RUN echo B`. Image C is `FROM B`. What prints when you build B and when you build C?

Answer: Building B prints `A` (A's trigger fires right after `FROM A`). B stores only its own trigger `echo B`, because A's trigger was consumed and is not inherited. Building C prints `B`. `A` does not print again. Triggers are one-level deep.

---

## ⚫ Interview Questions + Answers

Q1: When does an ONBUILD instruction run?
A1: In the build of a child image, immediately after its `FROM`, not when the image that contains it is built.

Q2: How can you see triggers?
A2: `docker inspect --format '{{.Config.OnBuild}}' IMAGE`.

Q3: Why are ONBUILD images discouraged?
A3: Hidden behaviour, harder debugging, build context assumptions, and surprising execution of commands. Explicit multi-stage Dockerfiles or reusable CI workflows are clearer.

Q4: Which instructions are not allowed with ONBUILD?
A4: `ONBUILD ONBUILD`, `ONBUILD FROM`, and `ONBUILD MAINTAINER`.

Q5: Are ONBUILD triggers inherited by grandchildren?
A5: No, they run once for the immediate child.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A platform team ships a tightly controlled language base for many similar services and documents it.
- Legacy tooling already depends on it.

❌ Avoid when:
- You can use multi-stage builds, templates, or shared CI workflows.
- Teams new to Docker will debug it (hidden steps).
- You cannot guarantee the build context layout in children.

---

## 📊 Visual Diagram

```
 Parent Dockerfile             Child Dockerfile
 -----------------             ----------------
 FROM node:20-alpine           FROM node-service:20
 ONBUILD COPY package*.json      |
 ONBUILD RUN npm ci              +--> triggers fire HERE (right after FROM)
 ONBUILD COPY . .                |      1. COPY package*.json
        |                        |      2. RUN npm ci
  docker build parent            |      3. COPY . .
  (triggers only STORED)         |
                                 v
                           CMD ["node","server.js"]  (child's own steps)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ONBUILD | Deferred build trigger | बाद में चलने वाला trigger |
| Trigger | Stored instruction to run later | बाद में चलने के लिए रखी instruction |
| Parent/base image | Image used in FROM | FROM में use होने वाली image |
| Child image | Image built FROM another | दूसरी से बनी image |
| Reusable workflow | Shared GitHub Actions workflow | साझा GitHub Actions workflow |
| Digest pin | Fix image by sha256 | sha256 से image fix करना |

---

## ⚡ 3-Line Summary
English: ONBUILD stores instructions that run only when another image builds FROM yours. It makes reusable bases possible but hides behaviour, so prefer explicit multi-stage Dockerfiles or shared workflows. Triggers run once, in the direct child.
Hindi: ONBUILD ऐसी instructions रखता है जो तभी चलती हैं जब कोई दूसरी image आप पर FROM करके बने। इससे reusable bases बनते हैं पर व्यवहार छिप जाता है, इसलिए explicit multi-stage Dockerfile या shared workflows बेहतर हैं। Triggers सिर्फ सीधे child में एक बार चलते हैं।

---

## ➡️ Next Topic
**087. SHELL Instruction**: next, how Docker decides which shell runs your `RUN` lines, and how to change it.
