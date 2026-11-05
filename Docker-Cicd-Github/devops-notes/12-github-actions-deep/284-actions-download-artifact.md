# 284. actions/download-artifact
# हिंदी में: actions/download-artifact (विस्तार से)

---

## 🔵 Simple Definition (English)
`actions/download-artifact` is the official GitHub Action that fetches artifacts uploaded earlier (by `actions/upload-artifact`) and unpacks them on the current runner. Main inputs: `name`, `path`, `pattern`, `merge-multiple`, and (to read from another run) `github-token`, `repository`, `run-id`. Output: `download-path`. Each job runs on a fresh machine, so this Action is how a later job gets files from an earlier job.

## 🔵 सरल परिभाषा (Hindi)
`actions/download-artifact` GitHub की official Action है जो पहले (`actions/upload-artifact` से) upload हुए artifacts को मौजूदा runner पर लाकर unpack करती है। मुख्य inputs: `name`, `path`, `pattern`, `merge-multiple`, और दूसरे run से पढ़ने के लिए `github-token`, `repository`, `run-id`। Output: `download-path`। हर job नई machine पर चलता है, इसलिए पिछले job की files अगले job तक पहुँचाने का तरीका यही Action है।

---

## 🔴 Problem it Solves
Every job in GitHub Actions starts on a clean VM. If the `build` job creates `dist/`, the `deploy` job cannot see it. Before this Action, people rebuilt in every job (slow, and the deployed bits may differ from the tested bits) or pushed files to S3/FTP by hand. Download-artifact lets you "build once, deploy the exact same bytes".

## 🔴 यह क्यों बना? (Hindi)
GitHub Actions में हर job साफ़ VM पर शुरू होता है। अगर `build` job ने `dist/` बनाया, तो `deploy` job उसे नहीं देख सकता। पहले लोग हर job में दोबारा build करते थे (धीमा, और deploy होने वाला code tested code से अलग हो सकता है) या files हाथ से S3/FTP पर डालते थे। Download-artifact से "एक बार build, वही bytes deploy" संभव होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Earlier job uploads artifact "web-dist" (upload-artifact@v4)
Step 2 → Later job declares needs: build (so the artifact exists)
Step 3 → download-artifact@v4 asks the Actions artifact service for the artifact
Step 4 → "name" => one artifact, "pattern" => many; none => ALL artifacts of the run
Step 5 → Zip is extracted into "path" (default: workspace)
         - single name: files go directly into path
         - no name / pattern: each artifact gets its own sub-folder (unless merge-multiple: true)
Step 6 → Output download-path tells you where files landed
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले वाला job artifact "web-dist" upload करता है (upload-artifact@v4)
Step 2 → बाद वाला job needs: build लिखता है (ताकि artifact मौजूद हो)
Step 3 → download-artifact@v4 Actions artifact service से artifact माँगता है
Step 4 → "name" => एक artifact, "pattern" => कई; दोनों नहीं => run के सारे artifacts
Step 5 → Zip, "path" में extract होती है
         - एक name: files सीधे path में
         - name/pattern नहीं: हर artifact का अपना sub-folder (जब तक merge-multiple: true न हो)
Step 6 → Output download-path बताता है files कहाँ उतरीं
```

---

## 🟡 Real World Example
Your React app is built once in CI (`npm ci && npm run build`) and tested by Playwright. The `deploy` job downloads the same `web-dist` artifact and `rsync`s it to the VPS at `/var/www/app`. Nobody rebuilds, so what QA tested is exactly what Nginx serves. Flipkart-style release pipelines work the same way: one immutable build artifact, promoted through staging to production.

## 🟡 Real Example Hindi mein
आपका React app CI में एक बार build होता है (`npm ci && npm run build`) और Playwright से test होता है। `deploy` job वही `web-dist` artifact download करके VPS के `/var/www/app` पर `rsync` करता है। दोबारा build नहीं होता, इसलिए QA ने जो test किया वही Nginx serve करता है। Flipkart जैसी release pipelines भी ऐसे ही चलती हैं: एक immutable build, staging से production तक promote।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/basic-download.yml
name: basic-download                      # workflow name shown in Actions tab
on: [push]                                # run on every push
jobs:
  build:                                  # first job: creates the file
    runs-on: ubuntu-latest                # fresh GitHub-hosted Linux VM
    steps:
      - run: mkdir out && echo "hello" > out/a.txt   # make a file to share
      - uses: actions/upload-artifact@v4  # example version, check latest
        with:
          name: demo-out                  # artifact name (unique per run)
          path: out/                      # folder to upload
  use:                                    # second job: consumes the file
    needs: build                          # wait until build finished
    runs-on: ubuntu-latest                # another fresh VM, no files yet
    steps:
      - uses: actions/download-artifact@v4   # fetch the artifact
        with:
          name: demo-out                  # which artifact to fetch
          path: received/                 # where to extract it
      - run: cat received/a.txt           # prove the file arrived
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/release.yml
# Build web + api once, download both, deploy to VPS
name: release                             # workflow name
on:
  push:
    branches: [main]                      # only main triggers a release
permissions:
  contents: read                          # least privilege for GITHUB_TOKEN
  actions: read                           # needed to read artifacts of other runs
concurrency:
  group: release-${{ github.ref }}        # one release at a time per branch
  cancel-in-progress: false               # never cancel a running deploy
jobs:
  build-web:
    runs-on: ubuntu-latest                # runner for React build
    steps:
      - uses: actions/checkout@v4         # get source code
      - uses: actions/setup-node@v4       # install Node
        with:
          node-version: 20                # example LTS version
          cache: npm                      # built-in npm cache
      - run: npm ci && npm run build      # reproducible install + build
        working-directory: web            # React app folder
      - uses: actions/upload-artifact@v4
        with:
          name: web-dist                  # artifact 1
          path: web/dist                  # build output
          retention-days: 7               # short life, saves storage
  build-api:
    runs-on: ubuntu-latest                # runner for Node API build
    steps:
      - uses: actions/checkout@v4
      - run: npm ci --omit=dev            # production deps only
        working-directory: api
      - run: tar -czf api.tgz -C api .    # pack API (keeps file modes)
      - uses: actions/upload-artifact@v4
        with:
          name: api-bundle                # artifact 2
          path: api.tgz
          retention-days: 7
  deploy:
    needs: [build-web, build-api]         # wait for both artifacts
    runs-on: ubuntu-latest
    environment: production               # approval + environment secrets
    steps:
      - uses: actions/download-artifact@v4
        with:
          pattern: '*'                    # every artifact of this run
          path: artifacts                 # each one in its own sub-folder
      - run: ls -R artifacts              # debug: see layout, web-dist/ and api-bundle/
      - name: Setup SSH key
        run: |
          install -m 700 -d ~/.ssh                       # private ssh dir
          echo "${{ secrets.VPS_SSH_KEY }}" > ~/.ssh/id   # key from secret
          chmod 600 ~/.ssh/id                            # ssh refuses loose perms
          ssh-keyscan -H "${{ secrets.VPS_HOST }}" >> ~/.ssh/known_hosts  # trust host
      - name: Ship
        run: |
          rsync -az --delete -e "ssh -i ~/.ssh/id" artifacts/web-dist/ deploy@${{ secrets.VPS_HOST }}:/var/www/app/   # static site
          scp -i ~/.ssh/id artifacts/api-bundle/api.tgz deploy@${{ secrets.VPS_HOST }}:/tmp/api.tgz                    # API bundle
          ssh -i ~/.ssh/id deploy@${{ secrets.VPS_HOST }} 'tar -xzf /tmp/api.tgz -C /srv/api && pm2 reload api'         # unpack + reload
```

---

## 🟠 My Stack Integration
- **React + Nginx on VPS**: download `web-dist`, rsync into the Nginx root, then `nginx -t && systemctl reload nginx`.
- **Node.js / FastAPI**: download the packed bundle (tarball of code or a wheel/zip), unpack on VPS, restart PM2 or systemd.
- **AWS**: download `web-dist` and run `aws s3 sync` to S3 + CloudFront invalidation, using OIDC role (no long-lived keys).
- **Docker images** are better pushed to a registry, not artifacts; artifacts suit tarballs, reports, build output.

```yaml
# Snippet: S3 deploy job using the downloaded artifact
  deploy-s3:
    needs: build-web                      # artifact must exist
    runs-on: ubuntu-latest
    permissions:
      id-token: write                     # for OIDC to AWS
      contents: read
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: web-dist                  # single artifact: files land directly in path
          path: dist
      - uses: aws-actions/configure-aws-credentials@v4   # example version
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy   # example ARN
          aws-region: ap-south-1          # Mumbai
      - run: aws s3 sync dist s3://my-app-bucket --delete   # publish files
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `needs:` so the download runs before the upload finishes ("Artifact not found").
✅ Correct: Add `needs: build` to the consumer job.

❌ Mistake 2: Using `download-artifact@v3` with `upload-artifact@v4`. The versions use different backends and are not compatible (v3 is deprecated).
✅ Correct: Use v4 on both sides (v4+ is the supported line; confirm the current major in the Action's README).

❌ Mistake 3: Downloading without `name` and expecting flat files. You get one sub-folder per artifact.
✅ Correct: Use `name:` for one artifact, or `merge-multiple: true` with `pattern:` to flatten.

❌ Mistake 4: Trying to download from another workflow run without a token.
✅ Correct: Pass `github-token`, `run-id` and `repository` (token needs `actions: read`).

❌ Mistake 5: Assuming file permissions survive. Artifact zips lose the executable bit.
✅ Correct: Tar the files first (as in `api.tgz`) or `chmod +x` after download.

---

## 🧠 Tricky Interview Question
Your `deploy` job downloads `web-dist` successfully, but the site shows a blank page. `ls` shows `dist/web-dist/index.html` inside the download folder. What happened?

Answer: With a single `name`, files are extracted directly into `path`. But if you used `pattern` or no name, each artifact is placed in a sub-folder named after it, so rsync copied `dist/` including the extra `web-dist/` directory level and Nginx root pointed to the wrong folder. Fix: use `name: web-dist` with `path: dist`, or `merge-multiple: true`, or rsync from `artifacts/web-dist/`. Also check `upload-artifact` path: the least common ancestor of uploaded files becomes the zip root.

---

## ⚫ Interview Questions + Answers

Q1: Why do we need download-artifact at all?
A1: Jobs run on separate fresh runners with no shared disk. Artifacts are the official way to move files between jobs (and from a run to a human).

Q2: Difference between `name` and `pattern`?
A2: `name` fetches exactly one artifact; `pattern` is a glob that selects many. Without both, all artifacts of the run are downloaded.

Q3: What does `merge-multiple` do?
A3: When several artifacts are downloaded, it merges their contents into one folder instead of one sub-folder each. Conflicting file names get overwritten, so keep names unique.

Q4: How do you download an artifact from a different workflow run?
A4: Set `run-id` (and `repository` if another repo) plus `github-token` with `actions: read`. Often used by a `workflow_run` triggered deploy workflow.

Q5: Is artifact data secure?
A5: Anyone with read access to the repo can download artifacts of its runs, and they appear in the UI. Never upload `.env`, SSH keys or tokens. Artifacts expire after the retention period (default up to 90 days, configurable).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Build once, deploy/test many times across jobs.
- Collecting test reports, coverage, logs from matrix jobs for one summary job.
- Promoting an exact build from CI workflow to a CD workflow.

❌ Avoid when:
- You only need to speed up dependency installs (use cache, topic 286).
- You need to share Docker images (use a registry like GHCR/ECR).
- Files are huge and long-lived (use S3 with lifecycle rules).

---

## 📊 Visual Diagram
```
 Job: build-web                Job: build-api
 +---------------+             +---------------+
 | npm run build |             | npm ci        |
 +-------+-------+             +-------+-------+
         | upload-artifact             | upload-artifact
         v                             v
   +------------------------------------------+
   |   Artifact Store (per workflow run)      |
   |   web-dist            api-bundle         |
   +-------------------+----------------------+
                       | download-artifact@v4
                       v
              Job: deploy (needs both)
              +-------------------------+
              | rsync -> VPS /var/www   |
              | scp + pm2 reload        |
              +-------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Artifact | Files saved from a workflow run | Run से सहेजी गई files |
| `name` | Exact artifact to download | कौन सा artifact |
| `pattern` | Glob to select many artifacts | कई artifacts चुनने का pattern |
| `merge-multiple` | Put all into one folder | सब एक folder में मिलाना |
| `run-id` | Run to read artifacts from | किस run से पढ़ना |
| Retention | How long artifact is kept | कितने दिन रखा जाए |

---

## ⚡ 3-Line Summary
English: Jobs have separate machines, so download-artifact brings earlier job files to the current job.
English: Use `name` for one artifact, `pattern`/`merge-multiple` for many; keep upload and download on v4.
English: Build once, deploy the same bytes, and never put secrets inside artifacts.
Hindi: Jobs की machines अलग होती हैं, इसलिए download-artifact पुराने job की files लाता है।
Hindi: एक के लिए `name`, कई के लिए `pattern`/`merge-multiple`; upload और download दोनों v4 रखें।
Hindi: एक बार build, वही bytes deploy, और artifacts में secrets कभी न रखें।

---

## ➡️ Next Topic
**285. Caching in GitHub Actions** — artifacts move build output between jobs; caching speeds up repeated dependency downloads across runs.
