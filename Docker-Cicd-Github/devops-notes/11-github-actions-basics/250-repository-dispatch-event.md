# 250. repository_dispatch Event
# हिंदी में: repository_dispatch Event (बाहर से API द्वारा trigger)

---

## 🔵 Simple Definition (English)
`repository_dispatch` lets an **external system** (a script, another repository, a CMS, a monitoring tool) trigger workflows in your repository by calling the REST API `POST /repos/{owner}/{repo}/dispatches` with a custom `event_type` and an optional `client_payload` JSON. The workflow listens with `on: repository_dispatch: types: [your-event]`.

## 🔵 सरल परिभाषा (Hindi)
`repository_dispatch` से कोई **बाहरी system** (script, दूसरा repository, CMS, monitoring tool) REST API `POST /repos/{owner}/{repo}/dispatches` को custom `event_type` और वैकल्पिक `client_payload` JSON के साथ बुलाकर आपके repository के workflows trigger कर सकता है। Workflow `on: repository_dispatch: types: [your-event]` से सुनता है।

---

## 🔴 Problem it Solves
Built-in events only react to things that happen inside GitHub. Real systems need cross-system triggers: the content team publishes in a headless CMS and the React site must rebuild; a library repo releases and 5 app repos must update; a Grafana alert wants to start a remediation runbook; the backend repo finished building and the infra repo must deploy. Without `repository_dispatch` you would poll or use fragile commits-to-trigger hacks.

## 🔴 यह क्यों बना? (Hindi)
Built-in events सिर्फ़ GitHub के भीतर होने वाली घटनाओं पर चलते हैं। असली systems को cross-system triggers चाहिए: content team headless CMS में publish करे तो React site दोबारा build हो; library repo का release आए तो 5 app repos update हों; Grafana alert remediation runbook चलाना चाहे; backend repo की build पूरी हो तो infra repo deploy करे। `repository_dispatch` के बिना आपको polling या commit-करके-trigger जैसे कमज़ोर तरीके अपनाने पड़ते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Workflow declares `on: repository_dispatch: types: [cms-published]`. File must be on the default branch.
Step 2 → External caller sends POST /repos/OWNER/REPO/dispatches with JSON {"event_type":"cms-published","client_payload":{...}}.
Step 3 → Auth: a token with `repo` scope (classic PAT) or fine-grained token with "Contents: write"/Actions write, or GitHub App token.
Step 4 → GitHub returns 204 No Content (no run id returned!).
Step 5 → A run starts on the DEFAULT branch latest commit; github.event.action = "cms-published".
Step 6 → Payload is read from `github.event.client_payload.<key>` (max 10 top-level properties, ~64 KB).
Step 7 → Treat payload as untrusted input; validate before using in shell.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Workflow में `on: repository_dispatch: types: [cms-published]`। File default branch पर होनी चाहिए।
Step 2 → बाहरी caller POST /repos/OWNER/REPO/dispatches को JSON {"event_type":"cms-published","client_payload":{...}} भेजता है।
Step 3 → Auth: `repo` scope वाला token (classic PAT), fine-grained token या GitHub App token।
Step 4 → GitHub 204 No Content लौटाता है (run id नहीं मिलता!)।
Step 5 → DEFAULT branch के latest commit पर run शुरू; github.event.action = "cms-published"।
Step 6 → Payload `github.event.client_payload.<key>` से पढ़ें (अधिकतम 10 top-level properties, ~64 KB)।
Step 7 → Payload को अविश्वसनीय मानें; shell में लेने से पहले validate करें।
```

---

## 🟡 Real World Example
A media company uses a headless CMS (Strapi) for articles and a React/Next static site served by Nginx. Editors hit "Publish"; a CMS webhook calls a small Lambda, which calls GitHub `dispatches` with `event_type: "content-updated"` and payload `{"slug": "budget-2026"}`. The workflow rebuilds only that section, syncs the static files to the VPS, and purges Nginx cache. Total delay: about 2 minutes, without any developer involved.

## 🟡 Real Example Hindi mein
एक media कंपनी लेखों के लिए headless CMS (Strapi) और Nginx से परोसी जाने वाली React/Next static site इस्तेमाल करती है। Editor "Publish" दबाता है; CMS webhook एक छोटे Lambda को बुलाता है, जो GitHub `dispatches` को `event_type: "content-updated"` और payload `{"slug": "budget-2026"}` के साथ कॉल करता है। Workflow सिर्फ़ उसी section को rebuild करता है, static files VPS पर sync करता है और Nginx cache purge करता है। देरी लगभग 2 मिनट, किसी developer के बिना।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/dispatch-basic.yml
name: Dispatch Basic                      # name in Actions tab

on:
  repository_dispatch:                    # external API trigger
    types: [ping]                         # only react to event_type "ping"

jobs:
  echo:                                   # job id
    runs-on: ubuntu-latest                # runner
    steps:
      - name: Print payload               # show what was sent
        env:
          MSG: ${{ github.event.client_payload.message }}   # payload via env (safe from injection)
        run: echo "Got msg - $MSG"        # print it
```

```bash
# Trigger it from any machine (replace OWNER/REPO and use a fine-grained token with Actions/Contents write)
curl -sS -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_PAT" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/dispatches \
  -d '{"event_type":"ping","client_payload":{"message":"hello"}}'   # expect HTTP 204
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/content-rebuild.yml  (in the website repo)
name: Content Rebuild

on:
  repository_dispatch:
    types: [content-updated, content-deleted]   # multiple event types handled by one workflow

concurrency:
  group: content-rebuild                  # collapse rapid-fire CMS webhooks
  cancel-in-progress: true                # newest content wins

permissions:
  contents: read                          # minimal

jobs:
  rebuild:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Validate payload            # untrusted input: whitelist characters
        env:
          SLUG: ${{ github.event.client_payload.slug }}
          ACTION: ${{ github.event.action }}      # the event_type that was sent
        run: |
          [[ "$SLUG" =~ ^[a-z0-9-]{1,80}$ ]] || { echo "invalid slug"; exit 1; }   # only safe characters
          echo "action=$ACTION slug=$SLUG"       # log for audit

      - uses: actions/checkout@v4         # default branch code
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci                       # install
      - run: npm run build                # build static site
        env:
          CMS_URL: ${{ vars.CMS_URL }}    # non-secret config from repository variables
          CMS_TOKEN: ${{ secrets.CMS_READ_TOKEN }}   # read-only CMS token

      - name: Sync to VPS and purge Nginx cache
        env:
          HOST: ${{ secrets.VPS_HOST }}
          KEY: ${{ secrets.VPS_SSH_KEY }}
        run: |
          install -m 600 /dev/null key && printf '%s\n' "$KEY" > key
          rsync -az --delete -e "ssh -i key -o StrictHostKeyChecking=accept-new" \
            dist/ "deploy@$HOST:/var/www/site/"          # copy files, remove stale ones
          ssh -i key "deploy@$HOST" 'sudo nginx -s reload' # reload Nginx (needs sudoers rule for this one command)
```

(YAML parsed locally. Not run against GitHub. `rsync --delete` removes files on the target: test on staging first.)

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** backend repo, after publishing an image, dispatches to the infra repo: `{"service":"api","tag":"sha-3fa91c2"}`.
- **React:** CMS or Shopify webhook rebuilds the site.
- **Nginx / VPS:** workflow rsyncs `dist/` and reloads Nginx.
- **AWS:** an EventBridge rule or Lambda calls the dispatch API when an ECR scan finds CRITICAL issues, starting a rebuild workflow.

```yaml
# Backend repo workflow step that notifies the infra repo after pushing the image
- name: Notify infra repo
  env:
    GH_TOKEN: ${{ secrets.INFRA_DISPATCH_TOKEN }}   # fine-grained token limited to the infra repo only
    TAG: ${{ steps.meta.outputs.version }}
  run: |
    gh api repos/acme/infra/dispatches \
      -f event_type=deploy-requested \
      -f 'client_payload[service]=api' \
      -f "client_payload[tag]=$TAG"       # gh api builds the JSON body; 204 on success
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Workflow file only on a feature branch; dispatch does nothing.
✅ Correct: The file must be on the default branch; the run uses default branch code.

❌ Mistake 2: Using a broad classic PAT with `repo` scope in a CMS.
✅ Correct: Use a fine-grained token limited to one repository and only needed permissions, or a GitHub App.

❌ Mistake 3: Expecting a run ID back from the API.
✅ Correct: Response is 204 with no body; find the run by listing runs or have the workflow report back.

❌ Mistake 4: Putting `${{ github.event.client_payload.x }}` directly in `run:`.
✅ Correct: Pass through `env:` and validate.

---

## 🧠 Tricky Interview Question
Your dispatch call returns 204, but no workflow starts. List the likely causes.

Answer: (1) the `event_type` does not match any `types:` list (case-sensitive); (2) the workflow file is not on the default branch; (3) the workflow is disabled (for example, inactive scheduled workflow, or Actions disabled); (4) you dispatched to a different repository (or a fork) than the one holding the workflow; (5) a bad token normally gives 403/404 and an oversized payload (more than 10 top-level properties) gives 422, so those are not silent. Check the Actions tab filtered by event "repository_dispatch" and the audit log.

---

## ⚫ Interview Questions + Answers

Q1: How does `repository_dispatch` differ from `workflow_dispatch`?
A1: It is repo-wide with a free `event_type` and `client_payload`; any number of workflows can listen. `workflow_dispatch` targets one workflow with typed inputs and a UI button.

Q2: Where does the run execute?
A2: On the default branch's latest commit.

Q3: What payload limits exist?
A3: Up to 10 top-level properties in `client_payload` and roughly 64 KB total (see current docs).

Q4: What permissions does the token need?
A4: Fine-grained: Contents write (check docs; Actions write for workflow_dispatch). Classic PAT: `repo` scope. GitHub App: contents write.

Q5: Can `GITHUB_TOKEN` trigger it from another workflow?
A5: Yes; `repository_dispatch` and `workflow_dispatch` are the exceptions allowed to be created with `GITHUB_TOKEN` and start new runs (same-repo token needs `contents: write`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cross-repo orchestration (library -> apps, backend -> infra).
- Webhooks from CMS, monitoring, or internal tools.

❌ Avoid when:
- Both sides are in one repo - use `workflow_call` or `needs`.
- You need typed inputs and a manual UI - use `workflow_dispatch`.

---

## 📊 Visual Diagram

```
  CMS / Lambda / other repo                         GitHub
  ────────────────────────                          ──────
  POST /repos/acme/site/dispatches
  { event_type: content-updated,   ───────────►   204 No Content
    client_payload: {slug: ...} }                       │
                                                        ▼
                                          match on.repository_dispatch.types ?
                                                 │ yes
                                                 ▼
                                       run on default branch (main)
                                                 │
                           validate payload ─► build ─► rsync to VPS ─► nginx reload
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| event_type | Custom name of the dispatched event | Event का custom नाम |
| client_payload | JSON data sent with the dispatch | साथ भेजा JSON data |
| webhook | HTTP callback from another system | दूसरे system का HTTP callback |
| fine-grained token | Token limited to chosen repos/permissions | सीमित repos/permissions वाला token |
| GitHub App | Bot identity with scoped access | सीमित access वाली bot पहचान |
| 204 | HTTP "success, no content" | सफल, बिना body |

---

## ⚡ 3-Line Summary
English: `repository_dispatch` starts workflows from outside via an API call with a custom type and payload.
English: Runs on the default branch; returns 204 without run ID.
English: Use minimal-scope tokens and validate payloads.
Hindi: `repository_dispatch` बाहर से API call द्वारा custom type और payload के साथ workflow शुरू करता है।
Hindi: Default branch पर चलता है; 204 लौटाता है, run ID नहीं।
Hindi: न्यूनतम-scope tokens रखें और payload validate करें।

---

## ➡️ Next Topic
**251. jobs: Structure** - now that we know all the triggers, study the building blocks inside a workflow: jobs, dependencies and outputs.
