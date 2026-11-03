---

# 560. GitHub Actions for AI
# हिंदी में: AI के लिए GitHub Actions

---

## 🔵 Simple Definition (English)
GitHub Actions is GitHub's built-in automation. You describe a workflow in a YAML file under `.github/workflows/`; GitHub runs it on its servers (runners) when events happen, like a push or pull request. It is the easiest way to run CI/CD for AI apps.

## 🔵 सरल परिभाषा (Hindi)
GitHub Actions GitHub की built-in automation है। आप `.github/workflows/` में YAML file में workflow लिखते हैं; push या pull request जैसे events पर GitHub अपने servers (runners) पर उसे चलाता है। AI apps के लिए CI/CD चलाने का सबसे आसान तरीका।

---

## 🔴 Problem it Solves
Running your own Jenkins server means maintenance. Teams need tests, evals and deploys on each PR, with secrets (API keys) handled safely. Actions gives hosted runners, a marketplace of reusable steps, and encrypted secrets, right next to the code.

## 🔴 यह क्यों बना? (Hindi)
अपना Jenkins चलाने का मतलब maintenance। Teams को हर PR पर tests, evals और deploys चाहिए, और API keys सुरक्षित चाहिए। Actions code के बगल में hosted runners, reusable steps और encrypted secrets देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Event (push / pull_request / schedule / workflow_dispatch) triggers a workflow
Step 2 → A job is assigned to a runner (ubuntu-latest)
Step 3 → Steps run in order: checkout, setup-python (with pip cache), install
Step 4 → Run ruff + pytest (mocked LLM) on every PR
Step 5 → Eval job runs only if prompt/ or retriever files changed (paths filter), using secrets.OPENAI_API_KEY
Step 6 → On main: build + push Docker image tagged with ${{ github.sha }}
Step 7 → Deploy job (environment: production, needs approval) uses OIDC to assume an AWS role
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Event (push / PR / schedule / manual) workflow trigger करता है
Step 2 → Job एक runner (ubuntu-latest) को मिलता है
Step 3 → Steps क्रम से: checkout, setup-python (pip cache), install
Step 4 → हर PR पर ruff + pytest (mocked LLM)
Step 5 → Eval job सिर्फ तब जब prompt/ या retriever files बदलीं, secrets.OPENAI_API_KEY के साथ
Step 6 → main पर: Docker image build + push, ${{ github.sha }} tag के साथ
Step 7 → Deploy job (production environment, approval) OIDC से AWS role लेता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: `ci.yml` runs on each PR: lint, unit tests, and (if `prompts/**` changed) a 30-case eval that posts accuracy as a PR comment. `deploy.yml` runs on merge to main: builds the image, pushes to ECR, and updates the ECS service.

**Zomato-style**: A nightly scheduled workflow replays 500 anonymised queries against the recommender and alerts Slack if quality drops.

## 🟡 Real Example Hindi mein
**Tariff System**: `ci.yml` हर PR पर: lint, unit tests, और (अगर `prompts/**` बदला) 30-case eval जो accuracy PR comment में डालता है। `deploy.yml` main merge पर: image build, ECR में push और ECS service update।

---

## 💻 Code Example — Basic
Workflow YAML (this is the main "code" for this topic):
```yaml
# .github/workflows/ci.yml
name: ci                              # name shown in the Actions tab
on:
  pull_request:                       # run on every PR
jobs:
  test:                               # job id
    runs-on: ubuntu-latest            # GitHub-hosted runner
    steps:
      - uses: actions/checkout@v4     # get the code
      - uses: actions/setup-python@v5 # install Python
        with:
          python-version: "3.12"      # pin the version
          cache: pip                  # cache pip downloads
      - run: pip install -r requirements.txt   # install deps
      - run: pytest -q                # tests must use mocked LLM (no key needed)
```
A Python file the workflow can run (pure Python, runs offline):
```python
# scripts/check_prompts.py - fail CI if a prompt file is empty or too long
import sys                                   # exit code
from pathlib import Path                     # file access

MAX_CHARS = 4000                             # ~1000 tokens budget per prompt

bad: list[str] = []                          # collect problems
for f in Path("prompts").glob("*.txt"):      # every prompt file
    text = f.read_text(encoding="utf-8")     # read it
    if not text.strip() or len(text) > MAX_CHARS:   # empty or too long
        bad.append(f.name)                   # record

print("bad prompts:", bad or "none")         # show result in logs
sys.exit(1 if bad else 0)                    # non-zero fails the job
```

## 💻 Code Example — Advanced
```yaml
# .github/workflows/deploy.yml - build, eval gate, push image, deploy
name: deploy
on:
  push:
    branches: [main]                  # only on merge to main
permissions:
  id-token: write                     # needed for OIDC to AWS (no long-lived keys)
  contents: read                      # least privilege
concurrency:
  group: deploy-prod                  # never run two deploys at once
  cancel-in-progress: false
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -r requirements.txt
      - run: python scripts/run_eval.py          # exits non-zero below threshold
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}   # encrypted secret
  deploy:
    needs: eval                       # only after eval passes
    runs-on: ubuntu-latest
    environment: production           # can require manual approval
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC role assumption
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gh-deploy   # placeholder ARN
          aws-region: ap-south-1
      - run: |
          docker build -t tariff-api:${{ github.sha }} .   # tag with commit SHA
          # push to ECR + update service (commands omitted for brevity)
```
Async eval script (pure Python, offline demo) called above:
```python
# scripts/run_eval.py - async eval with a fake model so it runs without keys
import asyncio                                # async runner
import os                                     # env check
import sys                                    # exit code


async def classify(text: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):       # no key: fake answer (demo only)
        return "8517" if "phone" in text.lower() else "6109"
    raise NotImplementedError("call the real chain here")   # real chain goes here


async def main() -> int:
    cases = [("iPhone", "8517"), ("Cotton shirt", "6109")]   # golden cases
    try:
        got = await asyncio.gather(*(classify(t) for t, _ in cases))   # parallel
    except Exception as exc:                  # provider errors
        print("eval error:", exc)
        return 2                              # distinct code for infra errors
    acc = sum(g == w for g, (_, w) in zip(got, cases)) / len(cases)
    print(f"accuracy={acc:.2f}")
    return 0 if acc >= 0.85 else 1


sys.exit(asyncio.run(main()))                 # run and exit
```

---

## 🟠 FastAPI Integration
Actions builds, tests and deploys the FastAPI app. Use `TestClient` in CI to hit routes without a server.

```python
# tests/test_api.py - run by pytest in the workflow (pip install httpx pytest fastapi)
from fastapi import FastAPI                   # framework
from fastapi.testclient import TestClient     # in-process client

app = FastAPI()                               # in real code: from app.main import app


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}                   # route under test


def test_health() -> None:
    client = TestClient(app)                  # no network, no uvicorn
    r = client.get("/health")                 # call the route
    assert r.status_code == 200               # must be OK
    assert r.json() == {"status": "ok"}       # body check
```

---

## 🔗 LangChain / LangGraph Connection
Set LangSmith env vars as secrets (`LANGSMITH_API_KEY`, `LANGSMITH_TRACING=true`) in the eval job so traces and dataset evals land in LangSmith. Keep unit tests on fake models; run LangSmith evals only on prompt changes. Verify the exact env variable names in the current LangSmith docs.

```yaml
# snippet: eval step with tracing (names illustrative; confirm in docs)
- run: python scripts/run_eval.py
  env:
    LANGSMITH_TRACING: "true"
    LANGSMITH_API_KEY: ${{ secrets.LANGSMITH_API_KEY }}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Exposing secrets to PRs from forks / printing them
✅ Correct: Use `secrets.*` (masked), avoid `pull_request_target` with untrusted code, and prefer OIDC over stored cloud keys.
```yaml
# Wrong
- run: echo ${{ secrets.OPENAI_API_KEY }}     # may leak in logs/derived output
# Right
env: { OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }} }   # passed as env, never echoed
```

❌ Mistake 2: Running paid evals on every push to every branch
✅ Correct: Use `paths:` filters, `workflow_dispatch`, and `concurrency` cancel-in-progress.
```yaml
# Wrong: on: push   (all branches, all files)
# Right:
on:
  pull_request:
    paths: ["prompts/**", "app/rag/**"]
```

---

## 🧠 Tricky Interview Question
**Q**: "Your Actions eval job is flaky: sometimes accuracy is 0.84, sometimes 0.90 on the same commit. How do you fix the gate?"

**Answer**: LLM output is non-deterministic. Set `temperature=0` and a seed where supported, increase the eval set so one case moves the score less, run each case several times and use the mean, gate on a tolerance versus baseline (e.g. drop > 2 points) instead of an absolute line, and cache model responses for unchanged inputs. Do not retry until green, because that hides real regressions.

---

## ⚫ Interview Questions + Answers

Q1: Where do workflow files live?
A1: `.github/workflows/*.yml`.

Q2: How do you store API keys?
A2: Repository/Environment secrets, referenced as `${{ secrets.NAME }}`.

Q3: Why use OIDC for AWS?
A3: Short-lived tokens, no stored access keys to leak or rotate.

Q4: How do you stop paid evals from running on unrelated changes?
A4: `paths` filters, path-based conditional jobs, and `workflow_dispatch` for manual runs.

Q5: Design a workflow where prompt changes need evals but docs changes do not, with approval for prod.
A5: Trigger on `pull_request` with path filters; eval job gated on prompt/retrieval paths; deploy job `needs: eval`, uses `environment: production` with required reviewers; `concurrency` group serializes deploys; artifacts store eval results for comparison.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Code is on GitHub and you want zero-server CI/CD
- You need PR-based evals

❌ Avoid when:
- Heavy GPU training/evals (use a dedicated runner or cloud batch)
- Strict on-prem requirement without self-hosted runners

---

## 📊 Visual Diagram
```
 push/PR ─► [Workflow YAML] ─► Runner (ubuntu-latest)
                                   │
        ┌──────────────┬───────────┴───────────┬──────────────┐
        ▼              ▼                       ▼              ▼
      lint           pytest                 eval job        docker build
      (ruff)      (fake LLM)              (secrets, paths)   :${{sha}}
                                              │ pass
                                              ▼
                                   deploy (OIDC, approval)
```

---

## 💰 Cost Impact
Public repos have free minutes; private repos have a monthly allowance, then per-minute billing (check current GitHub pricing). The bigger cost is tokens in eval jobs: 30 cases x ~1,500 tokens x several runs per PR adds up. Optimise: path filters, cheap eval model, response caching keyed by input hash, pip/Docker layer caching to shorten minutes.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Workflow | YAML automation file | YAML automation file |
| Runner | Machine that runs jobs | Job चलाने वाली machine |
| Secret | Encrypted variable | Encrypted variable |
| OIDC | Token-based cloud login | बिना keys cloud login |
| Matrix | Run job across variants | अलग versions पर job |
| Artifact | Saved build/eval output | Save किया गया output |

---

## ⚡ 3-Line Summary
English: GitHub Actions runs YAML workflows on events like PRs and merges. Use mocked tests on every PR, path-filtered evals for prompt changes, and OIDC plus approvals for deploys. Keep secrets masked and parallel paid runs under control.
Hindi: GitHub Actions PR और merge जैसे events पर YAML workflows चलाता है। हर PR पर mocked tests, prompt बदलाव पर path-filtered evals और deploy के लिए OIDC + approval रखें। Secrets masked रखें और paid runs नियंत्रित रखें।

---

## ➡️ Next Topic
**561. Testing AI Apps in CI** — how to test non-deterministic LLM code reliably.
