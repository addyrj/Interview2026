# 227. Image Promotion Strategy
# हिंदी में: Image Promotion Strategy (Build Once, Promote Many)

---

## 🔵 Simple Definition (English)
**Image promotion** means you build a Docker image **once**, then move that exact same image (same digest) through environments: dev, staging, production. Promotion is only re-tagging or copying the image after it passes tests and approvals. You never rebuild for each environment; environment differences come from configuration and secrets at runtime.

## 🔵 सरल परिभाषा (Hindi)
**Image promotion** का मतलब है कि आप Docker image **एक बार** build करते हो, फिर वही image (वही digest) dev, staging, production से गुज़ारते हो। Promotion सिर्फ tests और approvals के बाद re-tag या copy करना है। हर environment के लिए दोबारा build नहीं करते; environment के फर्क runtime पर configuration और secrets से आते हैं।

---

## 🔴 Problem it Solves
If you rebuild per environment (`docker build` on the staging branch, again on main), the production image is not the one you tested. Different dependency versions (`npm install` resolved a newer package), a changed base image, or a flaky build step can slip in. Classic outcome: "it passed staging but failed in production" or "we can't reproduce the production image". Promotion gives traceability, speed (no rebuild), and confidence that what was tested is what ships.

## 🔴 यह क्यों बना? (Hindi)
अगर आप हर environment के लिए rebuild करते हो (staging branch पर `docker build`, फिर main पर दोबारा), तो production image वह नहीं जो test हुई थी। अलग dependency versions (`npm install` ने नया package उठा लिया), बदली base image, या flaky build step घुस सकता है। नतीजा: "staging में पास, production में fail" या "production image दोबारा बन नहीं पा रही"। Promotion traceability, speed (rebuild नहीं) और भरोसा देता है कि जो test हुआ वही ship हुआ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Commit merged -> CI builds ONE image, tags it  app:sha-abc1234, pushes, records the digest.
Step 2 → Auto-deploy that digest to DEV; run smoke tests.
Step 3 → Tests pass -> promote: add tag  app:staging  (same digest, no rebuild). Deploy to STAGING.
Step 4 → Integration/E2E/performance tests + security scan run against staging.
Step 5 → Human approval (GitHub Environment protection rule) -> promote: add tag app:v1.4.2 and app:prod.
Step 6 → Deploy digest to PRODUCTION. Rollback = redeploy the previous digest/tag.
Rule  → Same digest everywhere. Only config (env vars, secrets, URLs) differs per environment.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Commit merge -> CI ONE image बनाता है, tag app:sha-abc1234, push, और digest record करता है।
Step 2 → वही digest DEV में auto-deploy; smoke tests चलते हैं।
Step 3 → Tests पास -> promote: tag app:staging जोड़ो (वही digest, rebuild नहीं)। STAGING में deploy।
Step 4 → Staging पर integration/E2E/performance tests और security scan।
Step 5 → इंसानी approval (GitHub Environment protection rule) -> promote: app:v1.4.2 और app:prod tag जोड़ो।
Step 6 → वही digest PRODUCTION में deploy। Rollback = पिछला digest/tag दोबारा deploy।
Rule  → हर जगह वही digest। सिर्फ config (env vars, secrets, URLs) environment के हिसाब से बदलता है।
```

---

## 🟡 Real World Example
A payments company had an incident: staging passed, production crashed. Investigation: production was built two hours later from the same Git commit, but `npm install` pulled a patch release of a library that broke date parsing. After moving to promotion, the pipeline builds `payments-api:sha-9f3c2a1` once. The same digest sits in staging for 24 hours of soak tests, then a manager approves, and the tag `prod` is moved. A rollback now takes 30 seconds: redeploy the previous digest. Auditors love it because every production image traces back to one commit and one test report.

## 🟡 Real Example Hindi mein
एक payments company में incident हुआ: staging पास, production crash। जाँच में पता चला कि production दो घंटे बाद उसी Git commit से build हुआ था, पर `npm install` ने एक library का patch release उठा लिया जिसने date parsing तोड़ दी। Promotion अपनाने के बाद pipeline `payments-api:sha-9f3c2a1` एक बार बनाती है। वही digest 24 घंटे staging में soak tests झेलता है, फिर manager approve करता है और `prod` tag आगे बढ़ता है। Rollback अब 30 सेकंड: पिछला digest दोबारा deploy। Auditors को यह पसंद है क्योंकि हर production image एक commit और एक test report तक trace होती है।

---

## 💻 Code / Config Example — Basic

```bash
# Promote WITHOUT rebuilding: re-tag the same image in the registry
REG=ghcr.io/myorg/node-api                       # registry path (example)
SHA=sha-abc1234                                  # tag created by CI at build time

docker pull $REG:$SHA                            # fetch the tested image
docker tag  $REG:$SHA $REG:staging               # same image ID, new label "staging"
docker push $REG:staging                         # registry stores another tag for the SAME digest

# After approval: promote to production
docker tag  $REG:$SHA $REG:v1.4.2                # human-readable release tag
docker tag  $REG:$SHA $REG:prod                  # moving pointer for "what is in prod"
docker push $REG:v1.4.2 && docker push $REG:prod # publish both tags

# Prove it is the same image: digests must be equal
docker buildx imagetools inspect $REG:staging --format '{{.Manifest.Digest}}'   # digest A
docker buildx imagetools inspect $REG:prod    --format '{{.Manifest.Digest}}'   # digest A again
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/pipeline.yml - build once, promote with environment approvals
name: build-promote                              # workflow name
on:
  push:
    branches: [main]                             # every merge to main
env:
  REGISTRY: ghcr.io                              # registry host
  IMAGE: ghcr.io/${{ github.repository }}/node-api   # image path from repo name
jobs:
  build:
    runs-on: ubuntu-latest                       # runner
    permissions:
      contents: read                             # read code
      packages: write                            # push to GHCR
    outputs:
      digest: ${{ steps.push.outputs.digest }}   # pass digest to next jobs
    steps:
      - uses: actions/checkout@v4                # get code (example version)
      - uses: docker/setup-buildx-action@v3      # buildx (example version)
      - uses: docker/login-action@v3             # log in to GHCR
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: push
        uses: docker/build-push-action@v6        # build once and push
        with:
          context: .
          push: true
          tags: ${{ env.IMAGE }}:sha-${{ github.sha }}   # immutable tag per commit
  deploy-staging:
    needs: build                                 # waits for the build
    runs-on: ubuntu-latest
    environment: staging                         # GitHub Environment (secrets, URL for staging)
    steps:
      - name: Deploy digest to staging
        run: |
          echo "Deploying ${IMAGE}@${{ needs.build.outputs.digest }} to staging"   # replace with ssh/ecs deploy
        env:
          IMAGE: ${{ env.IMAGE }}
  promote-prod:
    needs: [build, deploy-staging]               # only after staging succeeded
    runs-on: ubuntu-latest
    environment: production                      # protection rule: required reviewers = manual approval
    permissions:
      packages: write                            # need push for retag
    steps:
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/setup-buildx-action@v3
      - name: Retag the same digest as prod (no rebuild)
        run: |
          docker buildx imagetools create \
            --tag "${{ env.IMAGE }}:prod" \
            "${{ env.IMAGE }}@${{ needs.build.outputs.digest }}"
```

Checked: YAML parses; jobs/steps/uses/run present. `docker buildx imagetools create --tag` copies manifests registry-side without a pull. Not executed on a real runner. / YAML parse हुआ; असली runner पर नहीं चलाया।

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: build once in CI; the image has no `.env`. Environment config via Compose `env_file`, AWS SSM Parameter Store or Secrets Manager.
- **React**: build-time env vars (`REACT_APP_*`, `VITE_*`) are baked into the bundle, which breaks "build once". Fix: use runtime config (`/config.js` generated by the Nginx container entrypoint from env vars) or fetch config from the API.
- **Nginx**: bake `nginx.conf.template` into the image and use `envsubst` at start for environment-specific upstreams.
- **VPS**: one Compose file with `image: ...:${TAG}`, per-env `.env.staging`, `.env.prod`.
- **AWS**: ECR tags `staging` and `prod`; ECS task definition references a digest.

```bash
# Nginx image entrypoint snippet: runtime config for React (build once, run anywhere)
cat > /usr/share/nginx/html/config.js <<EOF
window.__CONFIG__ = { API_URL: "${API_URL}", ENV: "${APP_ENV}" };
EOF
# The React app reads window.__CONFIG__.API_URL instead of a build-time constant
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Separate builds for staging and prod branches.
✅ Correct: One build, promote the digest.

❌ Mistake 2: Baking environment config or secrets in the image.
✅ Correct: Inject at runtime (env, secrets manager).

❌ Mistake 3: Using a moving tag (`staging`) as the only record. Tag moves, history lost.
✅ Correct: Record the digest in deploy logs/Git; keep the `sha-` tag.

❌ Mistake 4: Skipping approval for production.
✅ Correct: Protected environment with required reviewers.

❌ Mistake 5: Not scanning before promotion.
✅ Correct: Scan at build and gate the promotion on results.

---

## 🧠 Tricky Interview Question
**Q:** Your React frontend uses `VITE_API_URL` and you "build once, promote". After promotion to production, the app still calls the staging API. Why, and what is the fix?

**Answer:** Vite/CRA replace `VITE_*` variables at build time, so the value is literally inside the JavaScript bundle. Promoting the same image therefore carries the staging URL. Fixes: (1) generate `config.js` at container start from runtime env and load it before the app; (2) use relative URLs (`/api`) and let Nginx proxy to the right backend per environment; (3) as a last resort, build per environment, but then you lose "same artifact" guarantees and must test the production build too.

---

## ⚫ Interview Questions + Answers

Q1: Why promote instead of rebuild?
A1: Identical artifact tested and deployed, faster pipeline, easy rollback, audit trail, reduced "works in staging" surprises.

Q2: How do you make sure two tags are the same image?
A2: Compare digests via `docker buildx imagetools inspect` or `crane digest`. Same digest = same bytes.

Q3: Where does environment-specific config live?
A3: Outside the image: env vars, mounted files, Secrets Manager/SSM, Kubernetes ConfigMaps/Secrets, GitHub Environments.

Q4: How do you roll back?
A4: Redeploy the previous digest/`sha-` tag (kept by lifecycle rules). Database migrations should be backward compatible so rollback is safe.

Q5: Single registry with tags or one registry per environment?
A5: Both work. Tags in one registry are simple. Separate registries/accounts (dev vs prod) improve isolation: CI copies the image with `crane copy` or ECR replication after approval.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have more than one environment (staging + prod)
- Compliance/audit asks for traceability
- You want fast, reliable rollback

❌ Avoid when:
- A hobby app on one VPS (simple build on server is fine)
- Build-time config is unavoidable and you cannot change it (then document the exception)

---

## 📊 Visual Diagram
```
 commit --> CI build ONCE --> app@sha256:9f3c...   (digest never changes)
                                   |
        +--------------------------+--------------------------+
        v                          v                          v
   DEV (auto)              STAGING (tests pass)        PROD (approval)
   tag sha-abc              tag staging                tag prod, v1.4.2
   env: dev config          env: staging config        env: prod config
        \________ same bytes, different config ________/
 Rollback: redeploy previous digest (seconds)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Promotion | Move same image to next stage | वही image अगले stage में |
| Digest | Immutable image hash | Image का hash |
| Artifact | Build output (image) | Build का नतीजा |
| Environment | dev / staging / prod | अलग वातावरण |
| Soak test | Long-running stability test | लंबा stability test |
| Protection rule | Required approval gate | Approval की शर्त |

---

## ⚡ 3-Line Summary
English: Build the image once, promote the same digest through dev, staging and prod.
Keep configuration outside the image and gate production with approval.
Rollback is just redeploying an older digest.

Hindi: Image एक बार build करो, वही digest dev, staging, prod में आगे बढ़ाओ।
Configuration image के बाहर रखो और production पर approval लगाओ।
Rollback यानी पुराना digest दोबारा deploy करना।

---

## ➡️ Next Topic
**228. Blue-Green with Docker** - with a promoted image ready, how do you switch production traffic to it instantly and roll back instantly?
