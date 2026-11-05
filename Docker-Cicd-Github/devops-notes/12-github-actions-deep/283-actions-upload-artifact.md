# 283. actions/upload-artifact
# हिंदी में: actions/upload-artifact (विस्तार से)

---

## 🔵 Simple Definition (English)
`actions/upload-artifact` is the official GitHub Action that packs files into a zip and stores them as a named artifact of the current workflow run. Main inputs: `name`, `path`, `if-no-files-found`, `retention-days`, `compression-level`, `overwrite`, `include-hidden-files`. Outputs: `artifact-id`, `artifact-url` (v4).

## 🔵 सरल परिभाषा (Hindi)
`actions/upload-artifact` GitHub की official Action है जो files को zip करके मौजूदा workflow run के नाम वाले artifact की तरह store करती है। मुख्य inputs: `name`, `path`, `if-no-files-found`, `retention-days`, `compression-level`, `overwrite`, `include-hidden-files`। Outputs: `artifact-id`, `artifact-url` (v4)।

---

## 🔴 Problem it Solves
Plain `scp` or `curl` uploads need your own storage and credentials. Wildcards, excludes, retention, zipping and permission handling would all be scripts you maintain. This Action gives a tested, first-party way to keep outputs from the run (including from failed runs) with zero extra infrastructure.

## 🔴 यह क्यों बना? (Hindi)
सीधे `scp` या `curl` upload के लिए आपको अपना storage और credentials चाहिए। Wildcards, excludes, retention, zip और permissions के scripts आपको खुद maintain करने पड़ते। यह Action बिना extra infrastructure के (fail हुए runs समेत) outputs रखने का tested, first-party तरीका देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Step reads the "path" globs (multi-line list, ! excludes allowed)
Step 2 → It resolves files relative to GITHUB_WORKSPACE (or absolute paths)
Step 3 → Least common ancestor of matched files becomes the zip root
Step 4 → Files are zipped (compression-level 0-9) and uploaded via the
         Actions artifact service (needs ACTIONS_RUNTIME_TOKEN, provided automatically)
Step 5 → If nothing matches: warn / error / ignore per if-no-files-found
Step 6 → Outputs artifact-id and artifact-url are set; artifact is immutable (v4)
```

Gotcha in step 3: uploading `dist/index.html` and `dist/app/main.js` keeps the `dist/...` structure only if the common root is above `dist`; uploading `path: dist/` stores contents relative to `dist/`. Always test with a download.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Step "path" globs पढ़ता है (multi-line list, ! excludes चलते हैं)
Step 2 → Files GITHUB_WORKSPACE के सापेक्ष (या absolute paths) ढूँढता है
Step 3 → Matched files का least common ancestor zip का root बनता है
Step 4 → Files zip होकर (compression-level 0-9) Actions artifact service पर upload होती हैं
         (ACTIONS_RUNTIME_TOKEN अपने-आप मिलता है)
Step 5 → कुछ match न हो तो if-no-files-found के अनुसार warn / error / ignore
Step 6 → Outputs artifact-id और artifact-url set होते हैं; artifact immutable है (v4)
```

Step 3 की gotcha: `path: dist/` upload करने पर contents `dist/` के सापेक्ष store होते हैं। हमेशा download करके जाँचो।

---

## 🟡 Real World Example
Playwright end-to-end tests for your checkout flow fail only in CI. The workflow uploads `playwright-report/` and `test-results/` with `if: always()` (or `if: failure()`), so the developer opens the run, downloads the zip, and sees the trace and screenshot of exactly where it failed. A Node.js API job also uploads `npm audit --json` and a Trivy scan report for the security team.

## 🟡 Real Example Hindi mein
आपके checkout flow के Playwright end-to-end tests सिर्फ CI में fail होते हैं। Workflow `playwright-report/` और `test-results/` को `if: always()` (या `if: failure()`) के साथ upload करता है, ताकि developer run खोलकर zip download करे और ठीक वह trace/screenshot देखे जहाँ fail हुआ। Node.js API job security team के लिए `npm audit --json` और Trivy scan report भी upload करता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/upload-basic.yml
name: upload-basic                     # workflow name
on: workflow_dispatch                  # run manually

jobs:
  make:
    runs-on: ubuntu-latest             # runner
    steps:
      - run: |
          mkdir -p out/logs                              # create folders
          date > out/build-time.txt                      # sample file
          echo "log line" > out/logs/app.log             # sample log
      - uses: actions/upload-artifact@v4                 # example version, check latest
        with:
          name: build-output           # artifact name shown in the UI
          path: out/                   # upload this folder
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/upload-advanced.yml
name: upload-advanced                  # workflow name
on:
  pull_request:                        # test every PR
  push:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false                 # keep other cells running if one fails
      matrix:
        node: [18, 20]                 # two Node versions
    steps:
      - uses: actions/checkout@v4      # example version
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: npm
      - run: npm ci                    # install
      - run: npx playwright install --with-deps chromium   # browser for e2e
      - id: tests                      # id used for outputs/outcome
        run: npx playwright test       # writes playwright-report/ and test-results/
      - name: Upload e2e evidence
        if: ${{ !cancelled() }}        # upload on success AND failure, but not on cancel
        id: up
        uses: actions/upload-artifact@v4
        with:
          name: e2e-node${{ matrix.node }}-${{ github.run_attempt }}   # UNIQUE per matrix cell + attempt
          path: |                      # newline list of globs
            playwright-report/
            test-results/**/*.png
            test-results/**/*.zip
            !**/*.tmp                  # exclude temp files
          if-no-files-found: error     # fail the step if nothing was produced
          retention-days: 5            # short life: large files cost storage
          compression-level: 6         # balanced size/speed (0 = none for already-compressed)
          include-hidden-files: false  # keep dotfiles (.env!) out (default false in v4.4+)
      - name: Link to artifact
        if: ${{ !cancelled() }}
        run: 'echo "Evidence: ${{ steps.up.outputs.artifact-url }}"'   # URL output (v4)

  merge:
    needs: e2e
    if: ${{ !cancelled() }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/upload-artifact/merge@v4     # sub-action that merges artifacts
        with:
          name: e2e-all                # new combined artifact
          pattern: e2e-node*           # which artifacts to merge
          delete-merged: true          # remove originals afterwards
```
Not run locally; YAML parsed only. `upload-artifact/merge` and `delete-merged` exist in v4; verify inputs against the README of the version you pin.

---

## 🟠 My Stack Integration
For Node.js/FastAPI: upload coverage (`coverage/lcov.info`), `pytest` JUnit XML, `npm audit` output. For React: `dist/` bundle and Lighthouse report. For Nginx config: the rendered `nginx.conf` plus `nginx -t` output so reviewers see what will go live. For AWS: upload Terraform plan files (but treat plan files as sensitive - they can contain secret values).

```yaml
# snippet: FastAPI test reports
      - run: pytest --junitxml=reports/junit.xml --cov=app --cov-report=xml:reports/coverage.xml
      - uses: actions/upload-artifact@v4
        if: always()                   # keep reports on failure too
        with:
          name: fastapi-reports
          path: reports/               # junit + coverage XML
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `path: .` or `path: ~/` (uploads node_modules, `.git`, `.env`).
✅ Correct: Upload specific folders; use `!` excludes.

❌ Mistake 2: Same `name` from every matrix cell or a re-run (`Failed to CreateArtifact: Conflict`).
✅ Correct: Make names unique (matrix value, `run_attempt`) or set `overwrite: true` where replacing is intended.

❌ Mistake 3: Upload step without `if: always()` so failure evidence is lost.
✅ Correct: `if: ${{ !cancelled() }}` or `always()`.

❌ Mistake 4: Uploading thousands of tiny files (very slow).
✅ Correct: tar them first, upload one archive (also preserves file permissions, which zip loses).

❌ Mistake 5: Huge retention for large files.
✅ Correct: Short `retention-days` for debug artifacts; storage counts toward quota.

---

## 🧠 Tricky Interview Question
You upload a shell script `deploy.sh` (executable) as an artifact, download it in another job and `./deploy.sh` gives "Permission denied". Why?

Answer: The artifact service zips files and does not preserve Unix permissions (the executable bit is lost). Either `chmod +x` after download, or `tar` the files before upload and extract after download, which keeps permissions.

---

## ⚫ Interview Questions + Answers

Q1: What are the key inputs?
A1: `name`, `path` (required), `if-no-files-found` (warn/error/ignore), `retention-days`, `compression-level`, `overwrite`, `include-hidden-files`.

Q2: What does the action output?
A2: `artifact-id`, `artifact-url` (and in newer versions `artifact-digest`; check the README).

Q3: Can you upload from multiple jobs with the same name in v4?
A3: No, names must be unique per run unless `overwrite: true`; for merging use `pattern` + `merge-multiple` on download or `upload-artifact/merge`.

Q4: Does it work on self-hosted runners?
A4: Yes, but the runner needs outbound access to the Actions artifact service; on GHES v4 may not be supported.

Q5: How do you run it after a failed step?
A5: `if: always()` or `if: ${{ !cancelled() }}`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Evidence from failed tests, build bundles, scan reports.

❌ Avoid when:
- Secrets, DB dumps, customer data.
- Release distribution (use GitHub Releases) or dependency cache (use actions/cache).

---

## 📊 Visual Diagram
```
 path globs        resolve files         zip              store
 dist/**   ----->  [a.js][b.css]  --->  web-dist.zip ---> GitHub artifact service
 !**/*.map  (excluded)                   (level 0-9)       name unique per run
                                                            retention N days
 outputs: artifact-id, artifact-url  --> used in summaries / API / gh run download
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| path | Files/globs to upload | Upload होने वाली files |
| if-no-files-found | Action when nothing matches | कुछ न मिलने पर व्यवहार |
| retention-days | Lifetime of the artifact | Artifact की उम्र |
| compression-level | Zip level 0-9 | Zip का स्तर |
| overwrite | Replace existing artifact name | उसी नाम को बदलना |

---

## ⚡ 3-Line Summary
English: `upload-artifact` zips globbed files into a named, immutable artifact for the run.
Use unique names, `if: always()` for evidence, short retention, and never include secrets.
Zip loses Unix permissions; tar first if needed.

Hindi: `upload-artifact` globbed files को run के नाम वाले, immutable artifact में zip करता है।
Unique नाम, evidence के लिए `if: always()`, छोटी retention रखो, और secrets कभी शामिल मत करो।
Zip में Unix permissions खो जाती हैं; ज़रूरत हो तो पहले tar करो।

---

## ➡️ Next Topic
**284. actions/download-artifact** — fetching artifacts by name, pattern, merge, and from other workflow runs.
