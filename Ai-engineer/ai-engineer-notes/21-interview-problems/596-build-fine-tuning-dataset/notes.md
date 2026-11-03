---

# 596. Build Fine Tuning Dataset
# हिंदी में: Fine Tuning Dataset बनाना

---

## 🔵 Simple Definition (English)
A fine-tuning dataset is a file of example conversations (input and ideal answer) used to teach a model your task and style. Building it means cleaning raw data, converting it to the provider's chat format (JSONL), removing duplicates and bad rows, and splitting into train and validation sets.

## 🔵 सरल परिभाषा (Hindi)
Fine-tuning dataset example conversations (input और ideal answer) की file है जिससे model आपका task और style सीखता है। इसमें raw data clean करना, chat format (JSONL) में बदलना, duplicates/bad rows हटाना और train/validation में बाँटना शामिल है।

---

## 🔴 Problem it Solves
Fine-tuning quality depends almost entirely on data quality. Duplicates, wrong labels, empty rows and inconsistent formats make the model worse, and a missing validation set hides overfitting.

## 🔴 यह क्यों बना? (Hindi)
Fine-tuning की quality लगभग पूरी तरह data पर निर्भर है। Duplicates, गलत labels, खाली rows और inconsistent format model को खराब करते हैं; validation set के बिना overfitting छिप जाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect raw rows (product, correct HS code, reason)
Step 2 → Normalise text (whitespace, case where safe)
Step 3 → Convert each row to {"messages": [system, user, assistant]}
Step 4 → Validate roles, non-empty content, last message = assistant
Step 5 → Deduplicate by hash of the user prompt
Step 6 → Shuffle with fixed seed, split train/validation
Step 7 → Write JSONL (one JSON object per line); report stats
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Raw rows इकट्ठा करो (product, सही HS code, reason)
Step 2 → Text normalise करो
Step 3 → हर row को {"messages": [system, user, assistant]} में बदलो
Step 4 → Roles, खाली content और आखिरी message = assistant validate करो
Step 5 → User prompt के hash से duplicates हटाओ
Step 6 → Fixed seed से shuffle करके train/validation बाँटो
Step 7 → JSONL लिखो और stats दिखाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs officers' past decisions (product description, final HS code, justification) become training examples so a small model matches the house style and rare product categories. Near-duplicate descriptions ("LED bulb 9W" vs "led bulb 9w ") are removed so the validation set is not leaked from the training set.

**Zomato-style**: support replies by senior agents are turned into examples for tone and refund policy.

## 🟡 Real Example Hindi mein
**Tariff System**: Officers के पुराने फ़ैसले (product description, final HS code, justification) training examples बनते हैं ताकि छोटा model house style और rare categories सीखे। लगभग-समान descriptions हटाए जाते हैं ताकि validation set में leakage न हो।

**Zomato**: Senior agents के replies से tone और refund policy के examples बनते हैं।

---

## 💻 Code Example — Basic
```python
# Convert one raw row into the chat fine-tuning format
import json

row: dict[str, str] = {"product": "Laptop", "hs": "8471.30"}   # raw data row

example: dict = {"messages": [                                  # chat-format record
    {"role": "user", "content": f"Classify: {row['product']}"},          # input
    {"role": "assistant", "content": f"HS {row['hs']}"},                 # ideal answer
]}

print(json.dumps(example))        # one line of a .jsonl file
```

## 💻 Code Example — Advanced
Full file: `main.py` (build, validate, dedupe, split, write). Observed output:
```
{'input': 7, 'invalid': 1, 'duplicate': 1, 'kept': 5} train: 4 val: 1
```
The empty-product row is rejected by a raw-field check in `to_example` (counted as invalid).
```python
# Excerpt from main.py
def validate(ex: dict) -> None:
    msgs = ex.get("messages")                            # must exist
    if not isinstance(msgs, list) or len(msgs) < 2:
        raise ValueError("need >= 2 messages")
    for m in msgs:
        if m.get("role") not in ROLES or not str(m.get("content", "")).strip():
            raise ValueError(f"bad message: {m}")        # reject empty/unknown role
    if msgs[-1]["role"] != "assistant":                  # model learns the last turn
        raise ValueError("last message must be assistant")
```
Async: dataset building is offline CPU/file work, so plain sync code is right; use async only when calling an LLM to generate or judge examples.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import build, split                            # our module

app = FastAPI()


class Row(BaseModel):
    product: str
    hs: str
    why: str


@app.post("/dataset/preview")
async def preview(rows: list[Row]) -> dict:
    if not rows:                                         # nothing to build
        raise HTTPException(status_code=422, detail="no rows")
    data, stats = build([r.model_dump() for r in rows])  # pydantic v2 dict
    train, val = split(data) if len(data) > 1 else (data, [])
    return {"stats": stats, "train": len(train), "val": len(val)}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain/LangSmith store datasets of examples for evaluation; the same cleaned rows can feed both fine-tuning and evals. LangGraph traces from production can be exported as candidate examples (after human review).

```python
from langchain_core.messages import HumanMessage, AIMessage

# Convert chat-format record back to LangChain messages for inspection/eval
def to_lc(ex: dict) -> list:
    mapping = {"user": HumanMessage, "assistant": AIMessage}     # skip system here
    return [mapping[m["role"]](m["content"]) for m in ex["messages"] if m["role"] in mapping]
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Splitting before deduplicating (same example lands in train and validation).
✅ Correct: dedupe first, then split.
```python
# Wrong
train, val = split(rows); data = dedupe(train)
# Right
data = dedupe(rows); train, val = split(data)
```

❌ Mistake 2: Training on noisy labels or on the model's own unreviewed outputs.
✅ Correct: human-reviewed gold labels.

❌ Mistake 3: Validating only the converted record. Also validate raw fields (empty product, unknown code format) before conversion.

---

## 🧠 Tricky Interview Question
**Q**: "Validation loss is great but production accuracy is poor. Why?"

**Answer**: Likely data leakage (near-duplicates in both splits) or a validation set that does not look like production traffic (different distribution, languages, rare classes). Fix: dedupe including near-duplicates, split by group (e.g. by product family or by date), build validation from real recent traffic, and evaluate on a held-out business metric, not just loss.

---

## ⚫ Interview Questions + Answers

Q1: What format do chat fine-tuning files use?
A1: JSONL where each line is an object with a `messages` list of role/content pairs (OpenAI style; check your provider).

Q2: Why a validation split?
A2: To detect overfitting and compare checkpoints on unseen data.

Q3: Fine-tune or RAG?
A3: RAG for changing facts/knowledge; fine-tune for style, format and consistent behaviour. They combine well.

Q4: How many examples are needed?
A4: Often tens to a few hundred good examples show a gain; more helps with diversity. Quality over quantity (rule of thumb, depends on task).

Q5 (Hard): How do you build a dataset when labelled data is scarce?
A5: Use a strong model to draft labels, have experts review and correct them, deduplicate, balance rare classes, hold out a human-only gold test set, and measure whether the fine-tuned small model matches the strong one.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Prompting plateaus; need strict format/style; want a cheaper small model to do a stable task

❌ Avoid when:
- Knowledge changes daily (use RAG); you have little reliable data

---

## 📊 Visual Diagram
```
 raw rows ─► normalise ─► to chat format ─► validate ─► dedupe
                                                          │
                                          shuffle(seed) ──┤
                                                          ▼
                                         train.jsonl   val.jsonl
                                                 │
                                          fine-tune job ─► eval on gold set
```

---

## 💰 Cost Impact
Training is billed per training token x epochs, so shorter, deduplicated examples directly cut cost (check provider pricing; illustrative). The payoff is at inference: a tuned small model can replace long few-shot prompts. Example: removing 800 tokens of few-shot examples from a prompt at 1M calls/month saves 800M input tokens. Count tokens per example before training to estimate cost.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JSONL | One JSON object per line | हर line में एक JSON |
| Fine-tuning | Further training on your data | अपने data पर अतिरिक्त training |
| Validation set | Held-out data to check | जाँच के लिए अलग data |
| Data leakage | Test data seen in training | Test data का training में आ जाना |
| Deduplication | Remove repeats | दोहराव हटाना |

---

## ⚡ 3-Line Summary
English: Clean, validate and deduplicate rows, then convert to chat-format JSONL. Dedupe before splitting to avoid leakage. Keep a gold test set from real traffic.
Hindi: Rows clean, validate और dedupe करो, फिर chat-format JSONL बनाओ। Leakage से बचने के लिए split से पहले dedupe करो। Real traffic से gold test set रखो।

---

## ➡️ Next Topic
**597. Debug Hallucination Issue** — after training or prompting, learn to diagnose answers that are not grounded.
