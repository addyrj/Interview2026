---

# 423. Datasets in LangSmith
# हिंदी में: LangSmith में Datasets

---

## 🔵 Simple Definition (English)
A LangSmith dataset is a saved collection of examples. Each example has `inputs`, optional reference `outputs` (the correct answer) and optional metadata. You run your app on a dataset to measure quality, compare versions, and catch regressions. Datasets can be created from code, CSV, or directly from production traces.

## 🔵 सरल परिभाषा (Hindi)
LangSmith dataset examples का सहेजा हुआ संग्रह है। हर example में `inputs`, optional reference `outputs` (सही answer) और optional metadata होता है। Dataset पर अपना app चलाकर quality मापते हैं, versions compare करते हैं और regressions पकड़ते हैं। Datasets code, CSV या सीधे production traces से बन सकते हैं।

---

## 🔴 Problem it Solves
- Test cases scattered in notebooks and spreadsheets, impossible to share or version.
- No single "golden set" to compare prompt v3 and v4 fairly.
- Production failures are forgotten instead of becoming permanent tests.

## 🔴 यह क्यों बना? (Hindi)
- Test cases notebooks और spreadsheets में बिखरे हैं, share या version करना असंभव।
- Prompt v3 और v4 को निष्पक्ष compare करने के लिए एक "golden set" नहीं।
- Production failures भुला दी जाती हैं, स्थायी tests नहीं बनतीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create dataset: client.create_dataset("tariff-golden")
Step 2 → Add examples: inputs + reference outputs (+ metadata, splits)
Step 3 → Every change creates a new dataset VERSION (timestamped, taggable)
Step 4 → Optionally split into train/dev/test (example "splits")
Step 5 → Run experiment: evaluate(target, data="tariff-golden", evaluators=[...])
Step 6 → Each example runs through target → outputs scored → experiment saved
Step 7 → Compare experiments side by side in the UI
Step 8 → Add new examples from failing production runs (flywheel)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Dataset बनाओ: client.create_dataset("tariff-golden")
Step 2 → Examples जोड़ो: inputs + reference outputs (+ metadata, splits)
Step 3 → हर बदलाव नया dataset VERSION बनाता है (timestamp, tag हो सकता है)
Step 4 → चाहें तो train/dev/test splits में बाँटो
Step 5 → Experiment चलाओ: evaluate(target, data="tariff-golden", evaluators=[...])
Step 6 → हर example target से गुज़रता है → outputs score होते हैं → experiment save
Step 7 → UI में experiments साथ-साथ compare करो
Step 8 → Failing production runs से नए examples जोड़ो (flywheel)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Dataset `tariff-golden` has 300 examples: `inputs={"product": "lithium power bank 10000mAh"}`, `outputs={"hs_code": "8507.60"}`, `metadata={"section": "XVI", "difficulty": "hard"}`. A 60-example `test` split is never used for prompt tuning. After each release, failures from `tariff-prod` with `correctness=0` are reviewed by a customs expert and appended, producing a new dataset version. The dataset grows from 300 to 420 over a quarter, and each release is evaluated on the latest version.

**Amazon-style catalog AI**: separate datasets per category group (electronics, apparel), so per-category accuracy is tracked.

## 🟡 Real Example Hindi mein
**Tariff System**: Dataset `tariff-golden` में 300 examples हैं: `inputs={"product": "lithium power bank 10000mAh"}`, `outputs={"hs_code": "8507.60"}`, `metadata={"section": "XVI", "difficulty": "hard"}`। 60 examples का `test` split prompt tuning में कभी इस्तेमाल नहीं होता। हर release के बाद `tariff-prod` के `correctness=0` failures customs expert review करता है और जोड़ देता है, जिससे नया dataset version बनता है। एक quarter में dataset 300 से 420 हो जाता है।

**Amazon-style catalog AI**: category groups (electronics, apparel) के अलग datasets, ताकि category-wise accuracy दिखे।

---

## 💻 Code Example — Basic
```python
# Basic: a local dataset with versioning idea (pure Python, offline)
import json                                                   # serialise datasets
from dataclasses import dataclass, asdict                     # structured example
from hashlib import sha256                                    # version fingerprint

@dataclass
class Example:                                                # one test example
    inputs: dict[str, str]                                    # what we give the app
    outputs: dict[str, str]                                   # expected answer
    split: str = "dev"                                        # dev or test

DATASET: list[Example] = [
    Example({"product": "power bank"}, {"hs_code": "8507.60"}),
    Example({"product": "laptop"}, {"hs_code": "8471.30"}, "test"),
]

def version_of(ds: list[Example]) -> str:
    blob = json.dumps([asdict(e) for e in ds], sort_keys=True)  # stable text form
    return sha256(blob.encode()).hexdigest()[:10]              # same data => same version

print("version before:", version_of(DATASET))
DATASET.append(Example({"product": "silk saree"}, {"hs_code": "5007.20"}))  # add an example
print("version after :", version_of(DATASET))                  # version changes
print("test split    :", [e.inputs for e in DATASET if e.split == "test"])
```

## 💻 Code Example — Advanced
```python
# Real LangSmith dataset management: create, add examples (batch), splits, read, async-safe
# pip install langsmith
import asyncio                                                # to run sync SDK calls in a thread
import logging                                                # logs
from langsmith import Client                                  # SDK client

log = logging.getLogger("datasets")                           # logger

EXAMPLES: list[dict] = [                                      # source data (could be CSV/DB)
    {"product": "lithium power bank 10000mAh", "hs": "8507.60", "split": "dev"},
    {"product": "cotton men's shirt", "hs": "6105.10", "split": "dev"},
    {"product": "ceramic floor tile", "hs": "6908.90", "split": "test"},
]

def get_or_create(client: Client, name: str, description: str):
    try:
        return client.read_dataset(dataset_name=name)         # reuse if it exists
    except Exception:                                         # not found => create
        return client.create_dataset(dataset_name=name, description=description)

def upload(client: Client, name: str, rows: list[dict]) -> int:
    ds = get_or_create(client, name, "Golden tariff classification examples")
    clean = [r for r in rows if r.get("product") and r.get("hs")]    # skip incomplete rows
    if not clean:
        raise ValueError("no valid rows to upload")           # fail loudly
    client.create_examples(
        inputs=[{"product": r["product"]} for r in clean],    # what the app receives
        outputs=[{"hs_code": r["hs"]} for r in clean],        # reference answers
        metadata=[{"source": "expert"} for _ in clean],       # same length as inputs
        splits=[r["split"] for r in clean],                   # per-example split name
        dataset_id=ds.id,                                     # target dataset
    )
    return len(clean)

async def main() -> None:
    try:
        client = Client()                                     # needs LANGSMITH_API_KEY
        n = await asyncio.to_thread(upload, client, "tariff-golden", EXAMPLES)
        print("uploaded", n)
        for ex in client.list_examples(dataset_name="tariff-golden", splits=["test"]):
            print(ex.inputs, "->", ex.outputs)                # read back the test split
    except Exception as exc:                                  # config/network errors
        print("dataset job failed:", type(exc).__name__)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Endpoint where an expert reviewer submits a corrected answer for a failed run; it becomes a new dataset example. Validate input and keep the call off the event loop.

```python
import asyncio                                                # thread offload
from fastapi import FastAPI, HTTPException                    # framework
from pydantic import BaseModel, Field                         # validation
from langsmith import Client                                  # SDK

app = FastAPI()                                               # app

class Correction(BaseModel):                                  # request body
    product: str = Field(min_length=2)                        # original input
    correct_hs: str = Field(pattern=r"^\d{4}(\.\d{2}){0,2}$") # 8507 or 8507.60 or 8507.60.00

def add_example(c: Correction) -> None:
    client = Client()                                         # create client
    ds = client.read_dataset(dataset_name="tariff-golden")    # must exist
    client.create_examples(inputs=[{"product": c.product}],
                           outputs=[{"hs_code": c.correct_hs}],
                           dataset_id=ds.id)

@app.post("/admin/corrections", status_code=201)
async def correction(c: Correction) -> dict[str, str]:
    try:
        await asyncio.to_thread(add_example, c)               # blocking SDK in a thread
    except Exception as exc:
        raise HTTPException(status_code=502, detail=type(exc).__name__)
    return {"status": "added"}
```

---

## 🔗 LangChain / LangGraph Connection
`evaluate()` consumes a dataset by name, id, or an iterable of examples. The `target` function receives `inputs` and returns outputs. Evaluators receive the run outputs and the reference example outputs. For LangGraph, the compiled graph's `invoke` is the target.

```python
# from langsmith import evaluate
# def target(inputs: dict) -> dict:
#     return {"hs_code": chain.invoke(inputs["product"])}
# def exact(outputs: dict, reference_outputs: dict) -> bool:
#     return outputs["hs_code"] == reference_outputs["hs_code"]
# evaluate(target, data="tariff-golden", evaluators=[exact], experiment_prefix="prompt-v4")
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting expected answers inside `inputs`, so the app (or prompt) sees them.
✅ Correct: keep reference answers only in `outputs`.

```python
# Wrong
inputs={"product": "power bank", "expected": "8507.60"}
# Right
inputs={"product": "power bank"}, outputs={"hs_code": "8507.60"}
```

❌ Mistake 2: Uploading unlabelled production failures as if they were correct references.
✅ Correct: have an expert fill the correct output before adding, or mark them `needs_review` in metadata.

```python
# Wrong: use the model's wrong answer as reference
outputs={"hs_code": run.outputs["hs_code"]}
# Right
outputs={"hs_code": expert_value}, metadata={"reviewed": True}
```

---

## 🧠 Tricky Interview Question
**Q**: "You improved the prompt, and the score on the dataset went from 78% to 91%, but production did not improve. Why?"

**Answer**: Likely overfitting to the dataset (you tuned on the same examples), a dataset that does not represent real traffic (too easy, wrong distribution), or leakage (reference answers visible in the prompt/examples). Check with a held-out `test` split, refresh the dataset with recent production samples, de-duplicate near-identical examples, and compare score by segment (difficulty, language, section).

---

## ⚫ Interview Questions + Answers

Q1: What does a dataset example contain? (Easy)
A1: `inputs`, optional `outputs` (reference), and optional `metadata`.

Q2: What are dataset versions? (Easy)
A2: Each add/edit/delete creates a version; you can run experiments against a specific version or tag to keep results comparable.

Q3: How do you build a dataset quickly? (Medium)
A3: Import CSV, sample production traces, add failures from negative feedback, and optionally generate synthetic examples with an LLM, then have humans review.

Q4: Why use splits? (Medium)
A4: To tune on `dev` and report on a never-touched `test` split, which gives honest generalisation numbers.

Q5: How do you keep a dataset healthy over a year? (Hard)
A5: Review quarterly: remove duplicates and obsolete cases (rules changed), rebalance coverage vs. current traffic (embedding clustering), tag a version per release, track label disagreement, and add the top-N production failure clusters each month. Keep PII out or masked and keep an audit trail of who edited examples.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Comparing prompts, models, retrievers
- Regression testing and CI gates

❌ Avoid when:
- You only have a handful of unlabeled examples (collect more first)
- Data contains raw PII that you are not allowed to store

---

## 📊 Visual Diagram
```
 Dataset "tariff-golden"  (versions: v1 → v2 → v3 ...)
 ┌──────────────────────────────────────────────┐
 │ example: inputs{product} outputs{hs_code}    │
 │          metadata{section,difficulty} split  │
 └──────────────────────────────────────────────┘
        ▲ add from failures/CSV/synthetic        │
        │                                        ▼
   production runs                  evaluate(target, evaluators)
   (feedback = 0)                          │
                                   Experiment A vs B  → ship best
```

---

## 💰 Cost Impact
- Storing datasets has little token cost. Running an experiment costs tokens: 300 examples x 2,000 tokens = 600K tokens, about $0.10-$0.40 on a small model; multiply by number of evaluators if they use LLM judges.
- Optimise: smoke subset (e.g. 40 examples via a `smoke` split) for PRs, full set before release; cache target outputs when only evaluators changed; deduplicate near-identical examples.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dataset | Saved set of examples | Examples का सहेजा संग्रह |
| Example | One input + reference output | एक input + सही output |
| Split | Named subset (dev/test) | नाम वाला उपसमूह |
| Version | Snapshot after changes | बदलाव के बाद का snapshot |
| Experiment | One evaluation run on a dataset | Dataset पर एक evaluation run |
| Reference output | Expected correct answer | अपेक्षित सही उत्तर |

---

## ⚡ 3-Line Summary
English: A LangSmith dataset stores examples with inputs, reference outputs and metadata, versioned automatically. Use splits to separate tuning from honest testing, and feed expert-corrected production failures back in. Run experiments with `evaluate()` to compare versions fairly.
Hindi: LangSmith dataset में inputs, reference outputs और metadata वाले examples रहते हैं, और versioning अपने-आप होती है। Tuning और ईमानदार testing अलग रखने के लिए splits इस्तेमाल करो और expert से सुधारी हुई production failures वापस जोड़ो। Versions को निष्पक्ष compare करने के लिए `evaluate()` से experiments चलाओ।

---

## ➡️ Next Topic
**424. Evaluation in LangSmith** — running experiments and evaluators on these datasets.
