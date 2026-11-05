# 232. GitHub Actions vs Jenkins vs GitLab CI vs CircleCI
# हिंदी में: GitHub Actions बनाम Jenkins बनाम GitLab CI बनाम CircleCI

---

## 🔵 Simple Definition (English)
These are four popular CI/CD tools that build, test and deploy your code automatically. **GitHub Actions** is built into GitHub, **Jenkins** is a self-hosted automation server, **GitLab CI** is built into GitLab, and **CircleCI** is a hosted CI service. They solve the same problem but differ in hosting, setup effort, cost and flexibility.

## 🔵 सरल परिभाषा (Hindi)
ये चार popular CI/CD tools हैं जो आपके code को अपने-आप build, test और deploy करते हैं। **GitHub Actions** GitHub के अंदर ही built-in है, **Jenkins** एक self-hosted automation server है, **GitLab CI** GitLab में built-in है, और **CircleCI** एक hosted CI service है। चारों का काम एक जैसा है, फर्क hosting, setup की मेहनत, cost और flexibility में है।

---

## 🔴 Problem it Solves
Before CI/CD tools, developers built the app on their laptop, zipped it, copied it to the server by hand, and hoped nothing broke. Every release depended on one person remembering 15 steps. Teams then installed Jenkins on a spare server, but someone had to patch, back up and scale it.

Choosing the right tool matters: a wrong choice means paying for servers you do not need, maintaining plugins that break, or being locked into a vendor that your code is not even hosted on. This topic helps you decide quickly and defend the decision in an interview.

## 🔴 यह क्यों बना? (Hindi)
CI/CD tools से पहले developer अपने laptop पर app build करता, zip करता, server पर हाथ से copy करता और उम्मीद करता कि कुछ न टूटे। हर release एक आदमी की याददाश्त पर टिका था जिसे 15 steps याद रखने पड़ते थे। फिर teams ने एक खाली server पर Jenkins लगाया, लेकिन उसे patch, backup और scale करने के लिए किसी को रखना पड़ा।

सही tool चुनना ज़रूरी है: गलत choice का मतलब है उन servers का bill भरना जिनकी ज़रूरत नहीं, plugins maintain करना जो टूटते रहते हैं, या ऐसे vendor में फँसना जहाँ आपका code host भी नहीं है। यह topic आपको जल्दी decide करना और interview में अपना फैसला defend करना सिखाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer pushes code to a Git host (GitHub / GitLab / Bitbucket)
Step 2 → The Git host sends a webhook / event to the CI system
Step 3 → CI system finds a pipeline definition file in the repo
           (GHA: .github/workflows/*.yml, GitLab: .gitlab-ci.yml,
            CircleCI: .circleci/config.yml, Jenkins: Jenkinsfile)
Step 4 → CI system gives the job to a machine (runner / agent / executor)
Step 5 → The machine checks out code, runs build + test + deploy steps
Step 6 → Result (pass/fail, logs, artifacts) is reported back on the commit / PR
```

How each tool differs at Step 2-4:
- **GitHub Actions**: events come natively from GitHub; GitHub gives you a fresh VM per job.
- **Jenkins**: you install Jenkins, add a webhook plugin, and register your own agent machines.
- **GitLab CI**: GitLab itself triggers; jobs run on GitLab Runners (shared or your own).
- **CircleCI**: you connect your repo via OAuth; jobs run in CircleCI's cloud (Docker or machine executors).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Developer code को Git host (GitHub / GitLab / Bitbucket) पर push करता है।
Step 2 → Git host एक webhook / event CI system को भेजता है।
Step 3 → CI system repo में pipeline की definition file ढूँढता है (GHA: `.github/workflows/*.yml`, GitLab: `.gitlab-ci.yml`, CircleCI: `.circleci/config.yml`, Jenkins: `Jenkinsfile`)।
Step 4 → CI system job को किसी machine (runner / agent / executor) को देता है।
Step 5 → वह machine code checkout करती है और build + test + deploy चलाती है।
Step 6 → नतीजा (pass/fail, logs, artifacts) commit / PR पर वापस दिखता है।

फर्क Step 2-4 में है: GitHub Actions में events GitHub से ही आते हैं और हर job को नई VM मिलती है; Jenkins में आप खुद install करते हैं और अपनी agent machines जोड़ते हैं; GitLab CI में GitLab खुद trigger करता है और GitLab Runner job चलाता है; CircleCI में repo OAuth से जुड़ता है और job CircleCI के cloud में चलता है।

---

## 🟡 Real World Example
A 6-person startup (like an early Swiggy-style food delivery team) keeps its Node.js API and React app on GitHub. They pick **GitHub Actions** because: no server to maintain, 2,000 free minutes per month on private repos (free plan; limits change, check current pricing), and PR checks appear right inside GitHub.

A large bank with strict on-prem rules and 300 legacy pipelines uses **Jenkins**, because the code must never leave their network and they already have a platform team to run it.

A company whose whole code lives in self-managed GitLab uses **GitLab CI** because the registry, issues and pipelines are in one product.

A team that wanted very fast Docker-layer-cached builds in 2018 chose **CircleCI**; today many have moved to GitHub Actions to cut one vendor bill.

## 🟡 Real Example Hindi mein
6 लोगों का startup (जैसे शुरुआती Swiggy जैसी food delivery team) अपना Node.js API और React app GitHub पर रखता है। वे **GitHub Actions** चुनते हैं क्योंकि: कोई server maintain नहीं करना, private repos पर हर महीने 2,000 free minutes (free plan; limits बदलती रहती हैं, current pricing देखें), और PR checks सीधे GitHub में दिखते हैं।

एक बड़ा bank जिसके on-prem rules सख्त हैं और 300 पुरानी pipelines हैं, **Jenkins** इस्तेमाल करता है, क्योंकि code network से बाहर नहीं जाना चाहिए और उनके पास platform team है जो इसे चलाती है।

जिस company का सारा code self-managed GitLab में है, वह **GitLab CI** लेती है क्योंकि registry, issues और pipelines एक ही product में हैं।

---

## 💻 Code / Config Example — Basic
Same job, "install deps and run tests on a Node.js app", written for all four tools. First the GitHub Actions version (the one you will use).

```yaml
# .github/workflows/basic-ci.yml  (GitHub Actions)
name: Basic CI                      # Name shown in the Actions tab
on: push                            # Run on every push to any branch
jobs:                               # All jobs live under this key
  test:                             # Job id (you choose it)
    runs-on: ubuntu-latest          # GitHub-hosted Linux VM
    steps:                          # Steps run one after another
      - uses: actions/checkout@v4   # Download repo code (example version, update as needed)
      - uses: actions/setup-node@v4 # Install Node.js
        with:
          node-version: 20          # Node version to use
      - run: npm ci                 # Clean install from package-lock.json
      - run: npm test               # Run the test suite
```

The same pipeline in the other three tools, for comparison:

```yaml
# .gitlab-ci.yml  (GitLab CI)
image: node:20                      # Docker image in which every job runs
test:                               # Job name (also acts as its id)
  stage: test                       # Stage this job belongs to
  script:                           # Commands to run
    - npm ci                        # Clean install
    - npm test                      # Run tests
```

```yaml
# .circleci/config.yml  (CircleCI)
version: 2.1                        # CircleCI config schema version
jobs:
  test:                             # Job name
    docker:
      - image: cimg/node:20.11       # CircleCI convenience image (example tag)
    steps:
      - checkout                    # Built-in step: get the code
      - run: npm ci                 # Clean install
      - run: npm test               # Run tests
workflows:
  main:                             # Workflow name
    jobs:
      - test                        # Run the "test" job
```

```groovy
// Jenkinsfile  (Jenkins declarative pipeline; Groovy, not YAML)
pipeline {
  agent { docker { image 'node:20' } }   // Run inside a Node 20 container (needs Docker Pipeline plugin)
  stages {
    stage('Test') {                      // One visible stage in Jenkins UI
      steps {
        sh 'npm ci'                      // Shell step: install
        sh 'npm test'                    // Shell step: test
      }
    }
  }
}
```

## 💻 Code / Config Example — Advanced
A production-style GitHub Actions workflow: lint + test with a Node version matrix, npm cache, concurrency control and least-privilege permissions. This is where Actions shines over older tools: all of this is a few lines of YAML.

```yaml
# .github/workflows/ci-advanced.yml
name: CI Advanced                    # Workflow display name
on:
  push:
    branches: [main]                 # Run on pushes to main only
  pull_request:                      # Also run on every pull request
    branches: [main]                 # ...that targets main
permissions:
  contents: read                     # Least privilege: token can only read code
concurrency:
  group: ci-${{ github.ref }}        # One run per branch at a time
  cancel-in-progress: true           # Cancel the older run when a new push arrives
jobs:
  test:
    runs-on: ubuntu-latest           # GitHub-hosted runner
    timeout-minutes: 15              # Kill hung jobs, saves minutes and money
    strategy:
      fail-fast: false               # Let all matrix legs finish
      matrix:
        node: [18, 20, 22]           # Test on three Node versions in parallel
    steps:
      - uses: actions/checkout@v4    # Get code
      - uses: actions/setup-node@v4  # Install Node
        with:
          node-version: ${{ matrix.node }}  # Version from the matrix
          cache: npm                 # Cache ~/.npm keyed by package-lock.json
      - run: npm ci                  # Reproducible install
      - run: npm run lint            # Static checks
      - run: npm test -- --ci        # Tests in CI mode
```

Quick comparison table:

| Feature | GitHub Actions | Jenkins | GitLab CI | CircleCI |
|---|---|---|---|---|
| Hosting | Cloud (or self-hosted runners) | You host it | GitLab.com or self-managed | Cloud (or self-hosted runners) |
| Config file | YAML in `.github/workflows/` | Groovy `Jenkinsfile` | YAML `.gitlab-ci.yml` | YAML `.circleci/config.yml` |
| Setup effort | Almost none | High (server, plugins) | Low if on GitLab | Low |
| Reusable pieces | Marketplace actions | Plugins (~1,800) | Includes / templates | Orbs |
| Best for | Code on GitHub | Custom, on-prem, legacy | Code on GitLab | Fast hosted CI |

---

## 🟠 My Stack Integration
Your code is on GitHub and you deploy to a VPS and AWS, so **GitHub Actions** is the natural choice: it needs no extra server, has first-party AWS OIDC login (no long-lived keys), and can SSH to your VPS.

```yaml
# .github/workflows/stack-ci.yml
name: Stack CI                       # Node API + React + FastAPI in one repo
on:
  pull_request:                      # Check every PR before merge
jobs:
  api:
    runs-on: ubuntu-latest           # Node.js API
    steps:
      - uses: actions/checkout@v4    # Get code
      - uses: actions/setup-node@v4  # Install Node
        with: { node-version: 20, cache: npm, cache-dependency-path: api/package-lock.json }
      - run: npm ci && npm test      # Install and test
        working-directory: api       # Run inside the api/ folder
  fastapi:
    runs-on: ubuntu-latest           # Python service
    steps:
      - uses: actions/checkout@v4    # Get code
      - uses: actions/setup-python@v5 # Install Python
        with: { python-version: "3.12", cache: pip }
      - run: pip install -r requirements.txt && pytest   # Install and test
        working-directory: fastapi   # Run inside fastapi/
  web:
    runs-on: ubuntu-latest           # React build check
    steps:
      - uses: actions/checkout@v4    # Get code
      - uses: actions/setup-node@v4  # Install Node
        with: { node-version: 20, cache: npm, cache-dependency-path: web/package-lock.json }
      - run: npm ci && npm run build # Make sure the production build passes
        working-directory: web       # Run inside web/
```

Security note: never put the VPS SSH key or AWS keys in the YAML; use GitHub Secrets (covered later) or OIDC. Pin third-party actions to a full commit SHA in sensitive repos.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Choosing Jenkins "because it is famous" for a 3-person team and then spending a week patching the server.
✅ Correct: Use a managed option (GitHub Actions) unless you have a hard on-prem or custom requirement.

❌ Mistake 2: Assuming Actions is free and unlimited. Private repos have a monthly minutes quota and Linux/Windows/macOS use different multipliers.
✅ Correct: Add `timeout-minutes`, caching and `concurrency` cancel, and check the current billing page.

❌ Mistake 3: Copy-pasting a Jenkins/GitLab pipeline into `.github/workflows` and expecting it to work. The syntax and concepts differ (stages vs jobs, `script` vs `run`).
✅ Correct: Re-map concepts: job, step, runner, `uses`/`run`.

❌ Mistake 4: Using the tool's default token permissions everywhere.
✅ Correct: Set `permissions:` to the minimum on every workflow.

---

## 🧠 Tricky Interview Question
"Our code is on GitHub, but the security team says build servers must be inside our private network and nothing may run on shared infrastructure. Can we still use GitHub Actions?"

Answer: Yes. GitHub Actions separates the **control plane** (GitHub schedules and shows workflows) from the **execution plane** (runners). Use **self-hosted runners** inside your VPC. Jobs run on your machines, in your network, and only job metadata and logs go back to GitHub. Add ephemeral runners (one job per VM/container) so a compromised job cannot leave anything behind, and never attach self-hosted runners to public repos where forks can run arbitrary code. Jenkins is not the only option for private builds.

---

## ⚫ Interview Questions + Answers

Q1: Why would you choose GitHub Actions over Jenkins?
A1: Zero server maintenance, native GitHub events and PR checks, a huge marketplace of actions, free minutes for small teams, and YAML in the repo next to the code. Jenkins wins only when you need heavy customization or fully on-prem control.

Q2: What are the config file names of the four tools?
A2: `.github/workflows/*.yml` (GHA), `Jenkinsfile` (Jenkins), `.gitlab-ci.yml` (GitLab), `.circleci/config.yml` (CircleCI).

Q3: What is the equivalent of GitHub Actions "runner" in other tools?
A3: Jenkins: agent/node. GitLab: GitLab Runner. CircleCI: executor (docker/machine) or self-hosted runner.

Q4: What are Jenkins plugins and why are they a risk?
A4: Plugins add features (Git, Docker, Slack). They are separately versioned, can conflict, and have had security vulnerabilities, so you must update and test them regularly.

Q5: What is a CircleCI Orb vs a GitHub Action?
A5: Both are reusable packaged pieces. An Orb bundles config (jobs, commands, executors) in CircleCI; an Action is a reusable step (JavaScript, Docker or composite) used with `uses:`.

---

## 🔷 When to Use + When Not to Use
✅ Use GitHub Actions when:
- Code is on GitHub and you want the least setup.
- You want PR checks, deploy on tag, scheduled jobs in one place.
- You deploy to AWS via OIDC or to a VPS via SSH.

❌ Avoid GitHub Actions (consider others) when:
- Code is hosted on GitLab / Bitbucket (use that platform's CI).
- You need very complex, custom, on-prem orchestration with existing Jenkins expertise.
- Free minute limits do not fit and you cannot run self-hosted runners.

---

## 📊 Visual Diagram

```
             +-----------------+
 git push -->|   Git host      |
             | (GitHub/GitLab) |
             +--------+--------+
                      | webhook / event
                      v
   +------------------+-------------------+
   |             CI system                |
   |  GHA | Jenkins | GitLab CI | Circle  |
   +----+--------------------------+------+
        | reads pipeline file      | assigns job
        v                          v
  .github/workflows/*.yml   +--------------+
  Jenkinsfile               | Runner/Agent |--> build, test, deploy
  .gitlab-ci.yml            +--------------+
  .circleci/config.yml             |
                                   v
                          status back on commit/PR
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CI | Continuous Integration, auto build+test on each change | लगातार integration |
| CD | Continuous Delivery/Deployment | लगातार delivery/deploy |
| Runner / Agent | Machine that executes jobs | job चलाने वाली machine |
| Jenkinsfile | Pipeline as code for Jenkins | Jenkins की pipeline file |
| Orb | Reusable CircleCI package | CircleCI का reusable package |
| Marketplace | Store of reusable Actions | Actions का बाज़ार |
| Self-hosted | Runs on your own infrastructure | अपनी machine पर |

---

## ⚡ 3-Line Summary
English: All four tools automate build, test and deploy from a pipeline file in your repo.
GitHub Actions is the lowest-effort choice for GitHub code; Jenkins gives full control at a maintenance cost.
GitLab CI and CircleCI fit when your code or team already lives there.

Hindi: चारों tools repo की pipeline file से build, test और deploy अपने-आप करते हैं।
GitHub code के लिए GitHub Actions सबसे कम मेहनत वाला है; Jenkins पूरा control देता है पर maintenance भारी है।
GitLab CI और CircleCI तब ठीक हैं जब आपका code या team पहले से वहीं हो।

---

## ➡️ Next Topic
**233. GitHub Actions Concepts** — now that you chose Actions, learn its vocabulary: workflow, event, job, step, action and runner, and how they fit together.

---
