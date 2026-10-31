---

# 066. Prompt Chaining
# हिंदी में: Prompt Chaining — बड़े काम को छोटे prompts की कड़ी में बाँटना

---

## 🔵 Simple Definition (English)
Prompt chaining splits a complex task into several smaller prompts. The output of step 1 becomes the input of step 2, and so on. Each step has one clear job, so it is easier to test, debug and improve than one giant prompt.

## 🔵 सरल परिभाषा (Hindi)
Prompt chaining में जटिल काम को कई छोटे prompts में बाँटते हैं। Step 1 का output, step 2 का input बनता है। हर step का एक साफ़ काम होता है, इसलिए एक बड़े prompt के मुक़ाबले test, debug और improve करना आसान है।

---

## 🔴 Problem it Solves
One big prompt ("read the invoice, extract items, classify each, compute duty, write a report") often fails: the model skips steps, mixes formats and is hard to debug. When the final answer is wrong you cannot tell which part failed.

Chaining gives focused prompts, per-step validation, per-step model choice (cheap vs strong) and clear logs.

## 🔴 यह क्यों बना? (Hindi)
एक बड़ा prompt ("invoice पढ़ो, items निकालो, classify करो, duty निकालो, report लिखो") अक्सर फेल होता है: model steps छोड़ देता है, formats मिला देता है, debug मुश्किल। अंतिम जवाब गलत हो तो पता नहीं चलता कौन सा हिस्सा गलत था। Chaining से focused prompts, हर step की validation, हर step का अलग model और साफ़ logs मिलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Break the task into small stages (extract -> classify -> price -> report)
Step 2 → Write one prompt per stage with a clear input and output format
Step 3 → Run stage 1, validate its output
Step 4 → Pass the validated output into stage 2 prompt
Step 5 → Repeat until the last stage
Step 6 → Add gates: stop or branch if a stage fails or confidence is low
Step 7 → Log each stage (input, output, tokens, latency)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → काम को छोटे stages में बाँटो (extract -> classify -> price -> report)
Step 2 → हर stage का एक prompt, साफ़ input/output format के साथ
Step 3 → Stage 1 चलाओ, output validate करो
Step 4 → Validated output को stage 2 के prompt में दो
Step 5 → आख़िरी stage तक दोहराओ
Step 6 → Gates लगाओ: stage फेल या confidence कम हो तो रुको/branch करो
Step 7 → हर stage log करो (input, output, tokens, latency)
```

---

## 🟡 Real World Example
**Tariff Classification System**: A shipping invoice (free text) arrives.
1. Extract line items -> JSON list.
2. For each item, classify HS code (with retrieved context).
3. Look up duty rate in a table (plain code, no LLM).
4. Write a short Markdown summary for the customs officer.
If step 2 gives confidence < 0.7, the chain branches to a human review queue.

**Amazon-style**: Review summariser: split reviews -> summarise each -> merge summaries -> final pros/cons.

## 🟡 Real Example Hindi mein
**Tariff System**: Shipping invoice (free text) आता है।
1. Line items निकालो -> JSON list।
2. हर item का HS code classify करो (retrieved context के साथ)।
3. Duty rate table से देखो (सिर्फ code, LLM नहीं)।
4. Officer के लिए छोटा Markdown summary लिखो।
Step 2 में confidence < 0.7 हो तो chain human review queue में branch करती है।

---

## 💻 Code Example — Basic
```python
# Basic: a 3-step chain with a fake LLM (runs offline)
import json  # to parse step outputs

def fake_llm(prompt: str) -> str:
    # Return canned answers depending on which stage the prompt is for
    if prompt.startswith("EXTRACT"):
        return json.dumps(["wireless earbuds", "usb cable"])          # list of items
    if prompt.startswith("CLASSIFY"):
        return "8518.30" if "earbuds" in prompt else "8544.42"        # HS code per item
    return "Report: 2 items classified."                              # summary stage

invoice = "2 x wireless earbuds, 5 x usb cable"                        # raw input

# Stage 1: extract items
items_json = fake_llm(f"EXTRACT items as JSON list from: {invoice}")   # LLM call 1
items: list[str] = json.loads(items_json)                              # parse into Python list

# Stage 2: classify each item separately (small focused prompts)
codes: dict[str, str] = {}                                             # item -> code
for item in items:                                                     # loop over items
    codes[item] = fake_llm(f"CLASSIFY HS code for: {item}")            # LLM call per item

# Stage 3: write the summary from validated data
summary = fake_llm(f"REPORT for codes: {codes}")                       # LLM call 3
print(codes)                                                           # {'wireless earbuds': '8518.30', ...}
print(summary)                                                         # Report: 2 items classified.
```

## 💻 Code Example — Advanced
```python
# Production: typed steps, gates, per-step logging, concurrency, error handling
from __future__ import annotations

import asyncio                                   # concurrency for per-item stage
import json                                      # parse JSON
import time                                      # measure latency
from dataclasses import dataclass, field         # data containers
from typing import Awaitable, Callable           # type hints

LLM = Callable[[str], Awaitable[str]]            # prompt -> reply

@dataclass
class StepLog:
    name: str                                    # step name
    seconds: float                               # how long it took
    ok: bool                                     # success flag

@dataclass
class ChainResult:
    codes: dict[str, str] = field(default_factory=dict)   # item -> code
    review: list[str] = field(default_factory=list)       # items needing a human
    logs: list[StepLog] = field(default_factory=list)     # step logs

async def timed(name: str, coro: Awaitable[str], result: ChainResult) -> str:
    start = time.perf_counter()                  # start timer
    try:
        out = await coro                         # run the LLM call
        result.logs.append(StepLog(name, time.perf_counter() - start, True))
        return out
    except Exception as exc:                     # log failures, then re-raise
        result.logs.append(StepLog(name, time.perf_counter() - start, False))
        raise RuntimeError(f"step {name} failed: {exc}") from exc

async def run_chain(llm: LLM, invoice: str) -> ChainResult:
    result = ChainResult()                                           # empty result
    raw = await timed("extract", llm(f"EXTRACT items JSON list: {invoice}"), result)
    try:
        items = list(json.loads(raw))                                # gate 1: valid JSON list
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("extract step returned invalid JSON") from exc

    async def classify(item: str) -> tuple[str, str]:                # stage 2 worker
        reply = await timed(f"classify:{item}", llm(f"CLASSIFY {item}"), result)
        return item, reply.strip()

    pairs = await asyncio.gather(*(classify(i) for i in items))      # run items concurrently
    for item, reply in pairs:
        if reply == "UNKNOWN":                                       # gate 2: low confidence
            result.review.append(item)                               # send to human
        else:
            result.codes[item] = reply                               # accept the code
    return result

async def _demo() -> None:
    async def llm(p: str) -> str:
        if p.startswith("EXTRACT"):
            return '["earbuds", "mystery gadget"]'
        return "8518.30" if "earbuds" in p else "UNKNOWN"
    r = await run_chain(llm, "earbuds + mystery gadget")
    print(r.codes, r.review, [l.name for l in r.logs])

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: chaining uses MORE total tokens (repeated instructions per step) but each prompt is small, so you can use cheaper models for simple steps. Run independent steps concurrently to cut latency.

---

## 🟠 FastAPI Integration
A chain is a natural service function. For long chains, return a job id and process in a background task, or stream step progress with SSE.

```python
from fastapi import FastAPI, HTTPException      # framework + errors
from pydantic import BaseModel                  # models
from openai import AsyncOpenAI                  # openai>=1

app = FastAPI()                                 # app
client = AsyncOpenAI()                          # client

class InvoiceIn(BaseModel):
    text: str                                   # raw invoice text

async def llm(prompt: str) -> str:
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=300,
        messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content or ""

@app.post("/invoice/classify")
async def classify_invoice(body: InvoiceIn) -> dict:
    try:
        result = await run_chain(llm, body.text)       # run_chain from advanced block
    except ValueError as exc:                          # bad intermediate output
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"codes": result.codes, "needs_review": result.review}
```

---

## 🔗 LangChain / LangGraph Connection
LCEL chains compose with `|`: `prompt1 | llm | parser | prompt2 | llm`. For branching, retries and loops use LangGraph: each stage is a node, state holds intermediate results, and conditional edges implement the gates.

```python
from langchain_core.prompts import ChatPromptTemplate          # prompts
from langchain_core.output_parsers import StrOutputParser      # string parser
from langchain_openai import ChatOpenAI                        # model

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)           # shared model
extract = ChatPromptTemplate.from_template("List items from: {text}") | llm | StrOutputParser()
classify = ChatPromptTemplate.from_template("HS codes for: {items}") | llm | StrOutputParser()
chain = {"items": extract} | classify                          # output of extract feeds classify
# result = await chain.ainvoke({"text": "2 earbuds, 5 usb cables"})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing unvalidated output to the next step
✅ Correct: Validate between steps.
```python
# Wrong: garbage in step 1 silently poisons everything after it
items = json.loads(step1_reply)

# Right: validate and fail fast (or retry)
if not isinstance(items, list) or not all(isinstance(i, str) for i in items):
    raise ValueError("step 1 invalid")
```

❌ Mistake 2: Splitting too much (10 tiny LLM calls for a simple task)
✅ Correct: Chain only where stages truly differ; do deterministic steps (lookups, math) in plain code.
```python
# Wrong: ask the LLM to multiply value x duty rate
# Right
duty = value * RATES[hs_code]
```

❌ Mistake 3: Running independent steps one by one. Use `asyncio.gather`.

---

## 🧠 Tricky Interview Question
**Q**: "Your 5-step chain is 95% accurate per step. What is the end-to-end accuracy and what do you do about it?"

**Answer**: Errors compound: 0.95^5 is about 77%. Fixes: validate and gate each step, add retries or self-check on the weakest step, replace LLM steps with deterministic code where possible, use stronger models for the critical steps, and measure accuracy per step so you improve the real bottleneck instead of guessing.

---

## ⚫ Interview Questions + Answers

Q1: What is prompt chaining?
A1: Splitting a task into multiple prompts where each output feeds the next.

Q2: Name two benefits over one big prompt.
A2: Easier debugging and testing (each step is isolated), and flexibility (different model, temperature or tools per step).

Q3: What is a gate in a chain?
A3: A check between steps that validates output or confidence and decides to continue, retry, branch to a human, or stop.

Q4: What are the downsides of chaining?
A4: More latency (sequential calls), more total tokens, error compounding, and more orchestration code.

Q5 (Hard): Chain or agent? How do you decide?
A5: Use a chain when the steps are known and fixed (invoice -> extract -> classify -> report): predictable, cheap, testable. Use an agent (LLM chooses tools/steps) when the path depends on the input and cannot be fixed upfront. Start with a chain; add LangGraph branching for limited flexibility; move to a full agent only when needed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The task has clear stages
- You need per-step validation or different models
- One big prompt is unreliable

❌ Avoid when:
- A single simple prompt already works well
- Latency is critical and steps cannot run in parallel
- The path is unpredictable (consider an agent)

---

## 📊 Visual Diagram
```
 Invoice text
      |
      v
 [Prompt 1: Extract items] --> JSON list --validate-->
      |
      v
 [Prompt 2: Classify each item] (parallel)
      |                    \
   confident              UNKNOWN --> Human review queue
      |
      v
 [Code: duty lookup]  (no LLM)
      |
      v
 [Prompt 3: Write summary] --> Final report
```

---

## 💰 Cost Impact
- Total tokens rise because each step repeats its instructions and passes context along.
- But steps can use different models: gpt-4o-mini for extract/classify, a stronger model only for the final reasoning.
- Retries cost per step, not for the whole task.

Optimisation: pass only the needed fields between steps (not full history), cache static instructions, run independent steps in parallel, do math and lookups in code, and set `max_tokens` per step.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chain | Ordered steps of prompts | Prompts की क्रमबद्ध कड़ी |
| Gate | Check between steps | Steps के बीच की जाँच |
| Error compounding | Small errors multiply | छोटी गलतियों का गुणा होना |
| Branching | Different path by result | Result के आधार पर अलग रास्ता |
| Orchestration | Code controlling the steps | Steps चलाने वाला code |
| LCEL | LangChain pipe syntax | LangChain की pipe syntax |

---

## ⚡ 3-Line Summary
English: Prompt chaining breaks a big task into small focused prompts, each feeding the next. Validate between steps and use plain code for deterministic work. Watch error compounding and total latency.
Hindi: Prompt chaining बड़े काम को छोटे focused prompts में बाँटती है, हर एक अगले को input देता है। Steps के बीच validate करो और deterministic काम plain code में करो। Error compounding और latency का ध्यान रखो।

---

## ➡️ Next Topic
**067. Meta Prompting** — using an LLM to write, critique and improve prompts themselves.
