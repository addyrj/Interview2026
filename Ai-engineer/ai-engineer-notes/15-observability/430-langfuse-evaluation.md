---

# 430. Langfuse Evaluation
# हिंदी में: Langfuse Evaluation (Quality नापना)

---

## 🔵 Simple Definition (English)
Langfuse evaluation means attaching **scores** to traces and running your app on a **dataset** of test cases to measure quality. Scores can come from users (thumbs up), code (exact match on HS code), or an LLM judge. Tracing tells you what happened; evaluation tells you if it was good.

## 🔵 सरल परिभाषा (Hindi)
Langfuse evaluation में traces पर **scores** लगाए जाते हैं और एक **dataset** के test cases पर app चलाकर quality नापी जाती है। Score user (thumbs up), code (HS code exact match) या LLM judge से आ सकता है। Tracing बताती है क्या हुआ, evaluation बताती है कि अच्छा हुआ या नहीं।

---

## 🔴 Problem it Solves
- "It feels better" is not a measurement. After changing a prompt or model you need numbers: accuracy went 82% to 88%, or it dropped.
- Production traces are thousands per day; humans cannot read them all. Automatic scoring surfaces the bad ones.
- Without a fixed dataset, two experiments are not comparable.

## 🔴 यह क्यों बना? (Hindi)
- "लगता है बेहतर है" measurement नहीं है। Prompt या model बदलने के बाद numbers चाहिए: accuracy 82% से 88% हुई या गिरी।
- Production में रोज़ हज़ारों traces होते हैं, इंसान सब नहीं पढ़ सकता। Automatic scoring खराब वाले ऊपर लाती है।
- Fixed dataset के बिना दो experiments की तुलना नहीं हो सकती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a DATASET: items with input + expected_output (golden HS codes)
Step 2 → Define an EVALUATOR: function(output, expected) -> score (0..1)
Step 3 → Run the app on every dataset item; each run becomes a trace linked to the item
Step 4 → Evaluator posts SCORES to each trace (accuracy, format_ok, judge_score)
Step 5 → Compare RUNS side by side in UI (prompt v1 vs v2, gpt-4o-mini vs gpt-4o)
Step 6 → Online: also score live production traces (sampled) and user feedback
Step 7 → Set alert/threshold; block deploy if accuracy drops
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → DATASET बनाओ: input + expected_output (सही HS codes)
Step 2 → EVALUATOR लिखो: function(output, expected) -> score (0..1)
Step 3 → हर dataset item पर app चलाओ; हर run एक trace बनता है
Step 4 → Evaluator हर trace पर SCORES डालता है (accuracy, format_ok, judge_score)
Step 5 → UI में RUNS की तुलना करो (prompt v1 vs v2, मॉडल vs मॉडल)
Step 6 → Online: live production traces और user feedback भी score करो
Step 7 → Threshold रखो; accuracy गिरे तो deploy रोको
```

---

## 🟡 Real World Example
**Tariff Classification System**: 200 golden products with correct 6-digit HS codes. A new prompt is tested: exact match on 6 digits (code evaluator) plus an LLM judge that rates the justification text 1-5. Result table: prompt v1 = 81% exact, prompt v2 = 87% exact but judge score dropped from 4.4 to 3.9 (explanations got shorter). The team ships v2 with a requirement to restore the explanation style.

**Amazon-style**: product-title generation scored by a judge for "no false claims"; thumbs-down from sellers recorded as a `user_feedback` score.

## 🟡 Real Example Hindi mein
**Tariff System**: 200 golden products जिनके सही 6-digit HS codes पता हैं। नया prompt test: code evaluator (6 digit exact match) और LLM judge जो justification को 1-5 रेट करता है। Result: prompt v1 = 81% exact, v2 = 87% exact लेकिन judge score 4.4 से 3.9 हो गया (explanation छोटी हो गई)। Team v2 ship करती है पर explanation style वापस लाने की शर्त के साथ।

---

## 💻 Code Example — Basic
Offline evaluation loop in pure Python (the same logic you later send to Langfuse).

```python
# Tiny evaluation harness: dataset -> app -> evaluators -> report
from dataclasses import dataclass            # simple data containers
from typing import Callable                  # type hints


@dataclass
class Item:                                  # one dataset item
    input: str                               # product description
    expected: str                            # golden HS code


DATASET: list[Item] = [                      # small golden set
    Item("Bluetooth speaker", "8518.22"),
    Item("Cotton t-shirt men", "6109.10"),
    Item("Lithium-ion battery pack", "8507.60"),
]


def fake_app(text: str) -> str:              # stand-in for the real LLM pipeline
    table = {"Bluetooth speaker": "8518.22", "Cotton t-shirt men": "6109.90"}
    return table.get(text, "0000.00")        # unknown -> wrong code


def exact_match(out: str, exp: str) -> float:    # evaluator 1: full code equal
    return 1.0 if out == exp else 0.0


def heading_match(out: str, exp: str) -> float:  # evaluator 2: first 4 digits equal
    return 1.0 if out[:4] == exp[:4] else 0.0


EVALS: dict[str, Callable[[str, str], float]] = {   # name -> function
    "exact": exact_match, "heading": heading_match,
}

totals = {name: 0.0 for name in EVALS}       # running sums
for item in DATASET:                         # run app on every item
    out = fake_app(item.input)               # get prediction
    for name, fn in EVALS.items():           # score with each evaluator
        totals[name] += fn(out, item.expected)

for name, total in totals.items():           # print averages
    print(f"{name}: {total / len(DATASET):.2f}")
```

## 💻 Code Example — Advanced
Langfuse SDK v3: create dataset, run app per item, push scores, LLM-as-judge. (`pip install langfuse openai`; needs Langfuse and OpenAI keys.)

```python
# Production evaluation with Langfuse datasets + scores + LLM judge (async-friendly)
import asyncio                                         # run judge calls concurrently
import logging                                         # log failures
from typing import Any                                 # type hints

from langfuse import get_client                        # Langfuse v3 client
from openai import AsyncOpenAI                         # async OpenAI client

log = logging.getLogger("eval")                        # logger
lf = get_client()                                      # singleton Langfuse client
oai = AsyncOpenAI()                                    # judge model client
DATASET_NAME = "tariff-golden-v1"                      # dataset name


def seed_dataset(rows: list[tuple[str, str]]) -> None:
    """Create dataset once and add items (input, expected HS code)."""
    try:
        lf.create_dataset(name=DATASET_NAME)           # raises or no-op if exists
    except Exception as exc:                           # dataset may already exist
        log.info("dataset exists? %s", exc)
    for text, code in rows:                            # add every golden item
        lf.create_dataset_item(
            dataset_name=DATASET_NAME,
            input={"product": text},
            expected_output={"hs_code": code},
        )


async def judge(product: str, answer: str) -> float:
    """LLM-as-judge: score explanation quality 0..1."""
    resp = await oai.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=5,   # tiny output = cheap
        messages=[
            {"role": "system", "content": "Rate 1-5 how well the answer justifies the HS code. Reply with one digit."},
            {"role": "user", "content": f"Product: {product}\nAnswer: {answer}"},
        ],
    )
    raw = (resp.choices[0].message.content or "3").strip()[:1]  # first char only
    return (int(raw) / 5) if raw.isdigit() else 0.0             # normalise, safe parse


async def run_experiment(app, run_name: str) -> dict[str, float]:
    """Run `app(product)->str` over the dataset and score each trace."""
    ds = lf.get_dataset(DATASET_NAME)                  # fetch dataset
    acc: list[float] = []                              # collect exact-match scores
    for item in ds.items:                              # iterate items
        with item.run(run_name=run_name) as span:      # links trace to dataset item
            out: str = await app(item.input["product"])    # run your pipeline
            exp = item.expected_output["hs_code"]      # golden answer
            exact = 1.0 if exp in out else 0.0         # code evaluator
            span.score_trace(name="exact_match", value=exact)       # push score
            span.score_trace(name="judge", value=await judge(item.input["product"], out))
            acc.append(exact)
    lf.flush()                                         # send everything
    return {"exact_match": sum(acc) / max(len(acc), 1)}


def user_feedback(trace_id: str, thumbs_up: bool) -> None:
    """Online score from the UI's thumbs button."""
    lf.create_score(trace_id=trace_id, name="user_feedback",
                    value=1.0 if thumbs_up else 0.0, data_type="NUMERIC")
```

---

## 🟠 FastAPI Integration
Expose a feedback endpoint so the front-end sends thumbs up/down against a `trace_id`.

```python
# FastAPI feedback route -> Langfuse score
from fastapi import FastAPI, HTTPException            # framework
from pydantic import BaseModel, Field                 # validation
from langfuse import get_client                       # client

app = FastAPI()                                       # app
lf = get_client()                                     # langfuse


class Feedback(BaseModel):                            # request body
    trace_id: str
    thumbs_up: bool
    comment: str | None = Field(default=None, max_length=500)


@app.post("/feedback")                                # POST /feedback
async def feedback(fb: Feedback) -> dict[str, str]:
    try:
        lf.create_score(trace_id=fb.trace_id, name="user_feedback",
                        value=1.0 if fb.thumbs_up else 0.0,
                        data_type="NUMERIC", comment=fb.comment)
        return {"status": "recorded"}
    except Exception as exc:                          # do not leak internals
        raise HTTPException(status_code=500, detail="could not record") from exc
```

---

## 🔗 LangChain / LangGraph Connection
Run a chain over dataset items with the Langfuse callback so each run is linked to its trace; then score.

```python
# LangChain chain evaluated against a Langfuse dataset
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

lf = get_client()
chain = ChatPromptTemplate.from_template("HS code for: {p}. Code only.") | ChatOpenAI(model="gpt-4o-mini")

for item in lf.get_dataset("tariff-golden-v1").items:       # loop dataset
    with item.run(run_name="chain-v2") as span:             # link run
        out = chain.invoke({"p": item.input["product"]},
                           config={"callbacks": [CallbackHandler()]})   # trace the chain
        ok = item.expected_output["hs_code"] in out.content
        span.score_trace(name="exact_match", value=float(ok))
# LangGraph: pass the same callback in graph.invoke(config=...) to score full agent runs.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Evaluating on the same examples you tuned the prompt on
✅ Correct: keep a held-out test split.

```python
# Wrong: tune and test on the same 50 items -> overfitting, inflated score
# Right: split once, tune on dev, report only on untouched test
dev, test = DATASET[:40], DATASET[40:]
```

❌ Mistake 2: Trusting an LLM judge blindly
✅ Correct: calibrate the judge against 30-50 human labels and use a stronger or different model than the one being judged.

```python
# Wrong: same model judges itself, no calibration
# Right: compare judge vs human labels, check agreement before using it in CI
agreement = sum(j == h for j, h in zip(judge_labels, human_labels)) / len(human_labels)
assert agreement > 0.8
```

---

## 🧠 Tricky Interview Question
**Q**: "Your offline accuracy is 90% but users thumbs-down 30% of answers. What is wrong?"

**Answer**: The dataset does not represent production. Typical causes: golden set is clean and short while real inputs are messy (typos, Hindi/English mix, vague descriptions); exact-match metric ignores explanation quality; selection bias in feedback (unhappy users click more). Fix: sample real production traces into the dataset (with labels), add online scores, stratify metrics by segment, and track both offline and online numbers.

---

## ⚫ Interview Questions + Answers

Q1 (Easy): What is a score in Langfuse?
A1: A named numeric, boolean or categorical value attached to a trace or observation, such as `exact_match=1` or `user_feedback=0`.

Q2 (Easy): What is a dataset?
A2: A versioned collection of inputs with optional expected outputs, used to run repeatable experiments.

Q3 (Medium): Offline vs online evaluation?
A3: Offline runs on a fixed dataset before release (regression testing). Online scores live traffic after release (drift, real user quality). You need both.

Q4 (Medium): When would you use LLM-as-judge instead of code evaluators?
A4: When quality is subjective or open-ended (explanation, tone, faithfulness). Use code evaluators when a ground truth exists (HS code equality) because they are free, fast and deterministic.

Q5 (Hard): How do you stop prompt regressions reaching production?
A5: Put the dataset run in CI: run the new prompt/model on the golden set, compute metrics, compare with the last accepted run, and fail the pipeline if any key metric drops beyond a tolerance. Add canary traffic and online scores after release, and keep adding failed production cases to the dataset.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You change prompts, models or retrieval and need proof of improvement
- You must monitor live quality with user feedback or sampled judge scores
- Several people compare experiments

❌ Avoid when:
- You have no idea what "correct" means yet (define the task first)
- A tiny prototype with 3 hand-checked examples

---

## 📊 Visual Diagram
```
 Dataset (200 items) ──> App v2 ──> Traces ──> Evaluators ──> Scores
        │                                          │
        │                                  exact_match 0.87
        └──── expected outputs ───────────>  judge       0.78
                                                  │
 Run "prompt-v1": 0.81      Run "prompt-v2": 0.87  ──> compare in UI
 Live traffic ──> sampled judge + thumbs ──> online scores ──> alert
```

---

## 💰 Cost Impact
- Code evaluators cost zero tokens. LLM judges add tokens: 200 items x (about 300 input + 5 output) on gpt-4o-mini is roughly 60k tokens, about $0.01 per full run.
- Online judging every request doubles LLM calls; sample 5-10% instead.
- Use `max_tokens` small for judges, cheap judge model, and cache judge results for unchanged outputs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Score | Metric attached to a trace | Trace पर लगा metric |
| Dataset | Golden inputs and expected outputs | Test cases का set |
| Run | One execution over a dataset | Dataset पर एक बार चलाना |
| LLM-as-judge | LLM that grades outputs | Output जाँचने वाला LLM |
| Golden set | Human-verified answers | इंसान से verified सही उत्तर |
| Regression | Quality drop after a change | बदलाव के बाद quality गिरना |
| Online eval | Scoring live traffic | Live traffic की scoring |

---

## ⚡ 3-Line Summary
English: Langfuse evaluation = datasets plus scores. Run your app on golden items, score with code, LLM judge and user feedback, and compare runs. Put it in CI to catch regressions and sample live traffic for drift.
Hindi: Langfuse evaluation = datasets और scores। Golden items पर app चलाओ, code, LLM judge और user feedback से score करो और runs की तुलना करो। CI में लगाओ ताकि regression पकड़ में आए, और live traffic sample करके drift देखो।

---

## ➡️ Next Topic
**431. Phoenix (Arize) Tracing** — another popular open-source tracing tool built on OpenTelemetry; compare with Langfuse.
