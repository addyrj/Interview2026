# 267. runner Context
# हिंदी में: runner Context

---

## 🔵 Simple Definition (English)
The `runner` context describes the machine currently executing the job: `runner.os` (Linux, Windows, macOS), `runner.arch` (X86, X64, ARM, ARM64), `runner.name`, `runner.temp`, `runner.tool_cache`, `runner.environment` (github-hosted or self-hosted) and `runner.debug`. It exists only inside steps, because a runner must already be assigned.

## 🔵 सरल परिभाषा (Hindi)
`runner` context उस machine का वर्णन करता है जो अभी job चला रही है: `runner.os` (Linux, Windows, macOS), `runner.arch` (X86, X64, ARM, ARM64), `runner.name`, `runner.temp`, `runner.tool_cache`, `runner.environment` (github-hosted या self-hosted) और `runner.debug`। यह सिर्फ steps के अंदर मिलता है क्योंकि runner पहले से assign होना चाहिए।

---

## 🔴 Problem it Solves
One workflow often runs on Linux, macOS and Windows, or on both x64 and ARM machines (for example Graviton servers on AWS). File paths, cache keys, binary downloads and shell syntax differ per OS. Hard-coding `/tmp` or `linux-amd64` breaks other runners. The `runner` context lets one YAML adapt without guessing.

## 🔴 यह क्यों बना? (Hindi)
एक workflow अक्सर Linux, macOS और Windows पर, या x64 और ARM दोनों (जैसे AWS Graviton servers) पर चलता है। File paths, cache keys, binary downloads और shell syntax हर OS पर अलग होते हैं। `/tmp` या `linux-amd64` hard-code करने से दूसरे runners पर टूटता है। `runner` context से एक YAML बिना अंदाज़े के खुद को adapt कर लेता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Job is queued with runs-on: label(s)
Step 2 → GitHub picks a matching runner (hosted VM or your self-hosted machine)
Step 3 → Runner agent starts the job and reports its facts
Step 4 → runner.os / arch / name / temp / tool_cache are filled in
Step 5 → Steps read ${{ runner.* }} (also $RUNNER_OS, $RUNNER_TEMP in shell)
Step 6 → Job ends; hosted runner is wiped, self-hosted keeps its disk state
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Job runs-on: label(s) के साथ queue में आता है
Step 2 → GitHub मेल खाता runner चुनता है (hosted VM या आपकी self-hosted machine)
Step 3 → Runner agent job शुरू करके अपनी जानकारी देता है
Step 4 → runner.os / arch / name / temp / tool_cache भर जाते हैं
Step 5 → Steps ${{ runner.* }} पढ़ते हैं (shell में $RUNNER_OS, $RUNNER_TEMP भी)
Step 6 → Job खत्म; hosted runner मिटा दिया जाता है, self-hosted की disk state बची रहती है
```

---

## 🟡 Real World Example
A CLI tool for your VPS is released as binaries for Linux x64, Linux ARM64 and macOS. The build matrix uses `runner.os` and `runner.arch` to name artifacts (`mytool-Linux-ARM64`). A self-hosted runner in your office (Bengaluru) with a GPU is detected by `runner.environment == 'self-hosted'` to skip downloading huge models already cached locally.

## 🟡 Real Example Hindi mein
आपके VPS के CLI tool की binaries Linux x64, Linux ARM64 और macOS के लिए release होती हैं। Build matrix artifacts का नाम (`mytool-Linux-ARM64`) `runner.os` और `runner.arch` से बनाता है। Office (Bengaluru) में GPU वाला self-hosted runner `runner.environment == 'self-hosted'` से पहचाना जाता है ताकि local cache में पड़े बड़े models दोबारा download न हों।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/runner-basic.yml
name: runner-basic                     # workflow name
on: workflow_dispatch                  # manual
jobs:
  info:
    strategy:
      matrix:
        os: [ubuntu-24.04, macos-14, windows-2022]   # example hosted labels, update over time
    runs-on: ${{ matrix.os }}          # choose runner from matrix
    steps:
      - name: Show runner facts        # works on all three OSes
        shell: bash                    # force bash (Windows has Git Bash)
        run: |                         # script
          echo "os    : ${{ runner.os }}"            # Linux / macOS / Windows
          echo "arch  : ${{ runner.arch }}"          # X64 / ARM64 ...
          echo "name  : ${{ runner.name }}"          # e.g. GitHub Actions 12
          echo "env   : ${{ runner.environment }}"   # github-hosted
          echo "temp  : ${{ runner.temp }}"          # cleaned per job
          echo "tools : ${{ runner.tool_cache }}"    # preinstalled tools
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/runner-advanced.yml
name: cross-platform-build             # per-OS artifacts + cache
on:
  push:
    branches: [main]                   # build on main
jobs:
  build:
    strategy:
      fail-fast: false                 # let all platforms finish
      matrix:
        include:
          - { os: ubuntu-24.04, target: linux-x64 }       # example labels
          - { os: ubuntu-24.04-arm, target: linux-arm64 } # ARM hosted label (check availability)
          - { os: macos-14, target: darwin-arm64 }        # Apple silicon
    runs-on: ${{ matrix.os }}          # pick runner
    steps:
      - uses: actions/checkout@v4      # source
      - uses: actions/setup-node@v4    # Node
        with: { node-version: 20 }     # inline map
      - uses: actions/cache@v4         # example version
        with:
          path: ~/.npm                 # npm cache dir
          # key includes OS + arch so binaries for one platform are never reused on another
          key: ${{ runner.os }}-${{ runner.arch }}-npm-${{ hashFiles('**/package-lock.json') }}
          restore-keys: ${{ runner.os }}-${{ runner.arch }}-npm-   # fallback prefix
      - name: Build                    # use runner-specific temp dir
        shell: bash                    # same script everywhere
        run: |                         # script
          npm ci                       # install
          npm run build -- --out "${{ runner.temp }}/out"   # temp dir exists on every OS
      - uses: actions/upload-artifact@v4   # upload result
        with:
          name: app-${{ matrix.target }}-${{ runner.os }}  # unique per platform
          path: ${{ runner.temp }}/out     # build output
      - name: Self-hosted hygiene      # only for your own machines
        if: runner.environment == 'self-hosted'
        run: docker system prune -f --filter "until=24h"   # remove old Docker data
```
Parsed as YAML locally; runner labels (especially ARM hosted labels) change, confirm in GitHub docs; not executed.

---

## 🟠 My Stack Integration
- **Node.js / React**: cache key = `runner.os` + lock hash; native modules (like `bcrypt`) are OS/arch specific.
- **FastAPI**: pip cache dir differs per OS; use `actions/setup-python` `cache: pip` which handles it.
- **Nginx/VPS**: build a Linux ARM64 Docker image when the VPS is Graviton: `docker buildx --platform linux/arm64` (QEMU on x64 runner is slow; use native ARM runner when possible).
- **AWS**: self-hosted runner on EC2 inside your VPC to reach private RDS; `runner.environment` tells hosted vs self-hosted.
- **Security**: self-hosted runners persist state between jobs. Never use them for public repos or untrusted PRs, and run them ephemeral (one job per VM/container).

```yaml
      - name: Fail if a private-network job lands on hosted runner   # safety check
        if: runner.environment != 'self-hosted'
        run: echo "This job needs the VPC runner" && exit 1          # stop wrong placement
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `runner.os` in `runs-on`.
✅ Correct: The `runner` context is unavailable in `runs-on` (no runner yet). Use `matrix` or `inputs`.

❌ Mistake 2: Hard-coding `/tmp` or `C:\temp`.
✅ Correct: Use `${{ runner.temp }}` / `$RUNNER_TEMP`.

❌ Mistake 3: Cache key without arch.
✅ Correct: Include `runner.arch` when caches contain compiled binaries.

❌ Mistake 4: Comparing `runner.os == 'linux'`.
✅ Correct: Values are `Linux`, `Windows`, `macOS`. Expression string comparison is case-insensitive, but the shell `$RUNNER_OS` comparison is not.

❌ Mistake 5: Assuming self-hosted runners are clean.
✅ Correct: Clean workspace, use ephemeral runners, and avoid leaving credentials on disk.

---

## 🧠 Tricky Interview Question
Why can't you write `runs-on: ${{ runner.os }}` and how do you run one job on different OSes?

Answer: `runs-on` selects the runner, so the `runner` context cannot exist yet. Use a build matrix: `strategy.matrix.os: [ubuntu-24.04, windows-2022]` with `runs-on: ${{ matrix.os }}`. Inside the job, `runner.os` then confirms what you got and drives conditional steps.

---

## ⚫ Interview Questions + Answers

Q1: Name `runner` context properties.
A1: name, os, arch, temp, tool_cache, debug, environment.

Q2: What is `runner.temp`?
A2: A per-job temporary directory emptied at job start/end; do not use it for persistent data.

Q3: Hosted vs self-hosted differences?
A3: Hosted: fresh VM per job, managed images, per-minute billing for private repos. Self-hosted: your hardware, persistent, you manage security and updates, access to private network.

Q4: What is `runner.debug`?
A4: `1` when debug logging is enabled (re-run with debug); useful to print extra info.

Q5: Environment variable equivalents?
A5: `RUNNER_OS`, `RUNNER_ARCH`, `RUNNER_NAME`, `RUNNER_TEMP`, `RUNNER_TOOL_CACHE`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cross-platform builds and cache keys
- Writing temp files portably
- Branching logic for self-hosted vs hosted

❌ Avoid when:
- Choosing the runner (use matrix/vars/inputs)
- You only run on a single known OS (keep it simple)
- Storing persistent data in `runner.temp`

---

## 📊 Visual Diagram
```
 runs-on: ${{ matrix.os }}
        |
        v
 +------------------ runner (VM / machine) ------------------+
 | os=Linux  arch=X64  name=GitHub Actions 7                 |
 | environment=github-hosted   temp=/home/runner/work/_temp  |
 | tool_cache=/opt/hostedtoolcache                           |
 +------------------------------------------------------------+
        |
  ${{ runner.os }}  /  $RUNNER_OS   used in steps, cache keys, if:
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| runner | Machine that runs a job | Job चलाने वाली machine |
| Self-hosted | Runner you manage | आपकी अपनी managed machine |
| tool_cache | Preinstalled tool folder | पहले से installed tools का folder |
| Ephemeral | Used for one job then destroyed | एक job के बाद नष्ट |
| Arch | CPU architecture | CPU architecture |

---

## ⚡ 3-Line Summary
English: `runner` describes the executing machine: os, arch, temp, name, environment.
Use it for portable paths and OS/arch aware cache keys inside steps.
It is unavailable in `runs-on`; self-hosted runners need extra security care.
Hindi: `runner` चलाने वाली machine बताता है: os, arch, temp, name, environment।
Steps के अंदर portable paths और OS/arch वाली cache keys के लिए इस्तेमाल करो।
यह `runs-on` में उपलब्ध नहीं; self-hosted runners में अतिरिक्त security चाहिए।

---

## ➡️ Next Topic
**268. steps Context** — reading outputs, outcome and conclusion of earlier steps.
