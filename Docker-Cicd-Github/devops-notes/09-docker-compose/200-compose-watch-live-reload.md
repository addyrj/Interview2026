# 200. Compose Watch (live reload)
# हिंदी में: Compose Watch (live reload)

---

## 🔵 Simple Definition (English)
**Compose Watch** is a feature of Docker Compose V2 (`develop.watch` in the file, run with `docker compose watch` or `up --watch`) that monitors files on your host and automatically **syncs** them into a running container, **rebuilds** the image, or **restarts** the service when they change. It gives you live reload without bind-mount tricks.

## 🔵 सरल परिभाषा (Hindi)
**Compose Watch** Docker Compose V2 का feature है (file में `develop.watch`, चलाने के लिए `docker compose watch` या `up --watch`) जो host की files पर नज़र रखता है और बदलाव होने पर running container में files अपने आप **sync** करता है, image **rebuild** करता है या service **restart** करता है। यह bind-mount की जुगाड़ के बिना live reload देता है।

---

## 🔴 Problem it Solves
Developers used to rebuild the image after every code change (slow) or bind-mount the whole project folder (fast but problematic: `node_modules` from the host clobbers the container's, file permission issues, slow file events on macOS/Windows). Compose Watch lets you sync only source folders, ignore `node_modules`, and rebuild only when `package.json` changes.

## 🔴 यह क्यों बना? (Hindi)
Developers हर code बदलाव पर image rebuild करते थे (धीमा) या पूरा project folder bind-mount करते थे (तेज़ पर दिक्कतें: host का `node_modules` container के वाले को खराब कर देता है, file permission की समस्या, macOS/Windows पर slow file events)। Compose Watch सिर्फ source folders sync करने देता है, `node_modules` ignore करता है, और सिर्फ `package.json` बदलने पर rebuild करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add `develop: watch:` rules under a service (path, action, target, ignore)
Step 2 → Run `docker compose up --watch` (or `docker compose watch` after `up -d`)
Step 3 → Compose watches each `path` on the host for file events
Step 4 → action: sync          -> copy changed file into container `target`
         action: rebuild       -> rebuild image + recreate container
         action: sync+restart  -> copy file, then restart the container
Step 5 → Your dev server (nodemon / vite / uvicorn --reload) sees the new file and reloads
Step 6 → Ctrl+C stops watching (containers keep running if started with -d)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Service के नीचे `develop: watch:` rules जोड़ें (path, action, target, ignore)
Step 2 → `docker compose up --watch` चलाएँ (या `up -d` के बाद `docker compose watch`)
Step 3 → Compose हर `path` पर host पर file events देखता है
Step 4 → action: sync          -> बदली file container के `target` में copy
         action: rebuild       -> image rebuild + container recreate
         action: sync+restart  -> file copy, फिर container restart
Step 5 → आपका dev server (nodemon / vite / uvicorn --reload) नई file देखकर reload करता है
Step 6 → Ctrl+C से watching बंद (-d से शुरू किए containers चलते रहते हैं)
```

---

## 🟡 Real World Example
A frontend/backend team at a **Zomato**-like startup onboards a new dev with one command: `docker compose up --watch`. React edits sync instantly into the Vite container; the Node API reloads through nodemon; adding a package in `package.json` triggers an automatic image rebuild so the new dependency is installed. No "works on my machine", no manual `npm install` inside containers.

## 🟡 Real Example Hindi mein
**Zomato** जैसे startup की frontend/backend team नए developer को एक command से शुरू कराती है: `docker compose up --watch`। React के edits Vite container में तुरंत sync होते हैं; Node API nodemon से reload होती है; `package.json` में नया package जोड़ने पर image अपने आप rebuild होकर dependency install हो जाती है। न "मेरी machine पर चलता है", न container में manual `npm install`।

---

## 💻 Code / Config Example — Basic

```yaml
# docker-compose.yml  (requires Compose V2.22 or newer for watch; check `docker compose version`)
services:
  api:
    build: .                          # image built from ./Dockerfile
    command: ["npx", "nodemon", "server.js"]   # dev server that reloads on file change
    ports:
      - "3000:3000"                   # host:container
    develop:                          # Compose Watch configuration
      watch:
        - action: sync                # copy changed files into the running container
          path: ./src                 # host folder to watch
          target: /app/src            # destination inside the container
        - action: rebuild             # rebuild image when dependencies change
          path: package.json          # host file to watch
```

```bash
docker compose up --watch             # start AND watch (foreground)
# or
docker compose up -d && docker compose watch   # start detached, then watch
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml : React (Vite) + Node API + FastAPI with different watch rules
services:
  web:
    build:
      context: ./web                          # React app folder
      target: dev                             # dev stage of a multi-stage Dockerfile
    ports:
      - "5173:5173"                           # Vite dev server
    command: ["npm", "run", "dev", "--", "--host"]   # --host lets the port be reached from outside the container
    develop:
      watch:
        - action: sync                        # hot-module reload: copy source only
          path: ./web/src
          target: /app/src
          ignore:
            - "**/*.test.tsx"                 # tests need not reach the container
        - action: sync
          path: ./web/public
          target: /app/public
        - action: rebuild                     # dependency change => reinstall via rebuild
          path: ./web/package.json
        - action: rebuild
          path: ./web/package-lock.json
  api:
    build: ./api                              # Node.js API
    command: ["npx", "nodemon", "--legacy-watch", "server.js"]   # polling fallback if events are missed
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: development
    develop:
      watch:
        - action: sync                        # nodemon restarts the process itself
          path: ./api/src
          target: /app/src
          ignore:
            - node_modules/                   # NEVER sync host node_modules into the container
        - action: rebuild
          path: ./api/package.json
  fastapi:
    build: ./fastapi
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]   # uvicorn reloads on change
    ports:
      - "8000:8000"
    develop:
      watch:
        - action: sync                        # copy python source
          path: ./fastapi/app
          target: /code/app
          ignore:
            - "__pycache__/"
        - action: sync+restart                # for config files read only at startup
          path: ./fastapi/config.yaml
          target: /code/config.yaml
        - action: rebuild                     # new pip packages
          path: ./fastapi/requirements.txt
```
`sync+restart` and some options need a recent Compose V2 release (check release notes). This file was YAML-parsed only; builds and watch were not run locally.

---

## 🟠 My Stack Integration
- **Node.js**: use `nodemon` (or `node --watch`) inside the container plus `sync`; rebuild on `package.json`.
- **FastAPI**: `uvicorn --reload` plus `sync` of `app/`; rebuild on `requirements.txt`.
- **React**: Vite dev server with `--host` plus `sync` of `src/`; this is DEV only. Production builds static files served by Nginx.
- **VPS / AWS**: never run `--watch` there. Production images are built in CI (GitHub Actions) and run without file syncing.

```yaml
# Keep dev-only watch rules out of production using an override file (see 202)
# docker-compose.override.yml  (auto-loaded on a dev laptop)
services:
  api:
    develop:
      watch:
        - action: sync
          path: ./api/src
          target: /app/src
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Watching `./` with no `ignore`, causing `node_modules` and `.git` to sync.
✅ Correct: Watch specific folders; add `ignore` for `node_modules/`, `.git/`, build output.

❌ Mistake 2: The service's process cannot reload (e.g. plain `node server.js`), so synced files change but the app does not.
✅ Correct: Use nodemon / `--watch` / uvicorn `--reload`, or `sync+restart`.

❌ Mistake 3: Expecting `sync` to work for files that are not under the Dockerfile's `WORKDIR` or when the container user cannot write.
✅ Correct: Make sure `target` exists and is writable by the container user.

❌ Mistake 4: Mixing bind mounts and watch for the same folder.
✅ Correct: Pick one mechanism per path.

❌ Mistake 5: Running on an old Compose version where `develop` is unknown.
✅ Correct: Upgrade Compose V2 (watch arrived around v2.22).

---

## 🧠 Tricky Interview Question
You use `action: sync` on `package.json`, add a dependency, and the app crashes with "module not found". Why?

Answer: `sync` only copies the file; it does not run `npm install` and cannot create `node_modules` in the image. Dependency changes require `action: rebuild` (new image with `RUN npm ci`). `sync` is for source code that the running dev server can reload.

---

## ⚫ Interview Questions + Answers

Q1: How is Compose Watch different from a bind mount?
A1: A bind mount shares the host folder live (and exposes host files/permissions); watch copies selected changes into the container and can rebuild or restart, keeping image `node_modules` intact.

Q2: What are the three actions?
A2: `sync`, `rebuild`, `sync+restart` (the `sync+exec` action also exists in newer versions; verify for your release).

Q3: How do you start watching?
A3: `docker compose up --watch` or `docker compose watch`.

Q4: Is it for production?
A4: No. Dev only. Production uses immutable images built in CI.

Q5: How to exclude files?
A5: `ignore:` list under a rule, plus `.dockerignore` for rebuilds. (A `.dockerignore` also matters because rebuild uses the build context.)

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Local development in containers on macOS/Windows where bind mounts are slow.
- You want automatic reinstall on dependency changes.

❌ Avoid when:
- Production, staging, CI (use immutable builds).
- Tiny apps where a plain bind mount is simpler.

---

## 📊 Visual Diagram
```
 Host (your laptop)                     Container
 +-----------------+  edit src/app.js  +-------------------+
 | VS Code         | ----------------> | /app/src/app.js   |  action: sync
 +-----------------+       watch       |  nodemon reloads  |
 | package.json    | ----------------> | image rebuilt     |  action: rebuild
 +-----------------+                   | container replaced|
                                       +-------------------+
 docker compose up --watch  (Ctrl+C stops watching)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| develop.watch | Compose block with watch rules | watch rules का block |
| sync | Copy changed files into container | बदली files container में copy |
| rebuild | Rebuild image and recreate container | image rebuild + container recreate |
| sync+restart | Copy then restart container | copy के बाद restart |
| hot reload | App reloads code without manual restart | बिना manual restart code reload |

---

## ⚡ 3-Line Summary
English: Compose Watch syncs, rebuilds or restarts containers when host files change.
Use `sync` for source code and `rebuild` for dependency files.
It is a dev-only feature of Compose V2.
Hindi: Compose Watch host files बदलने पर containers को sync, rebuild या restart करता है।
Source code के लिए `sync` और dependency files के लिए `rebuild` इस्तेमाल करें।
यह Compose V2 का सिर्फ dev feature है।

---

## ➡️ Next Topic
**201. Multiple Compose Files**: combine a base file with extra files using `-f`, the basis of dev/prod differences.
