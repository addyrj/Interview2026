---

# 559. CI/CD for AI Apps
# हिंदी में: AI Apps के लिए CI/CD

---

## 🔵 Simple Definition (English)
CI (Continuous Integration) automatically builds and tests every code change. CD (Continuous Delivery/Deployment) automatically ships passing builds to staging or production. For AI apps, the pipeline also tests prompts, retrieval quality and cost, not just code.

## 🔵 सरल परिभाषा (Hindi)
CI (Continuous Integration) हर code change को अपने आप build और test करता है। CD (Continuous Delivery/Deployment) pass हुए builds को अपने आप staging या production पर भेजता है। AI apps में pipeline code के साथ prompts, retrieval quality और cost भी test करती है।

---

## 🔴 Problem it Solves
Manual deploys are slow and error-prone ("works on my laptop"). In AI apps there is a second risk: a small prompt or model change can silently drop accuracy or double cost, and no unit test notices. CI/CD adds repeatable gates: lint, tests, evals, security scan, then a safe rollout.

## 🔴 यह क्यों बना? (Hindi)
Manual deploy धीमा और गलतियों वाला है ("मेरे laptop पर चल रहा है")। AI apps में दूसरा खतरा है: छोटा prompt या model बदलाव accuracy चुपचाप गिरा सकता है या cost दोगुना कर सकता है, और unit test को पता नहीं चलता। CI/CD दोहराने योग्य gates जोड़ता है: lint, tests, evals, security scan, फिर safe rollout।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer opens a pull request
Step 2 → CI: install deps (cached), lint + type-check (ruff, mypy)
Step 3 → CI: unit tests with mocked LLM (fast, free)
Step 4 → CI: small eval set on prompts/retrieval (threshold gate, e.g. accuracy >= 0.85)
Step 5 → Merge to main → build Docker image, tag with git SHA, push to registry
Step 6 → CD: deploy to staging, run smoke tests (/health, one real query)
Step 7 → Manual approval or auto-promote to prod (rolling / blue-green), auto-rollback on failure
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Developer pull request खोलता है
Step 2 → CI: deps install (cache), lint + type-check
Step 3 → CI: mocked LLM के साथ unit tests (तेज़, मुफ्त)
Step 4 → CI: prompts/retrieval पर छोटा eval set (threshold gate)
Step 5 → main में merge → Docker image build, git SHA tag, registry में push
Step 6 → CD: staging पर deploy, smoke tests
Step 7 → Approval या auto-promote, fail पर auto-rollback
```

---

## 🟡 Real World Example
**Tariff Classification System**: Every PR runs 30 golden invoices (known HS codes) against the classifier. If exact-match accuracy falls below the main-branch baseline by more than 2 points, the PR is blocked. On merge, an image tagged with the commit SHA is deployed to staging, then promoted to production with a rolling update.

**Amazon-style**: A search-ranking prompt change must pass an offline relevance eval before it can reach production.

## 🟡 Real Example Hindi mein
**Tariff System**: हर PR 30 golden invoices (ज्ञात HS codes) classifier पर चलाता है। अगर exact-match accuracy main baseline से 2 points से ज़्यादा गिरे तो PR block। Merge पर commit SHA वाली image staging पर और फिर rolling update से production पर जाती है।

---

## 💻 Code Example — Basic
```python
# A tiny "quality gate" script a CI job can run: exit code 1 fails the pipeline
import sys  # for exit codes

# Golden test cases: (invoice text, expected HS prefix)
GOLDEN: list[tuple[str, str]] = [
    ("Apple iPhone 15 smartphone", "8517"),      # phones
    ("Cotton t-shirt men", "6109"),              # knitted shirts
]


def fake_classifier(text: str) -> str:
    """Stand-in for the real classifier so CI needs no API key."""
    return "8517" if "phone" in text.lower() else "6109"   # trivial rules


def main() -> int:
    hits = sum(1 for text, want in GOLDEN if fake_classifier(text) == want)  # count correct
    acc = hits / len(GOLDEN)                                                 # accuracy
    print(f"accuracy={acc:.2f}")                                             # visible in CI logs
    return 0 if acc >= 0.85 else 1                                           # gate


if __name__ == "__main__":
    sys.exit(main())                                                         # CI reads the code
```

## 💻 Code Example — Advanced
```python
# Production eval gate: async, concurrent, compares with stored baseline, error-tolerant
import asyncio                                   # concurrency
import json                                      # read/write baseline
import sys                                       # exit code
from pathlib import Path                         # file paths
from typing import Awaitable, Callable           # type hints

Classifier = Callable[[str], Awaitable[str]]     # async function type
BASELINE = Path("eval_baseline.json")            # committed in repo
MAX_DROP = 0.02                                  # allow 2 points of noise


async def run_case(clf: Classifier, text: str, want: str, sem: asyncio.Semaphore) -> bool:
    """Run one case with concurrency limit and error tolerance."""
    async with sem:                              # respect provider rate limits
        try:
            got = await asyncio.wait_for(clf(text), timeout=20)  # bounded
            return got.startswith(want)          # prefix match on HS code
        except Exception:                        # API error counts as failure
            return False


async def evaluate(clf: Classifier, cases: list[tuple[str, str]]) -> float:
    sem = asyncio.Semaphore(5)                   # 5 parallel calls
    results = await asyncio.gather(*(run_case(clf, t, w, sem) for t, w in cases))
    return sum(results) / len(results)           # accuracy


def gate(acc: float) -> int:
    base = json.loads(BASELINE.read_text())["accuracy"] if BASELINE.exists() else 0.0
    print(f"accuracy={acc:.3f} baseline={base:.3f}")        # log both
    return 0 if acc >= base - MAX_DROP else 1               # fail if regression > 2 pts


async def demo_clf(text: str) -> str:
    return "8517" if "phone" in text.lower() else "6109"    # replace with real chain


if __name__ == "__main__":
    cases = [("iPhone 15", "8517"), ("Cotton shirt", "6109")]
    acc = asyncio.run(evaluate(demo_clf, cases))            # run all cases
    sys.exit(gate(acc))                                     # non-zero blocks the merge
```

---

## 🟠 FastAPI Integration
The pipeline builds the FastAPI image and smoke-tests it. Add a `/version` route that returns the git SHA so you can confirm exactly which build is live.

```python
# /version exposes the deployed build (SHA injected at image build time)
import os                                    # env access
from fastapi import FastAPI                  # framework

app = FastAPI()                              # app


@app.get("/version")
async def version() -> dict[str, str]:
    return {
        "git_sha": os.getenv("GIT_SHA", "dev"),          # set via docker build --build-arg / ENV
        "model": os.getenv("MODEL_NAME", "gpt-4o-mini"), # which model this build uses
    }
```
Smoke test in CD: `curl -f https://staging/version` must return the new SHA.

---

## 🔗 LangChain / LangGraph Connection
Test chains and graphs in CI with a fake model so no network is needed. `langchain_core` ships `FakeListChatModel`-style fakes for this (check the installed version for exact names). Evaluate real quality separately using LangSmith datasets/evals on a schedule or on PRs touching prompts.

```python
# Unit-test a chain with a fake LLM (no API key, deterministic)
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # fake model
from langchain_core.prompts import ChatPromptTemplate                           # prompt

prompt = ChatPromptTemplate.from_template("HS code for: {item}")   # simple prompt
llm = FakeListChatModel(responses=["8517"])                        # always answers 8517
chain = prompt | llm                                               # LCEL chain
assert chain.invoke({"item": "phone"}).content == "8517"           # deterministic test
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Running real LLM calls in every unit test
✅ Correct: Mock the LLM for unit tests; run a small real eval separately.
```python
# Wrong: 200 tests x real GPT calls = slow, flaky, costs money on every push
# Right: patch the client; run 20-30 real eval cases only on prompt/model changes
```

❌ Mistake 2: Deploying the `latest` tag
✅ Correct: Tag images with the git SHA so rollback is one command.
```python
# Wrong: image: tariff-api:latest      (which build is this?)
# Right: image: tariff-api:3f9c2ab     (traceable, rollback-able)
```

---

## 🧠 Tricky Interview Question
**Q**: "All your tests pass in CI but production accuracy drops after a deploy. Nothing in code changed except a dependency bump. How can this happen and how do you prevent it?"

**Answer**: LLM apps depend on non-code behaviour: a transitive bump (tokenizer, text splitter, embedding library) can change chunk boundaries or embeddings, shifting retrieval. Unit tests with mocks do not see this. Prevent with: pinned/locked dependencies (`uv.lock`/`requirements.txt` with hashes), an eval gate on a golden set that exercises real retrieval, and canary rollout with live quality metrics and auto-rollback.

---

## ⚫ Interview Questions + Answers

Q1: What does CI stand for and do?
A1: Continuous Integration: automatically build and test each change.

Q2: Why tag Docker images with the commit SHA?
A2: Traceability and easy rollback.

Q3: How do you test LLM code without paying for API calls?
A3: Mock or fake the model for logic tests; use a small, cached real eval for quality.

Q4: What is an eval gate?
A4: A CI step running a fixed dataset and failing if a metric (accuracy, faithfulness, cost per query) drops below a threshold or regresses vs baseline.

Q5: Design a CI/CD pipeline for a RAG app where prompts change daily.
A5: Prompts in version control; PR triggers lint, unit, then eval on golden set with metric thresholds and a cost-per-query cap; merge builds an immutable image; staging smoke test; canary 5% to prod with online metrics; auto-rollback via previous SHA; secrets from a vault, never in the repo.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one developer, or more than one deploy per month
- Prompts/models change often

❌ Avoid when:
- A throwaway prototype (a basic test + manual deploy is enough)

---

## 📊 Visual Diagram
```
 PR ─► lint/type ─► unit (mock LLM) ─► eval gate ─► security scan
                                                       │ pass
 merge ─► build image :SHA ─► push registry ─► deploy STAGING
                                                  │ smoke ok
                                   approve ─► deploy PROD (rolling/canary)
                                                  │ metrics bad?
                                                  └─► rollback to previous SHA
```

---

## 💰 Cost Impact
CI itself is cheap, but real LLM evals cost tokens. Example (illustrative): 30 cases x ~1,200 tokens = 36k tokens per run; at 20 PRs/week that is ~720k tokens/week, a few cents to a few dollars depending on the model. Optimise: cheap model for evals, cache responses by (prompt, input) hash, run full evals only when prompts/models/retrieval files change (path filters), and cap parallelism.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CI | Auto build + test | अपने आप build + test |
| CD | Auto deliver/deploy | अपने आप deploy |
| Eval gate | Quality threshold check | Quality की सीमा जाँच |
| Golden set | Fixed test dataset with answers | सही उत्तरों वाला fixed dataset |
| Rollback | Return to previous version | पिछले version पर वापस |
| Smoke test | Quick post-deploy check | Deploy के बाद तेज़ जाँच |

---

## ⚡ 3-Line Summary
English: CI/CD automates testing and deployment on every change. For AI apps add eval gates and cost checks, mock LLMs in unit tests, and tag images by SHA. Roll out gradually and roll back automatically.
Hindi: CI/CD हर change पर testing और deployment automate करता है। AI apps में eval gates और cost checks जोड़ें, unit tests में LLM mock करें और images को SHA से tag करें। धीरे-धीरे rollout करें और अपने आप rollback करें।

---

## ➡️ Next Topic
**560. GitHub Actions for AI** — writing the actual workflow YAML for this pipeline.
