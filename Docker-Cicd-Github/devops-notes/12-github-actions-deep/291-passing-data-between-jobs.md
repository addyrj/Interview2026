# 291. Passing Data Between Jobs
# हिंदी में: Jobs के बीच Data पास करना

---

## 🔵 Simple Definition (English)
Because every job runs on a separate runner, data must be passed explicitly. GitHub gives four main channels: **job outputs** (small strings, via `needs`), **artifacts** (files, upload/download-artifact), **cache** (speed-only reuse across runs, not a guarantee), and **external storage / registry** (S3, GHCR, ECR, a database). Choose by size, sensitivity and lifetime.

## 🔵 सरल परिभाषा (Hindi)
हर job अलग runner पर चलता है, इसलिए data साफ़ तरीके से पास करना पड़ता है। GitHub चार मुख्य रास्ते देता है: **job outputs** (छोटी strings, `needs` से), **artifacts** (files, upload/download-artifact), **cache** (runs के बीच सिर्फ़ speed के लिए, गारंटी नहीं), और **external storage / registry** (S3, GHCR, ECR, database)। चुनाव size, संवेदनशीलता और उम्र के हिसाब से होता है।

---

## 🔴 Problem it Solves
Beginners write `export VERSION=1.2` in job A and expect it in job B, or save a file to `/tmp` and look for it in the next job. It fails because nothing is shared. Choosing the wrong channel causes real bugs: secrets leaked in artifacts, huge outputs truncated, deploys using a stale cache instead of the built files.

## 🔴 यह क्यों बना? (Hindi)
Beginners job A में `export VERSION=1.2` करते हैं और job B में उम्मीद करते हैं, या `/tmp` में file रखकर अगले job में ढूँढते हैं। यह fail होता है क्योंकि कुछ साझा नहीं है। गलत channel चुनने से असली bugs आते हैं: artifacts में secrets leak, बड़े outputs कट जाना, deploy में built files की जगह पुराना cache इस्तेमाल होना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Ask: what am I passing?
         small text (<1 MB)  -> job output
         files / folders     -> artifact (same run)
         docker image        -> registry (GHCR / ECR), pass the tag via output
         speed-up only       -> cache (never rely on it)
         secret              -> secrets context in each job (never pass)
Step 2 → Producer job writes the data (GITHUB_OUTPUT / upload-artifact / docker push)
Step 3 → Consumer job declares  needs: producer  (ordering + access to outputs)
Step 4 → Consumer reads (needs.X.outputs / download-artifact / docker pull)
Step 5 → Verify integrity (checksum or image digest) before deploying
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पूछें: क्या पास कर रहा हूँ?
         छोटा text (<1 MB)  -> job output
         files / folders    -> artifact (उसी run में)
         docker image       -> registry (GHCR / ECR), tag output से भेजें
         सिर्फ़ speed-up     -> cache (उस पर निर्भर न रहें)
         secret             -> हर job में secrets context (पास कभी नहीं)
Step 2 → Producer job data लिखता है (GITHUB_OUTPUT / upload-artifact / docker push)
Step 3 → Consumer job  needs: producer  लिखता है (क्रम + outputs की पहुँच)
Step 4 → Consumer पढ़ता है (needs.X.outputs / download-artifact / docker pull)
Step 5 → Deploy से पहले integrity जाँचें (checksum या image digest)
```

---

## 🟡 Real World Example
A product-based company builds a Node API image in job `build`, pushes it to ECR, and passes only the **digest** (`sha256:...`) as a job output. The `deploy-staging` and `deploy-prod` jobs pull exactly that digest. Test reports (junit XML, coverage HTML) go as artifacts for the QA dashboard. The npm cache speeds up installs, but nothing depends on it. Each channel is used for what it is good at.

## 🟡 Real Example Hindi mein
एक product कंपनी `build` job में Node API image बनाकर ECR में push करती है और सिर्फ़ **digest** (`sha256:...`) को job output से पास करती है। `deploy-staging` और `deploy-prod` jobs ठीक वही digest pull करते हैं। Test reports (junit XML, coverage HTML) QA dashboard के लिए artifacts बनते हैं। npm cache installs तेज़ करता है, पर उस पर कुछ निर्भर नहीं। हर channel अपनी खूबी के लिए इस्तेमाल होता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/pass-basic.yml
name: pass-basic                          # workflow name
on: [workflow_dispatch]                   # manual run
jobs:
  make:
    runs-on: ubuntu-latest                # producer runner
    outputs:
      version: ${{ steps.v.outputs.version }}   # small string -> job output
    steps:
      - id: v
        run: echo "version=1.0.${{ github.run_number }}" >> "$GITHUB_OUTPUT"   # compute version
      - run: echo "built content" > app.txt      # create a file
      - uses: actions/upload-artifact@v4          # file -> artifact
        with:
          name: app                               # artifact name
          path: app.txt                           # file to share
  use:
    needs: make                           # wait and gain access
    runs-on: ubuntu-latest                # consumer runner
    steps:
      - uses: actions/download-artifact@v4        # fetch the file
        with:
          name: app                               # same name
      - run: echo "v${{ needs.make.outputs.version }}"; cat app.txt   # use both
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/pass-advanced.yml
# Image via registry digest, reports via artifact, integrity via checksum
name: pass-advanced                       # workflow name
on:
  push:
    branches: [main]
permissions:
  contents: read                          # checkout
  packages: write                         # push to GHCR with GITHUB_TOKEN
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.push.outputs.digest }}      # immutable image id
      sha_sum: ${{ steps.sum.outputs.sum }}         # checksum of the bundle
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3                # login to GHCR
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: push
        uses: docker/build-push-action@v6           # build + push (example version)
        with:
          context: ./api
          push: true
          tags: ghcr.io/${{ github.repository }}/api:${{ github.sha }}
      - run: tar -czf bundle.tgz -C web dist        # package static site files
      - id: sum
        run: echo "sum=$(sha256sum bundle.tgz | cut -d' ' -f1)" >> "$GITHUB_OUTPUT"   # checksum output
      - uses: actions/upload-artifact@v4
        with:
          name: web-bundle
          path: bundle.tgz
          retention-days: 3                         # short-lived
  deploy:
    needs: build                                    # gets outputs + ordering
    runs-on: ubuntu-latest
    environment: production                         # gated deploy
    env:
      IMAGE_DIGEST: ${{ needs.build.outputs.digest }}   # via env, not inline
      EXPECTED_SUM: ${{ needs.build.outputs.sha_sum }}
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: web-bundle
      - name: Verify bundle integrity
        run: echo "$EXPECTED_SUM  bundle.tgz" | sha256sum -c -   # fails if tampered
      - name: Show what will be deployed
        run: echo "image=ghcr.io/${{ github.repository }}/api@$IMAGE_DIGEST"   # deploy by digest
```

---

## 🟠 My Stack Integration
- **Node/FastAPI Docker images**: push to GHCR/ECR, pass digest; the VPS does `docker pull repo@sha256:...` and `docker compose up -d`.
- **React build**: tarball artifact, then rsync to Nginx root.
- **Terraform on AWS**: the plan file as artifact (`tfplan`) between `plan` and `apply` jobs, protected by environment approval; artifacts may contain secrets in plans, so restrict repo access.
- **Test results**: matrix jobs upload `junit-*.xml`; a summary job downloads with `pattern` + `merge-multiple`.

```yaml
# Snippet: SSH deploy on VPS using values passed from earlier jobs
      - run: |
          ssh -i ~/.ssh/id deploy@"$HOST" \
            "cd /srv/app && IMAGE=ghcr.io/org/api@$IMAGE_DIGEST docker compose up -d"   # compose reads IMAGE
        env:
          HOST: ${{ secrets.VPS_HOST }}                # secret from environment
          IMAGE_DIGEST: ${{ needs.build.outputs.digest }}   # from build job
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `export VAR=...` or `$GITHUB_ENV` in one job, reading in another.
✅ Correct: Both are per job. Use outputs.

❌ Mistake 2: Using cache to move build results between jobs.
✅ Correct: Cache can miss at any time. Use artifacts.

❌ Mistake 3: Passing a secret through outputs/artifacts.
✅ Correct: Each job reads `secrets.X` itself; scope with environments.

❌ Mistake 4: Deploying `:latest` tag passed around, which may change between jobs.
✅ Correct: Pass immutable digest or SHA tag.

❌ Mistake 5: Forgetting artifact `retention-days` and name uniqueness in matrices (v4 forbids duplicates).
✅ Correct: Include `${{ matrix.x }}` in names; set short retention.

---

## 🧠 Tricky Interview Question
You need to share a 700 MB Docker image tarball between `build` and `scan` jobs. Artifact upload takes 4 minutes. What is a better design?

Answer: Push the image to a registry (GHCR/ECR) from `build` under an immutable tag or digest, pass the digest as a job output, and let `scan` and `deploy` pull it. Registries use layer deduplication, so only changed layers move, which is much faster than zipping a whole tarball. If the image must not be published before scanning, push to a temporary tag or a private staging repo and promote/retag after the scan passes. Artifacts remain suitable for small files (reports, bundles).

---

## ⚫ Interview Questions + Answers

Q1: Name the ways to pass data between jobs.
A1: Job outputs (small strings), artifacts (files), registry/external storage (images and large data), and caches only for speed.

Q2: Why can't I use environment variables across jobs?
A2: Each job runs on its own runner (new VM or container), so process and file state are not shared.

Q3: How would you pass a JSON list of services to build in a matrix?
A3: Output a JSON string from a planning job and use `fromJSON(needs.plan.outputs.services)` in `strategy.matrix`.

Q4: How to ensure the deployed artifact is the tested one?
A4: Build once, publish with an immutable identifier (digest/checksum), deploy by that identifier, and verify before deploy.

Q5: How are secrets handled between jobs?
A5: They are not passed. Every job that needs a secret reads it from `secrets` (or an environment). Outputs containing secrets get redacted or are a leak risk.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Splitting pipelines into build / test / scan / deploy jobs.
- Using parallel jobs that feed a final summary job.

❌ Avoid when:
- A single job could do it all with less overhead (small projects), since each job has startup cost.
- Large binaries needed by many runs (host in S3/registry).

---

## 📊 Visual Diagram
```
                       needs: build
  +-----------+   outputs (strings)   +-------------+
  |  build    | --------------------> |   deploy    |
  |           |   artifact (files)    |             |
  |           | --------------------> |             |
  |           |   image digest        |             |
  |           | --push--> [GHCR/ECR] --pull-------> |
  +-----------+                       +-------------+
         |                                   ^
         +-- cache (speed only) ... maybe ---+   (never rely on it)

  secrets: NOT passed -> each job reads ${{ secrets.X }}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Job output | Small string value | छोटी string value |
| Artifact | File bundle from a run | Run की files का bundle |
| Digest | Immutable image hash | Image का अटल hash |
| Registry | Image storage (GHCR/ECR) | Image भंडार |
| Retention | How long data is stored | कितने दिन रखा जाए |
| Checksum | Hash to verify integrity | Integrity जाँचने का hash |

---

## ⚡ 3-Line Summary
English: Jobs do not share disk or variables, so pass data via outputs, artifacts or a registry.
English: Small strings use outputs, files use artifacts, images use registries, cache is only for speed.
English: Never pass secrets; deploy immutable digests and verify checksums.
Hindi: Jobs disk या variables साझा नहीं करते, इसलिए data outputs, artifacts या registry से पास करें।
Hindi: छोटी strings outputs से, files artifacts से, images registry से, cache सिर्फ़ speed के लिए।
Hindi: Secrets कभी पास न करें; अटल digest deploy करें और checksum जाँचें।

---

## ➡️ Next Topic
**292. Matrix Strategy** — run the same job across many versions and OSes automatically.
