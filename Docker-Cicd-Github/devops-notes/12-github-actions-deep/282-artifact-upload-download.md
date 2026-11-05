# 282. Artifact Upload + Download
# हिंदी में: Artifact Upload + Download (jobs के बीच files share करना)

---

## 🔵 Simple Definition (English)
An **artifact** is a file or folder produced by a workflow run (build output, test report, coverage, logs) that GitHub stores with the run. You **upload** it with `actions/upload-artifact` and **download** it in a later job with `actions/download-artifact`, or manually from the run page or via `gh run download`.

## 🔵 सरल परिभाषा (Hindi)
**Artifact** workflow run से बनी file या folder है (build output, test report, coverage, logs) जिसे GitHub run के साथ store करता है। इसे `actions/upload-artifact` से **upload** और बाद के job में `actions/download-artifact` से **download** करते हैं, या run page / `gh run download` से manually।

---

## 🔴 Problem it Solves
Every job runs on a fresh VM; files from the `build` job disappear when it finishes, so the `deploy` job cannot see `dist/`. Also, after a failed test run, you need the Playwright screenshots or coverage report to debug, but the VM is gone. Artifacts persist files beyond the job.

## 🔴 यह क्यों बना? (Hindi)
हर job नई VM पर चलता है; `build` job की files उसके खत्म होते ही गायब हो जाती हैं, इसलिए `deploy` job `dist/` नहीं देख पाता। Test fail होने पर debugging के लिए Playwright screenshots या coverage report चाहिए, पर VM जा चुकी होती है। Artifacts files को job के बाद भी रखते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Job "build" creates files (npm run build -> dist/)
Step 2 → upload-artifact zips them and sends them to GitHub artifact storage
Step 3 → Job "build" ends, VM destroyed; artifact stays (default 90 days)
Step 4 → Job "deploy" (needs: build) starts on a NEW VM
Step 5 → download-artifact fetches by name into a path
Step 6 → Deploy job copies dist/ to the VPS (Nginx web root)
Step 7 → Humans can also download the zip from the run summary page
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Job "build" files बनाता है (npm run build -> dist/)
Step 2 → upload-artifact उन्हें zip करके GitHub artifact storage में भेजता है
Step 3 → Job "build" खत्म, VM नष्ट; artifact रहता है (default 90 दिन)
Step 4 → Job "deploy" (needs: build) नई VM पर शुरू होता है
Step 5 → download-artifact नाम से fetch करके path में रखता है
Step 6 → Deploy job dist/ को VPS (Nginx web root) में copy करता है
Step 7 → लोग run summary page से zip भी download कर सकते हैं
```

---

## 🟡 Real World Example
A React storefront: the `build` job runs `npm ci && npm run build` once, uploads `dist/` as `web-dist`. Then `deploy-staging` and `deploy-production` both download the exact same bundle and `rsync` it to their servers. Production runs what staging verified, bit for bit; no rebuild with a slightly different dependency.

## 🟡 Real Example Hindi mein
React storefront: `build` job एक बार `npm ci && npm run build` चलाकर `dist/` को `web-dist` नाम से upload करता है। फिर `deploy-staging` और `deploy-production` दोनों वही bundle download करके अपने servers पर `rsync` करते हैं। Production वही चलाता है जो staging ने verify किया, bit-for-bit; थोड़ी अलग dependency के साथ rebuild नहीं होता।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/artifact-basic.yml
name: artifact-basic                   # workflow name
on: push                               # run on every push

jobs:
  build:
    runs-on: ubuntu-latest             # runner for build
    steps:
      - uses: actions/checkout@v4      # example version
      - run: |
          mkdir -p dist                                   # output folder
          echo "hello from build $GITHUB_SHA" > dist/info.txt   # fake build output
      - uses: actions/upload-artifact@v4   # example version
        with:
          name: web-dist               # artifact name (must be unique per run in v4)
          path: dist/                  # folder to upload
          retention-days: 7            # keep 7 days instead of default 90

  use:
    needs: build                       # wait for build job
    runs-on: ubuntu-latest             # NEW VM, empty disk
    steps:
      - uses: actions/download-artifact@v4   # example version
        with:
          name: web-dist               # same name as upload
          path: ./downloaded           # where to extract
      - run: cat ./downloaded/info.txt # prove the file arrived
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/artifact-advanced.yml
name: artifact-advanced                # workflow name
on:
  push:
    branches: [main]                   # main only

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4      # example version
      - uses: actions/setup-node@v4    # example version
        with:
          node-version: 20
          cache: npm
      - run: npm ci                    # install from lockfile
      - run: npm test -- --coverage    # produce coverage/ folder
        continue-on-error: false       # fail the job if tests fail
      - name: Upload coverage even if tests failed
        if: always()                   # run after failure too
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ github.run_id }}     # unique name per run
          path: coverage/                         # report folder
          if-no-files-found: warn                 # warn (default) | error | ignore
          retention-days: 14

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci && npm run build   # create dist/
      - uses: actions/upload-artifact@v4
        id: up                         # to read outputs
        with:
          name: web-dist
          path: |                      # several paths allowed
            dist/
            !dist/**/*.map             # exclude source maps from the deploy bundle
          compression-level: 6         # 0-9; use 0 for already-compressed files
      - run: echo "artifact id ${{ steps.up.outputs.artifact-id }}"   # output of upload v4

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production            # approval + production secrets
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: web-dist
          path: dist
      - name: Rsync to VPS
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}
          HOST: ${{ secrets.VPS_HOST }}
        run: |
          install -m 700 -d ~/.ssh
          printf '%s\n' "$SSH_KEY" > ~/.ssh/id_ed25519 && chmod 600 ~/.ssh/id_ed25519
          printf '%s\n' "${{ secrets.VPS_KNOWN_HOSTS }}" > ~/.ssh/known_hosts
          rsync -az --delete dist/ deploy@"$HOST":/var/www/app/   # Nginx serves /var/www/app
```
Not run locally; YAML parsed only. Check v4 behaviours (immutable artifacts, name uniqueness) in the current action README.

---

## 🟠 My Stack Integration
- React: upload `dist/` (or `build/`), deploy to Nginx web root on VPS or sync to S3.
- Node.js/FastAPI: usually ship Docker images (registry), not zip artifacts; but upload test reports, `npm audit` JSON, Trivy scan results.
- Nginx: upload the rendered config for review before `nginx -t && nginx -s reload`.

```yaml
# snippet: S3 + CloudFront deploy of a downloaded React build
      - uses: actions/download-artifact@v4
        with:
          name: web-dist
          path: dist
      - run: aws s3 sync dist/ s3://my-bucket --delete    # AWS CLI preinstalled on ubuntu runners
        # credentials from OIDC role (see secrets topics); never commit keys
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using the same artifact `name` from a matrix (v4 fails: "already exists").
✅ Correct: Include the matrix value: `name: dist-${{ matrix.os }}`; merge later with `pattern` + `merge-multiple`.

❌ Mistake 2: Uploading `.env`, `node_modules` or SSH keys by accident (`path: .`).
✅ Correct: Upload only the folder you need; artifacts are readable by anyone with repo read access (public repo: everyone).

❌ Mistake 3: Expecting hidden files (`.env`, `.next`) to be included.
✅ Correct: v4.4+ excludes hidden files by default; use `include-hidden-files: true` knowingly (check version).

❌ Mistake 4: Relying on artifacts for long-term storage.
✅ Correct: Retention is limited (1-90 days); use S3/registry for releases.

❌ Mistake 5: Path differences: uploaded `dist/` but downloaded into `.` and files appear at root.
✅ Correct: Download with explicit `path:` and verify with `ls -R`.

---

## 🧠 Tricky Interview Question
`deploy` job downloads artifact `web-dist` but fails with "Artifact not found" even though `build` succeeded. Name two causes.

Answer: (1) The upload happened with a different name (typo, or name included a matrix value / run id the download doesn't know). (2) The upload step was skipped or found no files (`if-no-files-found: ignore` hides it), or the jobs are not linked with `needs`, so deploy started before upload finished. Also, in v4, a download from a different workflow run needs `run-id` and a token with `actions: read`.

---

## ⚫ Interview Questions + Answers

Q1: Artifact vs cache?
A1: Cache speeds up repeated dependency downloads (keyed, best effort). Artifact preserves outputs of a specific run for later jobs and for humans.

Q2: Default retention?
A2: 90 days (repo/org setting can reduce); override with `retention-days`.

Q3: How to download from CLI?
A3: `gh run download <run-id> -n web-dist`.

Q4: Are artifacts private?
A4: Visible to anyone who can read the repo (public repo: public). Never upload secrets.

Q5: Difference between v3 and v4?
A5: v4 is faster, artifacts are immutable (cannot upload twice with the same name), up to 500 per job, and download across runs needs an explicit `run-id` and token.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Passing build output between jobs.
- Keeping test reports, screenshots, logs for debugging.
- Promoting the same bundle through environments.

❌ Avoid when:
- Storing releases long-term (use Releases/S3).
- Sharing dependencies between runs (use cache).
- Containing secrets or customer data.

---

## 📊 Visual Diagram
```
 JOB build (VM 1)                         GitHub artifact storage
  npm run build -> dist/                  +----------------------+
  upload-artifact (name=web-dist) ------> | web-dist.zip (90d)   |
  VM 1 destroyed                          +----------+-----------+
                                                     |
 JOB deploy (VM 2, empty disk)                       |
  download-artifact (name=web-dist) <----------------+
  rsync dist/ -> VPS:/var/www/app  -> Nginx serves it
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Artifact | Stored output of a run | Run का stored output |
| Retention | How long it is kept | कितने दिन रखा जाए |
| Upload / Download | Save / fetch artifact | Save / वापस लाना |
| Immutable (v4) | Cannot be changed after upload | Upload के बाद बदल नहीं सकता |
| Promote | Re-use same build for next env | वही build अगले env में |

---

## ⚡ 3-Line Summary
English: Artifacts carry files out of a job so later jobs and humans can use them.
Upload with a unique name, download with the same name and explicit path.
Never upload secrets and do not treat artifacts as permanent storage.

Hindi: Artifacts files को job से बाहर ले जाते हैं ताकि बाद के jobs और लोग उन्हें use कर सकें।
Unique नाम से upload करो, उसी नाम और explicit path से download करो।
Secrets कभी upload मत करो और artifacts को permanent storage मत समझो।

---

## ➡️ Next Topic
**283. actions/upload-artifact** — all inputs, outputs and options of the upload action in detail.
