# 300. Custom Actions (JS + Docker)
# हिंदी में: Custom Actions (JavaScript और Docker)

---

## 🔵 Simple Definition (English)
A **custom action** is your own reusable unit of work for GitHub Actions, defined by an `action.yml`. Two code-based types exist:
- **JavaScript action** (`using: node20`): runs directly on the runner, fast start.
- **Docker container action** (`using: docker`): runs inside a container image, any language, Linux runners only.
(The third type, composite, only groups steps.)

## 🔵 सरल परिभाषा (Hindi)
**Custom action** GitHub Actions के लिए आपकी अपनी reusable इकाई है, जो `action.yml` से define होती है। Code वाले दो types हैं:
- **JavaScript action** (`using: node20`): सीधे runner पर चलती है, तेज़ शुरू होती है।
- **Docker container action** (`using: docker`): container image के अंदर चलती है, कोई भी language, सिर्फ Linux runners पर।
(तीसरा type composite सिर्फ steps को group करता है।)

---

## 🔴 Problem it Solves
Shell steps become unreadable when you need real logic: call an API, parse JSON, compare versions, post a PR comment. You also want typed inputs, unit tests, versioning (`@v1`), and sharing across the organization. Shell-in-YAML gives none of that.
Docker actions additionally let you ship a tool with exact dependencies (Python 3.12 + a scanner binary) so it behaves the same everywhere.

## 🔴 यह क्यों बना? (Hindi)
जब असली logic चाहिए (API call, JSON parse, versions compare, PR पर comment) तब YAML में shell steps पढ़ने लायक नहीं रहते। आपको typed inputs, unit tests, versioning (`@v1`) और organization में sharing भी चाहिए। YAML के shell में यह सब नहीं मिलता।
Docker actions से आप tool को उसकी सटीक dependencies (Python 3.12 + scanner binary) के साथ ship कर सकते हैं, जो हर जगह एक जैसा चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create repo (or folder) with action.yml at its root
Step 2 → JS action: runs.using: node20, runs.main: dist/index.js
         Docker action: runs.using: docker, runs.image: Dockerfile
Step 3 → Inputs arrive as env vars:  INPUT_<NAME> (uppercase, spaces->_)
Step 4 → Outputs: append "name=value" to the file at $GITHUB_OUTPUT
Step 5 → Failure: exit code non-zero (or core.setFailed in toolkit)
Step 6 → Commit built code (JS: bundle node_modules with ncc/esbuild into dist/)
Step 7 → Tag release v1.0.0, move floating tag v1; callers use  owner/repo@v1
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → repo (या folder) बनाओ जिसकी root में action.yml हो
Step 2 → JS action: runs.using: node20, runs.main: dist/index.js
         Docker action: runs.using: docker, runs.image: Dockerfile
Step 3 → Inputs env vars के रूप में आते हैं:  INPUT_<NAME> (uppercase, space->_)
Step 4 → Outputs: $GITHUB_OUTPUT वाली file में "name=value" append करो
Step 5 → Failure: non-zero exit code (या toolkit का core.setFailed)
Step 6 → Built code commit करो (JS: ncc/esbuild से node_modules को dist/ में bundle)
Step 7 → v1.0.0 tag release करो, floating tag v1 आगे बढ़ाओ; callers  owner/repo@v1 लिखते हैं
```

---

## 🟡 Real World Example
A team wants every PR to fail if `package.json` version was not bumped. They write a small JS action `check-version-bump` (reads two JSON files, compares semver, exits 1 if equal). Another team has a Python-based license scanner that needs a pinned binary; they ship it as a Docker action `acme/license-scan@v2`. Both are used by 40 repos.

## 🟡 Real Example Hindi mein
एक team चाहती है कि अगर `package.json` का version bump नहीं हुआ तो PR fail हो। वे छोटी JS action `check-version-bump` लिखते हैं (दो JSON files पढ़ती है, semver compare करती है, बराबर हो तो exit 1)। दूसरी team के पास Python-based license scanner है जिसे pinned binary चाहिए; वे उसे Docker action `acme/license-scan@v2` बनाकर ship करते हैं। दोनों 40 repos में इस्तेमाल होती हैं।

---

## 💻 Code / Config Example — Basic
```yaml
# action.yml  (JavaScript action)
name: "Greeter"                         # display name
description: "Greets a user and returns the greeting length"
inputs:
  who-to-greet:                         # becomes env INPUT_WHO-TO-GREET
    description: "Person to greet"
    required: true                      # caller must pass it
    default: "World"
outputs:
  length:                               # output name
    description: "Length of greeting"
runs:
  using: "node20"                       # Node runtime provided by the runner
  main: "index.js"                      # entry file
```

```javascript
// index.js  (no dependencies; uses only Node built-ins so it runs as-is)
const fs = require('fs');                                     // to write outputs
const who = process.env['INPUT_WHO-TO-GREET'] || 'World';     // read input (dash kept, name uppercased)
const greeting = `Hello, ${who}!`;                            // build message
console.log(greeting);                                        // goes to step log
fs.appendFileSync(process.env.GITHUB_OUTPUT, `length=${greeting.length}\n`); // set output
```

## 💻 Code / Config Example — Advanced
```yaml
# action.yml  (Docker container action)
name: "Health Probe"
description: "Calls a URL N times and fails if success ratio is low"
author: "platform-team"
inputs:
  url:
    description: "URL to probe"
    required: true
  attempts:
    description: "How many requests"
    required: false
    default: "5"
outputs:
  success-count:
    description: "Number of 2xx responses"
runs:
  using: "docker"                       # container action (Linux runner only)
  image: "Dockerfile"                   # build image from this Dockerfile on each run
  args:                                 # passed as CMD arguments
    - ${{ inputs.url }}
    - ${{ inputs.attempts }}
branding:                               # icon in Marketplace
  icon: "activity"
  color: "green"
```

```dockerfile
# Dockerfile  (for the Docker action)
FROM python:3.12-slim                   # small base image (example tag, update)
RUN useradd -m probe                    # create non-root user (see notes below)
COPY probe.py /probe.py                 # copy script into image
ENTRYPOINT ["python", "/probe.py"]      # run script; args come from action.yml
```
Note: GitHub mounts the workspace and `GITHUB_OUTPUT` into the container as root-owned paths, and the official docs recommend NOT setting `USER` in the Dockerfile because file permissions for the workspace would break. So the `useradd` line above only prepares a user; do not add `USER probe` unless you tested file access.

```python
# probe.py  (the Docker action's code, standard library only)
import os, sys, urllib.request                      # stdlib imports

url, attempts = sys.argv[1], int(sys.argv[2])       # args from action.yml
ok = 0                                              # counter of good responses
for _ in range(attempts):                           # loop N times
    try:
        with urllib.request.urlopen(url, timeout=5) as r:   # GET with timeout
            ok += 1 if 200 <= r.status < 300 else 0         # count 2xx
    except Exception as e:                          # network error or non-2xx
        print(f"::warning::request failed: {e}")    # workflow command: warning
with open(os.environ["GITHUB_OUTPUT"], "a") as f:   # write output file
    f.write(f"success-count={ok}\n")
if ok < attempts * 0.8:                             # less than 80% success
    print(f"::error::only {ok}/{attempts} succeeded")   # error annotation
    sys.exit(1)                                     # fail the step
```

```yaml
# caller workflow using both actions
name: Verify
on: [workflow_dispatch]                 # manual trigger
jobs:
  probe:
    runs-on: ubuntu-latest              # Docker actions need Linux
    steps:
      - uses: actions/checkout@v4       # required for ./ local actions
      - id: p
        uses: ./.github/actions/health-probe   # local Docker action
        with:
          url: https://example.com/health
          attempts: "10"
      - run: echo "ok=${{ steps.p.outputs.success-count }}"
```

---

## 🟠 My Stack Integration
- **Node.js:** JS action to compare `package.json` versions, or post bundle-size diff on PRs. Bundle with `npx @vercel/ncc build index.js -o dist` (example tool) so `node_modules` need not be committed.
- **FastAPI:** Docker action that runs `schemathesis` or an OpenAPI diff with fixed Python deps.
- **React:** JS action uploading Lighthouse results as PR comment.
- **VPS / Nginx:** Docker action that SSH-checks `nginx -t` on the VPS before reload.
- **AWS:** use JS action `aws-actions/*` patterns; never bake AWS keys into an image; use OIDC and env vars.

```yaml
# using your published action from another repo in the release pipeline
      - uses: acme/health-probe@v1          # pinned major tag
        with:
          url: https://api.example.com/health   # public health endpoint behind Nginx
          attempts: "10"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using a JS action without committing `node_modules` or a bundled `dist/`. It fails with "Cannot find module".
✅ Correct: Bundle with ncc/esbuild and commit `dist/`, and add a CI check that `dist/` is up to date.

❌ Mistake 2: Using `set-output` / `save-state` workflow commands (`::set-output`). They are deprecated and disabled.
✅ Correct: Append to `$GITHUB_OUTPUT` / `$GITHUB_STATE`.

❌ Mistake 3: Choosing a Docker action for everything. It builds the image on every run (slow) and does not work on Windows/macOS runners.
✅ Correct: Prefer JS actions for speed; use `image: docker://ghcr.io/org/tool:1.2` (prebuilt) when you must use Docker.

❌ Mistake 4: Expecting inputs with dashes to be easy in env: `INPUT_WHO-TO-GREET` is awkward in shell.
✅ Correct: Use simple names (`name`) or read via toolkit `core.getInput('who-to-greet')`.

❌ Mistake 5: Publishing with `@main` usage or moving tags silently.
✅ Correct: Semantic version tags, floating `v1` for minor/patch, SHA pinning for high-trust pipelines.

---

## 🧠 Tricky Interview Question
**Q:** Your Docker action works on `ubuntu-latest` but a teammate runs the same workflow on `windows-latest` and it fails immediately. Why, and what are the options?

**Answer:** Docker container actions only run on Linux runners (the runner must be able to run Linux containers). On Windows/macOS GitHub-hosted runners there is no Linux container support for actions. Options: rewrite as a JavaScript action (cross-platform), make it a composite action using a cross-platform tool, or restrict the job to `runs-on: ubuntu-latest`.

---

## ⚫ Interview Questions + Answers

Q1: JS vs Docker vs composite action: how to choose?
A1: Composite for step bundles; JS for fast cross-platform logic; Docker when you need specific language/tools/OS packages and are fine with Linux only and slower start.

Q2: How do inputs reach a JS action?
A2: As env vars `INPUT_<UPPERCASE_NAME>` (spaces become underscores, dashes are kept). The `@actions/core` toolkit's `getInput` reads them for you.

Q3: How do you fail an action and write a log annotation?
A3: Exit with non-zero code or `core.setFailed(msg)`; for annotations print `::error::msg`, `::warning::msg`, `::notice::msg`.

Q4: What are `pre` and `post` in JS actions?
A4: Optional entry points: `runs.pre` runs before `main`, `runs.post` after the job (for cleanup, e.g. stop a daemon). `pre-if`/`post-if` control when they run.

Q5: Security considerations when publishing actions?
A5: Pin dependencies, keep a lockfile, review third-party actions, never log secrets (use `::add-mask::`), do not echo untrusted input into shell, use least privilege token permissions, and tell users to pin your action by SHA.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Logic is too complex for shell (APIs, parsing, comparison)
- You want a versioned, tested, shareable tool
- Docker: you need exact OS packages or a non-JS language

❌ Avoid when:
- A 3-step composite action is enough
- You need Windows/macOS support and chose Docker
- Only one workflow uses it once (inline script is simpler)

---

## 📊 Visual Diagram
```
 workflow step:  uses: acme/tool@v1  with: {url: ...}
                     |
                     v
        runner downloads repo at tag v1, reads action.yml
                     |
        +------------+-------------+
        |                          |
   using: node20              using: docker
        |                          |
  node dist/index.js        docker build / pull image
  (runs on host runner)     docker run -e INPUT_URL=... image args
        |                          |
        +------------+-------------+
                     v
       writes  name=value >> $GITHUB_OUTPUT
       exit 0 = success   exit != 0 = step fails
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `action.yml` | Action metadata/entry point | action की metadata |
| `runs.using` | `node20`, `docker`, or `composite` | action का type |
| `INPUT_*` | Env vars carrying inputs | inputs वाले env vars |
| `GITHUB_OUTPUT` | File for step outputs | outputs की file |
| `ncc` | Bundler to build single JS file | single file bundler |
| `pre` / `post` | Setup/cleanup entry points | पहले / बाद के entry points |
| Floating tag | Tag like `v1` moved to latest | आगे बढ़ने वाला tag |

---

## ⚡ 3-Line Summary
English: Custom actions are code-based reusable steps defined by `action.yml`, as JavaScript (fast, cross-platform) or Docker (any language, Linux only).
Inputs arrive as `INPUT_*` env vars and outputs go to `$GITHUB_OUTPUT`.
Bundle JS into `dist/`, version with tags, and pin by SHA in sensitive pipelines.
Hindi: Custom actions `action.yml` से define होने वाले code-based reusable steps हैं: JavaScript (तेज़, cross-platform) या Docker (कोई भी language, सिर्फ Linux)।
Inputs `INPUT_*` env vars में आते हैं और outputs `$GITHUB_OUTPUT` में जाते हैं।
JS को `dist/` में bundle करें, tags से version करें, और संवेदनशील pipelines में SHA से pin करें।

---

## ➡️ Next Topic
**301. CI Pipeline — Complete Guide** — now that you know every GitHub Actions building block, we assemble them into a full CI pipeline.
