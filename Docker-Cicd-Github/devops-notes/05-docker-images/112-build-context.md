# 112. Build Context
# हिंदी में: Build Context

---

## 🔵 Simple Definition (English)
The **build context** is the set of files (the PATH you pass to `docker build`) that the builder can access with `COPY` and `ADD`. Everything in it is sent to the builder first, so a huge context makes builds slow. `.dockerignore` filters it.

## 🔵 सरल परिभाषा (Hindi)
**Build context** उन files का समूह है (जो PATH आप `docker build` को देते हैं) जिन्हें builder `COPY` और `ADD` से access कर सकता है। पहले यह सब builder को भेजा जाता है, इसलिए बड़ा context build को धीमा करता है। `.dockerignore` इसे filter करता है।

---

## 🔴 Problem it Solves
- `node_modules` (500 MB), `.git` (history), logs and `.env` get uploaded to the builder on every build.
- Secrets such as `.env` or AWS keys can be copied into an image by `COPY . .`.
- Any change to an irrelevant file (README) can bust the cache for `COPY . .`.

## 🔴 यह क्यों बना? (Hindi)
- `node_modules` (500 MB), `.git` (history), logs और `.env` हर build पर builder को upload होते हैं।
- `COPY . .` से `.env` या AWS keys जैसे secrets image में चले जा सकते हैं।
- किसी बेमतलब file (README) में बदलाव से `COPY . .` का cache टूट सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run: docker build .   (context = current directory)
Step 2 → Docker reads .dockerignore in the context root
Step 3 → Remaining files are sent to the builder (BuildKit sends only what is needed)
Step 4 → COPY/ADD paths are resolved relative to the context root
Step 5 → Files outside the context (../secret) cannot be copied
Step 6 → Cache key of COPY depends on the file contents it copies
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप चलाते हैं: docker build .   (context = मौजूदा directory)
Step 2 → Docker context root में .dockerignore पढ़ता है
Step 3 → बाकी files builder को भेजी जाती हैं (BuildKit सिर्फ ज़रूरी हिस्सा भेजता है)
Step 4 → COPY/ADD के paths context root के सापेक्ष होते हैं
Step 5 → Context के बाहर की files (../secret) copy नहीं हो सकतीं
Step 6 → COPY का cache key उन files की content पर निर्भर है
```

---

## 🟡 Real World Example
A monorepo has `api/`, `web/` and a 2 GB `data/` folder. Running `docker build -f api/Dockerfile .` from the root uploaded 2 GB each time and took a minute before step 1. The team moved to context `./api` plus a `.dockerignore`, and the transfer dropped to 3 MB. Later a dev's `.env` with a database password almost shipped in an image; `.dockerignore` with `.env*` fixed it.

## 🟡 Real Example Hindi mein
एक monorepo में `api/`, `web/` और 2 GB का `data/` folder है। Root से `docker build -f api/Dockerfile .` हर बार 2 GB upload करता और step 1 से पहले एक मिनट लगता। Team ने context `./api` और `.dockerignore` पर किया, तो transfer 3 MB रह गया। बाद में एक dev की `.env` (database password) image में लगभग चली गई थी; `.dockerignore` में `.env*` से हल हुआ।

---

## 💻 Code / Config Example — Basic
```bash
# Context is the current directory; show how big it is first
du -sh .
# Build using only the api folder as context
docker build -t myorg/api:dev ./api
```

```dockerignore
# .dockerignore - one pattern per line, relative to the context root
# Dependencies are reinstalled inside the image
node_modules
# Git history is large and not needed
.git
# Never ship secrets
.env
.env.*
# Logs and local artifacts
*.log
dist
coverage
# Docker files themselves are not needed inside the image
Dockerfile*
docker-compose*.yml
# Editor and OS files
.vscode
.DS_Store
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - monorepo with different contexts and a shared folder
services:
  api:
    build:
      # Root context so the Dockerfile can COPY ./shared
      context: .
      # Dockerfile lives in the api folder
      dockerfile: api/Dockerfile
    image: myorg/api:${TAG:-dev}
  web:
    build:
      # Narrow context: only the web folder is uploaded
      context: ./web
      dockerfile: Dockerfile
      # Extra named context (BuildKit) usable with COPY --from=shared-lib
      additional_contexts:
        shared-lib: ./shared
    image: myorg/web:${TAG:-dev}
```
(`additional_contexts` requires a recent Compose v2 with BuildKit; version dependent, not run locally.)

```bash
# Build from a Git URL context (the repo is cloned by the builder)
docker build -t myorg/api:git "https://github.com/myorg/myrepo.git#main:api"
# Build from stdin with NO context (COPY is not available, only RUN etc.)
docker build -t tiny - <<'EOF'
FROM alpine:3.20
RUN echo hello > /hello.txt
EOF
```

---

## 🟠 My Stack Integration
For a Node + FastAPI + React repo: one `.dockerignore` per service folder, each service built with its own context. Per-service ignore files protect `.env` and `node_modules`/`.venv`.

```dockerignore
# api/.dockerignore (FastAPI service)
# Python virtual environments and caches
.venv
__pycache__
*.pyc
.pytest_cache
# Secrets and git
.env*
.git
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No `.dockerignore`.
✅ Correct: Always add one; start with `.git`, `node_modules`, `.env*`.

❌ Mistake 2: Using the repo root as context for every service.
✅ Correct: Use the narrowest context that works.

❌ Mistake 3: `COPY ../shared .` in a Dockerfile.
✅ Correct: Parent paths are outside the context and fail; widen the context or use `additional_contexts`.

❌ Mistake 4: Ignoring `package-lock.json` by mistake.
✅ Correct: Keep lockfiles in the context; `npm ci` needs them.

---

## 🧠 Tricky Interview Question
"Your `.dockerignore` lists `Dockerfile`. Will the build fail since the Dockerfile is excluded?"

Answer: No. The builder still reads the Dockerfile; `.dockerignore` only hides it from `COPY`/`ADD`. That is why ignoring `Dockerfile*` is safe and keeps it out of the image.

---

## ⚫ Interview Questions + Answers

Q1: What is the build context?
A1: The directory (or URL/tar) whose files are available to the build.

Q2: Why is a big context bad?
A2: Slower uploads, cache churn, and higher risk of leaking secrets.

Q3: Does `.dockerignore` use the same syntax as `.gitignore`?
A3: Similar (globs, `!` exceptions) but patterns are relative to the context root and follow Go filepath rules, with `**` support.

Q4: Can you COPY a file outside the context?
A4: No. Use a bigger context or extra named contexts.

Q5: How does BuildKit help?
A5: It transfers only the files actually referenced, rather than the whole tar like the legacy builder.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every project: `.dockerignore` is mandatory hygiene.

❌ Avoid when:
- Using the whole monorepo as context when one service needs only its folder.
- Putting `.dockerignore` rules that exclude files the Dockerfile needs (then `COPY` fails).

---

## 📊 Visual Diagram
```
 repo/
 ├─ api/        ◄── context for api   (docker build ./api)
 │   ├─ Dockerfile
 │   ├─ .dockerignore
 │   └─ src/
 ├─ web/        ◄── context for web
 ├─ data/ (2GB) ◄── never sent (outside both contexts)
 └─ .env        ◄── never sent

 [context files minus .dockerignore] ──► builder ──► COPY / ADD
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Build context | Files sent to builder | builder को भेजी files |
| .dockerignore | Exclude list | बाहर रखने की list |
| COPY | Copy from context | context से copy |
| Named context | Extra context source | अतिरिक्त context |
| Monorepo | Many services, one repo | एक repo में कई services |
| Cache bust | Cache invalidated | cache टूटना |

---

## ⚡ 3-Line Summary
English: The context is every file the build can see.
Keep it small and always use `.dockerignore`.
Never let `.env` or `.git` enter the context.
Hindi: Context वे सब files हैं जो build देख सकता है।
इसे छोटा रखो और हमेशा `.dockerignore` इस्तेमाल करो।
`.env` या `.git` को context में मत आने दो।

---

## ➡️ Next Topic
**113. Build Arguments** - pass values into the build safely (and learn what must never be passed).
