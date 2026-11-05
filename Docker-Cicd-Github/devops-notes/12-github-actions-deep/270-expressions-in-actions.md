# 270. Expressions in Actions
# हिंदी में: Actions में Expressions

---

## 🔵 Simple Definition (English)
Expressions let you compute values inside workflow YAML using the `${{ <expression> }}` syntax. They combine contexts (`github`, `env`, `needs` ...), literals, operators (`==`, `&&`, `||`, `!`) and functions (`contains`, `format`, `hashFiles`, `fromJSON`, `success`). They are evaluated by GitHub before the value reaches the step or shell.

## 🔵 सरल परिभाषा (Hindi)
Expressions से आप workflow YAML के अंदर `${{ <expression> }}` syntax में values compute करते हैं। ये contexts (`github`, `env`, `needs` ...), literals, operators (`==`, `&&`, `||`, `!`) और functions (`contains`, `format`, `hashFiles`, `fromJSON`, `success`) को जोड़ते हैं। GitHub इन्हें step या shell तक value पहुँचने से पहले evaluate करता है।

---

## 🔴 Problem it Solves
YAML is static, but a pipeline needs decisions: build only on `main`, cache key from lockfile hash, matrix generated from a JSON list, message formatted with run URL. Without expressions you would write wrapper scripts and lose the UI's skip/visibility features. Expressions add a small, safe, declarative language to YAML.

## 🔴 यह क्यों बना? (Hindi)
YAML static है, पर pipeline को फैसले चाहिए: सिर्फ `main` पर build, lockfile hash से cache key, JSON list से बना matrix, run URL वाला message। Expressions के बिना wrapper scripts लिखने पड़ते और UI के skip/visibility features खो जाते। Expressions YAML में एक छोटी, सुरक्षित, declarative भाषा जोड़ते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Workflow is parsed; every ${{ ... }} occurrence is found
Step 2 → GitHub checks that each context is allowed in that YAML key
Step 3 → Expression is evaluated at the earliest time its data exists
        (workflow start: github/vars/inputs; runtime: steps/env/runner)
Step 4 → Result type is coerced when needed (string/number/boolean/null/array/object)
Step 5 → Text is substituted into the YAML value or script BEFORE the shell runs
Step 6 → if: auto-wraps its value, other keys need explicit ${{ }}
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Workflow parse होता है; हर ${{ ... }} मिलता है
Step 2 → GitHub जाँचता है कि उस YAML key में वह context allowed है या नहीं
Step 3 → Expression उस सबसे जल्दी समय पर evaluate होता है जब data मौजूद हो
        (workflow शुरू: github/vars/inputs; runtime: steps/env/runner)
Step 4 → ज़रूरत पर result type बदलता है (string/number/boolean/null/array/object)
Step 5 → Shell चलने से पहले text YAML value या script में replace हो जाता है
Step 6 → if: अपनी value खुद wrap करता है, बाकी keys को explicit ${{ }} चाहिए
```

---

## 🟡 Real World Example
A release pipeline: cache key `${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}`; deploy gate `if: github.ref == 'refs/heads/main' && !contains(github.event.head_commit.message, '[skip deploy]')`; dynamic matrix `fromJSON(needs.plan.outputs.services)` so a monorepo (Zomato-like with 30 services) builds only changed services; Slack text via `format('Run {0} finished: {1}', github.run_number, job.status)`.

## 🟡 Real Example Hindi mein
Release pipeline: cache key `${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}`; deploy gate `if: github.ref == 'refs/heads/main' && !contains(github.event.head_commit.message, '[skip deploy]')`; dynamic matrix `fromJSON(needs.plan.outputs.services)` ताकि monorepo (Zomato जैसा 30 services वाला) सिर्फ बदली services build करे; Slack text `format('Run {0} finished: {1}', github.run_number, job.status)` से।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/expr-basic.yml
name: expr-basic                       # workflow name
on: [push, pull_request]               # triggers
jobs:
  demo:
    runs-on: ubuntu-24.04              # example runner
    steps:
      - name: Literals and operators   # simple comparisons
        run: |                         # script
          echo "is main     : ${{ github.ref == 'refs/heads/main' }}"          # true/false
          echo "is push     : ${{ github.event_name == 'push' }}"              # == is case-insensitive
          echo "fallback    : ${{ github.head_ref || github.ref_name }}"       # || returns first truthy value
          echo "ternary-ish : ${{ github.ref == 'refs/heads/main' && 'prod' || 'dev' }}"  # and/or pattern
      - name: Functions                # built-in functions
        run: |                         # script
          echo "${{ contains('Node FastAPI React', 'FastAPI') }}"              # true
          echo "${{ startsWith(github.ref, 'refs/tags/') }}"                   # tag build?
          echo "${{ format('{0}-{1}', github.run_number, github.run_attempt) }}"   # build-1
          echo "${{ toJSON(runner.os) }}"                                      # "Linux" with quotes
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/expr-advanced.yml
name: dynamic-matrix                   # plan -> matrix -> deploy
on:
  push:
    branches: [main]                   # main only
jobs:
  plan:
    runs-on: ubuntu-24.04              # example runner
    outputs:
      services: ${{ steps.p.outputs.services }}   # JSON string output
    steps:
      - id: p                          # step id
        run: |                         # build JSON list (could come from git diff)
          echo 'services=["api","worker","web"]' >> "$GITHUB_OUTPUT"   # single quotes keep JSON intact
  build:
    needs: plan                        # needs context
    if: ${{ needs.plan.outputs.services != '[]' }}   # skip when nothing to build
    strategy:
      fail-fast: false                 # continue other services
      matrix:
        service: ${{ fromJSON(needs.plan.outputs.services) }}   # JSON string -> array
    runs-on: ubuntu-24.04              # runner
    steps:
      - uses: actions/checkout@v4      # source
      - uses: actions/cache@v4         # example version
        with:
          path: ~/.npm                 # cache dir
          key: ${{ runner.os }}-${{ matrix.service }}-${{ hashFiles(format('{0}/package-lock.json', matrix.service)) }}  # per-service key
      - name: Build ${{ matrix.service }}   # expression in step name
        run: echo "build ${{ matrix.service }}"
      - name: Slack on failure         # status function + formatting
        if: ${{ failure() }}
        env:
          MSG: ${{ format('Build of {0} failed on {1} (run {2})', matrix.service, github.ref_name, github.run_id) }}  # message built by expression
        run: echo "$MSG"               # passed as env, not interpolated into shell code
```
Parsed as YAML locally; `hashFiles` needs files to exist (path relative to workspace); not executed on GitHub. See notes 271-273 for detailed syntax, operators and functions.

---

## 🟠 My Stack Integration
- **Node.js / React**: cache key with `hashFiles('**/package-lock.json')`; skip CI when only `docs/**` changed (prefer `paths-ignore`).
- **FastAPI**: `fromJSON('["3.11","3.12"]')` as python matrix; `contains(github.event.pull_request.labels.*.name, 'slow-tests')` for optional suites.
- **Nginx/VPS**: `if: github.ref_type == 'tag' && startsWith(github.ref_name, 'v')` for release deploys.
- **AWS**: `format('arn:aws:iam::{0}:role/gh-deploy', vars.AWS_ACCOUNT_ID)` builds role ARN.
- **Security**: never place untrusted expression values inside `run:` text; use `env:`.

```yaml
      - name: Safe construction of a command   # expression result goes to env, shell reads as data
        env:
          BRANCH: ${{ github.head_ref || github.ref_name }}   # attacker may control name
        run: 'echo "Deploying branch: $BRANCH"'                # quoted use only
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `if: "${{ false }}"` as a string.
✅ Correct: Any non-empty string is truthy. Avoid mixing text with `${{ }}` inside `if:`; write `if: false` or the pure expression.

❌ Mistake 2: Using double quotes for string literals (`"main"`).
✅ Correct: Expression strings use single quotes: `'main'`; escape a quote by doubling it (`'it''s'`).

❌ Mistake 3: Expecting `a == b` to be case-sensitive.
✅ Correct: String comparison is case-insensitive in expressions; use shell for case-sensitive checks.

❌ Mistake 4: Ternary `cond ? a : b`.
✅ Correct: Not supported. Use `cond && a || b` (works only if `a` is truthy).

❌ Mistake 5: Injecting untrusted values straight into `run:`.
✅ Correct: Map to `env:` and use `"$VAR"` in shell.

---

## 🧠 Tricky Interview Question
`${{ github.event_name == 'push' && '' || 'fallback' }}` returns `fallback` on push, not the empty string. Why?

Answer: The `&& ... ||` idiom relies on the middle value being truthy. An empty string is falsy, so `a && '' ` yields `''`, and then `'' || 'fallback'` picks `'fallback'`. The same happens for `0`, `false` and `null`. If the middle can be falsy, restructure the logic (compute with two steps, or use `format`/`fromJSON` tricks) instead of the pseudo-ternary.

---

## ⚫ Interview Questions + Answers

Q1: When do I need `${{ }}`?
A1: In every key except `if:` (and a few that implicitly evaluate), e.g. `with:`, `env:`, `run:`, `runs-on`.

Q2: What types exist?
A2: boolean, null, number, string, array, object.

Q3: How does truthiness work?
A3: Falsy: `false`, `0`, `-0`, `''`, `null`. Everything else (including `'false'` string and empty arrays/objects) is truthy.

Q4: What is the difference between expression and shell evaluation?
A4: Expressions run on GitHub's side before the script is created; the shell runs on the runner later. Expression output is pasted into the script text.

Q5: How to debug expressions?
A5: `echo '${{ toJSON(github) }}'` carefully, set `ACTIONS_STEP_DEBUG=true` secret, or re-run with debug logging enabled.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Gating steps/jobs, building cache keys, generating matrices
- Formatting messages and picking values from contexts
- Small decisions based on event data

❌ Avoid when:
- Complex branching (write a script or small action)
- Handling untrusted text inside `run:`
- Heavy data processing (use `jq` in a step)

---

## 📊 Visual Diagram
```
   YAML value:  key: text ${{ expr }} more text
                          |
        +-----------------+------------------+
        | contexts  github.ref, needs.x ...  |
        | operators == != && || ! < >        |
        | functions contains format hashFiles|
        |           fromJSON toJSON success  |
        +-----------------+------------------+
                          v
        evaluated by GitHub (before runner shell)
                          v
   final text: key: text <result> more text  --> step/shell runs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Expression | `${{ }}` computation | `${{ }}` की गणना |
| Literal | Fixed value in expression | Expression में fixed value |
| Truthy/Falsy | Boolean coercion result | Boolean बदलाव का नतीजा |
| Status function | success/failure/always/cancelled | Status जाँचने वाले functions |
| Interpolation | Pasting result into text | Result को text में डालना |

---

## ⚡ 3-Line Summary
English: Expressions are `${{ }}` snippets using contexts, operators and functions, evaluated before the shell.
Strings use single quotes, comparisons ignore case, and there is no ternary.
Pass untrusted results through `env:` to avoid script injection.
Hindi: Expressions `${{ }}` snippets हैं जो contexts, operators और functions इस्तेमाल करते हैं और shell से पहले evaluate होते हैं।
Strings में single quotes, comparisons में case ignore, और ternary नहीं होता।
Script injection से बचने के लिए untrusted results `env:` से पास करो।

---

## ➡️ Next Topic
**271. Expression Syntax ${{ }}** — a deeper look at literals, quoting and evaluation rules.
