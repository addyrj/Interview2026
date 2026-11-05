# 279. Organization Secrets
# हिंदी में: Organization Secrets (कई repos में एक secret)

---

## 🔵 Simple Definition (English)
An **organization secret** is a secret stored once at the GitHub organization level and shared with selected repositories (all, private only, or a chosen list). Workflows read it with the same `${{ secrets.NAME }}` syntax. Organization **variables** work the same way for non-secret values.

## 🔵 सरल परिभाषा (Hindi)
**Organization secret** एक secret है जो GitHub organization level पर एक बार store होता है और चुनी हुई repositories (सभी, सिर्फ private, या चुनी हुई list) के साथ share होता है। Workflows इसे वही `${{ secrets.NAME }}` syntax से पढ़ते हैं। Non-secret values के लिए organization **variables** भी ऐसे ही काम करते हैं।

---

## 🔴 Problem it Solves
With 30 microservice repos each needing `DOCKERHUB_TOKEN` or `SLACK_WEBHOOK`, per-repo secrets mean 30 places to update on rotation, and inevitable drift where one repo still uses the leaked token. Org secrets give a single source of truth and central access control.

## 🔴 यह क्यों बना? (Hindi)
30 microservice repos में हर एक को `DOCKERHUB_TOKEN` या `SLACK_WEBHOOK` चाहिए तो per-repo secrets का मतलब rotation पर 30 जगह update, और कोई repo leaked token पर अटका रह जाएगा। Org secrets एक single source of truth और central access control देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Org owner/admin: Organization > Settings > Secrets and variables > Actions
Step 2 → New organization secret: name, value
Step 3 → Choose Repository access: All / Private (and internal) / Selected repositories
Step 4 → Workflows in allowed repos use ${{ secrets.NAME }}
Step 5 → If a repo has a secret with the same name, precedence is:
         environment > repository > organization
Step 6 → Rotate once at org level; every allowed repo gets the new value on next run
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Org owner/admin: Organization > Settings > Secrets and variables > Actions
Step 2 → New organization secret: name, value
Step 3 → Repository access चुनो: All / Private (और internal) / Selected repositories
Step 4 → Allowed repos के workflows ${{ secrets.NAME }} use करते हैं
Step 5 → अगर repo में उसी नाम का secret हो तो priority:
         environment > repository > organization
Step 6 → Org level पर एक बार rotate करो; हर allowed repo को अगले run में नई value मिलती है
```

---

## 🟡 Real World Example
A company with repos `orders-api`, `payments-api`, `web-frontend`, `notifier` shares `SLACK_WEBHOOK_URL`, `SONAR_TOKEN` and `GHCR_PUSH_TOKEN` as organization secrets, limited to the four selected repos. A new intern's experimental repo is not in the list, so it cannot read them.

## 🟡 Real Example Hindi mein
एक कंपनी की repos `orders-api`, `payments-api`, `web-frontend`, `notifier` `SLACK_WEBHOOK_URL`, `SONAR_TOKEN` और `GHCR_PUSH_TOKEN` को organization secrets की तरह share करती हैं, सिर्फ इन चार selected repos तक सीमित। नए intern की experimental repo list में नहीं है, इसलिए वह इन्हें पढ़ नहीं सकती।

---

## 💻 Code / Config Example — Basic
```bash
# --- needs: gh auth login with org admin permission (admin:org scope) ---
ORG=my-company                                            # your organization login

# create an org secret visible to ALL private repos
gh secret set SLACK_WEBHOOK_URL --org "$ORG" --visibility private --body "https://hooks.slack.com/services/XXX/YYY/ZZZ"

# create one visible only to selected repos (comma separated)
gh secret set SONAR_TOKEN --org "$ORG" --repos "orders-api,payments-api" --body "sonar-token-value"

# list organization secrets (names and visibility, never values)
gh secret list --org "$ORG"

# remove a secret that is no longer needed
gh secret delete OLD_TOKEN --org "$ORG"
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/ci.yml  (identical file can live in many repos)
name: ci                               # workflow name
on:
  push:
    branches: [main]                   # main only
  pull_request:                        # PRs (fork PRs get no org secrets)

permissions:
  contents: read                       # token minimum
  packages: write                      # needed to push to ghcr.io

jobs:
  test-and-notify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4      # example version
      - uses: actions/setup-node@v4    # example version
        with:
          node-version: 20             # Node.js LTS example
          cache: npm                   # built-in npm cache
      - run: npm ci && npm test        # install exactly from lockfile, run tests

      - name: Sonar scan (org secret)
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'   # not on PRs
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}   # org secret, same name in every repo
        run: echo "run sonar scanner here"          # replace with real scanner action

      - name: Notify Slack on failure
        if: failure()                               # only when something failed
        env:
          HOOK: ${{ secrets.SLACK_WEBHOOK_URL }}    # org secret
        run: |
          curl -fsS -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"CI failed: $GITHUB_REPOSITORY @ ${GITHUB_SHA::7}\"}" \
            "$HOOK"                                  # webhook post, URL kept in env only

# Reusable workflow caller (org-wide template) can forward all secrets:
#   jobs:
#     call:
#       uses: my-company/.github/.github/workflows/ci.yml@main
#       secrets: inherit               # passes caller's accessible secrets
```
Not run locally; shell syntax checked and YAML parsed. Slack URL and tokens above are placeholders.

---

## 🟠 My Stack Integration
If you run an organization with a Node.js API, a FastAPI service and a React app, store shared registry/notification tokens at org level, and keep per-service deployment keys (VPS SSH key for each server) at repository or environment level, because each server should have its own credential.

```yaml
# snippet: org secret for registry, repo secret for server
      - name: Push image
        run: echo "${{ secrets.GHCR_PUSH_TOKEN }}" | docker login ghcr.io -u "${{ github.actor }}" --password-stdin
        # GHCR_PUSH_TOKEN = org secret shared by all services
      - name: Deploy
        run: ssh deploy@"${{ secrets.VPS_HOST }}" "docker compose pull && docker compose up -d"
        # VPS_HOST / VPS_SSH_KEY = repo/environment secrets, different per service
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Visibility "All repositories" for a powerful token, including public repos.
✅ Correct: Select only the needed repos; public repos can run attacker-modified workflows from branches.

❌ Mistake 2: Org secret not visible in a repo and the workflow shows empty value.
✅ Correct: Check repository access policy; free-plan orgs have limits on private repos usage; confirm repo is in the list.

❌ Mistake 3: Same name defined at repo level and forgotten; the repo value silently overrides the org value.
✅ Correct: Remember precedence; remove repo-level duplicates.

❌ Mistake 4: One shared admin-level token for everything.
✅ Correct: Separate narrow tokens per purpose (registry push, Slack, scanner).

---

## 🧠 Tricky Interview Question
You rotated an org secret but one repo keeps failing with the old token. What do you check?

Answer: (1) A repository- or environment-level secret with the same name overrides the org secret. (2) The repo may not be in the allowed list. (3) The run may be a re-run or a workflow from a stale branch that references a different name. (4) Dependabot runs use the separate Dependabot secret store. Delete the overriding secret or update it.

---

## ⚫ Interview Questions + Answers

Q1: Who can manage organization secrets?
A1: Organization owners (and users with custom roles allowing it).

Q2: What are the visibility options?
A2: All repositories, private repositories (and internal), selected repositories.

Q3: Precedence if names clash?
A3: Environment secret beats repository secret beats organization secret.

Q4: Do reusable workflows receive org secrets?
A4: Only if the caller passes them (`secrets:` mapping or `secrets: inherit`).

Q5: Can you create them by API/CLI?
A5: Yes: `gh secret set NAME --org ORG --repos a,b` or the REST API with encrypted payload.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many repos need the same credential (registry, scanner, Slack).
- You want central rotation and audit.

❌ Avoid when:
- Credential is repo-specific (server SSH key).
- You cannot restrict repo access: keep it at repo level.

---

## 📊 Visual Diagram
```
            Organization: my-company
          +-----------------------------+
          | SLACK_WEBHOOK_URL (secret)  |
          | access: selected repos      |
          +--------+----------+---------+
                   |          |
          orders-api    payments-api      intern-playground
          reads OK      reads OK          ---> NO ACCESS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Org secret | Secret shared across repos | कई repos में shared secret |
| Repository access policy | Which repos can read it | कौन सी repos पढ़ सकती हैं |
| Precedence | Environment > repo > org | Priority क्रम |
| secrets: inherit | Pass caller's secrets to reusable workflow | Caller के secrets आगे देना |
| Org variable | Non-secret shared setting | Non-secret shared setting |

---

## ⚡ 3-Line Summary
English: Org secrets store a credential once and share it with selected repos.
Restrict visibility; narrow tokens; repo/environment values override org values.
Rotate centrally for fast, consistent updates.

Hindi: Org secrets credential को एक बार रखकर चुनी हुई repos में share करते हैं।
Visibility सीमित रखो; narrow tokens बनाओ; repo/environment values org values को override करती हैं।
Central rotation से update तेज़ और consistent होता है।

---

## ➡️ Next Topic
**280. Environment Secrets** — secrets tied to a deployment environment (staging/production) with approvals and branch rules.
