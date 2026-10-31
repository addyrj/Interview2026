---

# 424. Evaluation in LangSmith
# हिंदी में: LangSmith में Evaluation

---

## 🔵 Simple Definition (English)
LangSmith evaluation runs your app (the "target") on every example of a dataset, scores each output with evaluators (code functions or LLM judges), and saves the whole thing as an experiment. You compare experiments to see if a new prompt/model is truly better. The main function is `langsmith.evaluate()` (and `aevaluate()` for async).

## 🔵 सरल परिभाषा (Hindi)
LangSmith evaluation आपके app ("target") को dataset के हर example पर चलाता है, हर output को evaluators (code functions या LLM judges) से score करता है और सब कुछ एक experiment के रूप में सहेजता है। Experiments compare करके देखते हैं कि नया prompt/model सच में बेहतर है या नहीं। मुख्य function `langsmith.evaluate()` है (async के लिए `aevaluate()`)।

---

## 🔴 Problem it Solves
- "It feels better" is not evidence. You need the same data, same metrics and side-by-side numbers.
- Writing your own eval loop (concurrency, retries, storage, UI) repeatedly wastes time.
- Per-example results with traces are needed to understand why a score changed.

## 🔴 यह क्यों बना? (Hindi)
- "बेहतर लग रहा है" सबूत नहीं है। वही data, वही metrics और साथ-साथ numbers चाहिए।
- Eval loop (concurrency, retries, storage, UI) बार-बार खुद लिखना समय की बर्बादी है।
- Score क्यों बदला समझने के लिए traces के साथ per-example results चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Have a dataset (inputs + reference outputs)
Step 2 → Write target(inputs) -> outputs (calls your chain/graph)
Step 3 → Write evaluators: f(outputs, reference_outputs) -> score
Step 4 → evaluate(target, data=..., evaluators=[...], experiment_prefix=...)
Step 5 → For each example: target runs (traced) → evaluators run → feedback saved
Step 6 → Experiment page: per-example outputs, scores, traces, aggregates
Step 7 → Compare experiments (baseline vs candidate); inspect regressions
Step 8 → Optionally repeat N times to measure variance (num_repetitions)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Dataset तैयार रखो (inputs + reference outputs)
Step 2 → target(inputs) -> outputs लिखो (आपकी chain/graph बुलाता है)
Step 3 → Evaluators लिखो: f(outputs, reference_outputs) -> score
Step 4 → evaluate(target, data=..., evaluators=[...], experiment_prefix=...)
Step 5 → हर example पर: target चलता है (traced) → evaluators चलते हैं → feedback save
Step 6 → Experiment page: per-example outputs, scores, traces, aggregates
Step 7 → Experiments compare करो (baseline बनाम candidate); regressions देखो
Step 8 → Variance मापने के लिए चाहें तो N बार दोहराओ (num_repetitions)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Compare `prompt-v3` (baseline) and `prompt-v4` (adds "check chapter notes first") on `tariff-golden` (300 examples). Evaluators: `exact_6digit` (code), `valid_format` (code), `reasoning_grounded` (LLM judge). Results: exact_6digit 0.82 -> 0.87, valid_format 0.99 -> 0.99, reasoning_grounded 0.74 -> 0.81, tokens/example 1,900 -> 2,300. The team decides the +5 points is worth +21% tokens and ships v4 behind a canary.

**Zomato AI**: Compare gpt-4o-mini vs a larger model for dietary-constraint accuracy to decide the cheapest model that passes 98%.

## 🟡 Real Example Hindi mein
**Tariff System**: `tariff-golden` (300 examples) पर `prompt-v3` (baseline) और `prompt-v4` ("पहले chapter notes देखो" जोड़ा) compare करते हैं। Evaluators: `exact_6digit` (code), `valid_format` (code), `reasoning_grounded` (LLM judge)। नतीजे: exact_6digit 0.82 -> 0.87, valid_format 0.99 -> 0.99, reasoning_grounded 0.74 -> 0.81, tokens/example 1,900 -> 2,300। Team तय करती है कि +5 points के लिए +21% tokens ठीक है और v4 को canary के साथ ship करती है।

**Zomato AI**: Dietary-constraint accuracy के लिए gpt-4o-mini बनाम बड़े model compare करके सबसे सस्ता model चुनते हैं जो 98% पास करे।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny evaluate() clone showing the idea: target + evaluators + aggregates (offline)
from typing import Callable                                   # typing

Target = Callable[[dict], dict]                               # inputs -> outputs
Evaluator = Callable[[dict, dict], dict]                      # (outputs, reference) -> {"key","score"}

def my_evaluate(target: Target, data: list[dict], evaluators: list[Evaluator]) -> dict[str, float]:
    totals: dict[str, list[float]] = {}                       # key -> list of scores
    for ex in data:                                           # one example at a time
        try:
            out = target(ex["inputs"])                        # run the app
        except Exception:                                     # app crash => empty output
            out = {}
        for ev in evaluators:                                 # score with each evaluator
            res = ev(out, ex["outputs"])                      # {"key": ..., "score": ...}
            totals.setdefault(res["key"], []).append(float(res["score"]))
    return {k: sum(v) / len(v) for k, v in totals.items()}    # mean score per metric

def target_v1(inputs: dict) -> dict:                          # baseline app
    return {"hs_code": "8507.60" if "bank" in inputs["product"] else "0000.00"}

def exact(out: dict, ref: dict) -> dict:                      # exact-match evaluator
    return {"key": "exact", "score": out.get("hs_code") == ref["hs_code"]}

DATA = [{"inputs": {"product": "power bank"}, "outputs": {"hs_code": "8507.60"}},
        {"inputs": {"product": "laptop"}, "outputs": {"hs_code": "8471.30"}}]
print(my_evaluate(target_v1, DATA, [exact]))                  # {'exact': 0.5}
```

## 💻 Code Example — Advanced
```python
# Real LangSmith evaluation: async target, code + LLM-judge evaluators, repetitions
# pip install langsmith openai
import asyncio                                                # async runtime
import os                                                     # env
from langsmith import aevaluate                               # async evaluate

async def target(inputs: dict) -> dict:
    """The app under test. Replace with chain.ainvoke(...)."""
    product = inputs["product"]
    await asyncio.sleep(0)                                    # placeholder for network calls
    return {"hs_code": "8507.60" if "bank" in product else "8471.30"}

def exact_6digit(outputs: dict, reference_outputs: dict) -> bool:   # evaluator: returns bool score
    a = (outputs.get("hs_code") or "").replace(".", "")[:6]   # first six digits of the answer
    b = reference_outputs["hs_code"].replace(".", "")[:6]     # first six of reference
    return a == b

def valid_format(outputs: dict) -> dict:                      # evaluator may take outputs only
    digits = (outputs.get("hs_code") or "").replace(".", "")
    return {"key": "valid_format", "score": int(digits.isdigit() and len(digits) in (6, 8, 10))}

async def judge_grounded(outputs: dict, inputs: dict) -> dict:
    """LLM judge (optional). Skipped offline."""
    if not os.getenv("OPENAI_API_KEY"):
        return {"key": "grounded", "score": None}            # None = not scored
    from openai import AsyncOpenAI                            # imported lazily
    client = AsyncOpenAI()
    resp = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=3,     # tiny output keeps cost low
        messages=[{"role": "user",
                   "content": f"Product: {inputs['product']}\nHS: {outputs.get('hs_code')}\n"
                              "Is this HS code plausible for the product? Answer YES or NO."}])
    verdict = (resp.choices[0].message.content or "").strip().upper()
    return {"key": "grounded", "score": int(verdict.startswith("Y"))}

async def main() -> None:
    try:
        results = await aevaluate(
            target,                                           # app under test
            data="tariff-golden",                             # dataset name (must exist)
            evaluators=[exact_6digit, valid_format, judge_grounded],
            experiment_prefix="prompt-v4",                    # experiment name prefix
            max_concurrency=4,                                # protect rate limits
            num_repetitions=1,                                # raise to measure variance
            metadata={"prompt": "v4", "model": "gpt-4o-mini"},
        )
        print("experiment:", results.experiment_name)
    except Exception as exc:                                  # dataset/key errors
        print("evaluation failed:", type(exc).__name__, exc)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Provide `POST /admin/evaluate` that starts an evaluation in the background and returns immediately. Evaluations take minutes, so never hold the HTTP request open.

```python
from fastapi import BackgroundTasks, FastAPI                  # framework
from pydantic import BaseModel                                # validation

app = FastAPI()                                               # app
STATUS: dict[str, str] = {}                                   # use Redis/DB in production

class EvalReq(BaseModel):
    prefix: str = "adhoc"
    dataset: str = "tariff-golden"

async def run_job(req: EvalReq) -> None:
    STATUS[req.prefix] = "running"
    try:
        from langsmith import aevaluate
        await aevaluate(target, data=req.dataset, evaluators=[exact_6digit, valid_format],
                        experiment_prefix=req.prefix, max_concurrency=4)
        STATUS[req.prefix] = "done"
    except Exception as exc:
        STATUS[req.prefix] = f"failed: {type(exc).__name__}"

@app.post("/admin/evaluate", status_code=202)
async def start(req: EvalReq, bg: BackgroundTasks) -> dict[str, str]:
    bg.add_task(run_job, req)                                 # runs after the response is sent
    return {"status": "started", "prefix": req.prefix}

@app.get("/admin/evaluate/{prefix}")
async def status(prefix: str) -> dict[str, str]:
    return {"status": STATUS.get(prefix, "unknown")}
```

---

## 🔗 LangChain / LangGraph Connection
Any Runnable or compiled LangGraph graph can be the target: `lambda inputs: chain.invoke(inputs)`. LangChain `Runnable`s can also be passed directly to `evaluate()`. Pre-built LLM-judge evaluators exist in the `openevals` package, which plug in as evaluators.

```python
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI
# chain = ChatPromptTemplate.from_template("HS code for {product}?") | ChatOpenAI(model="gpt-4o-mini")
# evaluate(chain, data="tariff-golden", evaluators=[...])      # Runnable as target
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Comparing experiments run on different dataset versions.
✅ Correct: pin the dataset version (or tag) for both runs.

```python
# Wrong
evaluate(target, data="tariff-golden")      # dataset changed between runs
# Right: fetch examples as of a fixed version/tag and pass them in
examples = client.list_examples(dataset_name="tariff-golden", as_of="v-2025-03")
evaluate(target, data=examples)
```

❌ Mistake 2: Using a noisy LLM judge at temperature > 0 and trusting a 1-point difference.
✅ Correct: `temperature=0`, repeat runs, report mean and spread.

```python
# Wrong
evaluate(..., num_repetitions=1)  # one noisy sample
# Right
evaluate(..., num_repetitions=3)  # estimate variance
```

---

## 🧠 Tricky Interview Question
**Q**: "Experiment B scores 0.86 and A scores 0.84 on 100 examples. Do you declare B the winner?"

**Answer**: Not necessarily. With 100 examples a 2-point difference is within sampling noise (standard error is about 3.5 points for accuracy near 0.85). Use paired comparison on the same examples, look at which examples flipped, repeat runs to estimate evaluator noise, or increase the dataset. Also weigh cost and latency. Declare a winner only when the gap exceeds the uncertainty or is consistently positive across segments.

---

## ⚫ Interview Questions + Answers

Q1: What are the three inputs of `evaluate()`? (Easy)
A1: The target function, the data (dataset), and the evaluators.

Q2: What is an experiment? (Easy)
A2: A saved result of running a target on a dataset, with outputs, scores and traces per example.

Q3: Code evaluator vs LLM-judge evaluator? (Medium)
A3: Code evaluators are deterministic, free and fast (format, exact match). LLM judges handle fuzzy qualities (groundedness, tone) but cost tokens, add noise and need calibration.

Q4: How do you evaluate a LangGraph agent? (Medium)
A4: Use the compiled graph as target; evaluate the final answer and also the trajectory (tools called, number of steps) with custom evaluators reading the run tree.

Q5: How do you stop evaluation costs from exploding? (Hard)
A5: Tiered datasets (smoke/full), `max_concurrency` to avoid rate-limit retries, cheap judge with binary output and `max_tokens` cap, caching target outputs when only evaluators change, deterministic checks first and judge only the ambiguous cases, and scheduled full runs instead of per-commit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Choosing between prompts, models, retrievers
- Pre-release regression checks

❌ Avoid when:
- No reliable reference data (build a dataset first)
- Judging tiny differences with small samples

---

## 📊 Visual Diagram
```
 Dataset ──► for each example ──► target(inputs) ──► outputs
 (v-pinned)                          │ traced
                                     ▼
                     evaluators: exact / format / LLM-judge
                                     │ feedback per example
                                     ▼
                       Experiment A  vs  Experiment B
                       exact 0.82        exact 0.87
                       tokens 1,900      tokens 2,300
                                     │
                              decision: ship / iterate
```

---

## 💰 Cost Impact
- Cost = examples x (target tokens + judge tokens) x repetitions. Example: 300 x (2,000 + 600) x 3 = 2.3M tokens, roughly $0.40-$1 on a small model, but 20x or more with a frontier judge.
- Optimise: judge only after code evaluators pass, binary outputs, small judge model, run a smoke split on PRs, cache outputs, avoid more repetitions than needed.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Target | Function/app being tested | जिस function/app को test कर रहे हैं |
| Evaluator | Scores an output | Output को score करने वाला |
| Experiment | One evaluation result set | एक evaluation का नतीजा |
| Repetitions | Run each example N times | हर example N बार चलाना |
| Pairwise eval | Compare two outputs head to head | दो outputs की सीधी तुलना |
| Aggregate | Mean score across examples | सभी examples का औसत score |

---

## ⚡ 3-Line Summary
English: `evaluate()` runs your target over a dataset, scores outputs with evaluators and stores an experiment you can compare. Use code evaluators first and LLM judges for fuzzy qualities, with temperature 0 and repetitions to measure noise. Always pin dataset versions and check the statistical significance of small gaps.
Hindi: `evaluate()` आपके target को dataset पर चलाता है, evaluators से outputs score करता है और compare करने लायक experiment सहेजता है। पहले code evaluators और फिर धुंधली qualities के लिए LLM judge, temperature 0 और repetitions के साथ। Dataset versions pin करो और छोटे अंतर की statistical significance जाँचो।

---

## ➡️ Next Topic
**425. LangSmith Hub (Prompts)** — versioning the prompts that you are now able to evaluate.
