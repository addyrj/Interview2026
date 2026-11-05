# 76. COPY vs ADD
# हिंदी में: COPY बनाम ADD (Image में files डालना)

---

## 🔵 Simple Definition (English)
Both copy files from the build context into the image. `COPY` only copies local files and folders (and files from another build stage with `--from`). `ADD` does the same and can also fetch remote URLs and auto-extract local tar archives. Best practice: use `COPY` by default; use `ADD` only for deliberate tar auto-extraction.

## 🔵 सरल परिभाषा (Hindi)
दोनों build context से files को image में copy करते हैं। `COPY` सिर्फ local files/folders copy करता है (और `--from` से दूसरे build stage की files)। `ADD` वही करता है, साथ में remote URL से download और local tar archive का auto-extract भी कर सकता है। Best practice: default में `COPY`; `ADD` सिर्फ जानबूझकर tar extract के लिए।

---

## 🔴 Problem it Solves
An image needs your source code, config and assets. `COPY` gives a predictable, explicit way. `ADD` was created earlier with extra magic, but magic causes surprises: a `.tar.gz` unexpectedly unpacks, a URL download is not cached reliably, has no checksum, and can pull in untrusted content. Understanding the difference avoids insecure and bloated images.

## 🔴 यह क्यों बना? (Hindi)
Image को आपका source code, config और assets चाहिए। `COPY` अनुमानित और साफ़ तरीका देता है। `ADD` पहले बना और उसमें अतिरिक्त "जादू" है, पर जादू से हैरानी होती है: `.tar.gz` अचानक खुल जाती है, URL download का cache भरोसेमंद नहीं, checksum नहीं, और untrusted content आ सकता है। फर्क समझने से insecure और भारी images से बचते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Paths are relative to the BUILD CONTEXT (you cannot COPY ../outside)
Step 2 → .dockerignore removes excluded files from the context first
Step 3 → COPY src dest: file checksums decide cache hit/miss for this layer
Step 4 → ADD extra: local .tar/.tar.gz/.tgz/.xz is auto-extracted into dest
Step 5 → ADD URL: downloaded as-is (not extracted); --checksum=sha256:... can verify (BuildKit)
Step 6 → COPY --chown=user:group and --chmod set ownership/permissions in the same layer
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Paths BUILD CONTEXT के सापेक्ष होते हैं (COPY ../outside नहीं चलता)
Step 2 → पहले .dockerignore context से excluded files हटाता है
Step 3 → COPY src dest: files के checksum से इस layer का cache hit/miss तय होता है
Step 4 → ADD का extra: local .tar/.tar.gz/.tgz/.xz अपने आप dest में extract होती है
Step 5 → ADD URL: जैसा है वैसा download होता है (extract नहीं); --checksum=sha256:... से verify (BuildKit)
Step 6 → COPY --chown=user:group और --chmod से owner/permission उसी layer में सेट होते हैं
```

---

## 🟡 Real World Example
A team wrote `ADD https://example.com/tool.tar.gz /opt/` in a Dockerfile. The upstream file was silently replaced with a malicious build; the next image build included it with no warning, and `ADD` remote downloads are not extracted. After a security review they switched to `RUN curl -fsSLO <url> && echo "<sha256>  tool.tar.gz" | sha256sum -c - && tar -xzf ...` (or `ADD --checksum=sha256:...`) and `COPY` for everything else. In the same repo, a build that used `COPY . .` before `npm ci` was rebuilding dependencies on each code change; fixed by copying `package*.json` first.

## 🟡 Real Example Hindi mein
एक team ने Dockerfile में `ADD https://example.com/tool.tar.gz /opt/` लिखा। upstream की file चुपचाप malicious build से बदल गई; अगली image build में बिना चेतावनी वही आ गई, और `ADD` का remote download extract भी नहीं होता। Security review के बाद उन्होंने `RUN curl -fsSLO <url> && echo "<sha256>  tool.tar.gz" | sha256sum -c - && tar -xzf ...` (या `ADD --checksum=sha256:...`) अपनाया और बाकी सब के लिए `COPY`। उसी repo में `npm ci` से पहले `COPY . .` होने से हर code बदलाव पर dependencies दोबारा बन रही थीं; पहले `package*.json` copy करके ठीक किया।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Dockerfile -- COPY basics (example versions)
FROM node:20-alpine
# All later relative paths are inside /app
WORKDIR /app
# Copy manifests first so the dependency layer stays cached
COPY package.json package-lock.json ./
# Install exact locked production dependencies
RUN npm ci --omit=dev
# Copy the rest of the source (filtered by .dockerignore)
COPY . .
# Start the server
CMD ["node", "server.js"]
```

## 💻 Code / Config Example — Advanced
```dockerfile
# syntax=docker/dockerfile:1.7
# Dockerfile -- multi-stage COPY --from, ownership, ADD for tar extraction and checksum download
FROM node:20-alpine AS build
WORKDIR /app
# Manifests first for cache efficiency
COPY package*.json ./
RUN npm ci
# Source after deps
COPY . .
# Produce /app/dist
RUN npm run build

FROM nginx:1.27-alpine AS runtime
# ADD auto-extracts a LOCAL tar into the destination (intended use of ADD); file must be in build context
ADD assets.tar.gz /usr/share/nginx/html/assets/
# ADD remote file with integrity check (BuildKit feature, version-dependent); replace URL and hash
ADD --checksum=sha256:0000000000000000000000000000000000000000000000000000000000000000 https://example.com/robots.txt /usr/share/nginx/html/robots.txt
# COPY from another stage: only the built static files, no node_modules or source
COPY --from=build /app/dist /usr/share/nginx/html
# Own config copied with explicit owner and permissions
COPY --chown=root:root --chmod=0644 nginx.conf /etc/nginx/conf.d/default.conf
# Document HTTP port
EXPOSE 80
```
The checksum value above is a placeholder (all zeros): the build fails until you put the real hash. `ADD --checksum` needs recent BuildKit (Dockerfile syntax 1.6+). The Dockerfile was only syntax-checked by script, not built; `assets.tar.gz` must exist in your context.

---

## 🟠 My Stack Integration
For React: build in a Node stage, `COPY --from=build` into nginx. For FastAPI: copy `requirements.txt` first. Keep secrets out with `.dockerignore`.

```text
# .dockerignore -- keep the context small and safe (applies to Node, React and FastAPI folders)
.git
node_modules
__pycache__
*.pyc
.env
.env.*
dist
coverage
*.log
Dockerfile
docker-compose*.yml
```
```yaml
# .github/workflows/build.yml -- context is the repo folder, so ignore rules directly affect CI cache hits
name: build
on: [push]
jobs:
  web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t web:ci ./web
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `ADD . /app` everywhere out of habit.
✅ Correct: `COPY` unless you specifically need tar extraction.

❌ Mistake 2: `COPY . .` with no `.dockerignore`, leaking `.env`, `.git`, SSH keys into the image.
✅ Correct: Create `.dockerignore`; scan the final image.

❌ Mistake 3: `COPY ../shared /app/shared` fails ("outside build context").
✅ Correct: Set the build context at the parent (`docker build -f svc/Dockerfile .`) or use Compose `additional_contexts`.

❌ Mistake 4: Copying a directory and expecting only contents: `COPY src /app` copies the contents of `src`, not the folder itself.
✅ Correct: `COPY src /app/src` when you want the folder name preserved.

---

## 🧠 Tricky Interview Question
You `ADD app.tar.gz /app/` and later the image has no `app.tar.gz` file but a folder of contents. A teammate wants the tarball itself kept. What do you do?

Answer: `ADD` auto-extracts recognised local archives. Use `COPY app.tar.gz /app/` to keep the archive as a file. Note: archives fetched from a URL are not extracted by ADD, so the behaviour differs between local and remote sources, another reason to avoid ADD.

---

## ⚫ Interview Questions + Answers

Q1: Why does Docker recommend COPY over ADD?
A1: COPY is explicit and predictable; ADD adds implicit behaviour (extraction, URL fetch) that is surprising and less secure.

Q2: How does COPY affect layer cache?
A2: Docker hashes the copied files' contents/metadata; any change invalidates that layer and all later ones.

Q3: Can COPY read files outside the context?
A3: No. Only inside the context (and other stages/images via `--from`).

Q4: What does `COPY --from` accept?
A4: A previous stage name/index or an external image (`COPY --from=nginx:1.27 /etc/nginx/nginx.conf /tmp/`).

Q5: What do `--chown` and `--chmod` solve?
A5: They set file owner and mode in the same layer; a later `RUN chown -R` would duplicate all files into a new layer and bloat the image.

---

## 🔷 When to Use + When Not to Use
✅ Use COPY when:
- Adding source, configs, built artifacts, files from other stages.

✅ Use ADD when:
- You have a local tarball that must be unpacked into the image.
- Verified remote files with `--checksum` (and you accept BuildKit dependency).

❌ Avoid ADD when:
- Fetching remote URLs without checksums.
- Anything COPY can do.

---

## 📊 Visual Diagram
```
 Build context (./)                         Image filesystem
 +-----------------+   COPY . .             +-------------+
 | package.json    | ---------------------> | /app/...    |
 | src/            |                        |             |
 | assets.tar.gz   |   ADD assets.tar.gz /x | /x/<files>  |  <- extracted
 | .env  (ignored) |                        |             |
 +-----------------+                        +-------------+
 Other stage (build) --COPY --from=build--> final runtime stage
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Build context | Files visible to build | Build को दिखने वाली files |
| .dockerignore | Exclude patterns | बाहर रखने के patterns |
| Auto-extract | ADD unpacks tar | ADD द्वारा tar खोलना |
| --from | Copy from another stage | दूसरे stage से copy |
| --chown | Set owner on copy | Copy पर owner सेट |
| Checksum | Hash to verify download | Download जाँचने का hash |

---

## ⚡ 3-Line Summary
English: COPY copies local files predictably; ADD also fetches URLs and extracts tarballs. Prefer COPY, add a `.dockerignore`, and copy dependency manifests before source. Verify any remote download with a checksum.
Hindi: COPY local files अनुमानित तरीके से copy करता है; ADD URL भी लाता है और tar खोलता है। COPY को प्राथमिकता दो, `.dockerignore` बनाओ, और source से पहले dependency manifests copy करो। Remote download को checksum से verify करो।

---

## ➡️ Next Topic
**77. WORKDIR Instruction** — COPY और RUN के paths किस directory के सापेक्ष चलते हैं, यह WORKDIR तय करता है।
