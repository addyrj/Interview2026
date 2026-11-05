# 269. inputs Context
# हिंदी में: inputs Context

---

## 🔵 Simple Definition (English)
The `inputs` context holds the input values passed to a manually triggered workflow (`workflow_dispatch`) or to a reusable workflow (`workflow_call`). Read them as `${{ inputs.name }}`. Unlike `github.event.inputs`, `inputs` keeps real types such as boolean and number.

## 🔵 सरल परिभाषा (Hindi)
`inputs` context उन input values को रखता है जो manual trigger वाले workflow (`workflow_dispatch`) या reusable workflow (`workflow_call`) को दिए जाते हैं। इन्हें `${{ inputs.name }}` से पढ़ते हैं। `github.event.inputs` के उलट, `inputs` boolean और number जैसे असली types बनाए रखता है।

---

## 🔴 Problem it Solves
Sometimes a human or another workflow must decide at run time: deploy to staging or production, which version, run migrations or not, dry-run or real. Hard-coding forces edits and commits; branches per environment cause drift. `inputs` makes workflows parameterized, like function arguments.

## 🔴 यह क्यों बना? (Hindi)
कभी इंसान या दूसरे workflow को run time पर तय करना होता है: staging या production, कौन सा version, migration चलाना है या नहीं, dry-run या असली। Hard-code करने पर edits और commits चाहिए; हर environment के लिए branch बनाने से drift होता है। `inputs` workflows को function arguments की तरह parameterized बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare inputs under on.workflow_dispatch.inputs or on.workflow_call.inputs
Step 2 → Each input has type: string | boolean | number | choice | environment
Step 3 → Manual run: UI/gh CLI prompts for values; reusable: caller passes with:
Step 4 → GitHub validates required inputs and choice options
Step 5 → Read ${{ inputs.name }} in jobs, steps, if:, runs-on, environment
Step 6 → Booleans are real booleans in inputs; inside shell they become strings
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → on.workflow_dispatch.inputs या on.workflow_call.inputs में inputs declare करो
Step 2 → हर input का type: string | boolean | number | choice | environment
Step 3 → Manual run: UI/gh CLI values पूछता है; reusable: caller with: से देता है
Step 4 → GitHub required inputs और choice options validate करता है
Step 5 → jobs, steps, if:, runs-on, environment में ${{ inputs.name }} पढ़ो
Step 6 → inputs में booleans असली boolean हैं; shell में वे string बन जाते हैं
```

---

## 🟡 Real World Example
Your ops engineer opens Actions > "Deploy" > Run workflow, picks `environment=production`, types `version=v2.3.1`, and ticks `run_migrations`. Another repo's workflow calls the same file as a reusable workflow with `with: { environment: staging, version: ${{ github.sha }} }`. One YAML, many callers, like a function.

## 🟡 Real Example Hindi mein
आपका ops engineer Actions > "Deploy" > Run workflow खोलता है, `environment=production` चुनता है, `version=v2.3.1` लिखता है और `run_migrations` tick करता है। दूसरे repo का workflow वही file reusable workflow की तरह `with: { environment: staging, version: ${{ github.sha }} }` के साथ call करता है। एक YAML, कई callers, function की तरह।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/inputs-basic.yml
name: inputs-basic                     # workflow name
on:
  workflow_dispatch:                   # manual trigger
    inputs:
      environment:
        description: Where to deploy   # label in the UI
        type: choice                   # dropdown
        options: [staging, production] # allowed values
        default: staging               # preselected
      dry_run:
        description: Skip real deploy  # checkbox label
        type: boolean                  # true/false
        default: true                  # safe default
      version:
        description: Image tag         # free text
        type: string                   # text input
        required: true                 # must be provided
jobs:
  deploy:
    runs-on: ubuntu-24.04              # example runner
    steps:
      - name: Show inputs              # print values
        run: |                         # script
          echo "env     = ${{ inputs.environment }}"   # staging/production
          echo "dry_run = ${{ inputs.dry_run }}"       # true/false
          echo "version = ${{ inputs.version }}"       # text (see injection note below)
      - name: Real deploy only when not dry-run   # boolean usable directly
        if: ${{ !inputs.dry_run }}     # real boolean negation
        run: echo "deploying"          # skipped by default
```
Run it with the CLI: `gh workflow run inputs-basic.yml -f environment=staging -f dry_run=false -f version=v1.0.0`.

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/deploy-reusable.yml
name: deploy-reusable                  # callable + manual
on:
  workflow_call:                       # reusable entry
    inputs:
      environment:
        type: string                   # string input
        required: true                 # caller must pass it
      image_tag:
        type: string
        required: true
      run_migrations:
        type: boolean
        default: false
    secrets:
      VPS_SSH_KEY:
        required: true                 # declared secret
    outputs:
      url:
        description: Deployed URL      # exposed to caller
        value: ${{ jobs.deploy.outputs.url }}   # from job output
  workflow_dispatch:                   # same inputs for manual runs
    inputs:
      environment: { type: environment, required: true }   # environment type = repo environments
      image_tag: { type: string, required: true }
      run_migrations: { type: boolean, default: false }
jobs:
  deploy:
    runs-on: ubuntu-24.04              # example runner
    environment: ${{ inputs.environment }}   # picks vars/secrets/approvals
    outputs:
      url: ${{ steps.u.outputs.url }}  # job output
    steps:
      - name: Validate inputs (treat as untrusted)   # guard against injection
        env:
          TAG: ${{ inputs.image_tag }}   # pass through env, not directly into script
        run: |                         # script
          [[ "$TAG" =~ ^[A-Za-z0-9._-]{1,64}$ ]] || { echo "bad tag"; exit 1; }   # allowlist characters
      - name: Migrate                  # conditional step
        if: ${{ inputs.run_migrations }}   # boolean input
        env:
          TAG: ${{ inputs.image_tag }}
        run: echo "run migrations for $TAG"   # placeholder
      - id: u                          # output step
        env:
          ENVNAME: ${{ inputs.environment }}
        run: echo "url=https://${ENVNAME}.example.com" >> "$GITHUB_OUTPUT"   # compute URL
```
```yaml
# .github/workflows/caller.yml  (another workflow calling it)
name: caller                           # caller workflow
on: push                               # trigger
jobs:
  call:
    uses: ./.github/workflows/deploy-reusable.yml   # local reusable workflow
    with:
      environment: staging             # input
      image_tag: ${{ github.sha }}     # input
      run_migrations: true             # boolean input
    secrets:
      VPS_SSH_KEY: ${{ secrets.VPS_SSH_KEY }}   # pass secret explicitly
```
Parsed as YAML locally; reusable-workflow behaviour follows GitHub docs, not run on GitHub.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: one reusable `build-and-push.yml` with inputs `service`, `dockerfile`, `context` for both apps.
- **React**: `inputs.api_url` for building preview environments.
- **Nginx/VPS**: input `dry_run` to run `nginx -t` only; `reload` input to apply.
- **AWS**: `inputs.environment` selects the OIDC role through `vars.AWS_ROLE_ARN` of that environment.
- **Security**: only users with write access can trigger `workflow_dispatch`; still treat string inputs as untrusted text.

```yaml
      - name: Hotfix deploy to VPS       # uses inputs safely via env
        env:
          TAG: ${{ inputs.image_tag }}   # validated earlier
        run: ssh deploy@"$HOST" "docker pull ghcr.io/acme/api:$TAG && docker compose up -d"   # tag is data, validated
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `run: ./deploy.sh ${{ inputs.version }}` unvalidated.
✅ Correct: Pass via `env:` and validate with an allowlist regex.

❌ Mistake 2: Using `github.event.inputs.dry_run == true` (compares string to bool).
✅ Correct: Use `inputs.dry_run` (typed). With `github.event.inputs` everything is a string: compare `== 'true'`.

❌ Mistake 3: More than 10 inputs (older limit) or nested objects.
✅ Correct: Check current limits (docs cite a max count/size); pass JSON in one string and `fromJSON` it.

❌ Mistake 4: Assuming `required: true` is enforced in the UI for choice only.
✅ Correct: It is enforced for manual runs; for `workflow_call` the caller must pass it or validation fails.

❌ Mistake 5: Forgetting that the workflow file must exist on the default branch for the Run workflow button.
✅ Correct: Merge it to the default branch (or use `--ref` with the CLI for branches).

---

## 🧠 Tricky Interview Question
A boolean input `dry_run` defaults to `false`. A step has `if: github.event.inputs.dry_run == false`. It never runs when dry_run is false. Why?

Answer: In `github.event.inputs` all values are strings, so `'false' == false` coerces differently: the string `'false'` converts to NaN/0-like comparison and the expression is not what you intended. Use the typed `inputs` context: `if: ${{ !inputs.dry_run }}` or compare string explicitly: `github.event.inputs.dry_run == 'false'`.

---

## ⚫ Interview Questions + Answers

Q1: Which triggers provide `inputs`?
A1: `workflow_dispatch` and `workflow_call`.

Q2: Input types?
A2: `string`, `boolean`, `number`, `choice` (dispatch only), `environment` (dispatch only).

Q3: `inputs` vs `github.event.inputs`?
A3: `inputs` preserves types and works for both triggers; `github.event.inputs` is dispatch only and all strings.

Q4: How to trigger with inputs from CLI/API?
A4: `gh workflow run file.yml -f key=value` or the REST `workflow_dispatch` endpoint with an `inputs` object.

Q5: How does a reusable workflow return values?
A5: Declare `on.workflow_call.outputs` mapped to job outputs; caller reads `needs.<job>.outputs`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Manual deploy, rollback, hotfix, maintenance workflows
- Reusable workflows shared by many services
- Dry-run / environment selection

❌ Avoid when:
- Automatic triggers (push/PR) have no inputs, use `vars` or defaults
- Secrets (never pass via inputs; they show in UI/logs)
- Unvalidated free text going to shell

---

## 📊 Visual Diagram
```
 Human (UI / gh CLI) ---- workflow_dispatch inputs ----+
                                                       v
 Caller workflow ------- with: {...} (workflow_call) -> ${{ inputs.* }}
                                                       |
                         typed: string/boolean/number/choice/environment
                                                       |
                  jobs.deploy: environment: ${{ inputs.environment }}
                  steps: if: inputs.run_migrations / env: TAG=${{ inputs.image_tag }}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| inputs | Typed run parameters | Typed run parameters |
| workflow_dispatch | Manual trigger | Manual trigger |
| workflow_call | Reusable workflow trigger | Reusable workflow trigger |
| choice | Dropdown input | Dropdown input |
| Dry run | Simulate without changes | बदलाव किए बिना सिमुलेशन |

---

## ⚡ 3-Line Summary
English: `inputs` carries typed parameters into manual and reusable workflows.
Prefer `inputs` over `github.event.inputs` for real booleans.
Validate string inputs and pass them via `env:` to avoid script injection.
Hindi: `inputs` manual और reusable workflows में typed parameters ले जाता है।
असली booleans के लिए `github.event.inputs` की जगह `inputs` चुनो।
String inputs validate करो और script injection से बचने के लिए `env:` से पास करो।

---

## ➡️ Next Topic
**270. Expressions in Actions** — tying contexts, operators and functions together in `${{ }}`.
