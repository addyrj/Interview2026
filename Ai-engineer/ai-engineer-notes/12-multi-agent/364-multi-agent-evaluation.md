---

# 364. Multi-Agent Evaluation
# हिंदी में: Multi-Agent Evaluation

---

## 🔵 Simple Definition (English)
Multi-agent evaluation measures whether a team of agents produces **correct results, via sensible steps, at acceptable cost and latency**. You test two levels: the **final outcome** (was the answer right?) and the **trajectory** (did each agent act correctly: right tools, right hand-offs, no loops?).

## 🔵 सरल परिभाषा (Hindi)
Multi-agent evaluation मापता है कि agents की team **सही नतीजे, समझदार steps के साथ, स्वीकार्य cost और latency में** देती है या नहीं। दो स्तरों पर test होता है: **अंतिम नतीजा** (answer सही था?) और **trajectory** (क्या हर agent ने सही किया: सही tools, सही hand-offs, कोई loop नहीं?)।

---

## 🔴 Problem it Solves
Multi-agent systems fail in many hidden ways: a wrong hand-off, a skipped tool, an infinite debate, or a lucky correct answer from bad reasoning. Looking at a few demo outputs is not enough. Without evaluation you cannot compare prompts, models or architectures, detect regressions, or prove the team is better than a single agent.

## 🔴 यह क्यों बना? (Hindi)
Multi-agent systems कई छिपे तरीकों से fail होते हैं: गलत hand-off, छूटा tool, अनंत debate, या खराब reasoning से मिला संयोग वाला सही answer। कुछ demo outputs देखना काफ़ी नहीं। Evaluation के बिना आप prompts, models या architectures की तुलना, regression की पहचान, या यह साबित नहीं कर सकते कि team एक अकेले agent से बेहतर है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a golden dataset: inputs + expected outputs (+ expected key steps)
Step 2 → Run the full multi-agent system on each case, capture traces
Step 3 → Score outcome: exact match, field accuracy, or LLM-as-judge rubric
Step 4 → Score trajectory: right agents/tools called, order, step count
Step 5 → Score each agent in isolation (unit evals) to find the weak one
Step 6 → Track cost: tokens per run, per agent; latency p50/p95
Step 7 → Compare against baseline (single agent) and previous version
Step 8 → Gate releases in CI; monitor production samples continuously
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Golden dataset बनाओ: inputs + अपेक्षित outputs (+ मुख्य steps)
Step 2 → हर case पर पूरा multi-agent system चलाओ, traces सहेजो
Step 3 → Outcome score करो: exact match, field accuracy या LLM-as-judge rubric
Step 4 → Trajectory score करो: सही agents/tools, क्रम, steps की संख्या
Step 5 → हर agent को अलग से test करो ताकि कमज़ोर कड़ी मिले
Step 6 → Cost नापो: प्रति run और प्रति agent tokens; latency p50/p95
Step 7 → Baseline (अकेला agent) और पिछले version से तुलना करो
Step 8 → CI में release gate लगाओ; production samples पर लगातार निगरानी
```

---

## 🟡 Real World Example
**Tariff Classification System**: A golden set of 200 products with verified HS codes. For each, record the expected tool calls (`search_tariff` must be called before `get_duty_rate`). Metrics: HS accuracy at 6 digits and 8 digits, validator pass rate, human-escalation rate, tokens per case, p95 latency. After changing the classifier prompt, accuracy rises from 86 to 91 percent but cost rises 40 percent, a trade-off you can now see and decide on.

**Amazon-style**: A support multi-agent team measured on resolution rate, wrong-refund rate and average turns.

## 🟡 Real Example Hindi mein
**Tariff System**: 200 products का golden set जिनके HS codes सत्यापित हैं। हर case के लिए अपेक्षित tool calls दर्ज करो (`get_duty_rate` से पहले `search_tariff` बुलाना ज़रूरी)। Metrics: 6-digit और 8-digit पर HS accuracy, validator pass rate, human-escalation rate, प्रति case tokens, p95 latency। Classifier prompt बदलने पर accuracy 86 से 91 प्रतिशत हुई पर cost 40 प्रतिशत बढ़ी; यह trade-off अब दिखता है और आप फैसला कर सकते हैं।

**Amazon-style**: Support multi-agent team को resolution rate, गलत-refund rate और औसत turns पर नापा जाता है।

---

## 💻 Code Example — Basic
```python
# Evaluate outcome + trajectory on a golden set with a mock system (runs offline)
from dataclasses import dataclass  # record types

@dataclass
class Case:
    product: str            # input
    expected_code: str      # correct HS code
    required_tools: list[str]  # tools that must appear in the trace, in order

@dataclass
class Run:
    code: str               # system answer
    tools: list[str]        # tools actually called
    tokens: int             # tokens used

def mock_system(product: str) -> Run:
    if "headphones" in product:
        return Run("8518.30", ["search_tariff", "get_duty_rate"], 1200)  # correct
    return Run("9999.99", ["get_duty_rate"], 600)  # wrong and skipped search

def in_order(required: list[str], actual: list[str]) -> bool:
    it = iter(actual)
    return all(any(r == a for a in it) for r in required)  # subsequence check

def evaluate(cases: list[Case]) -> dict[str, float]:
    ok_out = ok_traj = tok = 0
    for c in cases:
        r = mock_system(c.product)  # run system
        ok_out += r.code == c.expected_code          # outcome correct?
        ok_traj += in_order(c.required_tools, r.tools)  # trajectory correct?
        tok += r.tokens
    n = max(len(cases), 1)
    return {"outcome_acc": ok_out / n, "trajectory_acc": ok_traj / n, "avg_tokens": tok / n}

if __name__ == "__main__":
    data = [
        Case("bluetooth headphones", "8518.30", ["search_tariff", "get_duty_rate"]),
        Case("smart ring", "8517.62", ["search_tariff", "get_duty_rate"]),
    ]
    print(evaluate(data))  # {'outcome_acc': 0.5, 'trajectory_acc': 0.5, 'avg_tokens': 900.0}
```

## 💻 Code Example — Advanced
```python
# Async eval harness: concurrency limit, timeouts, per-agent stats, percentile latency
import asyncio  # async runtime
import statistics  # percentiles
import time  # latency

async def run_system(product: str) -> dict:
    await asyncio.sleep(0.01)  # fake latency; real code: await graph.ainvoke(...)
    return {"code": "8518.30" if "headphones" in product else "0000.00",
            "per_agent_tokens": {"classifier": 700, "duty": 200}}

async def eval_case(sem: asyncio.Semaphore, product: str, expected: str) -> dict:
    async with sem:  # limit parallel API usage
        t0 = time.perf_counter()
        try:
            out = await asyncio.wait_for(run_system(product), timeout=30)
            return {"ok": out["code"] == expected, "lat": time.perf_counter() - t0, "tok": out["per_agent_tokens"]}
        except Exception as exc:  # failures count as misses, not crashes
            return {"ok": False, "lat": time.perf_counter() - t0, "tok": {}, "err": str(exc)}

async def main() -> None:
    cases = [("bluetooth headphones", "8518.30"), ("smart ring", "8517.62")] * 10
    sem = asyncio.Semaphore(5)  # at most 5 concurrent runs
    res = await asyncio.gather(*(eval_case(sem, p, e) for p, e in cases))
    lats = sorted(r["lat"] for r in res)
    agent_tok: dict[str, int] = {}
    for r in res:
        for a, t in r["tok"].items():
            agent_tok[a] = agent_tok.get(a, 0) + t  # tokens per agent
    print("accuracy", sum(r["ok"] for r in res) / len(res))
    print("p50", statistics.median(lats), "p95", lats[int(0.95 * (len(lats) - 1))])
    print("tokens per agent", agent_tok)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Add an endpoint that triggers an evaluation run in the background and another that returns the latest report, so CI or a dashboard can use them.

```python
from fastapi import BackgroundTasks, FastAPI  # framework

app = FastAPI()
REPORTS: dict[str, dict] = {}  # use a DB in production

async def do_eval(run_id: str) -> None:
    REPORTS[run_id] = {"status": "running"}
    try:
        REPORTS[run_id] = {"status": "done", "metrics": evaluate([])}  # plug the real golden set here
    except Exception as exc:
        REPORTS[run_id] = {"status": "failed", "error": str(exc)}

@app.post("/eval/{run_id}")
async def start(run_id: str, bg: BackgroundTasks) -> dict:
    bg.add_task(do_eval, run_id)  # do not block the request
    return {"run_id": run_id, "status": "started"}

@app.get("/eval/{run_id}")
async def report(run_id: str) -> dict:
    return REPORTS.get(run_id, {"status": "unknown"})
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith datasets and `evaluate` run your graph on a dataset and score it with custom evaluators. LangGraph traces expose every node call, so trajectory checks are possible.

```python
from langsmith import Client, evaluate  # LangSmith SDK (needs LANGSMITH_API_KEY)

def target(inputs: dict) -> dict:
    out = graph.invoke({"description": inputs["product"]})  # your compiled LangGraph
    return {"hs_code": out["hs_code"]}

def correct(outputs: dict, reference_outputs: dict) -> bool:
    return outputs["hs_code"] == reference_outputs["hs_code"]  # custom evaluator

client = Client()
# dataset "tariff-golden" holds examples with inputs={"product":..}, outputs={"hs_code":..}
results = evaluate(target, data="tariff-golden", evaluators=[correct], experiment_prefix="classifier-v2")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Evaluating only the final answer
✅ Correct: also check trajectory, cost and step count.

```python
# Wrong
score = output == expected
# Right
score = {"outcome": output == expected, "trajectory_ok": in_order(req, tools), "tokens": tok}
```

❌ Mistake 2: A tiny, hand-picked test set and a single run
✅ Correct: a diverse set with edge cases, repeated runs for non-determinism.

```python
# Wrong
cases = cases[:3]
# Right
scores = [evaluate(cases) for _ in range(3)]   # average over runs, report variance
```

---

## 🧠 Tricky Interview Question
**Q**: "Your multi-agent system scores 92 percent, a single-agent baseline scores 91 percent but costs 5 times less. What do you do?"

**Answer**: A 1-point gain may be within noise; check confidence intervals and per-category breakdown. If the multi-agent is better only on a hard slice (for example ambiguous products), route only those cases to it (a router). Otherwise, ship the single agent. Always report quality per dollar and latency, not accuracy alone.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is a golden dataset?
A1: A set of inputs with verified expected outputs used to measure the system repeatedly.

Q2: [Easy] Outcome vs trajectory evaluation?
A2: Outcome checks the final result. Trajectory checks the path: tools used, order, hand-offs, and number of steps.

Q3: [Medium] What is LLM-as-judge and its risk?
A3: An LLM scores outputs against a rubric. Risks: bias toward its own style, verbosity bias, inconsistency. Mitigate with clear rubrics, calibration against human labels, and pairwise comparisons.

Q4: [Medium] How do you find which agent is the weak one?
A4: Unit-eval each agent with fixed inputs, inspect traces for first error, and compute per-agent error attribution.

Q5: [Hard] How do you handle non-determinism in evals?
A5: Low temperature, fixed seeds where possible, multiple runs per case, report mean and variance, use enough cases for statistical power, and compare with significance tests before deciding.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Before any production launch and after every prompt, model or tool change
- Comparing architectures (single vs multi-agent)

❌ Avoid when:
- Never skip it, but keep evals small and cheap during early prototyping

---

## 📊 Visual Diagram
```
 Golden set ---> [Multi-agent system] ---> trace + output
                                              |
        +-------------------+-----------------+-----------------+
        v                   v                 v                 v
   Outcome score      Trajectory score    Cost/latency     Per-agent errors
   (accuracy)         (tools, order)      (tokens, p95)    (who failed first)
        \__________________ report + CI gate vs baseline ________/
```

---

## 💰 Cost Impact
- An eval run costs the same as production runs: 200 cases x 3,000 tokens = 600K tokens (about $0.09 on gpt-4o-mini input prices, more with an LLM judge).
- LLM-as-judge adds another call per case.
- Optimise: small smoke set on every commit, full set nightly, cache unchanged cases, cheaper judge model, deterministic checks first, sample production traffic instead of re-running everything.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Golden dataset | Verified test cases | सत्यापित test cases |
| Trajectory | Sequence of agent steps | Agent steps का क्रम |
| LLM-as-judge | LLM scoring outputs | LLM द्वारा output की जाँच |
| Regression | New version gets worse | नया version खराब होना |
| Baseline | Reference system to beat | तुलना के लिए संदर्भ system |
| p95 latency | 95 percent of runs are faster | 95 प्रतिशत runs इससे तेज़ |

---

## ⚡ 3-Line Summary
English: Evaluate multi-agent systems on outcome, trajectory, cost and latency using a golden dataset. Test agents individually and compare with a single-agent baseline. Automate in CI and monitor production.
Hindi: Multi-agent systems को golden dataset से outcome, trajectory, cost और latency पर परखो। Agents को अलग-अलग test करो और अकेले agent baseline से तुलना करो। CI में automate करो और production पर नज़र रखो।

---

## ➡️ Next Topic
**365. Multi-Agent Best Practices** — a checklist that pulls the whole section together.
