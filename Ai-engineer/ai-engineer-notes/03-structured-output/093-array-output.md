---

# 093. Array Output
# हिंदी में: Array (List) Output

---

## 🔵 Simple Definition (English)
Array output means the LLM returns a list of items, such as ten product classifications or five extracted entities. Because strict structured output requires the root to be an object, you wrap the list: `{"items": [ ... ]}`. Each element follows the same item schema.

## 🔵 सरल परिभाषा (Hindi)
Array output में LLM items की list लौटाता है, जैसे दस product classifications या पाँच extracted entities। Strict structured output में root का object होना ज़रूरी है, इसलिए list को wrap करते हैं: `{"items": [ ... ]}`। हर element एक ही item schema को follow करता है।

---

## 🔴 Problem it Solves
Many tasks have a variable number of results: "list all products in this email". Free text lists ("1. Earbuds 2. Cable") need fragile parsing. A typed array gives a predictable list you can loop over, count and store.

## 🔴 यह क्यों बना? (Hindi)
कई tasks में results की संख्या बदलती है: "इस email के सारे products बताओ"। Free text lists ("1. Earbuds 2. Cable") को parse करना कमजोर है। Typed array predictable list देता है जिस पर आप loop, count और store कर सकते हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the item model (e.g. ProductTariff)
Step 2 → Wrap: class Result(BaseModel): items: list[ProductTariff]
Step 3 → Add limits in the prompt/description ("at most 20 items")
Step 4 → Call with response_format=Result
Step 5 → LLM returns {"items": [ {...}, {...} ]}
Step 6 → Validate: length, duplicates, order, each item
Step 7 → Use result.items in a normal loop; map back to input IDs
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Item model define करो (जैसे ProductTariff)
Step 2 → Wrap करो: class Result(BaseModel): items: list[ProductTariff]
Step 3 → Prompt/description में limit लिखो ("अधिकतम 20 items")
Step 4 → response_format=Result के साथ call करो
Step 5 → LLM {"items": [ {...}, {...} ]} लौटाता है
Step 6 → Validate: length, duplicates, order, हर item
Step 7 → result.items पर normal loop; input IDs से वापस map करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A user pastes a list of 8 products. We send them numbered with IDs and ask for one result per ID. We check that all 8 IDs come back exactly once, otherwise we retry only the missing ones.

**Zomato-style**: Extract every dish and quantity from a long order message into `items: list[OrderItem]`.

## 🟡 Real Example Hindi mein
**Tariff System**: User 8 products की list paste करता है। हम उन्हें IDs के साथ भेजते हैं और हर ID के लिए एक result माँगते हैं। Check करते हैं कि सारी 8 IDs ठीक एक बार लौटीं, वरना सिर्फ छूटे items दोबारा भेजते हैं।

**Zomato-style**: लंबे order message से हर dish और quantity `items: list[OrderItem]` में निकालना।

---

## 💻 Code Example — Basic
```python
# Basic: array wrapper model + completeness check. Needs: pip install pydantic
import json
from pydantic import BaseModel, Field

class ProductTariff(BaseModel):                        # one element
    id: int                                            # echoes the input id
    hs_code: str
    confidence: float = Field(ge=0, le=1)

class BatchResult(BaseModel):                          # root must be an object
    items: list[ProductTariff]                         # the array

inputs: dict[int, str] = {1: "earbuds", 2: "leather shoes", 3: "laptop"}   # id -> product

reply = json.dumps({"items": [                         # fake LLM reply (model forgot id 3)
    {"id": 1, "hs_code": "8518.30", "confidence": 0.9},
    {"id": 2, "hs_code": "6403.99", "confidence": 0.8},
]})

result = BatchResult.model_validate_json(reply)        # parse + validate
returned = [i.id for i in result.items]                # ids present
missing = sorted(set(inputs) - set(returned))          # ids not answered
dupes = sorted({i for i in returned if returned.count(i) > 1})   # ids answered twice
print("missing:", missing, "duplicates:", dupes)       # missing: [3] duplicates: []

by_id = {i.id: i for i in result.items}                # map back by id (never trust position)
for pid, name in inputs.items():
    item = by_id.get(pid)                              # None if missing
    print(name, "->", item.hs_code if item else "RETRY")
```

## 💻 Code Example — Advanced
```python
# Production: batch classify with id mapping, completeness check, retry of missing items.
import asyncio
from typing import Optional
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError

client = AsyncOpenAI()

class ProductTariff(BaseModel):
    id: int = Field(description="Same id as in the input")
    hs_code: str
    confidence: float

class BatchResult(BaseModel):
    items: list[ProductTariff] = Field(description="Exactly one entry per input id")

async def classify_batch(products: dict[int, str]) -> Optional[list[ProductTariff]]:
    """One LLM call for many products; returns parsed items or None on failure."""
    numbered = "\n".join(f"{pid}: {name}" for pid, name in products.items())   # id: text lines
    try:
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "Classify each product. Return one entry per id."},
                      {"role": "user", "content": numbered}],
            response_format=BatchResult, temperature=0, max_tokens=60 * len(products) + 100)
    except (OpenAIError, ValidationError) as exc:
        print("batch failed:", exc)
        return None
    parsed = completion.choices[0].message.parsed
    return parsed.items if parsed else None

async def classify_all(products: dict[int, str], max_rounds: int = 2) -> dict[int, ProductTariff]:
    """Repeat for missing ids until complete or rounds exhausted."""
    done: dict[int, ProductTariff] = {}
    pending = dict(products)                           # ids still to do
    for _ in range(max_rounds):
        if not pending:
            break
        items = await classify_batch(pending)
        if items is None:
            continue                                   # try the round again
        for it in items:
            if it.id in pending:                       # ignore hallucinated ids
                done[it.id] = it
        pending = {pid: n for pid, n in pending.items() if pid not in done}
    return done

if __name__ == "__main__":
    out = asyncio.run(classify_all({1: "earbuds", 2: "shoes", 3: "laptop"}))   # needs API key
    print(len(out), "classified")
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class BatchIn(BaseModel):
    products: list[str] = Field(min_length=1, max_length=50)   # cap input size

@app.post("/classify-batch")
async def classify_batch_route(body: BatchIn) -> dict:
    products = {i + 1: p for i, p in enumerate(body.products)}   # assign ids
    done = await classify_all(products)
    if len(done) < len(products):
        raise HTTPException(status_code=207, detail="partial result")   # partial success signal
    return {"items": [done[i].model_dump() for i in sorted(done)]}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
batch_llm = llm.with_structured_output(BatchResult)        # wrapper object with items list
# Alternative: process each product in parallel with the Runnable .batch():
single = llm.with_structured_output(ProductTariff)
results = single.batch([f"1: {p}" for p in ["earbuds", "shoes"]], config={"max_concurrency": 5})
# LangGraph: use Send() to fan out one node per item, then merge results in a reducer.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Relying on position in the array
✅ Correct: Echo an `id` and map by id.

```python
# Wrong: for name, item in zip(names, result.items)   # misaligned if one is skipped
# Right: by_id = {i.id: i for i in result.items}
```

❌ Mistake 2: No cap on length
✅ Correct: Validate `max_length`, chunk large inputs.

```python
# Wrong: 500 products in one call -> truncation, skipped items
# Right: chunks of 20-30 products per call, asyncio.gather the chunks
```

---

## 🧠 Tricky Interview Question

**Q**: "You send 25 products in one call and get 24 results back, no error. What happened and how do you design for it?"

**Answer**: LLMs may silently skip or merge items, especially in long lists. Because output is valid, nothing raises. Design: give each input an id, require one output per id, verify the id set equals the input set, retry only missing ids, and keep batch sizes moderate. Alternatively run one call per item concurrently when accuracy matters more than token cost.

---

## ⚫ Interview Questions + Answers

Q1: Why wrap an array in an object?
A1: Strict structured output (and tools) require a top-level object, so use `{"items": [...]}`.

Q2: How do you type a list in Pydantic?
A2: `items: list[Item]`.

Q3: How do you handle an empty list?
A3: Decide if empty is legitimate; add `min_length=1` if not, else treat as "nothing found" and log.

Q4: One call with many items vs many calls: trade-offs?
A4: One call saves shared prompt tokens and requests but risks skipped items and truncation; many calls cost more input tokens but are parallel and more accurate per item.

Q5: How would you stream a large array to the UI?
A5: Use streaming with an incremental parser (Instructor `create_iterable` or partial JSON parsing) so each completed item is emitted as soon as it closes, while the final validation happens at the end.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Variable number of extracted entities
- Small batches to share the prompt

❌ Avoid when:
- Hundreds of items (chunk or per-item calls)
- Strict ordering is critical without ids

---

## 📊 Visual Diagram
```
 inputs: 1:earbuds 2:shoes 3:laptop
              │
              ▼
         ┌────────┐
         │  LLM   │
         └───┬────┘
             ▼
 {"items":[{id:1,..},{id:2,..},{id:3,..}]}
             │
   check set(ids) == set(inputs)? ── no ─► retry missing ids
             │ yes
             ▼
        map by id ─► DB
```

---

## 💰 Cost Impact
Batching shares the system prompt and schema across items (saves input tokens) but output grows linearly with items (about 40-60 tokens per item). Output tokens cost more than input.
Optimise: batch 10-30 items, short keys, `max_tokens` proportional to items, Batch API (50% cheaper) for offline jobs, per-item calls only for hard cases.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Array / List | Ordered collection | क्रमबद्ध सूची |
| Wrapper object | Root object holding the list | List वाला root object |
| Batching | Many items per call | एक call में कई items |
| Fan-out | Parallel per-item calls | समानांतर calls |
| Completeness check | All inputs answered | सब inputs का जवाब आया? |

---

## ⚡ 3-Line Summary
English: Wrap arrays in an object and give every item an id. Verify that every input id comes back exactly once. Batch moderately and chunk big inputs.
Hindi: Arrays को object में wrap करो और हर item को id दो। Verify करो कि हर input id ठीक एक बार लौटी। मध्यम batches बनाओ और बड़े inputs को chunk करो।

---

## ➡️ Next Topic
**094. Enum in Structured Output** — restricting a field to a fixed set of allowed values.
