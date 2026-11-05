# 405. Nginx Config Management in CI/CD
# हिंदी में: CI/CD में Nginx Config Management

---

## 🔵 Simple Definition (English)
**Nginx config management in CI/CD** means treating Nginx configuration as code: it lives in Git, every change goes through a pull request, a pipeline validates it with `nginx -t` (and lint/security checks), and only validated config is shipped to the server and reloaded.

## 🔵 सरल परिभाषा (Hindi)
**CI/CD में Nginx config management** मतलब Nginx configuration को code की तरह रखना: Git में रहे, हर बदलाव pull request से जाए, pipeline `nginx -t` (और lint/security checks) से जाँचे, और सिर्फ validated config server पर भेजकर reload हो।

---

## 🔴 Problem it Solves
- Hand-edited configs drift between servers; nobody knows who changed `proxy_read_timeout` and why.
- A typo applied live can take every site down.
- No review, no rollback, no audit trail.
- Environment-specific values (domains, upstream names) get copy-pasted and diverge.

## 🔴 यह क्यों बना? (Hindi)
- हाथ से edit की config servers के बीच drift करती है; किसने `proxy_read_timeout` बदला और क्यों, कोई नहीं जानता।
- Live लगाई गई एक typo सारी sites गिरा सकती है।
- न review, न rollback, न audit trail।
- Environment-specific values (domain, upstream) copy-paste होकर अलग-अलग हो जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Repo layout: nginx/nginx.conf, nginx/conf.d/*.conf.template
Step 2 → Developer edits config on a branch, opens PR
Step 3 → CI job: render templates (envsubst) -> run `nginx -t` in the
         same image tag used in prod -> optional gixy/lint
Step 4 → Review + merge to main
Step 5 → CD job: copy config to VPS (rsync/scp or build image) ->
         run `nginx -t` on server -> `nginx -s reload`
Step 6 → If test fails, keep old config (nothing reloaded); if
         post-deploy smoke test fails, roll back to previous commit
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Repo layout: nginx/nginx.conf, nginx/conf.d/*.conf.template
Step 2 → Developer branch पर config बदलता है, PR खोलता है
Step 3 → CI job: templates render (envsubst) -> prod वाले ही image tag में
         `nginx -t` चलाओ -> optional gixy/lint
Step 4 → Review + main में merge
Step 5 → CD job: config VPS पर भेजो (rsync/scp या image build) ->
         server पर `nginx -t` -> `nginx -s reload`
Step 6 → Test fail हो तो पुरानी config रहती है (कुछ reload नहीं); deploy के बाद
         smoke test fail हो तो पिछले commit पर rollback
```

---

## 🟡 Real World Example
A team pushes a PR that changes `client_max_body_size` for an upload API. CI renders the template for production, runs `nginx -t` in `nginx:1.27-alpine`, and posts the result on the PR. Reviewer asks for a limit of 20m instead of 200m. After merge, the deploy job syncs the file to the Hostinger VPS and reloads Nginx with zero dropped connections. Three weeks later someone asks "why 20m?" and Git blame answers it.

## 🟡 Real Example Hindi mein
Team एक PR भेजती है जो upload API के लिए `client_max_body_size` बदलता है। CI production के लिए template render करता है, `nginx:1.27-alpine` में `nginx -t` चलाता है और नतीजा PR पर दिखाता है। Reviewer 200m की जगह 20m माँगता है। Merge के बाद deploy job file Hostinger VPS पर sync करके बिना कोई connection गिराए Nginx reload करता है। तीन हफ्ते बाद कोई पूछे "20m क्यों?", तो Git blame जवाब देता है।

---

## 💻 Code / Config Example — Basic

```bash
# scripts/test-nginx.sh -- local/CI validation of the config tree
set -euo pipefail                                   # stop on any error/undefined var

IMAGE="nginx:1.27-alpine"                           # same tag as production (example)
export DOMAIN="app.example.com"                     # values the template needs
export API_UPSTREAM="api:3000"

mkdir -p build/conf.d                               # output folder for rendered files
for f in nginx/conf.d/*.template; do                # every template
  out="build/conf.d/$(basename "${f%.template}")"   # drop .template suffix
  envsubst '${DOMAIN} ${API_UPSTREAM}' < "$f" > "$out"  # replace ONLY listed vars
done                                                # (so nginx's own $host stays intact)

docker run --rm \
  -v "$PWD/nginx/nginx.conf:/etc/nginx/nginx.conf:ro" \
  -v "$PWD/build/conf.d:/etc/nginx/conf.d:ro" \
  --add-host api:127.0.0.1 \
  "$IMAGE" nginx -t                                 # syntax test; exit != 0 on error
# --add-host api:127.0.0.1 : fake DNS so "host not found in upstream" does not fail the test
```

```nginx
# nginx/conf.d/site.conf.template -- uses ${DOMAIN} and ${API_UPSTREAM}
server {
    listen 80;                                      # HTTP
    server_name ${DOMAIN};                          # replaced by envsubst
    location / {
        proxy_pass http://${API_UPSTREAM};          # replaced by envsubst
        proxy_set_header Host $host;                # $host is NOT replaced (not in the list)
    }
}
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/nginx-config.yml -- validate on PR, deploy on main
name: nginx-config                                   # workflow name in Actions UI

on:
  pull_request:
    paths: ["nginx/**"]                              # run only when nginx files change
  push:
    branches: [main]
    paths: ["nginx/**"]

concurrency:
  group: nginx-deploy                                # one deploy at a time
  cancel-in-progress: false                          # never cancel a running deploy

jobs:
  validate:
    runs-on: ubuntu-latest                           # GitHub-hosted runner
    steps:
      - uses: actions/checkout@v4                    # get the repo (example version)
      - name: Render templates and test with nginx -t
        run: bash scripts/test-nginx.sh              # script from the Basic example
      - name: Lint with gixy (security misconfig scanner)
        run: |
          python3 -m pip install --user gixy        # pip package name; see gixy docs
          ~/.local/bin/gixy nginx/nginx.conf || true # advisory: remove "|| true" to enforce

  deploy:
    needs: validate                                  # only after validation passed
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production                          # can require manual approval
    steps:
      - uses: actions/checkout@v4
      - name: Setup SSH key
        run: |
          install -m 700 -d ~/.ssh                   # create .ssh with safe perms
          echo "${{ secrets.VPS_SSH_KEY }}" > ~/.ssh/id_ed25519   # private key from secret
          chmod 600 ~/.ssh/id_ed25519
          ssh-keyscan -H "${{ secrets.VPS_HOST }}" >> ~/.ssh/known_hosts  # trust host key
      - name: Sync config to server
        run: |
          rsync -az --delete nginx/ "deploy@${{ secrets.VPS_HOST }}:/opt/app/nginx.new/"
      - name: Test and swap on server
        run: |
          ssh deploy@"${{ secrets.VPS_HOST }}" 'bash -s' <<'EOF'
          set -euo pipefail
          cd /opt/app
          # keep a backup for rollback
          rm -rf nginx.prev && cp -a nginx nginx.prev
          # test NEW config inside the running nginx image before switching
          docker run --rm -v /opt/app/nginx.new:/etc/nginx:ro \
            --add-host api:127.0.0.1 nginx:1.27-alpine nginx -t
          # switch and reload gracefully
          rm -rf nginx && mv nginx.new nginx
          docker compose exec -T nginx nginx -s reload
          # smoke test; roll back if it fails
          curl -fsS https://app.example.com/healthz || {
            rm -rf nginx && mv nginx.prev nginx
            docker compose exec -T nginx nginx -s reload
            exit 1
          }
          EOF
```

Notes: workflow and shell were YAML/`bash -n` checked; not run against a real VPS. Action versions, the `gixy` usage and the paths are examples. Prefer a dedicated deploy user and restrict its key to needed commands. If config is mounted from `/opt/app/nginx`, the compose mount must point at that path.

---

## 🟠 My Stack Integration
Your repo can hold `api/`, `fastapi/`, `web/` and `nginx/` together; a `paths:` filter means Nginx-only changes redeploy only Nginx. For the Hostinger VPS use SSH + rsync as above; for AWS use an S3 sync + SSM Run Command or bake config into an image pushed to ECR.

```yaml
# Option: bake config into an image (immutable) -- nginx/Dockerfile
# FROM nginx:1.27-alpine
# COPY nginx.conf /etc/nginx/nginx.conf          # main config
# COPY conf.d/ /etc/nginx/conf.d/                # site configs
# RUN nginx -t                                   # build FAILS if config is invalid
```

Security: SSH keys live in GitHub Secrets/environment secrets, deploy user is non-root, `known_hosts` pinned, branch protection on `main`, CODEOWNERS for `nginx/**`, no TLS private keys in the repo.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `envsubst < template` without a variable list, which wipes `$host`, `$uri` and others.
✅ Correct: `envsubst '${DOMAIN} ${API_UPSTREAM}'` with an explicit list.

❌ Mistake 2: `nginx -t` fails in CI with "host not found in upstream" because backends are not running.
✅ Correct: Add `--add-host` entries, or use runtime resolution with `resolver`.

❌ Mistake 3: Using `restart` after deploy.
✅ Correct: `nginx -t` then `nginx -s reload`; keep the previous config for rollback.

❌ Mistake 4: Testing with a different Nginx version than production.
✅ Correct: Use the same pinned tag in CI and on the server.

---

## 🧠 Tricky Interview Question
CI is green (`nginx -t` OK), but after deploy the site returns 404 for every API call. How is that possible?

Answer: `nginx -t` checks syntax and file references, not behaviour. A wrong `location` order, a missing trailing slash in `proxy_pass`, or wrong upstream name is syntactically valid. Add post-deploy smoke tests (`curl` key endpoints), staging deploys, and config unit tests; and automate rollback when the smoke test fails.

---

## ⚫ Interview Questions + Answers

Q1: Why is `nginx -t` not enough?
A1: It validates syntax and includes, not routing correctness or upstream availability. Pair it with smoke tests.

Q2: Template vs baked vs mounted config?
A2: Templates (envsubst) handle per-environment values; baked images give immutability and easy rollback by tag; mounts give quick changes without rebuild.

Q3: How do you roll back?
A3: Redeploy the previous Git commit/image tag, or restore the saved `nginx.prev` directory and reload. Automated on smoke-test failure.

Q4: How do you stop two pipelines racing?
A4: `concurrency` group in GitHub Actions and an `environment` with approval.

Q5: What security checks can run in CI?
A5: Gixy for misconfigurations, secret scanning (gitleaks), checking no `autoindex on`, TLS versions, and required headers via grep rules.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one person or server touches Nginx config.
- You want audits, PR reviews and repeatable rollbacks.

❌ Avoid when:
- A throwaway single-developer lab (still keep it in Git, but a full pipeline is overkill).

---

## 📊 Visual Diagram
```
 Dev -> PR -> [CI: envsubst -> nginx -t -> gixy] -> review -> merge main
                                                         |
                                                         v
                                            [CD: rsync to VPS]
                                                         |
                                       nginx -t (on server, new dir)
                                          | ok                | fail
                                          v                   v
                                  swap + nginx -s reload   abort, keep old
                                          |
                                   smoke test (curl /healthz)
                                     | ok            | fail
                                     v               v
                                   done      restore nginx.prev + reload
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Config as code | Config stored/reviewed in Git | code की तरह config |
| `envsubst` | Replace `${VAR}` in files | variables भरने का tool |
| Drift | Servers differ from Git | server और Git में फर्क |
| Smoke test | Quick post-deploy check | जल्दी की जाँच |
| Rollback | Return to previous good state | पिछली स्थिति पर वापसी |
| CODEOWNERS | Required reviewers per path | path के मालिक reviewers |

---

## ⚡ 3-Line Summary
English: Keep Nginx config in Git, render templates, validate with `nginx -t` in the prod image.
Deploy only after green CI, reload gracefully, smoke test, and auto-rollback on failure.
Protect secrets, pin versions and serialise deploys.
Hindi: Nginx config Git में रखो, templates render करो, prod image में `nginx -t` से जाँचो।
CI green होने पर ही deploy करो, gracefully reload करो, smoke test करो, fail पर auto-rollback।
Secrets सुरक्षित रखो, versions pin करो और deploys एक-एक करके चलाओ।

---

## ➡️ Next Topic
406. Let's Encrypt in Docker - automate free, renewing certificates for the config you now manage.
