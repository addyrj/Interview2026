---

# 415. Evaluation in CI/CD Pipeline
# हिंदी में: CI/CD Pipeline में Evaluation

---

## 🔵 Simple Definition (English)
Running your AI evaluation automatically on every pull request or deploy, and blocking the merge if quality drops below a threshold. It is "unit tests" for prompts, retrievers and models. No human has to remember to run it.

## 🔵 सरल परिभाषा (Hindi)
हर pull request या deploy पर AI evaluation अपने-आप चलाना, और quality threshold से नीचे गिरे तो merge रोक देना। यह prompts, retrievers और models के लिए "unit tests" जैसा है। किसी इंसान को चलाना याद रखने की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
- A one-line prompt change can silently break 10% of answers. Normal unit tests do not notice because the code still "runs".
- Manual evaluation is skipped when the team is in a hurry.
- Model version upgrades, retriever config changes and library updates cause regressions nobody sees until users complain.

## 🔴 यह क्यों बना? (Hindi)
- Prompt की एक line बदलने से 10% answers चुपचाप टूट सकते हैं। Normal unit tests पकड़ नहीं पाते क्योंकि code तो "चलता" रहता है।
- जल्दी में manual evaluation छूट जाता है।
- Model version upgrade, retriever config या library update से regression आता है जो user की शिकायत तक किसी को नहीं दिखता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer opens a PR that changes prompt / retriever / model
Step 2 → CI starts (GitHub Actions) and installs dependencies
Step 3 → Eval script loads the golden dataset (smoke subset for PRs)
Step 4 → Runs the pipeline on each case (mock or real LLM, temperature 0)
Step 5 → Computes metrics: accuracy, faithfulness, latency, cost
Step 6 → Compares with thresholds AND with baseline from main branch
Step 7 → Exit code 0 = merge allowed, exit code 1 = PR blocked
Step 8 → Post a summary comment on the PR and upload the report as artifact
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Developer PR खोलता है जिसमें prompt / retriever / model बदला है
Step 2 → CI शुरू होता है (GitHub Actions), dependencies install होती हैं
Step 3 → Eval script golden dataset load करती है (PR के लिए छोटा smoke subset)
Step 4 → हर case पर pipeline चलती है (temperature 0)
Step 5 → Metrics निकलते हैं: accuracy, faithfulness, latency, cost
Step 6 → Threshold और main branch की baseline से compare होता है
Step 7 → Exit code 0 = merge OK, exit code 1 = PR block
Step 8 → PR पर summary comment और report artifact upload
```

---

## 🟡 Real World Example
**Tariff Classification System**: A developer changes the system prompt to "be concise". CI runs 40 smoke cases. Accuracy on main is 0.86; on the PR it is 0.78. The gate says "no regression greater than 2 points", so the PR is blocked with a comment listing the 6 products whose HS code changed. The developer sees that the concise prompt dropped the "check chapter notes" instruction and restores it.

**Amazon-style catalog AI**: Every nightly build re-classifies 500 sample products into categories and alerts Slack if category accuracy falls.

## 🟡 Real Example Hindi mein
**Tariff System**: Developer system prompt में "concise रहो" जोड़ता है। CI 40 smoke cases चलाता है। Main पर accuracy 0.86 है, PR पर 0.78। Gate कहता है "2 points से ज़्यादा गिरावट नहीं", इसलिए PR block हो जाता है और comment में उन 6 products की सूची आती है जिनका HS code बदल गया। Developer देखता है कि "chapter notes check करो" वाली line हट गई थी, और उसे वापस जोड़ देता है।

**Amazon-style catalog AI**: हर रात 500 sample products दोबारा category में classify होते हैं और accuracy गिरे तो Slack alert जाता है।

---

## 💻 Code Example — Basic
```python
# ci_eval_basic.py — minimal CI gate (pure Python, offline)
import sys                                                    # for exit codes

THRESHOLD: float = 0.80                                       # minimum allowed accuracy

def fake_classify(product: str) -> str:                       # stand-in for the real pipeline
    return {"power bank": "8507", "laptop": "8471"}.get(product, "0000")  # lookup or fallback

CASES: list[tuple[str, str]] = [                              # (input, expected) pairs
    ("power bank", "8507"),
    ("laptop", "8471"),
    ("banana", "0803"),
]

correct = sum(fake_classify(p) == e for p, e in CASES)        # count correct answers
accuracy = correct / len(CASES)                               # compute accuracy
print(f"accuracy={accuracy:.2f} threshold={THRESHOLD}")       # log result for CI logs

if accuracy < THRESHOLD:                                      # gate check
    print("FAIL: quality below threshold")                    # message in the CI log
    sys.exit(1)                                               # non-zero exit blocks the merge
print("PASS")                                                 # success path
```

## 💻 Code Example — Advanced
```python
# ci_eval.py — production CI gate: baseline comparison, async, JSON report, safe failures
import argparse                                               # CLI arguments
import asyncio                                                # concurrency
import json                                                   # read/write reports
import sys                                                    # exit codes
from pathlib import Path                                      # file paths
from typing import Awaitable, Callable                        # typing

Pipeline = Callable[[str], Awaitable[str]]                    # async pipeline signature

async def score_all(pipe: Pipeline, cases: list[dict[str, str]], concurrency: int = 4) -> dict[str, float]:
    sem = asyncio.Semaphore(concurrency)                      # avoid provider rate limits
    failures: list[str] = []                                  # ids of failed cases

    async def one(case: dict[str, str]) -> bool:              # score one case
        async with sem:                                       # respect concurrency limit
            try:
                out = await asyncio.wait_for(pipe(case["input"]), timeout=30)  # timeout per call
                return out.strip() == case["expected"]        # exact-match score
            except Exception as exc:                          # pipeline crash = failed case
                failures.append(f"{case['id']}: {type(exc).__name__}")
                return False

    results = await asyncio.gather(*(one(c) for c in cases))  # run all cases
    return {"accuracy": sum(results) / max(len(results), 1), "n": float(len(cases))}

def load_json(path: Path) -> dict:                            # safe JSON loader
    try:
        return json.loads(path.read_text(encoding="utf-8"))   # parse file
    except FileNotFoundError:                                 # first run has no baseline
        return {}
    except json.JSONDecodeError as exc:                       # corrupt file is a real error
        raise SystemExit(f"Bad JSON in {path}: {exc}")

def gate(current: float, baseline: float | None, floor: float, max_drop: float) -> list[str]:
    problems: list[str] = []                                  # reasons to block
    if current < floor:                                       # absolute floor
        problems.append(f"accuracy {current:.3f} < floor {floor}")
    if baseline is not None and baseline - current > max_drop:  # relative regression
        problems.append(f"regression {baseline - current:.3f} > allowed {max_drop}")
    return problems

async def mock_pipeline(text: str) -> str:                    # offline mock so CI works without keys
    await asyncio.sleep(0)                                    # yield control
    return "8507" if "power" in text else "8471"

def main() -> int:
    ap = argparse.ArgumentParser()                            # define CLI
    ap.add_argument("--dataset", type=Path, required=True)    # golden file
    ap.add_argument("--baseline", type=Path, default=Path("baseline.json"))
    ap.add_argument("--floor", type=float, default=0.80)
    ap.add_argument("--max-drop", type=float, default=0.02)
    args = ap.parse_args()                                    # parse arguments
    cases = load_json(args.dataset).get("cases", [])          # golden cases
    if not cases:                                             # empty dataset must not pass silently
        print("No cases found"); return 2
    metrics = asyncio.run(score_all(mock_pipeline, cases))    # run the evaluation
    base = load_json(args.baseline).get("accuracy")           # baseline from main
    problems = gate(metrics["accuracy"], base, args.floor, args.max_drop)
    Path("eval_report.json").write_text(json.dumps({**metrics, "problems": problems}, indent=2))
    print(json.dumps(metrics), problems)                      # visible in CI logs
    return 1 if problems else 0                               # exit code for CI

if __name__ == "__main__":
    sys.exit(main())                                          # propagate exit code
```

GitHub Actions workflow (YAML):
```yaml
name: llm-eval
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: python ci_eval.py --dataset evals/smoke.json --baseline evals/baseline.json
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: eval-report, path: eval_report.json }
```

---

## 🟠 FastAPI Integration
Add a `/health/quality` route that returns the last CI/nightly eval result, so deploy tools (or Kubernetes readiness checks) can refuse to promote a build whose latest eval failed. The route only reads the report file; it does not run the eval.

```python
import json                                                   # read report
from pathlib import Path                                      # file path
from fastapi import FastAPI, HTTPException                    # framework

app = FastAPI()                                               # app

@app.get("/health/quality")                                   # route for deploy tooling
async def quality() -> dict:
    path = Path("eval_report.json")                           # report written by CI
    if not path.exists():                                     # no report yet
        raise HTTPException(status_code=503, detail="no eval report")
    report = json.loads(path.read_text())                     # parse report
    if report.get("problems"):                                # failed gate => unhealthy
        raise HTTPException(status_code=503, detail=report["problems"])
    return {"status": "ok", "accuracy": report["accuracy"]}   # healthy
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith's `evaluate()` returns results you can assert on in `pytest`, so the same dataset powers both CI and the LangSmith UI. For LangGraph, the compiled graph is the `target` function. LangSmith also ships a pytest plugin (`@pytest.mark.langsmith`) for logging test cases as experiments.

```python
# test_quality.py (run by pytest in CI)
from langchain_core.runnables import RunnableLambda           # simple stand-in chain

chain = RunnableLambda(lambda q: "8507" if "power" in q else "8471")  # real project: your LCEL chain

def test_smoke_accuracy() -> None:                            # pytest finds this function
    cases = [("power bank", "8507"), ("laptop", "8471")]      # smoke cases
    outs = chain.batch([q for q, _ in cases])                 # run chain on all inputs
    acc = sum(o == e for o, (_, e) in zip(outs, cases)) / len(cases)  # accuracy
    assert acc >= 0.8, f"accuracy dropped to {acc}"           # failing assert blocks the PR
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running a high-temperature, real-model eval and failing on noise.
✅ Correct: `temperature=0`, fixed seed where supported, tolerance band, and re-run flaky cases.

```python
# Wrong: gate fails randomly
assert accuracy == 0.90
# Right: threshold with tolerance
assert accuracy >= 0.88
```

❌ Mistake 2: Exposing the API key to PRs from forks or committing it.
✅ Correct: use CI secrets, run real-LLM evals only on trusted branches; use a mock/cached pipeline for fork PRs.

```python
# Wrong
client = OpenAI(api_key="sk-abc123...")
# Right
client = OpenAI()   # reads OPENAI_API_KEY from CI secret environment
```

---

## 🧠 Tricky Interview Question
**Q**: "Your eval passes in CI but production quality dropped last week. How is that possible?"

**Answer**: CI only protects against code/prompt changes covered by the golden set. Causes: (1) golden set is stale and does not reflect new user queries (data drift), (2) the provider silently updated a model alias (pin dated model versions), (3) source documents in the vector DB changed, which is not a code change, (4) the CI uses mocks or temperature 0 while production does not. Fix: refresh the golden set from production failures monthly, pin models, run scheduled nightly evals against production data, and monitor online metrics (user feedback, LLM-judge on sampled traces).

---

## ⚫ Interview Questions + Answers

Q1: Why run evals in CI? (Easy)
A1: To catch quality regressions from prompt, model or retrieval changes before they reach users, automatically and consistently.

Q2: What makes an eval a "gate"? (Easy)
A2: A threshold check that returns a non-zero exit code so the pipeline fails and the merge is blocked.

Q3: How do you keep CI evals fast and cheap? (Medium)
A3: Small smoke set per PR, concurrency with a semaphore, response caching keyed on prompt+model, a cheap model for judging, and a full suite only nightly or pre-release.

Q4: How do you handle non-determinism? (Medium)
A4: `temperature=0`, fixed `seed`, metrics on aggregates rather than single cases, a tolerance band, and majority vote over 3 runs for flaky cases.

Q5: Design the full CI/CD quality strategy for a production RAG system. (Hard)
A5: Layers: (a) pre-commit and unit tests for parsers/schemas, (b) PR smoke eval with thresholds and baseline diff, (c) nightly full E2E plus component evals on the main branch, (d) canary deploy where 5% of traffic is scored online by sampled LLM-judge and user feedback, (e) automatic rollback if online metrics drop, (f) failed production traces pushed back into the golden dataset. Version prompts and datasets, pin model versions, and store reports as artifacts for audit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any team edits prompts, retrievers or models regularly
- Multiple developers share one AI codebase
- Compliance requires evidence of testing

❌ Avoid when:
- Dataset is tiny or unreliable (the gate will be noise)
- Full real-LLM evals on every commit with a big dataset (too slow and expensive; use tiers)

---

## 📊 Visual Diagram
```
 git push ─► PR ─► CI runner
                    │
        ┌───────────┴────────────┐
        ▼                        ▼
   unit tests              LLM eval (smoke set)
        │                        │
        │              metrics vs floor + baseline
        │                        │
        └───────► PASS ◄─────────┘───► FAIL ─► PR blocked + comment
                    │
                  merge ─► nightly full eval ─► deploy ─► online monitoring
```

---

## 💰 Cost Impact
- Example: 40 smoke cases x 3,000 tokens = 120K tokens per PR. On gpt-4o-mini that is under $0.05 per run; 50 PRs a month is about $2.50. Full 500-case nightly run is about $0.50 per night. A single production regression typically costs far more.
- Optimise: cache outputs for unchanged prompts, run only evals affected by changed files (path filters), mock the LLM for fork PRs, use cheaper judge models, reduce `max_tokens`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CI/CD | Automatic build, test and deploy | Automatic build/test/deploy pipeline |
| Quality gate | Pass/fail rule on metrics | Metrics पर pass/fail नियम |
| Baseline | Metrics of the main branch | Main branch की reference quality |
| Smoke set | Small fast subset of cases | छोटा तेज़ test set |
| Regression | Quality drop vs earlier | पहले से quality में गिरावट |
| Exit code | Number returned by a script | Script का return number (0 = ठीक) |

---

## ⚡ 3-Line Summary
English: CI/CD evaluation runs your golden dataset automatically on every PR and blocks merges if accuracy falls below a floor or regresses against the main baseline. Use a small smoke set per PR and a full suite nightly, with temperature 0 to reduce noise. Keep datasets fresh and models pinned or CI will pass while production degrades.
Hindi: CI/CD evaluation हर PR पर golden dataset चलाता है और accuracy floor से नीचे या baseline से कम हो तो merge रोकता है। हर PR के लिए छोटा smoke set और रात में full suite चलाओ, noise घटाने के लिए temperature 0 रखो। Dataset ताज़ा और models pinned रखो, वरना CI pass होगा और production खराब होता रहेगा।

---

## ➡️ Next Topic
**416. Evaluation Best Practices** — the checklist of habits that make all these evals trustworthy.
