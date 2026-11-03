---

# 492. Training Data Preparation
# हिंदी में: Training Data की तैयारी

---

## 🔵 Simple Definition (English)
Training data preparation is collecting, cleaning, labelling, balancing and splitting your examples before training. Data quality decides model quality: a small clean set beats a large messy one.

## 🔵 सरल परिभाषा (Hindi)
Training data preparation का मतलब training से पहले examples को इकट्ठा करना, साफ़ करना, label करना, balance करना और split करना है। Model की quality data की quality तय करती है: छोटा साफ़ set बड़े गंदे set से बेहतर है।

---

## 🔴 Problem it Solves
"Garbage in, garbage out." Raw logs contain duplicates, wrong labels, PII, inconsistent formats and skewed classes. Training on them teaches the model those flaws. Preparation turns raw logs into a trustworthy dataset and a fair evaluation set.

## 🔴 यह क्यों बना? (Hindi)
"Garbage in, garbage out." Raw logs में duplicates, गलत labels, PII, असंगत formats और असंतुलित classes होते हैं। उन पर training से model वही कमियाँ सीखता है। Preparation raw logs को भरोसेमंद dataset और निष्पक्ष evaluation set में बदलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect: production logs, expert-labelled data, synthetic data
Step 2 → Clean: drop empty/broken rows, normalise whitespace, fix encoding
Step 3 → Deduplicate: exact and near duplicates
Step 4 → Remove PII and secrets
Step 5 → Label review: sample and have a human check labels
Step 6 → Balance: avoid 95 percent of rows from one class
Step 7 → Split: train / validation / test (no overlap, split by source)
Step 8 → Convert to JSONL and version the dataset (hash + date)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Collect: production logs, expert-labelled data, synthetic data
Step 2 → Clean: खाली/टूटी rows हटाओ, whitespace normalise करो, encoding ठीक करो
Step 3 → Deduplicate: exact और near duplicates
Step 4 → PII और secrets हटाओ
Step 5 → Label review: sample लेकर इंसान से labels जँचवाओ
Step 6 → Balance: 95 percent rows एक ही class की न हों
Step 7 → Split: train / validation / test (overlap नहीं, source के हिसाब से split)
Step 8 → JSONL में बदलो और dataset को version करो (hash + date)
```

---

## 🟡 Real World Example
**Tariff Classification System**: We have 50,000 past customs declarations. 30 percent are exact duplicates, some contain importer phone numbers and 60 percent are electronics (class imbalance). We dedupe, mask phone numbers, cap each HS chapter at 300 examples, have a customs expert review 200 random labels (found 6 percent wrong, fixed), and split by importer so no importer appears in both train and test.

**Amazon-style**: Product titles from the same seller are near duplicates; split by seller to avoid leakage.

## 🟡 Real Example Hindi mein
**Tariff System**: हमारे पास 50,000 पुराने customs declarations हैं। 30 percent exact duplicates हैं, कुछ में importer के phone numbers हैं और 60 percent electronics हैं (class imbalance)। हम dedupe करते हैं, phone numbers mask करते हैं, हर HS chapter को 300 examples पर cap करते हैं, customs expert से 200 random labels जँचवाते हैं (6 percent गलत निकले, ठीक किए) और importer के हिसाब से split करते हैं ताकि कोई importer train और test दोनों में न आए।

**Amazon-style**: एक ही seller के product titles near duplicates होते हैं; leakage रोकने के लिए seller के हिसाब से split करो।

---

## 💻 Code Example — Basic
```python
# Basic: clean, dedupe, balance and split a small dataset (pure Python, runs offline)
import random  # shuffling and sampling
import re  # regex for masking
from collections import defaultdict  # group by label
from typing import Dict, List, Tuple  # type hints

Row = Tuple[str, str]  # (description, label)

rows: List[Row] = [
    ("Bluetooth  headphones ", "8518"), ("bluetooth headphones", "8518"),  # near duplicate
    ("Cotton shirt call 9876543210", "6109"), ("Laptop 14 inch", "8471"),
    ("Wired earphones", "8518"), ("Silk scarf", "6214"),
]


def clean(text: str) -> str:
    """Lowercase, collapse spaces, mask 10 digit phone numbers."""
    text = re.sub(r"\b\d{10}\b", "<PHONE>", text)  # mask phones
    return re.sub(r"\s+", " ", text).strip().lower()  # normalise spaces


seen = set()  # to remove duplicates
unique: List[Row] = []  # deduplicated rows
for d, y in rows:  # go through rows
    c = clean(d)  # cleaned text
    if (c, y) not in seen:  # new pair
        seen.add((c, y))
        unique.append((c, y))

by_label: Dict[str, List[Row]] = defaultdict(list)  # group
for r in unique:
    by_label[r[1]].append(r)
CAP = 2  # max examples per class (balance)
balanced: List[Row] = [x for v in by_label.values() for x in v[:CAP]]  # cap each class

random.seed(42)  # reproducible split
random.shuffle(balanced)  # shuffle
cut = int(len(balanced) * 0.8)  # 80/20 split
train, val = balanced[:cut], balanced[cut:]  # split
print(len(rows), "->", len(unique), "->", len(balanced), "| train", len(train), "val", len(val))
```

## 💻 Code Example — Advanced
```python
# Production style: pipeline with group-aware split, dataset hash and async label review hook
import asyncio  # async
import hashlib  # dataset version hash
import json  # serialise
import random  # shuffle
from dataclasses import dataclass  # row type
from typing import Awaitable, Callable, Dict, List, Tuple  # types


@dataclass(frozen=True)
class Example:
    text: str  # input text
    label: str  # target label
    group: str  # source group (importer, seller) used to prevent leakage


def group_split(
    data: List[Example], val_frac: float = 0.2, seed: int = 42
) -> Tuple[List[Example], List[Example]]:
    """Split so that a whole group goes to either train or validation."""
    if not 0 < val_frac < 1:  # validate input
        raise ValueError("val_frac must be between 0 and 1")
    groups = sorted({e.group for e in data})  # unique groups
    random.Random(seed).shuffle(groups)  # deterministic shuffle
    n_val = max(1, int(len(groups) * val_frac))  # number of validation groups
    val_groups = set(groups[:n_val])  # chosen groups
    train = [e for e in data if e.group not in val_groups]  # training rows
    val = [e for e in data if e.group in val_groups]  # validation rows
    return train, val


def dataset_hash(data: List[Example]) -> str:
    """Stable hash so each training run can reference its exact data version."""
    payload = json.dumps([(e.text, e.label) for e in data], sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:12]  # short id


async def review_sample(
    data: List[Example], reviewer: Callable[[Example], Awaitable[bool]], k: int = 3
) -> float:
    """Ask a reviewer (human tool or LLM judge) to check k random labels; return error rate."""
    sample = random.Random(1).sample(data, min(k, len(data)))  # random sample
    verdicts = await asyncio.gather(*(reviewer(e) for e in sample))  # parallel review
    return 1 - sum(verdicts) / len(verdicts)  # fraction judged wrong


async def always_ok(e: Example) -> bool:
    """Stub reviewer for offline demo."""
    return True


async def main() -> None:
    data = [Example(f"item {i}", "8518" if i % 2 else "6109", f"imp{i % 4}") for i in range(12)]
    train, val = group_split(data)  # leakage safe split
    print(len(train), len(val), dataset_hash(train))  # sizes and version id
    print("error rate:", await review_sample(data, always_ok))  # stub review


if __name__ == "__main__":
    asyncio.run(main())  # run demo
```

---

## 🟠 FastAPI Integration
Provide a `/dataset/prepare` endpoint that accepts raw rows and returns cleaning statistics, so data labelers get fast feedback.

```python
import re  # masking
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # schema
from typing import List  # types

app = FastAPI()  # app


class Rows(BaseModel):
    texts: List[str]  # raw texts


@app.post("/dataset/prepare")
async def prepare(body: Rows) -> dict:
    """Mask phones, drop empties and duplicates, return stats."""
    cleaned = [re.sub(r"\b\d{10}\b", "<PHONE>", t).strip() for t in body.texts]  # mask
    cleaned = [t for t in cleaned if t]  # drop empty
    unique = list(dict.fromkeys(cleaned))  # dedupe, keep order
    return {"input": len(body.texts), "output": len(unique), "removed": len(body.texts) - len(unique)}
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith lets you save production traces into datasets, filter by feedback and export them. LangChain document loaders and text utilities can help with cleaning.

```python
# Illustrative: collect good production examples from LangSmith (needs API key)
# from langsmith import Client
# client = Client()
# runs = client.list_runs(project_name="tariff-prod", filter='eq(feedback_key, "thumbs_up")')
# for r in runs: ...  # convert r.inputs / r.outputs into JSONL rows
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Random split with near-duplicate rows
✅ Correct: Split by group (seller, importer, date).

```python
# Wrong: random.shuffle(rows); train, test = rows[:80], rows[80:]  # leaks twins
# Right: group_split(rows)  # whole groups stay on one side
```

❌ Mistake 2: Ignoring class imbalance
✅ Correct: Cap big classes or add examples for rare ones.

```python
# Wrong: 95% electronics -> model always predicts electronics
# Right: cap each class (e.g. 300) and measure per-class accuracy
```

---

## 🧠 Tricky Interview Question
**Q**: "Your eval accuracy is 97 percent but real accuracy is 80 percent. The data was shuffled randomly. What went wrong?"

**Answer**: Data leakage. Near-duplicate or same-source examples appeared in both train and eval, so the model effectively memorised the test. Fix by deduplicating (including near duplicates), splitting by source or time, and building a fresh test set from recent production traffic.

---

## ⚫ Interview Questions + Answers

Q1: Quality or quantity? (Easy)
A1: Quality first. Hundreds of clean, consistent examples usually beat thousands of noisy ones.

Q2: Why split train/validation/test? (Easy)
A2: Train to learn, validation to tune (epochs, stop early), test for a final unbiased score.

Q3: How do you fix class imbalance? (Medium)
A3: Cap majority classes, collect or synthesise more for rare ones, and report per-class metrics not just overall accuracy.

Q4: Is synthetic data OK? (Medium)
A4: Yes if reviewed. A stronger LLM can generate examples, but sample-check them, check diversity and keep real data in the test set.

Q5: How do you make runs reproducible? (Hard)
A5: Fix random seeds, store the dataset with a content hash, log the cleaning code version, keep the split definition (group keys) and record the hash with each model id.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always, before any fine tuning

❌ Avoid when:
- Over-cleaning that removes real edge cases the model must handle (keep a representative sample of messy inputs)

---

## 📊 Visual Diagram
```
 Raw logs ─► Clean ─► Dedupe ─► Mask PII ─► Review labels
                                              │
                                              ▼
                                  Balance classes
                                              │
                     ┌────────────────────────┼───────────────┐
                     ▼                        ▼               ▼
                   Train                 Validation          Test
                     └──────► JSONL + version hash ◄──────────┘
```

---

## 💰 Cost Impact
- Duplicates and junk rows are paid training tokens with no benefit.
- Trimming 30 percent duplicates cuts that share of training cost directly.
- Labelling cost is human time: review a random sample, not everything.
- Use tiktoken to estimate total training tokens before launching.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Deduplication | Removing repeated rows | दोहराई rows हटाना |
| Data leakage | Test info seen in training | Test की जानकारी training में |
| Class imbalance | Uneven label counts | Labels की असमान गिनती |
| PII | Personal identifiable info | निजी पहचान की जानकारी |
| Synthetic data | LLM generated examples | LLM से बने examples |
| Dataset versioning | Tracking data versions | Data के versions ट्रैक करना |

---

## ⚡ 3-Line Summary
English: Prepare data by cleaning, deduplicating, masking PII, reviewing labels, balancing and splitting by group.
Clean small data beats large messy data.
Version the dataset so every model is reproducible.
Hindi: Data को साफ़ करो, dedupe करो, PII mask करो, labels review करो, balance करो और group के हिसाब से split करो।
छोटा साफ़ data बड़े गंदे data से बेहतर है।
Dataset version करो ताकि हर model reproducible हो।

---

## ➡️ Next Topic
**493. Fine Tuning Hyperparameters** — epochs, batch size and learning rate.
