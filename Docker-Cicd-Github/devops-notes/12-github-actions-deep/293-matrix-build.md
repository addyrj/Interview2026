# 293. Matrix Build
# हिंदी में: Matrix Build (कई services/platforms का build)

---

## 🔵 Simple Definition (English)
A matrix build uses `strategy.matrix` to build several targets from one job definition: several services (web, api, fastapi), several platforms (amd64, arm64), or several environments, each in its own parallel runner. Each matrix entry can carry custom fields (`context`, `dockerfile`, `image`) so one template builds everything. Results can be collected by a later job that merges manifests or deploys.

## 🔵 सरल परिभाषा (Hindi)
Matrix build `strategy.matrix` से एक job definition में कई targets बनाता है: कई services (web, api, fastapi), कई platforms (amd64, arm64), या कई environments, हर एक अपने parallel runner पर। हर matrix entry में custom fields (`context`, `dockerfile`, `image`) हो सकते हैं ताकि एक template सब कुछ बनाए। नतीजे बाद का job इकट्ठा करके manifests merge या deploy कर सकता है।

---

## 🔴 Problem it Solves
A monorepo with 3 services used to have 3 nearly identical workflow files or one job building images one after another (10 minutes + 8 + 12 = 30 minutes). Matrix build makes it one file, builds them in parallel (about the longest one, 12 minutes), and adding service number 4 is one line. Multi-arch builds under QEMU emulation are slow; a matrix with native arm64 runners is much faster.

## 🔴 यह क्यों बना? (Hindi)
3 services वाले monorepo में 3 लगभग एक जैसी workflow files होती थीं या एक job images को एक-एक करके बनाता था (10 + 8 + 12 = 30 मिनट)। Matrix build एक file बनाता है, सब parallel बनाता है (सबसे लंबे वाले जितना, 12 मिनट), और चौथी service जोड़ना एक पंक्ति है। QEMU emulation पर multi-arch build धीमा होता है; native arm64 runners वाला matrix बहुत तेज़ है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Describe each target as a matrix entry (include list):
         { service: api, context: ./api, image: shop-api }
Step 2 → GitHub spawns one job per entry, in parallel
Step 3 → Each job checks out code, logs in to registry, builds with its own context
Step 4 → Each job tags images with the shared SHA, pushes them
Step 5 → Optional: per-job cache scope (cache-from type=gha,scope=<service>)
Step 6 → A final job (needs: build) deploys or creates a manifest list for multi-arch
Step 7 → Aggregator job gives branch protection a stable check name
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर target को matrix entry की तरह लिखें (include list):
         { service: api, context: ./api, image: shop-api }
Step 2 → GitHub हर entry के लिए एक job parallel में बनाता है
Step 3 → हर job code checkout, registry login, और अपने context से build करता है
Step 4 → हर job साझा SHA से image tag करके push करता है
Step 5 → वैकल्पिक: job के हिसाब से cache scope (cache-from type=gha,scope=<service>)
Step 6 → अंतिम job (needs: build) deploy करता है या multi-arch के लिए manifest list बनाता है
Step 7 → Aggregator job branch protection को स्थिर check नाम देता है
```

---

## 🟡 Real World Example
A startup has `web` (React served by Nginx), `api` (Node.js) and `ml` (FastAPI). Their old workflow built the three Docker images serially in 28 minutes. After a matrix build with per-service cache scopes, PR builds take 9 minutes (the slowest, FastAPI with heavy wheels, dominates). Deployment to the VPS pulls three images by SHA with docker compose. When the team added a `worker` service, they added four lines to the matrix.

## 🟡 Real Example Hindi mein
एक startup में `web` (Nginx पर React), `api` (Node.js) और `ml` (FastAPI) हैं। पुराना workflow तीनों Docker images को क्रम से 28 मिनट में बनाता था। Per-service cache scopes के साथ matrix build के बाद PR builds 9 मिनट में होते हैं (सबसे धीमा, भारी wheels वाला FastAPI, समय तय करता है)। VPS पर deploy docker compose से तीनों images SHA से pull करता है। `worker` service जोड़ी तो matrix में बस चार पंक्तियाँ जोड़नी पड़ीं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/matrix-build-basic.yml
name: matrix-build-basic                  # workflow name
on: [push]                                # trigger
jobs:
  build:
    runs-on: ubuntu-latest                # runner
    strategy:
      matrix:
        service: [web, api, fastapi]      # one job per service folder
    steps:
      - uses: actions/checkout@v4         # source
      - name: Build image                 # step label
        run: docker build -t ${{ matrix.service }}:ci ./${{ matrix.service }}   # build from folder
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/matrix-build-advanced.yml
# Multi-service build + push to GHCR with per-service cache, then deploy by SHA
name: matrix-build-advanced               # workflow name
on:
  push:
    branches: [main]
  pull_request:
permissions:
  contents: read                          # checkout
  packages: write                         # push to GHCR
env:
  REGISTRY: ghcr.io                       # registry host
jobs:
  build:
    name: build ${{ matrix.service }}     # readable job name
    runs-on: ubuntu-latest
    timeout-minutes: 30                   # protect against hangs
    strategy:
      fail-fast: false                    # one failing service must not hide others
      matrix:
        include:                          # explicit list: each entry is a full target
          - service: web
            context: ./web
            dockerfile: ./web/Dockerfile
          - service: api
            context: ./api
            dockerfile: ./api/Dockerfile
          - service: fastapi
            context: ./fastapi
            dockerfile: ./fastapi/Dockerfile
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3          # buildx builder
      - uses: docker/login-action@v3                 # log in (skipped for fork PRs below)
        if: github.event_name != 'pull_request'      # PRs do not push
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6            # example version
        with:
          context: ${{ matrix.context }}             # from matrix entry
          file: ${{ matrix.dockerfile }}             # from matrix entry
          push: ${{ github.event_name != 'pull_request' }}   # push only on main
          tags: ${{ env.REGISTRY }}/${{ github.repository }}/${{ matrix.service }}:${{ github.sha }}
          cache-from: type=gha,scope=${{ matrix.service }}   # per-service cache
          cache-to: type=gha,mode=max,scope=${{ matrix.service }}
  build-ok:                               # stable required check
    if: always()                          # run even when build failed
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: test "${{ needs.build.result }}" = "success"   # fail if any matrix job failed
  deploy:
    if: github.ref == 'refs/heads/main'   # only main
    needs: build-ok                       # after every image exists
    runs-on: ubuntu-latest
    environment: production               # approval gate + secrets
    steps:
      - name: Deploy over SSH
        env:
          SHA: ${{ github.sha }}          # image tag to roll out
          HOST: ${{ secrets.VPS_HOST }}   # VPS address from environment secret
        run: |
          install -m 700 -d ~/.ssh
          printf '%s\n' "${{ secrets.VPS_SSH_KEY }}" > ~/.ssh/id && chmod 600 ~/.ssh/id
          ssh-keyscan -H "$HOST" >> ~/.ssh/known_hosts
          ssh -i ~/.ssh/id deploy@"$HOST" "cd /srv/shop && TAG=$SHA docker compose pull && TAG=$SHA docker compose up -d"
```

---

## 🟠 My Stack Integration
- **Monorepo**: matrix over `web` (React+Nginx), `api` (Node.js), `fastapi` as in the example.
- **VPS**: `docker-compose.yml` uses `image: ghcr.io/org/repo/api:${TAG}`; deploy sets `TAG` to the commit SHA.
- **AWS ECR / Graviton**: matrix `platform: [linux/amd64, linux/arm64]` with `runs-on: ubuntu-24.04-arm` for native arm builds (availability of arm runners depends on your plan/repo type; verify).
- **Nginx**: web image contains the built static files and `nginx.conf`.

```yaml
# Snippet: native two-arch build matrix (runner labels are examples - verify availability)
    strategy:
      matrix:
        include:
          - platform: linux/amd64
            runner: ubuntu-latest         # x64 runner
          - platform: linux/arm64
            runner: ubuntu-24.04-arm      # arm runner label (GitHub-hosted, where available)
    runs-on: ${{ matrix.runner }}         # pick runner from the matrix
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: One shared cache scope for all services, so each build evicts the others.
✅ Correct: `scope=${{ matrix.service }}`.

❌ Mistake 2: Running `deploy` as part of the matrix, deploying three times.
✅ Correct: A separate `deploy` job with `needs`.

❌ Mistake 3: Pushing images from fork PRs (no permission, or worse, using secrets).
✅ Correct: `push: ${{ github.event_name != 'pull_request' }}` and no secrets on `pull_request` from forks.

❌ Mistake 4: Using `latest` as the only tag, which two parallel builds could overwrite.
✅ Correct: Tag with the commit SHA, optionally add `latest` later in the deploy job.

❌ Mistake 5: Rebuilding every service when only one changed.
✅ Correct: Add a `changes` job (paths filter) producing a dynamic matrix of only changed services.

---

## 🧠 Tricky Interview Question
You have a 3-service matrix. Service `api` fails, but `web` and `fastapi` already pushed their images. Branch protection requires "build-ok". The deploy job is skipped. What state are you in, and what protects production?

Answer: The registry now holds images for two services with the new SHA, but not `api`. Because `deploy` has `needs: build-ok` and `build-ok` fails when any matrix job fails, nothing is rolled out, so production keeps running the previous consistent set. Unused SHA-tagged images are harmless (clean them with lifecycle rules). Had deploy depended on individual jobs with `if: always()`, you could deploy a mixed version set. This is why the aggregator pattern and immutable SHA tags matter.

---

## ⚫ Interview Questions + Answers

Q1: How do you pass different build contexts to each matrix job?
A1: Use `include:` entries with custom keys (context, dockerfile) and read them as `matrix.context`.

Q2: How to build only changed services?
A2: A `changes` job computes a JSON list (using `git diff` or a paths-filter action), outputs it, and the build job uses `matrix: ${{ fromJSON(needs.changes.outputs.services) }}`.

Q3: How do you make multi-arch images with a matrix?
A3: Build each platform in its own job (pushing by digest), then a final job runs `docker buildx imagetools create` to merge them into one manifest list.

Q4: Why `fail-fast: false` for builds?
A4: You see all failing services at once instead of fixing one at a time.

Q5: How to limit cost?
A5: Use caches, `max-parallel`, path filters, and cancel obsolete runs with `concurrency`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several images/packages share the same build steps.
- Native multi-arch builds.
- Test sharding.

❌ Avoid when:
- Services need different complex steps (use separate jobs/reusable workflows).
- One tiny service; matrix adds noise.

---

## 📊 Visual Diagram
```
  push to main
      |
      v
 +-------------------- matrix: build --------------------+
 | build web  | build api  | build fastapi | (build worker)|   parallel
 +------+-----+------+-----+-------+-------+---------------+
        \            |             /
         +-----------+------------+
                     v
               [ build-ok ]   needs: build, if: always()
                     |  success only
                     v
               [ deploy ]  -> VPS: TAG=<sha> docker compose up -d
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Matrix build | Build many targets in parallel | कई targets parallel build |
| Cache scope | Separate BuildKit cache namespace | अलग cache namespace |
| Manifest list | One tag pointing to many arch images | कई arch का एक tag |
| Native runner | Real hardware of that arch | उसी arch का असली runner |
| Dynamic matrix | Matrix from JSON output | JSON से बना matrix |
| Aggregator | Gate job for the matrix | Matrix का gate job |

---

## ⚡ 3-Line Summary
English: Matrix build builds many services or platforms from one job template in parallel.
English: Use `include` fields, per-service cache scope and SHA tags; deploy in a separate job.
English: An aggregator job protects production from partial failures.
Hindi: Matrix build एक job template से कई services या platforms parallel बनाता है।
Hindi: `include` fields, per-service cache scope और SHA tags इस्तेमाल करें; deploy अलग job में।
Hindi: Aggregator job आंशिक failures से production को बचाता है।

---

## ➡️ Next Topic
**294. Parallel Jobs** — how GitHub decides what runs at the same time and how to control it.
