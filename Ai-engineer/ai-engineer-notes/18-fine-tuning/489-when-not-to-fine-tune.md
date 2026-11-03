---

# 489. When NOT to Fine Tune
# हिंदी में: Fine Tune कब नहीं करना चाहिए

---

## 🔵 Simple Definition (English)
Do not fine tune when the real problem is missing knowledge, bad prompts, bad data or a task that keeps changing. In these cases fine tuning is slow, costly and often makes things worse.

## 🔵 सरल परिभाषा (Hindi)
जब असली समस्या knowledge की कमी, खराब prompt, खराब data या बार-बार बदलता task हो, तब fine tune मत करो। ऐसे में fine tuning धीमी, महँगी होती है और अक्सर हालत और बिगाड़ देती है।

---

## 🔴 Problem it Solves
Fine tuning is popular, so teams treat it as a magic fix. Wrongly tuned models hallucinate confidently, forget general skills and lock you to one model version. This note lists the anti-patterns so you can say no with reasons.

## 🔴 यह क्यों बना? (Hindi)
Fine tuning popular है, इसलिए teams इसे जादुई हल समझती हैं। गलत तरह से tune किया model आत्मविश्वास से hallucinate करता है, general skills भूल जाता है और आपको एक model version से बाँध देता है। यह note anti-patterns बताता है ताकि आप कारण के साथ "ना" कह सकें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Facts change often?            → use RAG, not tuning
Step 2 → Fewer than ~50 clean examples? → collect data / use few-shot
Step 3 → No eval set?                   → build eval first
Step 4 → Labels or schema unstable?     → stabilise first
Step 5 → Low call volume, prompt works? → keep prompting
Step 6 → Need citations / audit trail?  → RAG gives sources, tuning does not
Step 7 → Data has PII/secrets?          → clean or avoid training on it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Facts अक्सर बदलते हैं?        → RAG use करो, tuning नहीं
Step 2 → ~50 से कम साफ़ examples?      → data जुटाओ / few-shot use करो
Step 3 → Eval set नहीं है?             → पहले eval बनाओ
Step 4 → Labels या schema अस्थिर?      → पहले स्थिर करो
Step 5 → कम volume, prompt चल रहा?     → prompting जारी रखो
Step 6 → Citations / audit trail चाहिए? → RAG sources देती है, tuning नहीं
Step 7 → Data में PII/secrets?         → साफ़ करो या उस पर train मत करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A teammate wants to fine tune on the full customs tariff book so the model "knows all rates". Rates change with each Finance Act, the model cannot cite which notification gave a rate, and an auditor must see sources. Correct choice: RAG over the tariff book with citations. Fine tune only the output format.

**Amazon-style**: A returns-policy bot where policy changes weekly. Tuning would be stale in a week; RAG updates instantly.

## 🟡 Real Example Hindi mein
**Tariff System**: एक teammate पूरी customs tariff book पर fine tune करना चाहता है ताकि model "सारे rates जाने"। हर Finance Act के साथ rates बदलते हैं, model बता नहीं सकता कि rate किस notification से आया, और auditor को sources चाहिए। सही चुनाव: citations के साथ tariff book पर RAG। सिर्फ़ output format fine tune करो।

**Amazon-style**: Returns-policy bot जहाँ policy हर हफ़्ते बदलती है। Tuning एक हफ़्ते में पुरानी हो जाएगी; RAG तुरंत update होती है।

---

## 💻 Code Example — Basic
```python
# Basic: a "stop sign" checker that lists reasons NOT to fine tune
from typing import List  # type hints


def stop_reasons(
    facts_change_often: bool,
    n_clean_examples: int,
    has_eval_set: bool,
    labels_stable: bool,
    needs_citations: bool,
) -> List[str]:
    """Return a list of reasons that argue against fine tuning."""
    reasons: List[str] = []  # collect reasons
    if facts_change_often:  # knowledge problem
        reasons.append("facts change often -> use RAG")
    if n_clean_examples < 50:  # too little data
        reasons.append("fewer than 50 clean examples")
    if not has_eval_set:  # cannot measure
        reasons.append("no eval set")
    if not labels_stable:  # moving target
        reasons.append("labels not stable")
    if needs_citations:  # tuning cannot cite
        reasons.append("citations needed -> use RAG")
    return reasons  # empty list means no blockers


print(stop_reasons(True, 20, False, True, True))  # many blockers
print(stop_reasons(False, 500, True, True, False))  # [] means OK
```

## 💻 Code Example — Advanced
```python
# Production style: async data quality gate that blocks training on risky data
import asyncio  # async
import json  # parse lines
import re  # simple PII patterns
from typing import List, Tuple  # type hints

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")  # email pattern
PHONE = re.compile(r"\b\d{10}\b")  # 10 digit phone pattern (illustrative)


async def scan_dataset(lines: List[str]) -> Tuple[int, int, int]:
    """Return (total, with_pii, duplicates) for JSONL lines."""
    seen: set = set()  # for duplicate detection
    pii, dup = 0, 0  # counters
    for line in lines:  # check each example
        try:
            row = json.loads(line)  # parse
        except json.JSONDecodeError:  # skip broken lines
            continue
        text = json.dumps(row, ensure_ascii=False)  # flatten to string
        if EMAIL.search(text) or PHONE.search(text):  # PII found
            pii += 1
        if text in seen:  # exact duplicate
            dup += 1
        seen.add(text)  # remember
        await asyncio.sleep(0)  # cooperative yield
    return len(lines), pii, dup


async def main() -> None:
    sample = [
        json.dumps({"messages": [{"role": "user", "content": "mail me at a@b.com"}]}),
        json.dumps({"messages": [{"role": "user", "content": "laptop"}]}),
        json.dumps({"messages": [{"role": "user", "content": "laptop"}]}),
    ]
    total, pii, dup = await scan_dataset(sample)  # run scan
    print(f"total={total} pii={pii} duplicates={dup}")  # report
    if pii or dup:  # gate decision
        print("BLOCK: clean the data before training")


if __name__ == "__main__":
    asyncio.run(main())  # demo
```

---

## 🟠 FastAPI Integration
Add a gate endpoint to your ML platform so training jobs cannot start unless checks pass.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # schema

app = FastAPI()  # app


class TrainRequest(BaseModel):
    n_examples: int  # dataset size
    has_eval_set: bool  # eval exists?
    facts_change_often: bool  # knowledge problem?


@app.post("/finetune/gate")
async def gate(req: TrainRequest) -> dict:
    """Reject training requests that fail basic sanity checks."""
    problems = []  # reasons to reject
    if req.n_examples < 50:
        problems.append("need at least 50 examples")
    if not req.has_eval_set:
        problems.append("create an eval set first")
    if req.facts_change_often:
        problems.append("use RAG for changing facts")
    if problems:  # block
        raise HTTPException(status_code=422, detail=problems)
    return {"approved": True}  # allowed
```

---

## 🔗 LangChain / LangGraph Connection
In LangGraph, a router node can send "knowledge" questions to a RAG branch and "format" tasks to the tuned model, rather than tuning for everything.

```python
# Illustrative routing logic inside a LangGraph conditional edge
def route(state: dict) -> str:
    """Return the next node name based on question type."""
    if state.get("needs_fresh_facts"):  # knowledge question
        return "rag_node"  # use retrieval
    return "tuned_classifier_node"  # behaviour task
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Training on PII and secrets
✅ Correct: Redact before training; the model can regurgitate training data.

```python
# Wrong: dump raw support chats (names, phone numbers) into the training file
# Right: run a redaction step, then validate with a scan like the one above
```

❌ Mistake 2: Training on model-generated labels without review
✅ Correct: Human review a sample; errors in labels become the model's "truth".

```python
# Wrong: label 10,000 rows with another LLM and train directly
# Right: review a random sample, fix systematic errors, then train
```

---

## 🧠 Tricky Interview Question
**Q**: "We fine tuned and accuracy on our test set jumped to 99 percent, but production complaints rose. What happened?"

**Answer**: Likely data leakage or overfitting: the test set overlapped with training data (duplicates, near-duplicates), so 99 percent is fake. Production inputs differ from the curated set. Fix by deduplicating, splitting by source/time, and building an eval from real production traffic.

---

## ⚫ Interview Questions + Answers

Q1: Why not fine tune to add facts? (Easy)
A1: Tuning adjusts behaviour and patterns; facts learned this way are unreliable, can't be cited and go stale.

Q2: What is catastrophic forgetting? (Easy)
A2: After training on a narrow task the model loses some general abilities it had before.

Q3: What is model lock-in? (Medium)
A3: A tuned model belongs to one base version. When that base is deprecated you must retrain, so keep your dataset and pipeline reusable.

Q4: How does bad data hurt? (Medium)
A4: The model copies errors, inconsistencies and biases. Small noisy sets can make it worse than the base model.

Q5: A regulated client needs explainable answers. Tune or not? (Hard)
A5: Prefer RAG with citations so every answer is traceable to a source document. Use tuning only for style, and keep logs, versions and eval records for audit.

---

## 🔷 When to Use + When Not to Use
✅ Skip fine tuning when:
- Facts change or need citations
- Data is small, noisy or sensitive
- Prompting already works

❌ Do not skip evaluation:
- Even a "no" decision should be backed by measured baseline

---

## 📊 Visual Diagram
```
 Problem type            Right tool
 ─────────────────────   ─────────────────────
 Missing / fresh facts   RAG
 Need sources            RAG
 Bad instructions        Better prompt
 Format enforcement      Structured outputs / tuning
 Tone, narrow skill      Fine tuning
 Tiny/noisy data         Collect data first
```

---

## 💰 Cost Impact
- Wasted training runs cost money and engineer time (price illustrative per provider).
- Mis-tuned models raise support costs and re-work.
- Cheaper checks first: prompt iteration costs only a few tokens per test.
- Optimise by gating training behind data quality and eval-set checks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Catastrophic forgetting | Loses old skills after tuning | Tuning के बाद पुरानी skills भूलना |
| Data leakage | Test data seen in training | Test data का training में आ जाना |
| Lock-in | Tied to one base model | एक base model से बँध जाना |
| PII | Personal data | निजी जानकारी |
| Deduplication | Remove repeated rows | दोहराई हुई rows हटाना |
| Citation | Source reference | स्रोत का हवाला |

---

## ⚡ 3-Line Summary
English: Do not fine tune for changing facts, tiny or noisy data, missing evals or when prompts already work.
Bad tuning causes hallucination, forgetting and lock-in.
Use RAG for knowledge and citations.
Hindi: बदलते facts, छोटे या noisy data, eval न होने पर या prompt पहले से चल रहा हो तो fine tune मत करो।
गलत tuning से hallucination, forgetting और lock-in होता है।
Knowledge और citations के लिए RAG use करो।

---

## ➡️ Next Topic
**490. OpenAI Fine Tuning** — the practical API workflow: upload file, create job, use the model.
