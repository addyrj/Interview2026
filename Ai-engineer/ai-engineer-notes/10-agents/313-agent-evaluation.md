---

# 313. Agent Evaluation
# हिंदी में: Agent Evaluation (agent कितना सही है, मापना)

---

## 🔵 Simple Definition (English)
Agent evaluation measures how well an agent works using a fixed test set and metrics. You check the **final answer** (is it correct?) and the **trajectory** (did it use the right tools in a sensible order, within cost and step limits?). Results are compared across versions before shipping.

## 🔵 सरल परिभाषा (Hindi)
Agent evaluation एक fixed test set और metrics से मापता है कि agent कितना अच्छा काम करता है। आप **final answer** (सही है?) और **trajectory** (सही tools सही क्रम में, cost और step सीमा में?) दोनों जाँचते हैं। Ship करने से पहले versions की तुलना होती है।

---

## 🔴 Problem it Solves
Agents "feel" fine in a demo but fail on edge cases. A prompt tweak can fix one case and break ten others. Without evals you rely on vibes and users find the bugs. Evals give a regression safety net and a number you can track.

## 🔴 यह क्यों बना? (Hindi)
Demo में agent ठीक लगता है पर edge cases में फेल होता है। एक prompt बदलाव एक case ठीक करके दस बिगाड़ सकता है। Evals के बिना भरोसा सिर्फ एहसास पर होता है। Evals regression से बचाते हैं और एक ट्रैक करने योग्य संख्या देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a dataset: input + expected output (+ expected tools)
Step 2 → Run the agent on every case, record answer, tool calls, tokens, latency
Step 3 → Score with code checks (exact match, schema, tool names)
Step 4 → Score fuzzy parts with LLM-as-judge (rubric) or human review
Step 5 → Aggregate: accuracy, tool-call accuracy, avg steps, cost, p95 latency
Step 6 → Compare against baseline version; block release on regression
Step 7 → Add production failures to the dataset (the dataset grows)
Step 8 → Run in CI on each prompt/model/tool change
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Dataset बनाओ: input + अपेक्षित output (+ अपेक्षित tools)
Step 2 → हर case पर agent चलाओ, answer, tool calls, tokens, latency record करो
Step 3 → Code से score (exact match, schema, tool names)
Step 4 → अस्पष्ट हिस्सों के लिए LLM-as-judge (rubric) या human review
Step 5 → Aggregate: accuracy, tool accuracy, औसत steps, cost, p95 latency
Step 6 → Baseline से तुलना; regression हो तो release रोको
Step 7 → Production failures को dataset में जोड़ो
Step 8 → हर prompt/model/tool बदलाव पर CI में चलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: A golden set of 200 products with verified HS codes (from past customs rulings). Metrics: exact 6-digit match, 4-digit (chapter/heading) match, correct tool order (`search` before `duty`), average steps, and cost per item. New prompt v2 raises 6-digit accuracy from 78% to 84% but cost rises 30%; the team decides whether it is worth it.

**Zomato-style**: check the agent picks the correct restaurant and respects "no onion".

## 🟡 Real Example Hindi mein
**Tariff System**: 200 products का golden set, जिनके HS codes पुराने customs rulings से verified हैं। Metrics: 6-digit exact match, 4-digit (heading) match, सही tool क्रम, औसत steps, प्रति item cost। नया prompt v2 6-digit accuracy 78% से 84% करता है पर cost 30% बढ़ती है; team तय करती है कि यह सही सौदा है या नहीं।
**Zomato**: सही restaurant चुना और "बिना प्याज" माना या नहीं।

---

## 💻 Code Example — Basic
```python
# Basic: tiny eval harness with exact-match scoring (offline).
from dataclasses import dataclass               # test case record
from typing import Callable

@dataclass
class Case:
    question: str                               # input
    expected_code: str                          # golden answer
    expected_tools: list[str]                   # expected tool order

def fake_agent(question: str) -> dict:
    # Pretend agent: returns answer and the tools it used.
    table = {"bluetooth speaker": "8518.22", "usb cable": "8544.42"}
    return {"answer": table.get(question, "0000.00"), "tools": ["search_hs_code"], "steps": 2}

def evaluate(agent: Callable[[str], dict], cases: list[Case]) -> dict[str, float]:
    exact = heading = tool_ok = steps = 0       # counters
    for c in cases:
        out = agent(c.question)                 # run agent
        exact += out["answer"] == c.expected_code             # 6-digit exact
        heading += out["answer"][:4] == c.expected_code[:4]   # same heading
        tool_ok += out["tools"] == c.expected_tools           # right tool trajectory
        steps += out["steps"]
    n = len(cases)
    return {"exact": exact / n, "heading": heading / n, "tool_acc": tool_ok / n, "avg_steps": steps / n}

if __name__ == "__main__":
    cases = [
        Case("bluetooth speaker", "8518.22", ["search_hs_code"]),
        Case("usb cable", "8544.42", ["search_hs_code"]),
        Case("servo motor", "8501.32", ["search_hs_code"]),     # agent will miss this one
    ]
    print(evaluate(fake_agent, cases))          # exact=0.667 ...
```

## 💻 Code Example — Advanced
```python
# Production: async eval runner with concurrency, LLM-as-judge, thresholds and cost.
import asyncio
import json
import statistics
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

AgentFn = Callable[[str], Awaitable[dict[str, Any]]]     # async agent
JudgeFn = Callable[[str, str, str], Awaitable[int]]      # (question, expected, actual) -> score 1..5

@dataclass
class Result:
    question: str
    exact: bool
    judge: int
    tokens: int
    latency_ms: float
    error: str | None = None

async def run_case(agent: AgentFn, judge: JudgeFn, q: str, expected: str, sem: asyncio.Semaphore) -> Result:
    async with sem:                                      # limit concurrency (rate limits)
        loop = asyncio.get_running_loop()
        start = loop.time()
        try:
            out = await asyncio.wait_for(agent(q), timeout=60)   # per-case timeout
            score = await judge(q, expected, out["answer"])      # fuzzy score
            return Result(q, out["answer"] == expected, score, out.get("tokens", 0),
                          (loop.time() - start) * 1000)
        except Exception as exc:                         # one failure must not kill the run
            return Result(q, False, 1, 0, (loop.time() - start) * 1000, error=repr(exc))

async def run_eval(agent: AgentFn, judge: JudgeFn, dataset: list[tuple[str, str]], concurrency: int = 5) -> dict[str, Any]:
    sem = asyncio.Semaphore(concurrency)
    results = await asyncio.gather(*[run_case(agent, judge, q, e, sem) for q, e in dataset])
    lat = sorted(r.latency_ms for r in results)
    p95 = lat[max(0, int(len(lat) * 0.95) - 1)]          # simple p95
    return {
        "n": len(results),
        "exact_acc": sum(r.exact for r in results) / len(results),
        "judge_avg": statistics.mean(r.judge for r in results),
        "errors": sum(r.error is not None for r in results),
        "avg_tokens": statistics.mean(r.tokens for r in results),
        "p95_ms": p95,
    }

def gate(report: dict[str, Any], baseline: dict[str, Any]) -> bool:
    # Block release if accuracy drops more than 2 points or errors increase.
    return report["exact_acc"] >= baseline["exact_acc"] - 0.02 and report["errors"] <= baseline["errors"]

async def demo_agent(q: str) -> dict[str, Any]:
    await asyncio.sleep(0.01)
    return {"answer": "8518.22" if "speaker" in q else "0000.00", "tokens": 450}

async def demo_judge(q: str, expected: str, actual: str) -> int:
    return 5 if expected == actual else (3 if expected[:4] == actual[:4] else 1)   # replace with LLM judge

if __name__ == "__main__":
    data = [("bluetooth speaker", "8518.22"), ("usb cable", "8544.42")]
    report = asyncio.run(run_eval(demo_agent, demo_judge, data))
    print(json.dumps(report, indent=2))
    print("PASS" if gate(report, {"exact_acc": 0.5, "errors": 0}) else "FAIL")
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, BackgroundTasks     # framework + background jobs
from pydantic import BaseModel

app = FastAPI()
REPORTS: dict[str, dict] = {}                    # use a DB in production

class EvalReq(BaseModel):
    run_id: str
    dataset: list[tuple[str, str]]

async def _do_eval(run_id: str, dataset: list[tuple[str, str]]) -> None:
    REPORTS[run_id] = await run_eval(demo_agent, demo_judge, dataset)   # from Advanced

@app.post("/evals", status_code=202)             # 202 = accepted, running
async def start_eval(req: EvalReq, bg: BackgroundTasks) -> dict:
    bg.add_task(_do_eval, req.run_id, req.dataset)   # do not block the request
    return {"run_id": req.run_id, "status": "running"}

@app.get("/evals/{run_id}")
async def get_eval(run_id: str) -> dict:
    return REPORTS.get(run_id, {"status": "running or unknown"})
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith provides datasets and `evaluate()`; `agentevals` and `openevals` give trajectory and LLM-judge helpers.

```python
from langsmith import Client, evaluate           # LangSmith SDK

client = Client()                                # needs LANGSMITH_API_KEY

def exact_match(outputs: dict, reference_outputs: dict) -> bool:
    return outputs["answer"] == reference_outputs["answer"]   # simple evaluator

def target(inputs: dict) -> dict:
    return {"answer": agent_answer(inputs["question"])}       # call your agent (define agent_answer)

# evaluate(target, data="tariff-golden-set", evaluators=[exact_match], experiment_prefix="prompt-v2")
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Evaluating only the final answer.
✅ Correct: also score trajectory, step count, cost and tool errors.

```python
# Wrong
score = answer == expected
# Right
score = {"answer": answer == expected, "tools_ok": tools == expected_tools, "steps": steps, "tokens": tokens}
```

❌ Mistake 2: Tiny dataset of easy cases.
✅ Correct: include edge cases, adversarial inputs and real production failures.

❌ Mistake 3: Trusting an LLM judge blindly.
✅ Correct: calibrate the judge against human labels, use a rubric, use a different model family than the agent when possible.

---

## 🧠 Tricky Interview Question
**Q**: "Your eval score went up from 80% to 90% after a prompt change, but users complain more. Why?"

**Answer**: Possible reasons: the dataset is not representative (over-fitted to the test set because you tuned the prompt on it), the judge rewards verbose or confident answers, the metric ignores latency/cost or tone, or production inputs differ (languages, typos). Fix: keep a held-out set that you never tune on, refresh with real traffic, use multiple metrics, compare online (A/B, thumbs, escalation rate), and check judge-human agreement.

---

## ⚫ Interview Questions + Answers

Q1: What is a golden dataset?
A1: A curated set of inputs with verified correct outputs, used as a repeatable benchmark.

Q2: Offline vs online evaluation?
A2: Offline runs on a fixed dataset before release. Online measures real traffic (feedback, success rate, cost) after release.

Q3: What is trajectory evaluation?
A3: Checking the steps the agent took: correct tools, order, arguments and number of steps, not only the final answer.

Q4: What is LLM-as-judge and its risks?
A4: A model scores outputs against a rubric. Risks: bias to long answers, self-preference, inconsistency. Reduce with clear rubrics, pairwise comparison and human calibration.

Q5: (Hard) How do you evaluate a non-deterministic agent reliably?
A5: Run each case several times (pass@k or pass^k), use temperature 0 where possible, report variance and confidence intervals, use sufficiently large datasets, and fix seeds/tool mocks so differences come from the agent, not the environment.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Before every prompt, model or tool change
- Comparing models for cost versus quality
- Setting release gates in CI

❌ Avoid when:
- Treating one score as the full truth
- Using eval data to tune the prompt endlessly (overfitting)

---

## 📊 Visual Diagram
```
 Dataset (golden + prod failures)
        │
        ▼
 Run agent ──► answer + tools + tokens + latency
        │
        ▼
 Scorers: code checks │ LLM judge │ human
        │
        ▼
 Report: accuracy, tool acc, steps, cost, p95
        │
        ▼
 Compare with baseline ──► PASS (ship) / FAIL (fix)
```

---

## 💰 Cost Impact
Evals cost tokens: dataset size x agent tokens, plus judge tokens (often as large as the agent call). 200 cases x 2,000 tokens x 2 (agent + judge) is about 800K tokens per run, about $0.12 on a small model at current mini pricing (check prices). Optimise: run a small smoke set on every commit and the full set nightly, cache agent outputs when only the judge changes, use a cheaper judge for easy checks, and run concurrently within rate limits.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Golden set | Verified test dataset | जाँचा हुआ test dataset |
| Trajectory | Steps the agent took | Agent के उठाए कदम |
| LLM-as-judge | Model scores outputs | Model से scoring |
| Regression | New version gets worse | नया version बदतर होना |
| pass@k | Success in at least one of k tries | k में से कम से कम एक सफल |
| Rubric | Scoring guidelines | Scoring के नियम |

---

## ⚡ 3-Line Summary
English: Evaluate agents on a fixed dataset for both answer quality and trajectory, cost and latency. Use code checks plus a calibrated LLM judge, and gate releases on regressions. Keep growing the dataset from real failures.
Hindi: Fixed dataset पर agent का answer quality, trajectory, cost और latency मापो। Code checks और calibrated LLM judge इस्तेमाल करो, regression पर release रोको। Real failures से dataset बढ़ाते रहो।

---

## ➡️ Next Topic
**314. Agent Security** — prompt injection, tool abuse and permissions, because a capable agent is also an attack surface.
