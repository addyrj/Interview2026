---

# 29. Git Hooks
# हिंदी में: Git Hooks (Git के स्वचालित scripts)

---

## 🔵 Simple Definition (English)
**Git hooks** are scripts that Git runs automatically at certain moments, such as before a commit (`pre-commit`), when writing a commit message (`commit-msg`) or before a push (`pre-push`). They live in `.git/hooks/` and can stop the action by exiting with a non-zero code.

## 🔵 सरल परिभाषा (Hindi)
**Git hooks** ऐसी scripts हैं जिन्हें Git खास मौकों पर अपने-आप चलाता है, जैसे commit से पहले (`pre-commit`), commit message लिखते समय (`commit-msg`) या push से पहले (`pre-push`)। ये `.git/hooks/` में रहती हैं और non-zero exit code देकर action रोक सकती हैं।

---

## 🔴 Problem it Solves
Developers forget to run lint and tests, commit `console.log`, accidentally commit `.env` or an AWS key, and write messages like "asdf". CI catches this only after the push, wasting minutes and polluting history. Hooks give instant feedback on the developer's laptop, before the bad commit exists.

## 🔴 यह क्यों बना? (Hindi)
Developers lint और tests चलाना भूल जाते हैं, `console.log` या `.env` या AWS key तक commit कर देते हैं, और "asdf" जैसे messages लिखते हैं। CI यह push के बाद पकड़ता है, जिससे समय बर्बाद होता है और history गंदी होती है। Hooks developer के laptop पर ही तुरंत feedback देते हैं, गलत commit बनने से पहले।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run: git commit
Step 2 → Git looks in the hooks directory (.git/hooks or core.hooksPath)
Step 3 → pre-commit script runs (lint staged files, scan secrets)
Step 4 → exit 0 -> continue;  exit non-zero -> commit is CANCELLED
Step 5 → commit-msg hook validates the message (e.g. Conventional Commits)
Step 6 → commit created. Later: git push -> pre-push hook runs tests
Step 7 → Server side: pre-receive/update hooks (self-hosted Git only; GitHub uses branch protection + Actions)
Skip (emergency only): git commit --no-verify
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप git commit चलाते हैं
Step 2 → Git hooks directory (.git/hooks या core.hooksPath) देखता है
Step 3 → pre-commit script चलती है (staged files का lint, secret scan)
Step 4 → exit 0 = आगे बढ़ो; non-zero = commit रद्द
Step 5 → commit-msg hook message का format जाँचती है (Conventional Commits)
Step 6 → commit बनता है। बाद में git push पर pre-push hook tests चलाती है
Step 7 → Server side hooks सिर्फ self-hosted Git पर; GitHub पर branch protection + Actions होते हैं
आपात स्थिति में skip: git commit --no-verify
```

---

## 🟡 Real World Example
A startup shipped a Node.js service whose `.env` with a Razorpay key was committed twice in one month. They added a `pre-commit` hook that blocks files named `.env*` and greps staged changes for `AKIA[0-9A-Z]{16}` (AWS access key pattern). A `commit-msg` hook enforces `feat:`, `fix:` prefixes so the release script can auto-generate changelog. `pre-push` runs `npm test` only for changed packages. Result: zero leaked keys in 6 months, cleaner CI bill.

## 🟡 Real Example Hindi mein
एक startup ने Node.js service में Razorpay key वाली `.env` file एक महीने में दो बार commit कर दी। उन्होंने `pre-commit` hook लगाई जो `.env*` files रोकती है और staged changes में `AKIA[0-9A-Z]{16}` (AWS access key pattern) खोजती है। `commit-msg` hook `feat:`, `fix:` prefix अनिवार्य करती है ताकि release script changelog खुद बना सके। `pre-push` सिर्फ बदले हुए packages के tests चलाती है। नतीजा: 6 महीने में कोई key leak नहीं, CI का खर्च भी कम।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit   (make executable: chmod +x .git/hooks/pre-commit)
# Blocks the commit if .env files are staged or JS files contain console.log

set -euo pipefail                                    # fail fast on any error

# list staged files (Added, Copied, Modified), one per line
STAGED=$(git diff --cached --name-only --diff-filter=ACM)   # only files going into this commit

# --- check 1: never commit env files ---
if echo "$STAGED" | grep -E '(^|/)\.env($|\.)' | grep -v '\.env\.example$'; then   # allow .env.example
  echo "ERROR: .env file staged. Remove it: git restore --staged <file>"          # tell the dev what to do
  exit 1                                             # non-zero = abort commit
fi

# --- check 2: no console.log in JS/TS source ---
JS_FILES=$(echo "$STAGED" | grep -E '\.(js|ts|jsx|tsx)$' || true)   # filter by extension; || true avoids pipefail exit
if [ -n "$JS_FILES" ]; then                          # only if some JS files exist
  # shellcheck disable=SC2086
  if git diff --cached -U0 -- $JS_FILES | grep -E '^\+.*console\.log'; then  # look at ADDED lines only
    echo "ERROR: remove console.log before committing"       # explain
    exit 1                                           # abort
  fi
fi

echo "pre-commit OK"                                 # success message
exit 0                                               # allow commit
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# setup-hooks.sh - share hooks with the whole team (hooks in .git are NOT versioned)
# Idea: keep hooks in ./.githooks (committed) and point Git to that folder.
set -euo pipefail                                    # strict mode

mkdir -p .githooks                                   # versioned hooks folder inside repo

# ---------- commit-msg: Conventional Commits ----------
cat > .githooks/commit-msg <<'EOF'
#!/usr/bin/env bash
# $1 = path to the file containing the commit message
msg_file="$1"                                        # Git passes the message file path
first_line=$(head -n1 "$msg_file")                   # subject line only
pattern='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9-]+\))?!?: .{1,72}$'  # type(scope): text
if ! echo "$first_line" | grep -Eq "$pattern"; then  # does the subject match?
  echo "Bad commit message. Use: type(scope): summary   e.g. feat(api): add otp login"
  exit 1                                             # reject message
fi
EOF

# ---------- pre-push: tests + secret scan before leaving laptop ----------
cat > .githooks/pre-push <<'EOF'
#!/usr/bin/env bash
set -euo pipefail                                    # strict mode
# block pushes straight to main (read: local seatbelt, real protection is GitHub branch protection)
branch=$(git rev-parse --abbrev-ref HEAD)            # current branch name
if [ "$branch" = "main" ]; then                      # direct push to main?
  echo "Do not push directly to main. Open a PR."    # explain
  exit 1                                             # abort push
fi
if [ -f package.json ]; then                         # Node project?
  npm test --silent                                  # run tests, non-zero exit aborts the push
fi
EOF

chmod +x .githooks/commit-msg .githooks/pre-push     # hooks must be executable
git config core.hooksPath .githooks                  # tell Git to use the versioned folder
echo "Hooks installed. Each developer runs this once after clone (or via npm 'prepare' script)."
```

---

## 🟠 My Stack Integration
For Node.js use the `prepare` script so hooks install on `npm install`; for FastAPI use the Python `pre-commit` framework (next topic). Hooks are only a convenience; the real gate is CI on GitHub.

```yaml
# .github/workflows/ci.yml - the SAME checks again on server (hooks can be skipped with --no-verify)
name: CI                                   # name in Actions tab
on:
  pull_request:                            # every PR
    branches: [main]                       # into main
jobs:
  verify:                                  # job id
    runs-on: ubuntu-latest                 # hosted runner
    steps:
      - uses: actions/checkout@v4          # example version
      - uses: actions/setup-node@v4        # Node setup
        with:
          node-version: 20                 # example LTS
          cache: npm                       # cache npm downloads
      - run: npm ci                        # install exactly from lockfile
      - run: npm run lint                  # same lint as the pre-commit hook
      - run: npm test                      # same tests as the pre-push hook
```
In `package.json` add: `"scripts": { "prepare": "git config core.hooksPath .githooks" }`.
Security: hooks run arbitrary code from the repo. When you clone an untrusted repo, Git does NOT auto-enable `.githooks` (you must set `core.hooksPath`), which is why this is safe by default; never run a setup script from a repo you do not trust.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting hooks only in `.git/hooks/` and assuming teammates have them.
✅ Correct: Keep them in a committed folder and set `core.hooksPath` (or use husky / pre-commit framework).

❌ Mistake 2: Forgetting `chmod +x`, so Git silently ignores the hook.
✅ Correct: `chmod +x` and verify with `git commit` printing your message.

❌ Mistake 3: Relying on hooks as the only security control.
✅ Correct: `--no-verify` bypasses them. Repeat checks in CI and enforce with branch protection.

❌ Mistake 4: Slow pre-commit hooks (running the full test suite), so devs bypass them.
✅ Correct: pre-commit = fast (lint staged files, <5 s). Heavy tests go to pre-push or CI.

---

## 🧠 Tricky Interview Question
A developer says "my pre-commit hook exists and is executable but never runs". Name three causes.

Answer: (1) The file has an extension, like `pre-commit.sh`, or a wrong name; Git looks for exact names. (2) `core.hooksPath` points somewhere else, so `.git/hooks` is ignored. (3) Missing or wrong shebang (`#!/usr/bin/env bash`) or Windows line endings (CRLF) break execution. Also: running commit from a GUI client that uses `--no-verify`, or using `git commit --no-verify` in an alias.

---

## ⚫ Interview Questions + Answers

Q1: Where are hooks stored and are they version controlled?
A1: In `.git/hooks/`, which is not versioned. To share, store scripts in the repo and set `git config core.hooksPath <dir>`.

Q2: Name the common client-side hooks.
A2: `pre-commit`, `prepare-commit-msg`, `commit-msg`, `post-commit`, `pre-rebase`, `post-merge`, `pre-push`.

Q3: How does a hook stop a commit?
A3: By exiting with a non-zero status. Exit 0 lets it proceed.

Q4: Client-side vs server-side hooks?
A4: Client-side run on the developer machine and can be bypassed. Server-side (`pre-receive`, `update`) run on the Git server and enforce rules for everyone; on GitHub you use branch protection and Actions instead.

Q5: How do you skip hooks and when is it OK?
A5: `git commit --no-verify` / `git push --no-verify`. Only for emergencies (e.g., broken hook), and CI must still validate.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Fast checks: formatting, lint, secret scan, commit message format
- You want feedback before pushing to save CI minutes

❌ Avoid when:
- The check is slow (full integration tests) or needs network/services
- You treat them as the only enforcement; they are advisory

---

## 📊 Visual Diagram
```
 git commit
     |
     v
 [pre-commit]  --exit 1--> COMMIT BLOCKED
     | exit 0
     v
 [commit-msg]  --exit 1--> COMMIT BLOCKED
     | exit 0
     v
  commit created
     |
 git push
     v
 [pre-push]    --exit 1--> PUSH BLOCKED
     | exit 0
     v
   GitHub  --> CI (Actions) re-checks everything (cannot be skipped)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hook | Script Git runs on an event | event पर चलने वाली script |
| pre-commit | Runs before commit is created | commit से पहले |
| commit-msg | Validates the message | message की जाँच |
| pre-push | Runs before push | push से पहले |
| core.hooksPath | Custom hooks folder setting | hooks folder की setting |
| --no-verify | Skip hooks | hooks छोड़ना |

---

## ⚡ 3-Line Summary
English: Hooks are scripts Git runs at events like commit and push; a non-zero exit blocks the action.
Store them in a committed folder and set `core.hooksPath` so the whole team uses them.
They can be skipped, so always repeat checks in CI.
Hindi: Hooks वे scripts हैं जो commit और push जैसे events पर चलती हैं; non-zero exit action रोक देता है।
इन्हें repo के folder में रखो और `core.hooksPath` set करो ताकि पूरी team इस्तेमाल करे।
इन्हें skip किया जा सकता है, इसलिए CI में वही checks दोबारा चलाओ।

---

## ➡️ Next Topic
**30. pre-commit Hooks**: a ready-made framework that manages hooks for Python/Node projects without writing shell scripts by hand.

---
