# 247. workflow_dispatch Event
# हिंदी में: workflow_dispatch Event (हाथ से workflow चलाना)

---

## 🔵 Simple Definition (English)
`workflow_dispatch` lets you start a workflow **manually** from the GitHub UI ("Run workflow" button), the `gh workflow run` CLI, or the REST API. You can define typed **inputs** (string, boolean, choice, environment, number) so the person triggering it can pass parameters such as target environment or image tag.

## 🔵 सरल परिभाषा (Hindi)
`workflow_dispatch` से आप workflow को GitHub UI ("Run workflow" button), `gh workflow run` CLI या REST API से **हाथ से** शुरू कर सकते हैं। आप typed **inputs** (string, boolean, choice, environment, number) तय कर सकते हैं ताकि चलाने वाला target environment या image tag जैसे parameters दे सके।

---

## 🔴 Problem it Solves
Not everything should run automatically. Production deploys, rollbacks, database migrations and one-off maintenance need a human decision and parameters ("deploy tag v1.4.2 to prod"). Before this, teams edited a file and pushed a dummy commit, or SSH-ed into servers. `workflow_dispatch` gives a safe, audited, parameterized button: GitHub records who clicked and with which inputs.

## 🔴 यह क्यों बना? (Hindi)
सब कुछ अपने-आप नहीं चलना चाहिए। Production deploy, rollback, database migration और एक-बार के maintenance में इंसान का निर्णय और parameters ("tag v1.4.2 को prod पर deploy करो") चाहिए। पहले लोग file बदलकर dummy commit push करते थे या server में SSH करते थे। `workflow_dispatch` सुरक्षित, audit होने वाला, parameter वाला button देता है: GitHub दर्ज करता है कि किसने किन inputs से चलाया।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add `on: workflow_dispatch:` (optionally with `inputs:`) to a workflow file.
Step 2 → The file must exist on the default branch for the UI button to appear (CLI/API can target other refs once the file exists).
Step 3 → User opens Actions -> workflow -> "Run workflow", picks a branch/tag and fills the inputs.
Step 4 → GitHub creates a run with github.event_name == "workflow_dispatch".
Step 5 → Inputs are available as `${{ inputs.name }}` (and `github.event.inputs.name`, which are always strings).
Step 6 → Permission needed: write access to the repo. Environment protection rules can still require approval.
Step 7 → Same via CLI: `gh workflow run deploy.yml -f environment=prod -f tag=v1.4.2`.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Workflow file में `on: workflow_dispatch:` (चाहें तो `inputs:` के साथ) जोड़ें।
Step 2 → UI button दिखने के लिए file default branch पर होनी चाहिए (file बनने के बाद CLI/API दूसरे ref पर भी चला सकते हैं)।
Step 3 → User Actions -> workflow -> "Run workflow" खोलकर branch/tag चुनता है और inputs भरता है।
Step 4 → GitHub github.event_name == "workflow_dispatch" वाला run बनाता है।
Step 5 → Inputs `${{ inputs.name }}` से मिलते हैं (और `github.event.inputs.name` से, जो हमेशा string होते हैं)।
Step 6 → ज़रूरी permission: repo का write access। Environment protection rules फिर भी approval माँग सकते हैं।
Step 7 → CLI से: `gh workflow run deploy.yml -f environment=prod -f tag=v1.4.2`।
```

Limits: up to 25 inputs (check current docs, limits change), payload max about 65 KB. Input types: `string`, `boolean`, `choice`, `number`, `environment`.

---

## 🟡 Real World Example
A SaaS team in Pune has a "Deploy" workflow with inputs `environment` (staging/production) and `image_tag`. The tester clicks Run workflow with `staging` and tag `sha-3fa91c2` after QA. For production, the `production` environment demands approval from a lead. When a release goes bad, anyone on call runs the same workflow with the previous tag - that is the rollback, 2 minutes, no SSH.

## 🟡 Real Example Hindi mein
Pune की एक SaaS team के पास "Deploy" workflow है जिसमें inputs `environment` (staging/production) और `image_tag` हैं। QA के बाद tester `staging` और tag `sha-3fa91c2` के साथ Run workflow दबाता है। Production के लिए `production` environment lead की approval माँगता है। Release बिगड़ जाए तो on-call वही workflow पिछले tag के साथ चलाता है - यही rollback है, 2 मिनट, बिना SSH।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/manual-hello.yml
name: Manual Hello                        # name in the Actions list

on:
  workflow_dispatch:                      # enable the "Run workflow" button
    inputs:                               # parameters asked in the form
      name:                               # input key, used as inputs.name
        description: "Who to greet"       # label shown in the UI
        required: true                    # UI will not allow an empty value
        default: "DevOps"                 # prefilled value
        type: string                      # free text

jobs:
  hello:                                  # job id
    runs-on: ubuntu-latest                # hosted runner
    steps:
      - name: Say hello                   # step label
        run: echo "Hello, $NAME"          # use env var, safer than inlining the expression in shell
        env:
          NAME: ${{ inputs.name }}        # pass input via env to avoid shell injection
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  workflow_dispatch:
    inputs:
      environment:                        # where to deploy
        description: "Target environment"
        required: true
        type: choice                      # dropdown, limits typos
        options: [staging, production]    # allowed values
        default: staging
      image_tag:                          # which image to deploy (also used for rollback)
        description: "Image tag, e.g. sha-3fa91c2 or v1.4.2"
        required: true
        type: string
      run_migrations:                     # optional DB migration switch
        description: "Run DB migrations?"
        required: false
        type: boolean                     # checkbox
        default: false

permissions:
  contents: read                          # least privilege

concurrency:
  group: deploy-${{ inputs.environment }} # one deploy per environment at a time
  cancel-in-progress: false               # never cancel a deploy halfway

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}   # triggers environment protection / secrets for that env
    timeout-minutes: 15
    steps:
      - name: Validate tag format         # reject suspicious input before using it
        env:
          TAG: ${{ inputs.image_tag }}    # pass through env, never interpolate into the script
        run: |
          [[ "$TAG" =~ ^[A-Za-z0-9._-]{1,64}$ ]] || { echo "Bad tag"; exit 1; }   # whitelist characters

      - name: Deploy over SSH
        env:
          HOST: ${{ secrets.VPS_HOST }}           # environment-scoped secret
          KEY: ${{ secrets.VPS_SSH_KEY }}         # private key (restricted deploy user)
          TAG: ${{ inputs.image_tag }}
          MIGRATE: ${{ inputs.run_migrations }}   # "true"/"false" string in shell
        run: |
          install -m 600 /dev/null key && printf '%s\n' "$KEY" > key   # write key with 600 perms
          ssh -i key -o StrictHostKeyChecking=accept-new "deploy@$HOST" \
            "cd /srv/app && TAG=$TAG docker compose pull && TAG=$TAG docker compose up -d"   # pull and restart
          if [ "$MIGRATE" = "true" ]; then
            ssh -i key "deploy@$HOST" "cd /srv/app && docker compose run --rm api npm run migrate"  # one-off migration
          fi
```

(YAML parsed locally; not executed on GitHub. `accept-new` trusts host key on first connect; pin known_hosts in real use.)

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** inputs for `image_tag`; run migrations (`npm run migrate` / `alembic upgrade head`) via a boolean.
- **React:** manual "invalidate CloudFront cache and re-sync S3 build" button.
- **Nginx / VPS:** dispatch deploy = `docker compose pull && up -d`; rollback = same with an older tag.
- **AWS:** dispatch with `environment` input; use OIDC role chosen per environment; `aws ecs update-service --force-new-deployment`.

```bash
# Trigger from terminal (GitHub CLI), including watching the run
gh workflow run deploy.yml -f environment=staging -f image_tag=sha-3fa91c2 -f run_migrations=false  # start
gh run list --workflow=deploy.yml --limit 3                                                         # find the run
gh run watch                                                                                        # stream progress
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Interpolating `${{ inputs.cmd }}` directly in `run:` - a user can inject shell commands.
✅ Correct: Pass inputs via `env:` and quote `"$VAR"`; validate with a whitelist.

❌ Mistake 2: Expecting the "Run workflow" button on a branch-only workflow file.
✅ Correct: Merge the file to the default branch first.

❌ Mistake 3: Using `github.event.inputs.flag == true` for booleans (it is the string `'true'`).
✅ Correct: Use `inputs.flag` (real boolean) in expressions, or compare to `'true'` for the event context.

❌ Mistake 4: Letting anyone with write access deploy to prod without a gate.
✅ Correct: Use `environment: production` with required reviewers.

---

## 🧠 Tricky Interview Question
You added `workflow_dispatch` to a workflow on a feature branch, but the Actions tab shows no "Run workflow" button. Why, and how do you test?

Answer: The UI lists dispatchable workflows from the default branch. Until the file exists on the default branch, there is no button. Options: merge a minimal version to default, then run it selecting your feature branch in the "Use workflow from" dropdown (it then executes the feature branch's version of the file); or use the API/`gh workflow run -r feature` once GitHub knows the workflow.

---

## ⚫ Interview Questions + Answers

Q1: What input types exist?
A1: string, boolean, choice, number and environment.

Q2: Who can trigger it?
A2: Users with write access to the repository (or via token with `actions: write`).

Q3: How is it different from `repository_dispatch`?
A3: `workflow_dispatch` targets a specific workflow file with typed inputs and a UI; `repository_dispatch` is an API-only event with a custom `event_type` and free-form `client_payload` that can fan out to many workflows.

Q4: How can another workflow trigger a `workflow_dispatch` one?
A4: With the API (`gh workflow run` / `POST .../dispatches`) using a token with `actions: write`. Events created with `GITHUB_TOKEN` do not trigger new workflow runs except `workflow_dispatch` and `repository_dispatch`.

Q5: Can you combine it with push?
A5: Yes: `on: [push, workflow_dispatch]`; `inputs` are empty on push, so use defaults carefully.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Manual production deploys, rollbacks, migrations, cache purges.
- Testing scheduled workflows on demand.

❌ Avoid when:
- A step should always run automatically (use push/PR).
- You cannot validate inputs - free text into shell is dangerous.

---

## 📊 Visual Diagram

```
 UI button ─┐
 gh CLI ────┼──► POST /actions/workflows/deploy.yml/dispatches
 REST API ──┘      { ref: main, inputs: {environment, image_tag} }
                               │
                               ▼
                    run (event = workflow_dispatch)
                               │
                  environment: production ?
                    ├── yes ─► wait for required reviewer approval
                    └── no  ─► continue
                               ▼
                    SSH -> VPS: docker compose pull && up -d
                               ▼
                         audit log: who + inputs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| workflow_dispatch | Manual trigger | हाथ से trigger |
| inputs | Parameters given at trigger time | चलाते समय दिए parameters |
| choice | Dropdown input type | Dropdown प्रकार |
| environment | Deployment target with rules/secrets | Rules/secrets वाला लक्ष्य |
| rollback | Redeploy an older version | पुराना version फिर से चलाना |
| shell injection | Malicious input run as commands | Input से हानिकारक commands चलना |

---

## ⚡ 3-Line Summary
English: `workflow_dispatch` is the manual trigger with typed inputs, via UI, CLI or API.
English: Great for deploys and rollbacks, combined with environments for approvals.
English: Always validate inputs and pass them through `env:`.
Hindi: `workflow_dispatch` typed inputs वाला manual trigger है, UI, CLI या API से।
Hindi: Deploy और rollback के लिए बढ़िया, approvals के लिए environments के साथ।
Hindi: Inputs हमेशा validate करें और `env:` से पास करें।

---

## ➡️ Next Topic
**248. workflow_call Event** - make a workflow reusable so other workflows can call it like a function.
