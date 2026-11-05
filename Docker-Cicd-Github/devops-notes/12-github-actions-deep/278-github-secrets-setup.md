# 278. GitHub Secrets Setup
# हिंदी में: GitHub Secrets Setup (बनाना और इस्तेमाल करना)

---

## 🔵 Simple Definition (English)
Setting up a repository secret means adding a name/value pair at **Settings > Secrets and variables > Actions > New repository secret** (or with `gh secret set`). After that any workflow in that repository can use it as `${{ secrets.NAME }}`.

## 🔵 सरल परिभाषा (Hindi)
Repository secret setup का मतलब है **Settings > Secrets and variables > Actions > New repository secret** में name/value जोड़ना (या `gh secret set` से)। उसके बाद उस repository का कोई भी workflow इसे `${{ secrets.NAME }}` की तरह use कर सकता है।

---

## 🔴 Problem it Solves
Teams know secrets must not be in git but do not know the practical steps: where to click, how to store a multi-line SSH key without breaking newlines, how to script it for many repos, and how to rotate. Wrong setup (extra spaces, missing newline, wrong name) is the most common reason for "Permission denied (publickey)" in CI.

## 🔴 यह क्यों बना? (Hindi)
Teams जानती हैं कि secrets git में नहीं होने चाहिए, पर practical steps नहीं पता: कहाँ click करना है, multi-line SSH key को newlines बिगाड़े बिना कैसे store करें, कई repos के लिए script कैसे बनाएँ, rotate कैसे करें। गलत setup (extra spaces, newline गायब, गलत नाम) CI में "Permission denied (publickey)" का सबसे आम कारण है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Generate a dedicated deploy key:  ssh-keygen -t ed25519 -f deploy_key -N ""
Step 2 → Put deploy_key.pub into the VPS ~/.ssh/authorized_keys of user "deploy"
Step 3 → GitHub repo > Settings > Secrets and variables > Actions
Step 4 → New repository secret > Name: VPS_SSH_KEY > paste FULL private key
         (including BEGIN/END lines and trailing newline) > Add secret
Step 5 → Add VPS_HOST, VPS_USER (or as Variables), VPS_KNOWN_HOSTS
Step 6 → Reference as ${{ secrets.VPS_SSH_KEY }} in workflow, delete local private key copy
```

Names: letters, digits, underscore; cannot start with a digit or `GITHUB_`; case-insensitive in reference, stored uppercase.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Dedicated deploy key बनाओ:  ssh-keygen -t ed25519 -f deploy_key -N ""
Step 2 → deploy_key.pub को VPS पर user "deploy" की ~/.ssh/authorized_keys में डालो
Step 3 → GitHub repo > Settings > Secrets and variables > Actions
Step 4 → New repository secret > Name: VPS_SSH_KEY > पूरी private key paste करो
         (BEGIN/END lines और आखिरी newline समेत) > Add secret
Step 5 → VPS_HOST, VPS_USER (या Variables), VPS_KNOWN_HOSTS भी जोड़ो
Step 6 → Workflow में ${{ secrets.VPS_SSH_KEY }} से use करो, local private key की copy delete करो
```

Names: letters, digits, underscore; digit या `GITHUB_` से शुरू नहीं हो सकते।

---

## 🟡 Real World Example
A startup deploys a Node.js API to a DigitalOcean/EC2 VPS. The founder creates a limited `deploy` Linux user with docker group access, generates an ed25519 key just for GitHub, adds the public half to the server, and stores the private half as `VPS_SSH_KEY`. When an engineer leaves, they only remove one line from `authorized_keys` and rotate the secret.

## 🟡 Real Example Hindi mein
एक startup अपना Node.js API DigitalOcean/EC2 VPS पर deploy करता है। Founder docker group वाला limited `deploy` Linux user बनाता है, सिर्फ GitHub के लिए ed25519 key बनाता है, public हिस्सा server में जोड़ता है और private हिस्सा `VPS_SSH_KEY` में रखता है। कोई engineer जाए तो सिर्फ `authorized_keys` की एक line हटानी और secret rotate करना होता है।

---

## 💻 Code / Config Example — Basic
```bash
# --- run on your laptop (needs GitHub CLI: gh auth login) ---
ssh-keygen -t ed25519 -C "gha-deploy" -f ./deploy_key -N ""   # new key pair, no passphrase (CI cannot type one)

# copy the PUBLIC key to the server's deploy user
ssh-copy-id -i ./deploy_key.pub deploy@203.0.113.10           # example IP (documentation range)

# store PRIVATE key as a repository secret; < reads file content incl. newlines
gh secret set VPS_SSH_KEY < ./deploy_key                      # prompts nothing, reads stdin
gh secret set VPS_HOST --body "203.0.113.10"                  # simple value via --body
ssh-keyscan -t ed25519 203.0.113.10 > known_hosts.txt         # host fingerprint (verify manually!)
gh secret set VPS_KNOWN_HOSTS < known_hosts.txt               # pin server identity

shred -u ./deploy_key 2>/dev/null || rm -P ./deploy_key       # delete local private key (Linux / macOS)

gh secret list                                                # shows names + updated time, never values
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/deploy-vps.yml
name: deploy-vps                       # workflow name
on:
  push:
    branches: [main]                   # deploy on main
  workflow_dispatch:                   # allow manual re-run

concurrency:
  group: deploy-prod                   # never run two deploys together
  cancel-in-progress: false            # queue instead of killing a running deploy

permissions:
  contents: read                       # minimum token scope

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 15                # stop hung SSH sessions
    steps:
      - name: Validate required secrets exist
        env:
          HAS_KEY: ${{ secrets.VPS_SSH_KEY != '' }}     # boolean string, value never printed
          HAS_HOST: ${{ secrets.VPS_HOST != '' }}
        run: |
          [ "$HAS_KEY" = "true" ] || { echo "VPS_SSH_KEY missing"; exit 1; }   # fail early
          [ "$HAS_HOST" = "true" ] || { echo "VPS_HOST missing"; exit 1; }
      - name: Prepare SSH
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}
          KNOWN_HOSTS: ${{ secrets.VPS_KNOWN_HOSTS }}
        run: |
          install -m 700 -d ~/.ssh
          printf '%s\n' "$SSH_KEY" > ~/.ssh/id_ed25519
          chmod 600 ~/.ssh/id_ed25519
          printf '%s\n' "$KNOWN_HOSTS" > ~/.ssh/known_hosts
      - name: Deploy and health check
        env:
          HOST: ${{ secrets.VPS_HOST }}
        run: |
          ssh -o StrictHostKeyChecking=yes deploy@"$HOST" \
            "cd /srv/app && git pull --ff-only && docker compose up -d --build"   # update app
          curl --fail --retry 5 --retry-delay 3 "https://api.example.com/health"  # via Nginx
```
Not run locally; shell blocks syntax-checked, YAML parsed. `gh secret set` options (`--body`, `--env`, `--org`, `--repos`) are real; verify with `gh secret set --help` for your version.

---

## 🟠 My Stack Integration
Recommended secrets for your stack: `VPS_SSH_KEY`, `VPS_HOST`, `VPS_KNOWN_HOSTS`, `DOCKERHUB_TOKEN`; app runtime values (DATABASE_URL, JWT_SECRET) stay in `/srv/app/.env` on the VPS (chmod 600) or AWS SSM Parameter Store. Nginx never sees them; it only proxies to Node.js/FastAPI.

```yaml
# snippet: write runtime .env on VPS from secrets (alternative to manual edit)
      - name: Update remote .env
        env:
          JWT_SECRET: ${{ secrets.JWT_SECRET }}
          DB_URL: ${{ secrets.DATABASE_URL }}
        run: |
          printf 'JWT_SECRET=%s\nDATABASE_URL=%s\n' "$JWT_SECRET" "$DB_URL" | \
            ssh deploy@"${{ secrets.VPS_HOST }}" "umask 077 && cat > /srv/app/.env"
          # umask 077 makes the file readable only by the deploy user
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Pasting the key without the `-----END ...-----` line or with extra indentation.
✅ Correct: Use `gh secret set NAME < file` to avoid copy-paste errors.

❌ Mistake 2: Using your personal SSH key for CI.
✅ Correct: Dedicated deploy key, limited user, revoke independently.

❌ Mistake 3: `StrictHostKeyChecking=no` or `ssh-keyscan` at deploy time without verification.
✅ Correct: Pin host key once in `VPS_KNOWN_HOSTS`.

❌ Mistake 4: Secret name typo (`VPS_SSH_KEY` vs `VPS_SSHKEY`): value silently becomes empty.
✅ Correct: Add a validation step like above.

❌ Mistake 5: Forgetting that Dependabot PRs use a separate "Dependabot secrets" store.
✅ Correct: Add the secret under Settings > Secrets > Dependabot if those runs need it.

---

## 🧠 Tricky Interview Question
You rotated `DOCKERHUB_TOKEN` in the UI but the old workflow run is still using the old token. Why?

Answer: Secret values are resolved when a job starts. A run already in progress (or a re-run of an older attempt) keeps the value it received at start; and for a re-run, GitHub re-reads current secrets only for a fresh job start. Always revoke the old token at the provider (Docker Hub) too; updating GitHub alone does not invalidate it.

---

## ⚫ Interview Questions + Answers

Q1: Where do you add repository secrets?
A1: Settings > Secrets and variables > Actions > New repository secret, or `gh secret set`.

Q2: Can you edit a secret's value?
A2: You can overwrite it, never view it.

Q3: Do secrets exist for pull requests from forks?
A3: No (except `GITHUB_TOKEN` with read-only), unless you use risky triggers.

Q4: Difference between repository secret and environment secret?
A4: Repository secrets are available to all jobs; environment secrets only to jobs that reference that environment (and pass its protection rules).

Q5: How do you list secrets?
A5: `gh secret list` shows names and update times only.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You must give CI a credential that is not public.
- You want per-repo control and easy rotation.

❌ Avoid when:
- Dozens of repos share the same value (use organization secrets).
- Different environments need different values with approvals (use environment secrets).

---

## 📊 Visual Diagram
```
 laptop                       GitHub                         VPS
 ssh-keygen
   |-- deploy_key.pub --------------------------------> authorized_keys
   |-- deploy_key (private) --gh secret set--> [VPS_SSH_KEY]
                                   |
                              workflow run
                                   | ssh -i key deploy@host
                                   +-----------------------> docker compose up -d
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Repository secret | Secret usable by one repo | एक repo का secret |
| Deploy key | SSH key used only for deployment | सिर्फ deploy के लिए SSH key |
| known_hosts | Trusted server fingerprints | Trusted server fingerprints |
| gh secret set | CLI to create secrets | Secret बनाने की CLI |
| Dependabot secrets | Separate store for Dependabot runs | Dependabot के लिए अलग store |

---

## ⚡ 3-Line Summary
English: Add secrets in Settings or with `gh secret set NAME < file`.
Use a dedicated deploy key, pin known_hosts, validate that secrets exist.
Revoke old credentials at the provider when rotating.

Hindi: Secrets Settings में या `gh secret set NAME < file` से जोड़ो।
Dedicated deploy key use करो, known_hosts pin करो, और जाँचो कि secrets मौजूद हैं।
Rotate करते समय provider पर पुरानी credential भी revoke करो।

---

## ➡️ Next Topic
**279. Organization Secrets** — share one secret across many repositories with access policies.
