---

# 30. pre-commit Hooks
# हिंदी में: pre-commit Hooks (pre-commit framework)

---

## 🔵 Simple Definition (English)
**pre-commit** is a framework (a Python tool) that manages Git hooks for you. You list the checks in a `.pre-commit-config.yaml` file (formatters, linters, secret scanners) and run `pre-commit install`. It downloads each tool in an isolated environment and runs it on staged files before every commit.

## 🔵 सरल परिभाषा (Hindi)
**pre-commit** एक framework (Python tool) है जो आपके लिए Git hooks संभालता है। आप `.pre-commit-config.yaml` में checks (formatter, linter, secret scanner) लिखते हैं और `pre-commit install` चलाते हैं। यह हर tool को अलग environment में download करता है और हर commit से पहले staged files पर चलाता है।

---

## 🔴 Problem it Solves
Writing shell hooks by hand (topic 29) is repetitive, OS-dependent and not shared easily. Each developer needs the right versions of Black, Prettier, ESLint, gitleaks. "Works on my machine" formatting differences create noisy diffs and failed CI. pre-commit gives one declarative, version-pinned config that behaves the same for everyone, in any language.

## 🔴 यह क्यों बना? (Hindi)
Hooks हाथ से shell में लिखना (topic 29) दोहराव वाला है, OS पर निर्भर है और आसानी से share नहीं होता। हर developer को Black, Prettier, ESLint, gitleaks के सही versions चाहिए। "मेरी machine पर चलता है" वाले formatting फ़र्क से गंदे diffs और CI failures होते हैं। pre-commit एक declarative, version-pinned config देता है जो सबके लिए, किसी भी भाषा में, एक जैसा चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install pre-commit   (or pipx install pre-commit / brew install pre-commit)
Step 2 → Create .pre-commit-config.yaml listing repos + rev (pinned tag) + hook ids
Step 3 → pre-commit install       (writes .git/hooks/pre-commit that calls the framework)
Step 4 → git commit               -> pre-commit finds staged files
Step 5 → For each hook: builds an isolated env (cached in ~/.cache/pre-commit), runs on matching files
Step 6 → Hooks that modify files (black, prettier) make the commit FAIL; you `git add` the fixes and commit again
Step 7 → pre-commit run --all-files  (run on whole repo, e.g. in CI)
Step 8 → pre-commit autoupdate    (bump rev tags to latest)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install pre-commit (या pipx / brew)
Step 2 → .pre-commit-config.yaml बनाओ: repos + rev (pinned tag) + hook ids
Step 3 → pre-commit install से .git/hooks/pre-commit लिख जाती है
Step 4 → git commit पर staged files मिलती हैं
Step 5 → हर hook अलग env में (cache में) बनकर matching files पर चलता है
Step 6 → जो hooks files बदलते हैं (black, prettier) वे commit fail कर देते हैं; fix को git add करके फिर commit करो
Step 7 → pre-commit run --all-files पूरे repo पर चलाता है (CI के लिए)
Step 8 → pre-commit autoupdate से rev नए tags पर जाते हैं
```

---

## 🟡 Real World Example
A FastAPI + React monorepo: Python files must pass `black` and `ruff`, frontend must pass `prettier`, and every commit is scanned by `gitleaks` for secrets. New joiner clones the repo, runs `pre-commit install`, and from the first commit gets auto-formatted code. The Pull Request diffs show only real changes, reviewers stop commenting on spaces and quotes. The same config runs in GitHub Actions with `pre-commit run --all-files` so un-hooked commits (made with `--no-verify`) still fail the PR.

## 🟡 Real Example Hindi mein
FastAPI + React monorepo: Python files को `black` और `ruff` पास करना होता है, frontend को `prettier`, और हर commit `gitleaks` से secrets के लिए scan होता है। नया developer repo clone करके `pre-commit install` चलाता है और पहले commit से ही code auto-format होता है। PR diffs में सिर्फ असली बदलाव दिखते हैं, reviewers spaces और quotes पर comment करना बंद कर देते हैं। वही config GitHub Actions में `pre-commit run --all-files` से चलता है, इसलिए `--no-verify` से किए commits भी PR में fail होते हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# .pre-commit-config.yaml  (basic)
# Place at repository root, then run: pre-commit install
repos:                                              # list of hook repositories
  - repo: https://github.com/pre-commit/pre-commit-hooks   # official collection of small checks
    rev: v4.6.0                                     # pinned tag (example, run `pre-commit autoupdate` to refresh)
    hooks:                                          # which hooks from that repo to enable
      - id: trailing-whitespace                     # remove spaces at end of lines
      - id: end-of-file-fixer                       # ensure file ends with one newline
      - id: check-yaml                              # fail on invalid YAML (compose, workflows)
      - id: check-json                              # fail on invalid JSON (package.json)
      - id: check-merge-conflict                    # fail if conflict markers are present
      - id: check-added-large-files                 # block huge files accidentally added
        args: ["--maxkb=1024"]                      # limit 1 MB
      - id: detect-private-key                      # block committing private keys
```

## 💻 Code / Config Example — Advanced

```yaml
# .pre-commit-config.yaml  (production: FastAPI + React + Docker + secrets)
minimum_pre_commit_version: "3.0.0"                 # fail early if team has an old tool
default_install_hook_types: [pre-commit, commit-msg]   # one `pre-commit install` installs both hook types
default_stages: [pre-commit]                        # (older versions call this stage "commit"); default stage for hooks
fail_fast: false                                    # run all hooks even if one fails (see all problems at once)
exclude: '^(node_modules/|dist/|build/|.*\.min\.js$)'   # global regex of paths to skip

repos:                                              # list of sources
  - repo: https://github.com/pre-commit/pre-commit-hooks   # generic hygiene checks
    rev: v4.6.0                                     # pinned (example)
    hooks:
      - id: trailing-whitespace                     # tidy whitespace
      - id: end-of-file-fixer                       # final newline
      - id: check-yaml                              # validate YAML syntax
        args: ["--allow-multiple-documents"]        # needed for k8s manifests with ---
      - id: check-merge-conflict                    # catch leftover markers
      - id: detect-private-key                      # block PEM keys
      - id: no-commit-to-branch                     # local seatbelt: no direct commits to main
        args: ["--branch", "main"]                  # protected branch name

  - repo: https://github.com/psf/black              # Python formatter
    rev: 24.4.2                                     # pinned example
    hooks:
      - id: black                                   # format FastAPI code
        language_version: python3                   # use whichever python3 is installed

  - repo: https://github.com/astral-sh/ruff-pre-commit   # fast Python linter
    rev: v0.4.4                                     # pinned example
    hooks:
      - id: ruff                                    # lint
        args: ["--fix"]                             # auto-fix what it safely can

  - repo: https://github.com/pre-commit/mirrors-prettier   # JS/TS/CSS/JSON/MD formatter
    rev: v3.1.0                                     # pinned example
    hooks:
      - id: prettier                                # format React/Node code
        types_or: [javascript, jsx, ts, tsx, css, json, yaml]   # which file types

  - repo: https://github.com/gitleaks/gitleaks      # secret scanner
    rev: v8.18.4                                    # pinned example
    hooks:
      - id: gitleaks                                # scan staged changes for keys/tokens

  - repo: https://github.com/hadolint/hadolint      # Dockerfile linter
    rev: v2.12.0                                    # pinned example
    hooks:
      - id: hadolint-docker                         # runs hadolint in Docker (needs Docker locally)

  - repo: https://github.com/compilerla/conventional-pre-commit   # commit message format
    rev: v3.2.0                                     # pinned example
    hooks:
      - id: conventional-pre-commit                 # enforce feat:, fix: ...
        stages: [commit-msg]                        # runs on the commit-msg hook type

  - repo: local                                     # hooks defined in your own repo
    hooks:
      - id: eslint                                  # unique id
        name: eslint (frontend)                     # label shown in output
        entry: npx --prefix frontend eslint --max-warnings=0   # command to run (receives file names)
        language: system                            # use tools already installed on the machine
        files: ^frontend/.*\.(js|jsx|ts|tsx)$       # only frontend source files
```
Commands: `pre-commit install` then `pre-commit run --all-files`. (Hook revs and ids above are examples; verify against each project's README. Not run locally here.)

---

## 🟠 My Stack Integration
Put one config at monorepo root. Developers run `pre-commit install` once; CI runs the same hooks so the rules are enforced even if someone bypasses locally.

```yaml
# .github/workflows/pre-commit.yml - enforce the same hooks on every PR
name: pre-commit                           # workflow name
on:
  pull_request:                            # every PR
  push:
    branches: [main]                       # and pushes to main
jobs:
  pre-commit:                              # job id
    runs-on: ubuntu-latest                 # hosted runner
    steps:
      - uses: actions/checkout@v4          # example version
      - uses: actions/setup-python@v5      # Python needed by pre-commit
        with:
          python-version: "3.12"           # example version
      - uses: actions/cache@v4             # cache hook environments
        with:
          path: ~/.cache/pre-commit        # where pre-commit stores envs
          key: pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}   # new cache when config changes
      - run: pip install pre-commit        # install the tool
      - run: pre-commit run --all-files --show-diff-on-failure   # run every hook on every file
```
Security: pin `rev` to a tag (or better a commit SHA) because hooks execute third-party code on your laptop; review new hook repos like any dependency. Add `gitleaks` so secrets are blocked before they reach GitHub.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Cloning the repo and expecting hooks to work without `pre-commit install`.
✅ Correct: Document it in README and add it to the onboarding/`make setup` step.

❌ Mistake 2: Using `rev: main` or `master` (a moving target, non-reproducible).
✅ Correct: Pin a tag/SHA and update deliberately with `pre-commit autoupdate`.

❌ Mistake 3: Panic when the commit fails after black reformats files.
✅ Correct: That is expected: files were modified. `git add -u` and commit again.

❌ Mistake 4: Hooks only local, CI does not run them.
✅ Correct: Run `pre-commit run --all-files` in CI (or use pre-commit.ci) to enforce for all.

---

## 🧠 Tricky Interview Question
Your hook `black` passes locally, but CI `pre-commit run --all-files` fails on a file you never touched. Why?

Answer: Locally pre-commit only checks **staged** files, while `--all-files` checks the whole repo. An old file was never formatted (committed before the hook existed or with `--no-verify`). Fix: run `pre-commit run --all-files` once, commit the formatting change in a separate "style" commit (and add it to `.git-blame-ignore-revs`), so future runs are clean.

---

## ⚫ Interview Questions + Answers

Q1: What is the file name and format of the config?
A1: `.pre-commit-config.yaml` in the repo root; a `repos:` list, each with `repo`, `rev`, and `hooks` (ids).

Q2: How is pre-commit different from husky?
A2: husky is Node-specific and just runs scripts. pre-commit is language-agnostic, installs tools in isolated environments and has a large ecosystem of ready hooks. Teams often use pre-commit in polyglot repos.

Q3: How do you skip one hook once?
A3: `SKIP=black git commit -m "..."` skips only that hook; `--no-verify` skips all.

Q4: What does `language: system` mean?
A4: The hook uses a command already on the user's PATH rather than a managed environment; the developer must install it.

Q5: How to speed up hooks?
A5: Run only on changed files (default), use fast tools (ruff, prettier), avoid heavy tests, cache `~/.cache/pre-commit` in CI.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Team with mixed languages (Python + JS + Docker + YAML)
- You want identical formatting/lint rules for everyone

❌ Avoid when:
- Checks are slow or need services (move them to CI)
- Single-developer tiny script repo where overhead is not worth it

---

## 📊 Visual Diagram
```
 .pre-commit-config.yaml (committed, pinned revs)
            |
   pre-commit install
            v
 git commit --> .git/hooks/pre-commit --> framework
                                           |
              +--------+---------+---------+---------+
              v        v         v         v         v
           black     ruff    prettier  gitleaks  hadolint
              \________ all pass? ________/
                 yes -> commit    no -> blocked (files fixed or errors shown)
 GitHub Actions: pre-commit run --all-files  (same rules, cannot be skipped)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pre-commit framework | Tool that manages multi-language hooks | hooks manager |
| rev | Pinned version/tag of a hook repo | pinned version |
| hook id | Name of a hook inside a repo | hook का नाम |
| --all-files | Run on whole repo | पूरे repo पर चलाना |
| autoupdate | Bump revs to latest | versions अपडेट करना |
| SKIP | Env var to skip chosen hooks | चुने hooks छोड़ना |

---

## ⚡ 3-Line Summary
English: pre-commit manages Git hooks from one YAML file with pinned tool versions.
Run `pre-commit install` locally and `pre-commit run --all-files` in CI.
Pin revs and add a secret scanner for security.
Hindi: pre-commit एक YAML file से pinned tool versions के साथ Git hooks संभालता है।
Local में `pre-commit install` और CI में `pre-commit run --all-files` चलाओ।
Revs pin करो और security के लिए secret scanner जोड़ो।

---

## ➡️ Next Topic
**31. Monorepo vs Polyrepo**: now that tooling is per-repo, decide how many repositories your Node, FastAPI and React code should live in.

---
