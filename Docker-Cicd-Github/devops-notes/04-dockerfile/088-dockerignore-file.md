# 088. .dockerignore File
# हिंदी में: .dockerignore फ़ाइल

---

## 🔵 Simple Definition (English)
`.dockerignore` is a file in the build context root that lists files and folders Docker must **exclude** from the build context sent to the builder. It works like `.gitignore`, but for `docker build`, `COPY` and `ADD`.

## 🔵 सरल परिभाषा (Hindi)
`.dockerignore` build context की root में रखी file है जो उन files और folders की सूची देती है जिन्हें Docker को builder को भेजे जाने वाले build context से **बाहर** रखना है। यह `.gitignore` की तरह है, पर `docker build`, `COPY` और `ADD` के लिए।

---

## 🔴 Problem it Solves
`docker build .` sends the whole folder (the build context) to the builder first. If it includes `node_modules` (500 MB), `.git` (history), `.env` (secrets) and `venv/`, then: (1) the build starts slowly, (2) `COPY . .` copies junk and host-compiled binaries (macOS `node_modules` break on Linux), (3) cache is invalidated by irrelevant changes (a README edit), and (4) **secrets like `.env` or `.aws/credentials` end up inside the image layers**, where anyone who pulls the image can read them.

## 🔴 यह क्यों बना? (Hindi)
`docker build .` पहले पूरा folder (build context) builder को भेजता है। अगर उसमें `node_modules` (500 MB), `.git` (history), `.env` (secrets) और `venv/` हैं तो: (1) build धीरे शुरू होता है, (2) `COPY . .` कचरा और host पर बने binaries copy करता है (macOS के `node_modules` Linux पर टूटते हैं), (3) बेकार बदलाव (README edit) से cache invalid होता है, और (4) **`.env` या `.aws/credentials` जैसे secrets image layers में चले जाते हैं**, जिसे image pull करने वाला कोई भी पढ़ सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run: docker build -t app .   (the "." is the build context)
Step 2 → Docker reads .dockerignore from the context root
Step 3 → Matching paths are removed from the context BEFORE it is sent
Step 4 → COPY/ADD cannot see excluded files (they do not exist for the build)
Step 5 → Smaller context = faster build + more stable cache + no leaked secrets
Step 6 → Patterns: *.log, **/node_modules, !keep.me (re-include), # comments
```

Pattern rules: matching is relative to the context root; `*` matches within one folder, `**` matches across folders; `!` re-includes; the **last matching line wins**; a pattern like `node_modules` only matches at the root, so use `**/node_modules` for nested ones.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → आप चलाते हो: docker build -t app .   ("." ही build context है)
Step 2 → Docker context root से .dockerignore पढ़ता है
Step 3 → मेल खाने वाले paths context भेजने से पहले हटा दिए जाते हैं
Step 4 → COPY/ADD बाहर रखी files नहीं देख सकते (build के लिए वे हैं ही नहीं)
Step 5 → छोटा context = तेज़ build + स्थिर cache + secrets leak नहीं
Step 6 → Patterns: *.log, **/node_modules, !keep.me (वापस शामिल), # comments
```

Pattern नियम: matching context root के सापेक्ष होती है; `*` एक folder में मेल खाता है, `**` कई folders में; `!` वापस शामिल करता है; **आखिरी मेल खाती line जीतती है**; `node_modules` जैसा pattern सिर्फ root पर मेल खाता है, nested के लिए `**/node_modules` लिखो।

---

## 🟡 Real World Example
A developer's Node.js repo has `node_modules` (400 MB), `.git` (200 MB), and `.env` with Stripe keys. Without `.dockerignore`, `docker build` says "Sending build context to Docker daemon 620MB" and takes 40 seconds just to start; `COPY . .` copies `.env` into the image, which is then pushed to a public Docker Hub repo by mistake. Bots scan public images for keys and the Stripe key is abused within hours. With a proper `.dockerignore`, the context drops to 2 MB and `.env` never enters the image.

## 🟡 Real Example Hindi mein
एक developer के Node.js repo में `node_modules` (400 MB), `.git` (200 MB) और Stripe keys वाली `.env` है। `.dockerignore` के बिना `docker build` "Sending build context ... 620MB" कहता है और शुरू होने में ही 40 सेकंड लगते हैं; `COPY . .` `.env` को image में डाल देता है, जिसे गलती से public Docker Hub repo में push कर दिया जाता है। Bots public images में keys खोजते हैं और कुछ ही घंटों में Stripe key का दुरुपयोग होता है। सही `.dockerignore` से context 2 MB हो जाता है और `.env` कभी image में नहीं जाती।

---

## 💻 Code / Config Example — Basic

```gitignore
# .dockerignore (Node.js project): place next to the Dockerfile
# Dependencies are installed inside the image by npm ci
node_modules
# Version control history is not needed in the image
.git
# Git ignore file is not needed
.gitignore
# Local secrets must NEVER enter the image
.env
.env.*
# Logs
*.log
npm-debug.log*
# Build output (rebuilt inside the image)
dist
# Docker files themselves are not needed inside the image
Dockerfile
docker-compose*.yml
.dockerignore
# Editor and OS files
.vscode
.idea
.DS_Store
```

```bash
# Build and compare context size in the output
docker build -t demo .
# Check what ended up in the image (should NOT list .env or node_modules from host)
docker run --rm demo ls -la /app
```

## 💻 Code / Config Example — Advanced

```gitignore
# .dockerignore (monorepo: React frontend + FastAPI backend + Node API)
# Strategy: ignore everything, then allow-list what each build needs (safest against leaks)
# 1) Exclude everything by default
*
# 2) Re-include only what the build requires (last matching line wins)
!package.json
!package-lock.json
!src/
!public/
!app/
!requirements.txt
# 3) Even inside allowed folders, exclude junk (these come AFTER the allow rules)
**/node_modules
**/__pycache__
**/*.pyc
**/.pytest_cache
**/.venv
**/venv
**/*.log
**/.env
**/.env.*
# 4) Keep env templates out too; keys must come from runtime secrets
**/*.pem
**/*.key
**/.aws
**/.ssh
# 5) Tests and docs are not needed in production images
**/tests
**/*.md
!README.md
```

```dockerfile
# Dockerfile using the allow-list above (FastAPI example)
# Python slim base (example tag)
FROM python:3.12-slim
# Working directory
WORKDIR /app
# requirements.txt is allowed by .dockerignore, so this COPY works
COPY requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# app/ is allowed; __pycache__, tests and .env inside it are excluded
COPY app ./app
# Non-root user
USER 10001
# Start API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# BuildKit also supports per-Dockerfile ignore files: Dockerfile.dockerignore
# Example: Dockerfile.api uses Dockerfile.api.dockerignore automatically (BuildKit)
docker build -f Dockerfile.api -t api .
```

```yaml
# .github/workflows/ci.yml fragment: fail the build if secrets would enter the image
- name: Guard against secrets in image
  # Build, then scan the filesystem for .env files
  run: |
    # Build the image locally in the runner
    docker build -t ci-image .
    # Fail if any .env file exists inside the image
    docker run --rm --entrypoint sh ci-image -c 'find / -name ".env*" -not -path "/proc/*" 2>/dev/null | grep . && exit 1 || exit 0'
```

---

## 🟠 My Stack Integration
- **Node.js**: ignore `node_modules` (installed in image), `.env`, `dist` (if built in image), `.git`.
- **FastAPI**: ignore `venv`, `__pycache__`, `.pytest_cache`, `.env`, `*.pyc`.
- **React**: ignore `node_modules`, `build`/`dist`, `.env.local` (keep `VITE_*` public values in build args).
- **Nginx**: ignore everything except `nginx.conf` and `conf.d/` in the nginx image's context.
- **GitHub Actions**: `docker/build-push-action` honours `.dockerignore` for the path context (it does for the default Git/path contexts; verify if you use a Git URL context).
- **VPS**: faster builds on small servers (less CPU/disk I/O), and you avoid uploading context for no reason when using remote Docker hosts.
- **Security**: also add `*.pem`, `*.key`, `.aws`, `.ssh`, `terraform.tfstate*`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Having `.gitignore` but no `.dockerignore` and assuming Docker reads `.gitignore`.
✅ Correct: Docker does not read `.gitignore`. Create `.dockerignore`.

❌ Mistake 2: `.dockerignore` listing `Dockerfile` and then wondering about odd errors with old builders.
✅ Correct: Ignoring Dockerfile is allowed (it is still sent to the builder, but not available to COPY). Be sure you know why you do it.

❌ Mistake 3: Writing `node_modules` and expecting nested `packages/*/node_modules` to be excluded.
✅ Correct: Use `**/node_modules`.

❌ Mistake 4: Ignoring a file that a `COPY` needs, e.g., `*.md` while the Dockerfile copies `README.md`; the build fails with "not found".
✅ Correct: Re-include with `!README.md` placed AFTER the ignore pattern.

❌ Mistake 5: Believing `.dockerignore` protects `docker cp` or bind mounts.
✅ Correct: It only affects the build context. Runtime mounts are unaffected.

---

## 🧠 Tricky Interview Question
Your `.dockerignore` contains `.env` and you still see `.env` values inside the running container. How is that possible?

Answer: `.dockerignore` only filters the build context. The values can still arrive through other paths: `docker run --env-file .env` or Compose `env_file:`/`environment:` (runtime injection, which is intended); a bind mount `./:/app` that exposes the host folder; `ARG`/`ENV` instructions that copy the values; or a nested file like `config/.env` that a root-only pattern `.env` does not match (needs `**/.env`). Check each of these with `docker inspect` and `docker history`.

---

## ⚫ Interview Questions + Answers

Q1: What does .dockerignore do?
A1: Removes matching files from the build context before it is sent to the builder, so COPY/ADD cannot use them.

Q2: Does `.dockerignore` use .gitignore syntax?
A2: Similar but not identical: Go filepath matching with `**` and `!` exceptions; the last matching rule wins. Docker does not read `.gitignore`.

Q3: Why exclude `node_modules` if the Dockerfile runs `npm ci`?
A3: Otherwise `COPY . .` overwrites the clean install with host modules (maybe built for a different OS) and slows the build.

Q4: How does it help caching?
A4: Irrelevant file changes (logs, README) no longer change the `COPY . .` layer checksum, so later layers stay cached.

Q5: Can you have more than one?
A5: With BuildKit, `<Dockerfile-name>.dockerignore` next to a specific Dockerfile takes precedence over the root `.dockerignore`, useful in monorepos.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always. Every project that has a Dockerfile.
- Monorepos with several Dockerfiles (per-Dockerfile ignore files).

❌ Avoid when:
- (Rare) You deliberately need `.git` inside the build (e.g., version stamping with `git describe`); pass the info as a build arg instead.

---

## 📊 Visual Diagram

```
 project/
  |-- node_modules/  (400MB) --X  excluded
  |-- .git/          (200MB) --X  excluded
  |-- .env           (secret)--X  excluded  <- never reaches the image
  |-- src/                    -->  sent
  |-- package*.json           -->  sent
  |-- Dockerfile              -->  sent to builder
  |-- .dockerignore  (rules)
         |
         v
  docker build .  -> context 2MB (not 600MB) -> fast, safe, cache-stable
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Build context | Files sent to the builder | builder को भेजी गई files |
| .dockerignore | Exclude list for the context | context से बाहर रखने की सूची |
| `**` | Match any folder depth | किसी भी गहराई के folders |
| `!` | Re-include exception | अपवाद (वापस शामिल) |
| Allow-list | Ignore all, include few | सब बाहर, कुछ ही अंदर |
| Secret leak | Credentials in image layers | image में credentials का चला जाना |

---

## ⚡ 3-Line Summary
English: `.dockerignore` removes files from the build context before the build starts. It speeds builds, stabilises cache and keeps secrets out of images. Prefer an allow-list and use `**/` for nested paths.
Hindi: `.dockerignore` build शुरू होने से पहले files को context से हटाती है। इससे build तेज़ होता है, cache स्थिर रहता है और secrets image से बाहर रहते हैं। Allow-list बेहतर है और nested paths के लिए `**/` use करो।

---

## ➡️ Next Topic
**089. Dockerfile Best Practices**: with every instruction covered, we combine them into a production checklist.
