---

# 407. Evaluation Dataset Creation
# हिंदी में: Evaluation Dataset बनाना

---

## 🔵 Simple Definition (English)
An evaluation dataset is a fixed set of test inputs (and usually expected outputs or criteria) used to measure an LLM system. Creating it means choosing sources, covering all important scenarios, cleaning and de-duplicating, splitting, and versioning, so scores are trustworthy and comparable over time.

## 🔵 सरल परिभाषा (Hindi)
Evaluation dataset test inputs का एक fixed set है (आमतौर पर expected outputs या criteria के साथ) जिससे LLM system नापा जाता है। इसे बनाने में sources चुनना, सभी ज़रूरी scenarios cover करना, cleaning व de-duplication, splitting और versioning शामिल है, ताकि scores भरोसेमंद और समय के साथ comparable रहें।

---

## 🔴 Problem it Solves
Without a proper dataset, teams test on 5 favourite examples, tune the prompt to them, and ship regressions. Datasets that are too easy, duplicated, or leaked into the prompt give inflated scores that vanish in production.

## 🔴 यह क्यों बना? (Hindi)
सही dataset के बिना teams 5 पसंदीदा examples पर test करती हैं, prompt उन्हीं पर tune करती हैं और regression ship कर देती हैं। बहुत आसान, duplicate या prompt में leak हुआ dataset फुलाए हुए scores देता है जो production में गायब हो जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define what to measure (tasks, user types, failure modes)
Step 2 → Collect candidates: production logs, SME-written, support tickets, synthetic
Step 3 → Scrub PII/secrets
Step 4 → Label: expected answer / expected HS code / pass-fail criteria
Step 5 → Tag each row (category, difficulty, language) for slice analysis
Step 6 → De-duplicate (exact + near-duplicate)
Step 7 → Split: dev (tune) vs test (frozen, never tune on it)
Step 8 → Version it (git/DVC) with a changelog; refresh regularly
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → तय करो क्या नापना है (tasks, user types, failure modes)
Step 2 → Candidates इकट्ठा करो: production logs, SME-लिखित, support tickets, synthetic
Step 3 → PII/secrets हटाओ
Step 4 → Label करो: expected answer / expected HS code / pass-fail criteria
Step 5 → हर row को tag करो (category, difficulty, language) ताकि slice analysis हो
Step 6 → De-duplicate करो (exact + near-duplicate)
Step 7 → Split करो: dev (tune) बनाम test (frozen, इस पर कभी tune नहीं)
Step 8 → Version करो (git/DVC) और changelog रखो; नियमित refresh
```

---

## 🟡 Real World Example
**Tariff Classification System**: 300 rows: 150 sampled from real importer queries (PII removed), 100 written by customs experts for tricky chapters (composite goods, parts vs whole), 50 synthetic edge cases (typos, Hinglish). Tags: `chapter`, `difficulty`, `language`. Test split of 80 rows is frozen. Every production bug becomes a new dev row.

**Amazon-style**: Product-QA dataset stratified by category (electronics, grocery, fashion) so a weak category is not hidden by a strong average.

## 🟡 Real Example Hindi mein
**Tariff System**: 300 rows: 150 असली importer queries से (PII हटाकर), 100 customs experts द्वारा कठिन chapters के लिए (composite goods, parts बनाम whole), 50 synthetic edge cases (typos, Hinglish)। Tags: `chapter`, `difficulty`, `language`। 80 rows का test split frozen है। हर production bug नई dev row बनती है।

**Amazon-style**: Product-QA dataset category (electronics, grocery, fashion) के हिसाब से stratified, ताकि कमज़ोर category मजबूत average में न छुपे।

---

## 💻 Code Example — Basic
```python
# Basic: dedupe + stratified split on a small dataset (pure Python, offline)
import random  # for reproducible shuffling
from collections import defaultdict  # group rows by tag

rows: list[dict[str, str]] = [  # tiny example dataset
    {"q": "HS code for lithium battery?", "cat": "electronics"},
    {"q": "hs code for lithium battery?", "cat": "electronics"},  # near duplicate (case)
    {"q": "HS code for basmati rice?", "cat": "food"},
    {"q": "HS code for cotton shirt?", "cat": "textile"},
    {"q": "HS code for wheat flour?", "cat": "food"},
    {"q": "HS code for laptop?", "cat": "electronics"},
]


def dedupe(items: list[dict[str, str]]) -> list[dict[str, str]]:  # remove duplicates
    seen: set[str] = set()  # normalised questions already kept
    out: list[dict[str, str]] = []  # unique rows
    for r in items:  # go through rows
        key = " ".join(r["q"].lower().split())  # normalise case/spaces
        if key not in seen:  # first time seen
            seen.add(key)  # remember it
            out.append(r)  # keep row
    return out  # unique rows


def stratified_split(items: list[dict[str, str]], test_ratio: float = 0.4, seed: int = 7):
    rng = random.Random(seed)  # reproducible randomness
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)  # category -> rows
    for r in items:  # group
        groups[r["cat"]].append(r)  # add to its category
    dev: list[dict[str, str]] = []  # tuning rows
    test: list[dict[str, str]] = []  # frozen rows
    for cat, g in groups.items():  # each category
        rng.shuffle(g)  # shuffle inside category
        k = max(1, round(len(g) * test_ratio)) if len(g) > 1 else 0  # at least 1 to test if possible
        test.extend(g[:k])  # test part
        dev.extend(g[k:])  # dev part
    return dev, test  # both splits


clean = dedupe(rows)  # 5 unique rows
dev, test = stratified_split(clean)  # split
print(len(rows), "->", len(clean), "| dev", len(dev), "test", len(test))  # 6 -> 5 | dev/test counts
```

## 💻 Code Example — Advanced
```python
# Advanced: validated, PII-scrubbed, hashed, versioned JSONL dataset builder (async source loading)
import asyncio  # async loading
import hashlib  # stable row ids
import json  # write JSONL
import logging  # logs
import re  # PII regex
from pathlib import Path  # file paths
from typing import Literal  # difficulty type

from pydantic import BaseModel, Field, ValidationError  # schema validation

log = logging.getLogger("dataset")  # logger
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")  # simple email pattern
PHONE = re.compile(r"\b\d{10}\b")  # 10-digit phone numbers


class EvalRow(BaseModel):  # schema every row must satisfy
    id: str = ""  # filled after hashing
    question: str = Field(min_length=5)  # input
    reference: str = Field(min_length=1)  # expected answer
    category: str  # slice tag
    difficulty: Literal["easy", "medium", "hard"] = "medium"  # slice tag
    source: Literal["prod", "expert", "synthetic"] = "expert"  # where it came from


def scrub(text: str) -> str:  # remove obvious PII
    return PHONE.sub("[PHONE]", EMAIL.sub("[EMAIL]", text))  # mask both


def row_id(q: str) -> str:  # stable id from normalised question
    return hashlib.sha256(" ".join(q.lower().split()).encode()).hexdigest()[:12]  # short hash


async def load_source(name: str) -> list[dict]:  # stand-in for DB/API/file read
    await asyncio.sleep(0.01)  # simulate IO
    return [{"question": f"HS code for item from {name}? contact a@b.com",
             "reference": "8507.60", "category": "electronics", "source": "prod"}]  # sample


async def build(sources: list[str], out: Path, version: str) -> int:
    batches = await asyncio.gather(*(load_source(s) for s in sources), return_exceptions=True)  # load all
    seen: set[str] = set()  # dedupe ids
    good: list[EvalRow] = []  # valid rows
    for b in batches:  # each source result
        if isinstance(b, Exception):  # source failed
            log.error("source failed: %s", b)  # log and continue
            continue
        for raw in b:  # each raw row
            try:
                raw["question"] = scrub(raw["question"])  # remove PII
                row = EvalRow(**raw)  # validate
                row.id = row_id(row.question)  # assign id
            except ValidationError as exc:  # bad row
                log.warning("invalid row skipped: %s", exc.errors()[0]["msg"])  # log
                continue
            if row.id in seen:  # duplicate
                continue
            seen.add(row.id)  # remember
            good.append(row)  # keep
    out.parent.mkdir(parents=True, exist_ok=True)  # ensure folder
    with out.open("w", encoding="utf-8") as f:  # write JSONL
        f.write(json.dumps({"_meta": {"version": version, "rows": len(good)}}) + "\n")  # header line
        for r in good:  # one row per line
            f.write(r.model_dump_json() + "\n")  # serialise
    return len(good)  # number written
```

---

## 🟠 FastAPI Integration
An internal tool lets experts add labelled rows, and the endpoint validates and appends them.

```python
from fastapi import FastAPI, HTTPException  # web

app = FastAPI()  # app
STORE: dict[str, EvalRow] = {}  # in-memory (use a DB in production)


@app.post("/dataset/rows", status_code=201)  # add a row
async def add_row(row: EvalRow) -> dict:  # FastAPI validates via pydantic
    row.question = scrub(row.question)  # remove PII
    row.id = row_id(row.question)  # assign id
    if row.id in STORE:  # duplicate check
        raise HTTPException(409, "duplicate question")  # conflict
    STORE[row.id] = row  # save
    return {"id": row.id, "total": len(STORE)}  # confirmation


@app.get("/dataset/stats")  # coverage report
async def stats() -> dict:
    by_cat: dict[str, int] = {}  # counts per category
    for r in STORE.values():  # each row
        by_cat[r.category] = by_cat.get(r.category, 0) + 1  # count
    return {"total": len(STORE), "by_category": by_cat}  # report
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith datasets store input/output examples and run LangChain/LangGraph apps against them; you can create a dataset from production traces. Your JSONL maps directly to `client.create_examples`.

```python
from langsmith import Client  # pip install langsmith

def push_to_langsmith(rows: list[EvalRow], name: str) -> None:
    client = Client()  # uses LANGSMITH_API_KEY
    ds = client.create_dataset(dataset_name=name)  # new dataset
    client.create_examples(
        inputs=[{"question": r.question} for r in rows],  # app inputs
        outputs=[{"reference": r.reference} for r in rows],  # expected outputs
        dataset_id=ds.id)  # attach to dataset
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Tuning the prompt on the test split
✅ Correct: freeze the test split

```python
# Wrong - iterate prompt using all rows, report the same rows
score = evaluate(all_rows)
# Right
tune_on(dev_rows)
final_score = evaluate(test_rows)   # looked at rarely
```

❌ Mistake 2: Only easy, clean questions
✅ Correct: include typos, ambiguous, multi-language, out-of-scope and adversarial rows.

❌ Mistake 3: Real customer PII in the dataset
✅ Correct: scrub before storing and sharing.

---

## 🧠 Tricky Interview Question
**Q**: "Eval score is 92% but production thumbs-down rate is 25%. The dataset has 500 rows. What do you check?"

**Answer**: Dataset distribution mismatch. Compare the dataset's category/difficulty/language mix with production traffic; check for leakage (examples in few-shot prompt or training), duplicates inflating easy cases, and missing failure slices. Fix by sampling from production logs, adding hard rows for the thumbs-down clusters, and reporting per-slice scores rather than one average.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Why version an eval dataset?
A1: So score changes can be attributed to the system or to the dataset; old results stay reproducible.

Q2: [Easy] Why remove duplicates?
A2: Duplicates over-weight some cases and can leak between dev and test splits.

Q3: [Medium] What is a good size?
A3: 50-100 for early iteration, 200-500 for decisions; more important is coverage and slice sizes (30+ per important slice).

Q4: [Medium] Best sources for rows?
A4: Real production queries (most representative), expert-written hard cases, bug reports, and carefully reviewed synthetic data.

Q5: [Hard] How do you keep a dataset fresh without breaking comparability?
A5: Keep a frozen core set for long-term trends and a rolling set refreshed from production; always report both, bump the version on any change, and re-run the baseline on the new version.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You tune prompts, retrievers or models
- You need regression tests and slice-level insight

❌ Avoid when:
- It becomes a blocker for a quick prototype (start with 20 rows, then grow)

---

## 📊 Visual Diagram
```
 prod logs ─┐
 experts ───┼─► scrub PII ─► label ─► tag ─► dedupe ─► split ─┬─► dev  (tune here)
 synthetic ─┘                                                  └─► test (frozen)
                                  │
                         version v1 → v2 → v3 (changelog)
```

---

## 💰 Cost Impact
Dataset building is mostly human time; LLM costs come from synthetic generation and labelling help (e.g. 300 rows x ~800 tokens on gpt-4o-mini ≈ $0.04). The bigger cost is later: every eval run pays judge tokens per row, so dataset size multiplies evaluation cost.
Optimise: keep a small smoke set (30 rows) for PRs and the full set nightly; remove redundant rows; cache results by row id + system version.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stratified split | Split keeping category mix | Category अनुपात बनाए रखकर split |
| Leakage | Test data influences tuning | Test data का tuning पर असर |
| Slice | Subset by tag | Tag के आधार पर subset |
| PII scrubbing | Removing personal data | निजी data हटाना |
| Frozen test set | Never tuned on | जिस पर कभी tuning नहीं |

---

## ⚡ 3-Line Summary
English: A good eval dataset is representative, labelled, tagged, de-duplicated, split and versioned. Freeze the test split and report per-slice scores. Feed it with production logs, expert cases and every bug.
Hindi: अच्छा eval dataset representative, labelled, tagged, de-duplicated, split और versioned होता है। Test split frozen रखो और per-slice scores बताओ। इसमें production logs, expert cases और हर bug जोड़ते रहो।

---

## ➡️ Next Topic
**408. Synthetic Test Data** - generate rows with LLMs when real data is scarce.
