# 77. WORKDIR Instruction
# हिंदी में: WORKDIR Instruction (Working directory तय करना)

---

## 🔵 Simple Definition (English)
`WORKDIR /path` sets the working directory for the instructions that follow (`RUN`, `CMD`, `ENTRYPOINT`, `COPY`, `ADD`) and for the running container's main process. It creates the directory if it does not exist. Relative paths in later `WORKDIR` lines build on the previous one.

## 🔵 सरल परिभाषा (Hindi)
`WORKDIR /path` आगे की instructions (`RUN`, `CMD`, `ENTRYPOINT`, `COPY`, `ADD`) और चलते container की main process के लिए working directory तय करता है। Directory न हो तो वह बना देता है। बाद की `WORKDIR` में relative path पिछली directory के ऊपर जुड़ता है।

---

## 🔴 Problem it Solves
Without WORKDIR, files land in `/` (the filesystem root), mixing app code with system folders, and people write `RUN cd /app && ...` which does not persist to the next instruction. WORKDIR gives one clean, persistent place for the app, making paths short, predictable and the container's startup directory correct.

## 🔴 यह क्यों बना? (Hindi)
WORKDIR के बिना files `/` (root) में पहुँचती हैं और app code system folders में मिल जाता है, और लोग `RUN cd /app && ...` लिखते हैं जो अगली instruction तक नहीं टिकता। WORKDIR app के लिए एक साफ़, स्थायी जगह देता है: paths छोटे और अनुमानित, और container की startup directory सही।

---

## 🟢 How it Works — Step by Step

```
Step 1 → WORKDIR /app   -> directory is created (mode 755, owned by root) if missing
Step 2 → Every later RUN/CMD/ENTRYPOINT/COPY/ADD starts in /app
Step 3 → COPY . .  means: context root -> /app (relative destination uses WORKDIR)
Step 4 → WORKDIR src    -> becomes /app/src (relative path is appended)
Step 5 → WORKDIR can use ENV variables: WORKDIR $HOME/app
Step 6 → docker run -w /other overrides it at runtime
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → WORKDIR /app   -> directory न हो तो बनती है (mode 755, owner root)
Step 2 → आगे की हर RUN/CMD/ENTRYPOINT/COPY/ADD /app में शुरू होती है
Step 3 → COPY . .  का मतलब: context root -> /app (relative destination WORKDIR से बनता है)
Step 4 → WORKDIR src    -> /app/src बन जाता है (relative path जुड़ता है)
Step 5 → WORKDIR में ENV variables चलते हैं: WORKDIR $HOME/app
Step 6 → docker run -w /other runtime पर इसे बदल देता है
```

---

## 🟡 Real World Example
A junior wrote `RUN cd /app` then `RUN npm install` in the next line; npm ran in `/` and failed or polluted the root with `node_modules`. Another team ran the Node app as a non-root user but `WORKDIR` was created by root, so the app could not write `/app/uploads` and returned 500 on file upload. Fix: `WORKDIR /app` plus `COPY --chown=node:node` and `RUN mkdir -p uploads && chown node:node uploads` before `USER node`.

## 🟡 Real Example Hindi mein
एक junior ने `RUN cd /app` लिखा और अगली line में `RUN npm install`; npm `/` में चला और fail हुआ या root में `node_modules` बन गया। दूसरी team ने Node app non-root user से चलाया पर `WORKDIR` root ने बनाई थी, इसलिए app `/app/uploads` में लिख नहीं पाई और file upload पर 500 आया। समाधान: `WORKDIR /app`, `COPY --chown=node:node`, और `USER node` से पहले `RUN mkdir -p uploads && chown node:node uploads`।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Dockerfile -- basic WORKDIR (example tag)
FROM node:20-alpine
# Create and enter /app; all relative paths below use it
WORKDIR /app
# Copies package files into /app/
COPY package*.json ./
# Runs in /app, so node_modules is created at /app/node_modules
RUN npm ci --omit=dev
# Copies source into /app
COPY . .
# Runs from /app at container start
CMD ["node", "server.js"]
```

## 💻 Code / Config Example — Advanced
```dockerfile
# Dockerfile -- WORKDIR with non-root user, nested relative paths and ENV (example tags)
FROM python:3.12-slim
# Variable usable inside WORKDIR
ENV APP_HOME=/srv/api
# Create a system user without login shell
RUN groupadd -r app && useradd -r -g app -d /srv/api -s /usr/sbin/nologin app
# Create /srv/api (owned by root, we fix ownership below)
WORKDIR $APP_HOME
# Create writable folders and hand them to the app user while still root
RUN mkdir -p data logs && chown -R app:app data logs
# Relative WORKDIR: becomes /srv/api/app
WORKDIR app
# Back to /srv/api for dependency install
WORKDIR $APP_HOME
# Manifest first for cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Source copied with correct owner so the app can read it
COPY --chown=app:app ./app ./app
# Drop privileges AFTER all root-needed steps
USER app
# CMD runs with /srv/api as the working directory
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
Checked with a Dockerfile instruction script; not built locally. Uses `python:3.12-slim` as an example tag.

---

## 🟠 My Stack Integration
Use the same convention across all services so logs, volumes and Compose paths are predictable.

```yaml
# docker-compose.yml -- paths line up with WORKDIR /app in each Dockerfile
services:                                 # services
  api:                                    # FastAPI
    build: ./api                          # Dockerfile has WORKDIR /srv/api
    volumes:                              # mounts relative to WORKDIR layout
      - api-data:/srv/api/data            # persistent data folder (owned by app user)
    working_dir: /srv/api                 # Compose override; same as Dockerfile WORKDIR
  node-api:                               # Node.js API
    build: ./node-api                     # Dockerfile has WORKDIR /app
    volumes:                              # dev-only live reload bind mount
      - ./node-api/src:/app/src:ro        # mount source over image source, read-only
volumes:                                  # named volumes
  api-data:                               # declared volume
```
In GitHub Actions, a `working-directory:` on a step plays the same role for `run:` commands; it does not affect Docker builds.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `RUN cd /app && npm install` then expecting the next `RUN` to be in `/app`.
✅ Correct: `WORKDIR /app`; `cd` only lasts within one RUN.

❌ Mistake 2: Skipping WORKDIR and copying code to `/`.
✅ Correct: Always set a dedicated directory such as `/app`.

❌ Mistake 3: Switching to `USER app` and expecting write access to WORKDIR created earlier as root.
✅ Correct: `chown` the needed folders or use `COPY --chown`.

❌ Mistake 4: Using relative WORKDIR carelessly (`WORKDIR app` twice gives `/app/app`).
✅ Correct: Prefer absolute paths.

---

## 🧠 Tricky Interview Question
You mount a bind volume `./src:/app` in Compose for development and suddenly `node_modules` disappears from the container. Why does this relate to WORKDIR, and how do you fix it?

Answer: The image installed `node_modules` into `/app` (WORKDIR). A bind mount on `/app` hides everything the image had at that path and shows the host folder instead (which has no node_modules). Fix: mount only `./src:/app/src`, or add an anonymous/named volume for `/app/node_modules`, or install dependencies in a separate path (`/deps`) and set `NODE_PATH`.

---

## ⚫ Interview Questions + Answers

Q1: Does WORKDIR create the directory?
A1: Yes, including parents, if missing.

Q2: Can WORKDIR be used multiple times?
A2: Yes; relative paths chain from the previous WORKDIR; the last one is the container's start directory.

Q3: Why not `RUN cd /app`?
A3: Each RUN is a separate shell; the directory change is lost after it ends.

Q4: How can you override at runtime?
A4: `docker run -w /path` or Compose `working_dir:`; Kubernetes `workingDir`.

Q5: Does WORKDIR add a layer?
A5: It adds a metadata change (and creates the folder when needed), but no meaningful size.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every app image: set one stable working directory.
- Making paths in COPY/RUN short and consistent.

❌ Avoid when:
- Mapping a bind mount directly over it without understanding what it hides.
- Using `/` or system folders (`/usr`, `/etc`) as app directory.

---

## 📊 Visual Diagram
```
 FROM node:20-alpine
 WORKDIR /app        --->   cwd = /app
 COPY . .            --->   host ./*  ->  /app/*
 RUN npm ci          --->   runs in /app  -> /app/node_modules
 WORKDIR src         --->   cwd = /app/src
 CMD ["node","x.js"] --->   container starts in /app/src

 RUN cd /app   ... next RUN starts again in the WORKDIR (cd forgotten)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cwd | Current working directory | मौजूदा working directory |
| Absolute path | Starts with / | / से शुरू होने वाला path |
| Relative path | Based on current dir | मौजूदा directory के सापेक्ष |
| Bind mount | Host folder mounted in container | Host folder का mount |
| working_dir | Compose override of WORKDIR | Compose में WORKDIR override |
| Non-root | Unprivileged user | बिना root अधिकार का user |

---

## ⚡ 3-Line Summary
English: WORKDIR sets and creates the directory used by later instructions and by the container at start. Use absolute paths and never rely on `cd`. Fix ownership before switching to a non-root user.
Hindi: WORKDIR आगे की instructions और container के start के लिए directory तय करता और बनाता है। Absolute paths इस्तेमाल करो, `cd` पर भरोसा मत करो। Non-root user पर जाने से पहले ownership ठीक करो।

---

## ➡️ Next Topic
**78. ENV Instruction** — image और container के लिए environment variables सेट करना, और secrets से जुड़ी गलतियाँ।
