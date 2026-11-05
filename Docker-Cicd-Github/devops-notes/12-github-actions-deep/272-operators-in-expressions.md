# 272. Operators in Expressions
# हिंदी में: Expressions में Operators

---

## 🔵 Simple Definition (English)
Operators are the symbols you use inside `${{ }}` or `if:` to compare and combine values: `( )`, `[ ]`, `.`, `!`, `<`, `<=`, `>`, `>=`, `==`, `!=`, `&&`, `||`.
They turn raw context values into true/false decisions or choose between two values.

## 🔵 सरल परिभाषा (Hindi)
Operators वे symbols हैं जो `${{ }}` या `if:` के अंदर values को compare और combine करने के लिए use होते हैं: `( )`, `[ ]`, `.`, `!`, `<`, `<=`, `>`, `>=`, `==`, `!=`, `&&`, `||`।
ये raw context values को true/false decision में बदलते हैं, या दो values में से एक चुनते हैं।

---

## 🔴 Problem it Solves
Reading `github.ref` alone does nothing. You need "is it main AND is it a push AND is the actor not dependabot". Without operators, you would write shell `if` blocks inside every step and the job would still start, wasting runner minutes. Operators let GitHub skip steps/jobs before they start.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ `github.ref` पढ़ने से कुछ नहीं होता। आपको चाहिए "main है AND push है AND actor dependabot नहीं है"। Operators के बिना हर step में shell `if` लिखना पड़ता और job फिर भी start होकर runner minutes खर्च करता। Operators से GitHub steps/jobs को शुरू होने से पहले skip कर देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Context values are read:  github.ref = 'refs/heads/main'
Step 2 → Comparison operators give booleans: (ref == 'refs/heads/main') -> true
Step 3 → Logical operators combine them:   true && (actor != 'dependabot[bot]')
Step 4 → && and || short-circuit: stop as soon as result is known
Step 5 → || also returns the first truthy VALUE (used as a default): inputs.env || 'staging'
Step 6 → Final truthy/falsy decides if the step/job runs
```

Rules to remember: string comparison is case-insensitive; type mismatch coerces to numbers; falsy values are `false`, `0`, `-0`, `''`, `null`.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Context values पढ़ी जाती हैं:  github.ref = 'refs/heads/main'
Step 2 → Comparison operators boolean देते हैं
Step 3 → Logical operators उन्हें जोड़ते हैं:   true && (actor != 'dependabot[bot]')
Step 4 → && और || short-circuit करते हैं: result पता चलते ही रुक जाते हैं
Step 5 → || पहली truthy VALUE भी return करता है (default के लिए): inputs.env || 'staging'
Step 6 → आखिर में truthy/falsy तय करता है कि step/job चलेगा या नहीं
```

याद रखें: string comparison case-insensitive है; type अलग हो तो numbers में convert होता है; falsy values हैं `false`, `0`, `-0`, `''`, `null`।

---

## 🟡 Real World Example
Zomato-style deploy pipeline: deploy to production only when it is a push to `main`, the tests job succeeded, and the commit message does not contain `[skip deploy]`. Hotfix branches (`hotfix/*`) may deploy to staging. Operators `&&`, `||`, `!` combine these rules in one `if:` line.

## 🟡 Real Example Hindi mein
Zomato जैसा deploy pipeline: production में deploy तभी हो जब `main` पर push हुआ हो, tests job सफल रहा हो, और commit message में `[skip deploy]` न हो। Hotfix branches (`hotfix/*`) staging में deploy हो सकती हैं। `&&`, `||`, `!` operators ये सारे rules एक `if:` line में जोड़ते हैं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/operators-basic.yml
name: operators-basic                  # workflow name

on: [push]                             # trigger on every push

jobs:
  check:
    runs-on: ubuntu-latest             # runner
    steps:
      - name: equality
        if: github.ref == 'refs/heads/main'          # == compares (case-insensitive)
        run: echo "on main"                          # runs only on main

      - name: not equal
        if: github.actor != 'dependabot[bot]'        # != means different
        run: echo "human push"                       # skipped for dependabot

      - name: negation
        if: ${{ !startsWith(github.ref, 'refs/tags/') }}  # ! flips boolean
        run: echo "not a tag push"                   # runs on branches only

      - name: AND
        if: github.event_name == 'push' && github.ref_name == 'main'  # both true
        run: echo "push to main"                     # needs both conditions

      - name: OR
        if: github.ref_name == 'main' || github.ref_name == 'develop' # either one
        run: echo "long-lived branch"                # main or develop

      - name: grouping
        if: (github.ref_name == 'main' || github.ref_name == 'develop') && github.event_name == 'push'
        run: echo "push to main or develop"          # parentheses control order
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/operators-advanced.yml
name: operators-advanced               # workflow name

on:
  workflow_dispatch:                   # manual trigger with inputs
    inputs:
      target:
        description: "staging or production"   # shown in UI
        required: false                # optional input
        default: ""                    # empty means "not provided"
      replicas:
        description: "number of replicas"
        required: false
        default: "2"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4      # example version
      - run: echo "tests ok"           # placeholder for npm test / pytest

  deploy:
    needs: test                        # run after test
    # Run only if tests passed, ref is main OR hotfix/*, and message lacks skip tag
    if: >-
      needs.test.result == 'success' &&
      (github.ref_name == 'main' || startsWith(github.ref_name, 'hotfix/')) &&
      !contains(github.event.head_commit.message, '[skip deploy]')
    runs-on: ubuntu-latest
    env:
      # || returns first truthy value => default to 'staging' when input is empty
      TARGET: ${{ inputs.target || 'staging' }}
      # ternary-style idiom: cond && a || b (works only when a is truthy)
      TAG: ${{ github.ref_name == 'main' && 'stable' || 'canary' }}
      # numeric comparison: string '2' is coerced to number
      BIG: ${{ fromJSON(inputs.replicas || '2') > 3 }}
    steps:
      - name: Show decisions
        run: |
          echo "target=$TARGET tag=$TAG big=$BIG"   # shell reads env values
```
Not run locally; YAML parse checked only. The `workflow_dispatch` inputs are empty on push events, which is why the `||` default matters.

---

## 🟠 My Stack Integration
Typical rule for a Node.js API + React frontend on one VPS: build both on every push, deploy only for `main`, and deploy the frontend only when files under `frontend/` changed (path filters are better, but operators help for manual runs).

```yaml
# snippet: deploy gates for the VPS
  deploy-vps:
    needs: [test-api, test-web]        # both suites must pass
    if: |                              # multi-line if, all inside one expression
      github.event_name == 'push' &&
      github.ref == 'refs/heads/main' &&
      needs.test-api.result == 'success' &&
      needs.test-web.result == 'success'
    runs-on: ubuntu-latest
    steps:
      - run: echo "ssh to VPS, docker compose pull, up -d, nginx -s reload"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Relying on case-sensitivity: `github.ref_name == 'Main'` still matches `main`.
✅ Correct: Remember comparisons ignore case; use exact naming rules or `format()`/scripts if case matters.

❌ Mistake 2: `a && 'x' || 'y'` when `'x'` could be falsy (empty string or 0) - result falls to `'y'`.
✅ Correct: Make sure the middle value is always truthy, or use separate steps.

❌ Mistake 3: Comparing arrays/objects with `==` (they compare by reference, so always false).
✅ Correct: Compare `toJSON(a) == toJSON(b)` or compare specific fields.

❌ Mistake 4: Forgetting `needs.job.result` when a needed job was skipped; `success()` default fails.
✅ Correct: Use `always() && needs.x.result == 'success'` or `!failure() && !cancelled()` explicitly.

---

## 🧠 Tricky Interview Question
`if: github.event.inputs.dry_run == false` never skips the step when you set dry_run to false in the UI. Why?

Answer: `workflow_dispatch` inputs arrive as strings (`'false'`), not booleans, in the `github.event.inputs` context. `'false' == false` coerces: boolean becomes number 0, the string `'false'` becomes NaN, so the comparison is false. Use `inputs.dry_run` (typed boolean input) or compare to the string `'false'`.

---

## ⚫ Interview Questions + Answers

Q1: List the comparison and logical operators.
A1: `<`, `<=`, `>`, `>=`, `==`, `!=` for comparison; `!`, `&&`, `||` for logic; `( )` grouping; `.` and `[ ]` for property access.

Q2: Is `==` case-sensitive?
A2: No, string comparisons ignore case.

Q3: What does `||` return?
A3: Not just a boolean. It returns the first truthy operand (or the last operand), so `inputs.x || 'default'` works as a default.

Q4: What is falsy?
A4: `false`, `0`, `-0`, `''`, `""` (empty string) and `null`. Objects and arrays are always truthy.

Q5: How do you write a ternary?
A5: There is no `?:`. Use `cond && valueIfTrue || valueIfFalse` and make sure valueIfTrue is truthy.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Gating deploy steps by branch, event, actor, job result.
- Providing default values with `||`.
- Choosing a value (tag, environment) from a condition.

❌ Avoid when:
- Logic exceeds 3-4 conditions: move to a script or reusable workflow.
- You need real regex or arithmetic (no such operators; use shell).

---

## 📊 Visual Diagram
```
 precedence (high -> low)
 ( )  .  [ ]      grouping / property access
 !                negation
 < <= > >=        ordering
 == !=            equality
 &&               AND  (short-circuit)
 ||               OR   (short-circuit, returns first truthy)

 github.ref=='refs/heads/main'  --true--+
                                         &&--> true --> step runs
 needs.test.result=='success'   --true--+
        any false  ------------------------> step SKIPPED
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Operator | Symbol that compares/combines values | Values compare/combine करने वाला symbol |
| Short-circuit | Stop evaluating once result is known | Result पता चलते ही रुकना |
| Truthy / Falsy | Value treated as true / false | True / False माना जाने वाला value |
| Coercion | Automatic type conversion | अपने-आप type बदलना |
| Grouping | `( )` to set order | क्रम तय करना |

---

## ⚡ 3-Line Summary
English: Operators compare and combine context values to gate steps and jobs.
`==` ignores case; `||` returns the first truthy value, so it gives defaults.
There is no ternary; use `cond && a || b` with a truthy `a`.

Hindi: Operators context values को compare और combine करके steps/jobs को gate करते हैं।
`==` case ignore करता है; `||` पहली truthy value देता है, इसलिए default देने में काम आता है।
Ternary नहीं है; `cond && a || b` use करो, जहाँ `a` truthy हो।

---

## ➡️ Next Topic
**273. Functions in Expressions** — operators are the grammar; functions (`contains`, `startsWith`, `format`, `toJSON`, `hashFiles`, status checks) are the vocabulary.
