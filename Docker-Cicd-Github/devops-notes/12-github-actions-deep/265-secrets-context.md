# 265. secrets Context
# हिंदी में: secrets Context

---

## 🔵 Simple Definition (English)
The `secrets` context gives access to encrypted values stored at organization, repository or environment level, read as `${{ secrets.NAME }}`. Values are masked in logs, write-only in the UI, and not passed to workflows triggered from forks (except the automatic `GITHUB_TOKEN`).

## 🔵 सरल परिभाषा (Hindi)
`secrets` context organization, repository या environment level पर रखी encrypted values का access देता है, जिन्हें `${{ secrets.NAME }}` से पढ़ते हैं। Values logs में masked होती हैं, UI में write-only होती हैं, और fork से trigger हुए workflows को नहीं मिलतीं (automatic `GITHUB_TOKEN` को छोड़कर)।

---

## 🔴 Problem it Solves
Pipelines need passwords, SSH keys, cloud keys and API tokens. Committing them to Git leaks them forever (bots scan GitHub within minutes). Typing them in each job is unmanageable. `secrets` stores them encrypted, injects them only at run time, redacts them from logs and restricts who can read them.

## 🔴 यह क्यों बना? (Hindi)
Pipelines को passwords, SSH keys, cloud keys और API tokens चाहिए। इन्हें Git में commit करने से वे हमेशा के लिए leak हो जाते हैं (bots कुछ ही मिनटों में GitHub scan करते हैं)। हर job में हाथ से डालना संभव नहीं। `secrets` इन्हें encrypted रखता है, सिर्फ run time पर inject करता है, logs से छुपाता है और read access सीमित करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Admin adds secret (UI, gh secret set, or API); stored encrypted (libsodium sealed box)
Step 2 → Workflow runs; secrets are sent to the runner only for jobs that reference them
Step 3 → ${{ secrets.NAME }} is substituted in env:/with:/run: (not in if:)
Step 4 → Runner registers the value as a mask: matching text in logs becomes ***
Step 5 → Job ends; runner is destroyed (hosted) so the value does not persist
Step 6 → Fork PRs, Dependabot (separate secrets store) and reusable workflows have special rules
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Admin secret जोड़ता है (UI, gh secret set, या API); encrypted store होता है
Step 2 → Workflow चलता है; secrets सिर्फ उन jobs के runner को जाते हैं जो उन्हें refer करते हैं
Step 3 → ${{ secrets.NAME }} env:/with:/run: में replace होता है (if: में नहीं)
Step 4 → Runner value को mask register करता है: logs में वही text *** बन जाता है
Step 5 → Job खत्म; runner नष्ट (hosted) इसलिए value बची नहीं रहती
Step 6 → Fork PRs, Dependabot (अलग secrets store) और reusable workflows के खास नियम हैं
```

---

## 🟡 Real World Example
Your pipeline pushes to Docker Hub (`DOCKERHUB_TOKEN`), deploys to a VPS (`VPS_SSH_KEY`) and hits Razorpay test APIs in e2e tests (`RAZORPAY_TEST_SECRET`). Production keys live in the `production` environment with required reviewers, so a feature-branch job can never read them. When a developer leaves, you rotate `VPS_SSH_KEY` in one place.

## 🟡 Real Example Hindi mein
आपकी pipeline Docker Hub पर push करती है (`DOCKERHUB_TOKEN`), VPS पर deploy करती है (`VPS_SSH_KEY`) और e2e tests में Razorpay test APIs hit करती है (`RAZORPAY_TEST_SECRET`)। Production keys `production` environment में required reviewers के साथ हैं, इसलिए feature-branch का job उन्हें पढ़ नहीं सकता। Developer के जाने पर `VPS_SSH_KEY` एक जगह rotate कर देते हैं।

---

## 💻 Code / Config Example — Basic
```bash
# Create secrets with the GitHub CLI (run locally, not in CI)
gh secret set DOCKERHUB_TOKEN --repo acme/orders-api          # prompts for value, stored encrypted
gh secret set VPS_SSH_KEY --repo acme/orders-api < ~/.ssh/deploy_ed25519   # read key from file
gh secret set DB_PASSWORD --env production --repo acme/orders-api          # environment-scoped secret
gh secret list --repo acme/orders-api                          # shows names only, never values
```
```yaml
# .github/workflows/secrets-basic.yml
name: secrets-basic                    # workflow name
on: workflow_dispatch                  # manual
jobs:
  login:
    runs-on: ubuntu-24.04              # example runner
    steps:
      - name: Login to Docker Hub      # secret passed through env, read by shell as data
        env:
          DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}   # scoped to this step
        run: echo "$DOCKERHUB_TOKEN" | docker login -u acme --password-stdin   # stdin keeps it out of ps/history
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/secrets-advanced.yml
name: secure-deploy                    # production grade secret handling
on:
  push:
    branches: [main]                   # deploy from main only
permissions:
  contents: read                       # minimal token
jobs:
  deploy:
    runs-on: ubuntu-24.04              # example runner
    environment: production            # unlocks production secrets + approvals
    steps:
      - uses: actions/checkout@v4      # source
      - name: Fail early if secret missing   # secrets cannot be used in if:, so map to env
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}   # may be empty on fork/no access
        run: |                         # shell
          test -n "$SSH_KEY" || { echo "VPS_SSH_KEY not set"; exit 1; }   # explicit check, no value printed
      - name: Prepare SSH              # write key safely
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}       # step-scoped
          KNOWN_HOSTS: ${{ vars.VPS_KNOWN_HOSTS }}  # host key fingerprint line (public data)
        run: |                         # shell
          set -euo pipefail            # strict mode
          umask 077                    # new files private
          mkdir -p ~/.ssh              # ssh dir
          printf '%s\n' "$SSH_KEY" > ~/.ssh/id_ed25519      # key file, never echoed
          printf '%s\n' "$KNOWN_HOSTS" > ~/.ssh/known_hosts # pin host key (prevents MITM)
      - name: Mask a derived value     # derived secrets are NOT auto-masked
        env:
          RAW: ${{ secrets.API_TOKEN }} # base token
        run: |                         # shell
          B64=$(printf '%s' "$RAW" | base64)   # transformed value
          echo "::add-mask::$B64"      # register mask for the derived string
      - name: Deploy                   # run deploy
        run: ssh deploy@"${{ vars.VPS_HOST }}" 'cd /srv/app && docker compose pull && docker compose up -d'   # remote deploy
  call-reusable:
    needs: deploy                      # run after deploy
    uses: acme/shared-workflows/.github/workflows/notify.yml@v1   # example reusable workflow
    secrets: inherit                   # pass all caller secrets (or list them explicitly)
```
YAML parsed locally; not executed on GitHub. The reusable workflow path is a placeholder. `secrets:` alongside `uses:` is valid only at job level for reusable workflow calls.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: DB URL, JWT secret, Razorpay keys live in secrets; the app on the VPS reads its own `.env` created from them, not from the repo.
- **React**: never put secrets in `VITE_*`; they are bundled into public JS.
- **Nginx/VPS**: SSH deploy key with `command=` restriction in `authorized_keys`, TLS private keys stay on the server.
- **AWS**: prefer OIDC (`id-token: write` + role) over `AWS_SECRET_ACCESS_KEY` secrets.
- **Rotation**: `gh secret set` in a script after rotating; pair with expiry reminders.

```yaml
      - name: Write .env on VPS from secrets   # create runtime config remotely
        env:
          DB_URL: ${{ secrets.DATABASE_URL }}  # from secrets
        run: ssh deploy@"$HOST" "umask 077; cat > /srv/app/.env" <<< "DATABASE_URL=$DB_URL"   # file mode 600
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `if: secrets.X != ''`.
✅ Correct: Secrets are not available in `if:`; map to `env:` and test `env.X`, or check inside a script.

❌ Mistake 2: Printing secrets "to verify" (`echo $SECRET | base64`).
✅ Correct: Masking only catches exact matches; encoded forms leak. Verify length with `${#SECRET}` instead.

❌ Mistake 3: Storing a multi-line private key but losing newlines.
✅ Correct: Upload from file with `gh secret set NAME < key`; write it with `printf '%s\n'`.

❌ Mistake 4: Using `pull_request_target` and checking out PR code with secrets available.
✅ Correct: Use `pull_request` for untrusted code; never run fork code with secrets.

❌ Mistake 5: Passing secrets in command-line args (`--password $PW`).
✅ Correct: Use stdin or env; args show up in process lists.

---

## 🧠 Tricky Interview Question
A secret `TOKEN=abc123` is masked in logs. A step runs `echo ${TOKEN:0:3} ${TOKEN:3}` and the log shows `abc 123`. Why, and how do you prevent it?

Answer: Masking is exact string matching on the full value. Printing parts (or encoded/split forms) bypasses it. Prevention: never print secrets, restrict who can edit workflows (a malicious PR to a workflow can exfiltrate), require environment approvals, use OIDC short-lived credentials, and rotate if exposure is suspected. Registering derived values with `::add-mask::` helps only for values you know.

---

## ⚫ Interview Questions + Answers

Q1: Where can secrets be defined?
A1: Organization, repository and environment levels; also separate Dependabot and Codespaces secrets.

Q2: Are secrets passed to forked PR workflows?
A2: No (only a read-only `GITHUB_TOKEN`) for `pull_request`. This blocks theft by malicious forks.

Q3: How do reusable workflows get secrets?
A3: Via `secrets:` (explicit mapping) or `secrets: inherit` in the caller job.

Q4: Size limit?
A4: About 48 KB per secret; for larger content encrypt a file with GPG and store the passphrase as the secret.

Q5: How to avoid long-lived cloud keys?
A5: OIDC federation: the job gets a short-lived token from GitHub and exchanges it for temporary cloud credentials.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Passwords, tokens, SSH/API keys, certificates
- Values that must not appear in repo or UI
- Gating production credentials behind environments

❌ Avoid when:
- Non-sensitive config (use `vars`)
- Supporting fork PRs (they cannot read them)
- Long-lived cloud keys when OIDC is available

---

## 📊 Visual Diagram
```
 Org secrets -----+
 Repo secrets ----+--> job references ${{ secrets.X }} --> sent to runner (encrypted channel)
 Env secrets -----+       (env needs environment: key + approvals)
                                   |
                                   v
                      runner: value used in step process
                      logs: exact value replaced by ***
                                   |
                         job ends -> runner discarded
 Fork PR (pull_request) ---------> NO secrets (read-only token only)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Secret | Encrypted credential | Encrypted credential |
| Masking | Replacing value with *** | Value को *** से बदलना |
| OIDC | Short-lived token federation | Short-lived token federation |
| Rotation | Replacing old credential | पुराना credential बदलना |
| secrets: inherit | Pass all secrets to reusable workflow | सारे secrets reusable workflow को देना |

---

## ⚡ 3-Line Summary
English: `secrets` stores encrypted credentials, masked in logs, hidden from fork PRs.
Scope them per step/environment, never print them, never use them in `if:` directly.
Prefer OIDC over long-lived keys and rotate regularly.
Hindi: `secrets` encrypted credentials रखता है, logs में masked और fork PRs से छुपा।
उन्हें step/environment के हिसाब से scope करो, print मत करो, `if:` में सीधे मत इस्तेमाल करो।
Long-lived keys की जगह OIDC चुनो और नियमित rotate करो।

---

## ➡️ Next Topic
**266. needs Context** — reading results and outputs of the jobs your job depends on.
