---

# 491. Fine Tuning Data Format (JSONL)
# हिंदी में: Fine Tuning Data Format (JSONL)

---

## 🔵 Simple Definition (English)
JSONL means JSON Lines: one complete JSON object per line. For chat fine tuning each line holds a `messages` list with `system`, `user` and `assistant` turns. The assistant turn is the answer you want the model to learn.

## 🔵 सरल परिभाषा (Hindi)
JSONL का मतलब JSON Lines: हर line में एक पूरा JSON object। Chat fine tuning में हर line में `messages` की list होती है जिसमें `system`, `user` और `assistant` turns होते हैं। Assistant turn वह जवाब है जो आप model को सिखाना चाहते हैं।

---

## 🔴 Problem it Solves
Training pipelines need a simple, streamable, line-by-line format. A big JSON array would have to be loaded whole and one bad comma breaks everything. JSONL lets tools read, validate and count examples line by line, and a bad line affects only itself.

## 🔴 यह क्यों बना? (Hindi)
Training pipelines को simple, streamable, line-by-line format चाहिए। बड़ा JSON array पूरा load करना पड़ता है और एक गलत comma सब तोड़ देता है। JSONL में tools line-by-line पढ़, validate और count कर सकते हैं, और खराब line सिर्फ़ खुद को प्रभावित करती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → One example = one line = one JSON object
Step 2 → Object has key "messages": list of {role, content}
Step 3 → Roles: system (optional), user, assistant (the target answer)
Step 4 → Last message should be the assistant answer to learn
Step 5 → No trailing commas, no blank lines, UTF-8 encoding
Step 6 → Optional: "weight" on assistant messages (0 or 1) to skip training on some turns
Step 7 → Validate every line before uploading
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक example = एक line = एक JSON object
Step 2 → Object में key "messages": {role, content} की list
Step 3 → Roles: system (optional), user, assistant (सीखने वाला जवाब)
Step 4 → आख़िरी message वह assistant जवाब हो जो सीखना है
Step 5 → Trailing comma नहीं, blank lines नहीं, UTF-8 encoding
Step 6 → Optional: assistant messages पर "weight" (0 या 1) ताकि कुछ turns पर training न हो
Step 7 → Upload से पहले हर line validate करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: One training line:

`{"messages":[{"role":"system","content":"You classify goods to HS codes. Reply JSON only."},{"role":"user","content":"Bluetooth wireless headphones"},{"role":"assistant","content":"{\"hs_code\":\"8518.30\",\"confidence\":\"high\"}"}]}`

Note the assistant content is itself a JSON string, so its quotes are escaped. Using `json.dumps` in code avoids escaping errors.

**Zomato-style**: `user`: review text, `assistant`: `delivery`.

## 🟡 Real Example Hindi mein
**Tariff System**: एक training line ऊपर दी गई है। ध्यान दें कि assistant का content खुद JSON string है, इसलिए उसके quotes escape होते हैं। Code में `json.dumps` use करने से escaping की गलतियाँ नहीं होतीं।

**Zomato-style**: `user`: review text, `assistant`: `delivery`।

---

## 💻 Code Example — Basic
```python
# Basic: build and write a tiny JSONL training file (pure Python, runs offline)
import json  # JSON encoding
from typing import Dict, List  # type hints

# Raw labelled data: (description, hs_code)
raw: List[Dict[str, str]] = [
    {"desc": "Bluetooth wireless headphones", "hs": "8518.30"},
    {"desc": "Cotton T-shirt men", "hs": "6109.10"},
]

SYSTEM: str = "You classify goods to HS codes. Reply JSON only."  # same system prompt every line


def to_line(desc: str, hs: str) -> str:
    """Convert one labelled row into one JSONL line."""
    answer = json.dumps({"hs_code": hs})  # assistant answer as a JSON string
    row = {  # chat format row
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": desc},
            {"role": "assistant", "content": answer},
        ]
    }
    return json.dumps(row, ensure_ascii=False)  # one line, keep non-ASCII readable


with open("train_demo.jsonl", "w", encoding="utf-8") as f:  # write file
    for r in raw:  # each example
        f.write(to_line(r["desc"], r["hs"]) + "\n")  # one line plus newline

print(open("train_demo.jsonl", encoding="utf-8").read())  # show the file
```

## 💻 Code Example — Advanced
```python
# Production style: strict validator for chat JSONL with async streaming and error report
import asyncio  # async
import json  # parse
from dataclasses import dataclass, field  # report
from typing import Any, Dict, List  # types

ALLOWED_ROLES = {"system", "user", "assistant"}  # valid roles (tool roles exist for tool tuning)


@dataclass
class Report:
    total: int = 0  # lines checked
    valid: int = 0  # lines OK
    errors: List[str] = field(default_factory=list)  # messages like "line 3: ..."


def validate_row(row: Dict[str, Any]) -> List[str]:
    """Return a list of problems for one parsed row (empty means valid)."""
    problems: List[str] = []  # collect
    msgs = row.get("messages")  # get messages
    if not isinstance(msgs, list) or not msgs:  # must be a non empty list
        return ["messages missing or empty"]
    for m in msgs:  # check each message
        if not isinstance(m, dict) or m.get("role") not in ALLOWED_ROLES:
            problems.append(f"bad role in {m!r}")
        elif not isinstance(m.get("content"), str) or not m["content"].strip():
            problems.append("empty content")
    if msgs[-1].get("role") != "assistant":  # last must be the target answer
        problems.append("last message must be assistant")
    if not any(m.get("role") == "user" for m in msgs if isinstance(m, dict)):
        problems.append("no user message")
    return problems


async def validate_file(path: str) -> Report:
    """Validate a JSONL file line by line."""
    rep = Report()  # new report
    try:
        with open(path, "r", encoding="utf-8") as f:  # open file
            for i, line in enumerate(f, start=1):  # 1-based line numbers
                rep.total += 1
                try:
                    row = json.loads(line)  # parse
                except json.JSONDecodeError as exc:  # invalid JSON
                    rep.errors.append(f"line {i}: invalid JSON ({exc.msg})")
                    continue
                probs = validate_row(row)  # semantic checks
                if probs:
                    rep.errors.extend(f"line {i}: {p}" for p in probs)
                else:
                    rep.valid += 1
                if i % 1000 == 0:  # yield sometimes on huge files
                    await asyncio.sleep(0)
    except FileNotFoundError:
        rep.errors.append("file not found")
    return rep


if __name__ == "__main__":
    print(asyncio.run(validate_file("train_demo.jsonl")))  # run after the basic example
```

---

## 🟠 FastAPI Integration
Offer a validation endpoint so non-engineers can upload a dataset and see line-level errors before training.

```python
import json  # parse
from fastapi import FastAPI, UploadFile  # framework

app = FastAPI()  # app


@app.post("/dataset/validate")
async def validate(file: UploadFile) -> dict:
    """Return line level errors for an uploaded JSONL file."""
    text = (await file.read()).decode("utf-8")  # read upload
    errors = []  # list of errors
    for i, line in enumerate(text.splitlines(), start=1):  # each line
        try:
            row = json.loads(line)  # parse
            if row["messages"][-1]["role"] != "assistant":  # target must be last
                errors.append(f"line {i}: last role must be assistant")
        except (json.JSONDecodeError, KeyError, IndexError, TypeError):
            errors.append(f"line {i}: malformed")
    return {"ok": not errors, "errors": errors[:50]}  # cap error list
```

---

## 🔗 LangChain / LangGraph Connection
LangChain message objects can be converted to this format, so you can export good production conversations (from LangSmith traces) into training data.

```python
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage  # message types

ROLE = {SystemMessage: "system", HumanMessage: "user", AIMessage: "assistant"}  # type to role


def to_jsonl_row(msgs: list) -> dict:
    """Convert LangChain messages into one chat fine tuning row."""
    return {"messages": [{"role": ROLE[type(m)], "content": m.content} for m in msgs]}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building JSON strings by hand
✅ Correct: Always use `json.dumps`.

```python
# Wrong: f'{{"role":"assistant","content":"{answer}"}}'  # quotes in answer break JSON
# Right: json.dumps({"role": "assistant", "content": answer})
```

❌ Mistake 2: Training prompt differs from production prompt
✅ Correct: Use the identical system prompt and message layout at inference.

```python
# Wrong: train with system prompt A, serve with no system prompt
# Right: keep one shared constant for both training data and API calls
```

---

## 🧠 Tricky Interview Question
**Q**: "Upload fails with an invalid file error but your file opens fine in an editor. What do you check?"

**Answer**: Check each line is valid JSON on its own (not a pretty-printed multi-line array), no blank trailing lines in the middle, UTF-8 encoding, every row has `messages`, valid roles, non-empty content, last turn is assistant, and the file meets the minimum example count and size limits. A line-by-line validator finds the exact line.

---

## ⚫ Interview Questions + Answers

Q1: What does JSONL stand for? (Easy)
A1: JSON Lines: one JSON object per line.

Q2: Which role holds the training target? (Easy)
A2: The `assistant` message.

Q3: Why is the system prompt in training important? (Medium)
A3: The model learns behaviour conditioned on the prompt layout. Mismatch between training and serving prompts reduces quality.

Q4: Can multi-turn chats be used? (Medium)
A4: Yes: include several user/assistant turns in one `messages` list. The `weight` field on assistant messages can mark which turns to learn from (0 means ignore).

Q5: How do you handle data from production logs safely? (Hard)
A5: Filter by quality signals (thumbs up, human review), remove PII, dedupe, balance classes, split train/validation by time or customer, and version the dataset with a hash for reproducibility.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Fine tuning chat models (OpenAI style)
- You want streamable, diff-friendly datasets

❌ Avoid when:
- A provider needs another schema (check its docs, e.g. preference data for DPO has its own format)

---

## 📊 Visual Diagram
```
 train.jsonl
 ┌────────────────────────────────────────────────────┐
 │ {"messages":[sys, user, assistant]}   ← example 1  │
 │ {"messages":[sys, user, assistant]}   ← example 2  │
 │ {"messages":[sys, user, assistant]}   ← example 3  │
 └────────────────────────────────────────────────────┘
   one line = one JSON object = one training example
```

---

## 💰 Cost Impact
- Training tokens are counted from every message in every line, so long system prompts repeat in each example and multiply cost.
- Keep the system prompt short; the tuned model will not need long instructions.
- Remove duplicates and near-empty rows before upload.
- Token usage per example = system + user + assistant tokens (count with tiktoken).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JSONL | One JSON object per line | हर line में एक JSON object |
| messages | List of role/content turns | Role/content turns की list |
| Role | system, user or assistant | बोलने वाले की भूमिका |
| Escape | Backslash before quotes in strings | String में quotes से पहले backslash |
| Validator | Script that checks format | Format जाँचने वाली script |
| weight | 0 or 1 to skip/learn a turn | Turn सीखना या छोड़ना |

---

## ⚡ 3-Line Summary
English: Chat fine tuning data is JSONL with a `messages` list per line, ending with the assistant answer.
Build rows with `json.dumps` and keep the training prompt identical to the production prompt.
Validate line by line before upload.
Hindi: Chat fine tuning data JSONL होता है, हर line में `messages` list और आख़िर में assistant का जवाब।
Rows `json.dumps` से बनाओ और training prompt को production prompt जैसा ही रखो।
Upload से पहले line-by-line validate करो।

---

## ➡️ Next Topic
**492. Training Data Preparation** — collecting, cleaning, balancing and splitting data.
