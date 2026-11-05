# 115. BuildKit Cache
# हिंदी में: BuildKit Cache

---

## 🔵 Simple Definition (English)
BuildKit has two kinds of caching: **layer cache** (reuse a whole step if its instruction and inputs are unchanged) and **cache mounts** (`RUN --mount=type=cache`) which give a persistent directory (like `~/.npm` or pip's cache) to a step, even when that step must re-run. Cache mounts are not part of the final image.

## 🔵 सरल परिभाषा (Hindi)
BuildKit में दो तरह की caching है: **layer cache** (instruction और inputs न बदले हों तो पूरा step दोबारा इस्तेमाल) और **cache mounts** (`RUN --mount=type=cache`) जो step को एक persistent directory देते हैं (जैसे `~/.npm` या pip का cache), भले ही step दोबारा चलाना पड़े। Cache mounts final image का हिस्सा नहीं होते।

---

## 🔴 Problem it Solves
- Changing one dependency in `package.json` invalidates `npm ci` and re-downloads all 800 packages.
- `apt-get install` re-downloads the same .deb files each time.
- Slow CI minutes cost money and delay deploys.

## 🔴 यह क्यों बना? (Hindi)
- `package.json` में एक dependency बदलने पर `npm ci` invalid होता है और सारे 800 packages दोबारा download होते हैं।
- `apt-get install` हर बार वही .deb files फिर से download करता है।
- धीमे CI minutes पैसे खर्च करते हैं और deploy देर से होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → For each instruction BuildKit computes a cache key (instruction + parent + input file hashes)
Step 2 → Key found -> step is CACHED, skipped
Step 3 → Key changed -> step re-runs AND all later steps re-run
Step 4 → With a cache mount, a persistent dir is attached to the RUN, so the package manager finds already-downloaded files
Step 5 → The cache dir is NOT copied into the image layer
Step 6 → Local cache lives in the builder; for CI export it (topic 116)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर instruction के लिए BuildKit cache key बनाता है (instruction + parent + input files का hash)
Step 2 → Key मिली -> step CACHED, skip
Step 3 → Key बदली -> यह step और बाद के सब steps दोबारा चलते हैं
Step 4 → Cache mount के साथ RUN को persistent dir मिलती है, तो package manager को पहले से download files मिल जाती हैं
Step 5 → Cache dir image layer में copy नहीं होती
Step 6 → Local cache builder में रहता है; CI के लिए export करो (topic 116)
```

---

## 🟡 Real World Example
A Node monorepo CI step `npm ci` took 2 minutes whenever any dependency changed. Adding `--mount=type=cache,target=/root/.npm` meant only the new package was downloaded; the step dropped to 20 seconds. For apt, the team used cache mounts for `/var/cache/apt` and `/var/lib/apt` with `sharing=locked`, avoiding corrupt cache when two builds run together.

## 🟡 Real Example Hindi mein
Node monorepo की CI में किसी भी dependency के बदलने पर `npm ci` 2 मिनट लेता था। `--mount=type=cache,target=/root/.npm` जोड़ने पर सिर्फ नया package download हुआ; step 20 सेकंड रह गया। apt के लिए team ने `/var/cache/apt` और `/var/lib/apt` पर `sharing=locked` वाले cache mounts इस्तेमाल किए ताकि दो builds साथ चलें तो cache corrupt न हो।

---

## 💻 Code / Config Example — Basic
```dockerfile
# syntax=docker/dockerfile:1
# Node image (example tag)
FROM node:22.11.0-slim
# Work dir
WORKDIR /app
# Copy only manifests: layer cache is reused until these change
COPY package.json package-lock.json ./
# Cache mount: npm's download cache persists across builds, not stored in the image
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev
# Source copy after install so code edits do not re-run npm ci
COPY . .
# Start
CMD ["node", "server.js"]
```

## 💻 Code / Config Example — Advanced
```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12.7-slim-bookworm
# Debian images auto-clean apt cache; keep it so the mount is useful
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
 && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
# apt cache mounts, locked so parallel builds do not corrupt them
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends libpq5
# Work dir
WORKDIR /app
# Bind mount requirements.txt (no COPY layer needed) and cache pip downloads
RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
# App code last (changes most often)
COPY . .
# Run API as non-root
RUN useradd --uid 10001 --create-home appuser
USER appuser
# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
(Dockerfile syntax checked by script; not built locally. The `docker-clean` tweak is the documented Docker pattern for apt cache mounts.)

```bash
# Inspect and clean BuildKit cache usage on a machine
docker buildx du
# Remove build cache older than 7 days (168h)
docker builder prune --filter until=168h -f
```

---

## 🟠 My Stack Integration
- **Node**: cache `/root/.npm`; **FastAPI**: cache `/root/.cache/pip`; **React**: same npm cache plus Vite output is not cached by the mount.
- **GitHub Actions**: runners are fresh each run, so local cache mounts vanish; use `cache-from/cache-to` (type=gha) from topic 116.
- **VPS**: if you do build on the VPS, run `docker builder prune` weekly so cache does not fill the disk.

```yaml
# Cron-like cleanup via compose-free one-liner in a systemd timer / crontab (shown as a workflow step)
- name: Prune old build cache on the builder
  run: docker builder prune --filter until=168h -f
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Placing `COPY . .` before `npm ci`.
✅ Correct: Copy manifests, install, then copy source.

❌ Mistake 2: Putting application files in a cache mount and expecting them in the image.
✅ Correct: Cache mounts are not in the image; only put download caches there.

❌ Mistake 3: Parallel builds sharing an apt cache without `sharing=locked`.
✅ Correct: Use `sharing=locked` for apt.

❌ Mistake 4: Never pruning; builder cache grows to tens of GB.
✅ Correct: `docker builder prune` with filters on schedule.

---

## 🧠 Tricky Interview Question
"You use a cache mount for `node_modules` itself (`target=/app/node_modules`) and your final image has an empty `node_modules`. Why?"

Answer: Cache mount contents are not committed into the layer; they exist only during that RUN. The cache mount is for download caches (`~/.npm`), while real install output must go to a normal path (the default `node_modules` created by `npm ci`).

---

## ⚫ Interview Questions + Answers

Q1: What invalidates a layer's cache?
A1: A changed instruction, changed copied file contents, changed ARG/ENV used, or a changed parent layer.

Q2: Layer cache vs cache mount?
A2: Layer cache skips a whole step. Cache mount speeds up a step that still runs, by keeping tool caches.

Q3: Is a cache mount part of the image?
A3: No.

Q4: What does `sharing=locked` do?
A4: Only one build at a time can use the mount, preventing concurrent corruption.

Q5: Why does cache not persist on GitHub-hosted runners?
A5: The VM is destroyed after each job; export/import cache using `cache-to`/`cache-from`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Package-manager heavy builds (npm, pip, apt, go modules, maven).

❌ Avoid when:
- You need fully clean, reproducible builds (use `--no-cache` in scheduled security rebuilds).
- Cache could hold secrets; treat it as non-secret storage.

---

## 📊 Visual Diagram
```
 Layer cache (skip whole step)
   COPY package*.json ─► [HIT] ─► RUN npm ci ─► [HIT] ─► COPY . . ─► [MISS: code changed]

 Cache mount (step re-runs but is faster)
   RUN npm ci
      └── /root/.npm  <── persistent builder dir (packages already downloaded)
          (not saved in the image layer)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Layer cache | Reuse finished steps | पूरे step का reuse |
| Cache mount | Persistent tool cache | persistent tool cache |
| Cache key | Hash identifying a step | step की पहचान hash |
| sharing=locked | One writer at a time | एक बार में एक build |
| Prune | Delete cache | cache हटाना |
| Invalidate | Make cache unusable | cache बेकार करना |

---

## ⚡ 3-Line Summary
English: Layer cache skips unchanged steps; cache mounts speed up steps that must run.
Order Dockerfile from stable to changing.
Prune cache regularly and export it in CI.
Hindi: Layer cache unchanged steps skip करता है; cache mounts चलने वाले steps तेज़ करते हैं।
Dockerfile को stable से बदलने वाले क्रम में रखो।
Cache नियमित prune करो और CI में export करो।

---

## ➡️ Next Topic
**116. Remote Build Cache** - sharing cache between CI runs and machines.
