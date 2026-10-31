---

# 240. RunnableLambda
# हिंदी में: RunnableLambda

---

## 🔵 Simple Definition (English)
`RunnableLambda` wraps any Python function (sync or async) into a Runnable so it can sit in an LCEL chain and gain `invoke`, `batch`, `stream`, async support and tracing. The `@chain` decorator does the same for a function.

## 🔵 सरल परिभाषा (Hindi)
`RunnableLambda` किसी भी Python function (sync या async) को Runnable में लपेटता है ताकि वह LCEL chain में बैठ सके और उसे `invoke`, `batch`, `stream`, async और tracing मिले। `@chain` decorator function के लिए यही काम करता है।

---

## 🔴 Problem it Solves
Real pipelines need custom glue: clean text, format documents, route, validate, call a service. Without a wrapper these steps break the chain (no tracing, no batch, no async). RunnableLambda makes plain functions first-class chain citizens.

## 🔴 यह क्यों बना? (Hindi)
असली pipelines में अपना glue चाहिए: text साफ करना, docs format करना, routing, validation, service call। Wrapper के बिना ये steps chain तोड़ते हैं (tracing, batch, async नहीं)। RunnableLambda सादे functions को chain का पूरा सदस्य बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a function f(x) -> y  (type-hinted)
Step 2 → Wrap: RunnableLambda(f)  or  decorate with @chain
Step 3 → Place in chain: a | RunnableLambda(f) | b
Step 4 → invoke(x) calls f(x); sync functions in async chains run in an executor
Step 5 → Async function: RunnableLambda(af) uses ainvoke natively
Step 6 → Function may accept (x, config) to propagate callbacks
Step 7 → If f returns a Runnable, LCEL invokes it (dynamic routing)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → function f(x) -> y लिखो (type hints के साथ)
Step 2 → Wrap: RunnableLambda(f) या @chain
Step 3 → Chain में रखो: a | RunnableLambda(f) | b
Step 4 → invoke(x) f(x) बुलाता है; async chain में sync function executor में चलता है
Step 5 → Async function के लिए ainvoke native चलता है
Step 6 → f(x, config) लेने से callbacks आगे जाते हैं
Step 7 → f कोई Runnable लौटाए तो LCEL उसे चला देता है (dynamic routing)
```

---

## 🟡 Real World Example
**Tariff Classification System**: `RunnableLambda(route)` inspects the product text: if it contains a known HS code, return a cheap "lookup" chain; otherwise return the full RAG chain. The result is a dynamic router with tracing. **Zomato AI**: a lambda that strips PII (phone numbers) before the text reaches the LLM.

## 🟡 Real Example Hindi mein
**Tariff System**: `RunnableLambda(route)` product text देखता है: उसमें known HS code हो तो सस्ती "lookup" chain लौटाओ, वरना पूरी RAG chain। नतीजा tracing वाला dynamic router है। **Zomato AI**: LLM तक पहुँचने से पहले PII (phone numbers) हटाने वाला lambda।

---

## 💻 Code Example — Basic
```python
# Runs offline
import re
from langchain_core.runnables import RunnableLambda, chain

def mask_phone(text: str) -> str:
    return re.sub(r"\b\d{10}\b", "<PHONE>", text)  # hide 10-digit numbers

def count_words(text: str) -> dict:
    return {"text": text, "words": len(text.split())}  # add a stat

pipeline = RunnableLambda(mask_phone) | RunnableLambda(count_words)  # two lambdas piped
print(pipeline.invoke("call 9876543210 about earbuds"))  # {'text': 'call <PHONE> about earbuds', 'words': 4}
print(pipeline.batch(["a b", "c d e"]))  # batch for free

# Decorator form:
@chain
def shout(text: str) -> str:
    return text.upper()  # becomes a Runnable

print(shout.invoke("hs code"))  # HS CODE

# Dynamic routing: returning a Runnable from a lambda runs it
cheap = RunnableLambda(lambda x: f"lookup:{x}")
full = RunnableLambda(lambda x: f"rag:{x}")
router = RunnableLambda(lambda x: cheap if re.fullmatch(r"\d{4}\.\d{2}", x) else full)
print(router.invoke("8518.30"), router.invoke("earbuds"))  # lookup:8518.30 rag:earbuds
```

## 💻 Code Example — Advanced
```python
# Async lambdas with config propagation, error handling, typed output
import asyncio
import re
from pydantic import BaseModel
from langchain_core.runnables import RunnableLambda, RunnableConfig

class Cleaned(BaseModel):
    text: str
    pii_removed: bool

async def clean(text: str, config: RunnableConfig) -> Cleaned:
    """Remove emails/phones. `config` arg lets tracing/callbacks flow in."""
    try:
        new = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "<EMAIL>", text)  # emails
        new = re.sub(r"\b\d{10}\b", "<PHONE>", new)  # phones
        return Cleaned(text=new, pii_removed=new != text)
    except re.error as exc:
        raise ValueError(f"cleaning failed: {exc}") from exc

async def enrich(c: Cleaned) -> dict:
    await asyncio.sleep(0)  # placeholder for real async IO
    return {**c.model_dump(), "length": len(c.text)}

pipeline = RunnableLambda(clean) | RunnableLambda(enrich)  # async-native steps

async def main() -> None:
    results = await pipeline.abatch(["mail me a@b.com", "plain text"], config={"max_concurrency": 4})
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class In(BaseModel):
    text: str

@app.post("/sanitize")
async def sanitize(body: In) -> dict:
    return await pipeline.ainvoke(body.text)  # async lambdas run natively on the event loop
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph nodes are functions, which LangGraph wraps similarly. In LCEL, `RunnableLambda` is for glue between model-related steps; in LangGraph, conditional edge functions replace lambda routers. Wrapped functions keep tracing names via `run_name`.

```python
# RunnableLambda(clean).with_config(run_name="pii_clean")   # shows by name in LangSmith
# graph.add_node("clean", clean)    # LangGraph treats the function as a node
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Lambda that takes more than one argument
```python
# Wrong: RunnableLambda(lambda a, b: a + b)    # a Runnable receives ONE input
# Right: RunnableLambda(lambda d: d["a"] + d["b"])    # take a dict
```

❌ Mistake 2: Breaking streaming with a lambda at the end
```python
# Wrong: llm | StrOutputParser() | RunnableLambda(str.upper)   # waits for the full text
# Right: use a generator function (RunnableGenerator) that transforms chunks as they arrive
```

---

## 🧠 Tricky Interview Question
**Q**: "A RunnableLambda calls `requests.get` and under load your FastAPI app freezes. Why, and how to fix?"

**Answer**: A sync function in an async chain is run via an executor thread (default pool), so many concurrent requests exhaust the pool; or if invoked with `.invoke` inside the event loop, it blocks the loop. Fix: make the lambda `async def` with `httpx.AsyncClient`, reuse a client, set timeouts, and call `ainvoke`.

---

## ⚫ Interview Questions + Answers

Q1: What is RunnableLambda for? (Easy)
A1: Wrap any function as a Runnable to use it in LCEL chains.

Q2: Can it be async? (Easy)
A2: Yes: pass an `async def`; use `ainvoke`. You can also give both `func` and `afunc`.

Q3: What does `@chain` do? (Medium)
A3: Turns a function into a Runnable; inside, you can invoke other runnables and the traces nest correctly.

Q4: What happens if the lambda returns a Runnable? (Medium)
A4: LCEL invokes the returned Runnable with the same input: this is the dynamic routing pattern.

Q5: When prefer LangGraph conditional edges to lambda routing? (Hard)
A5: When routing is complex, needs state, loops, retries or human approval, or when you want visual graph and checkpoints. Lambda routing suits small stateless branching inside a chain.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cleaning, formatting, validation, small routers

❌ Avoid when:
- Heavy logic that deserves its own tested class/Runnable
- Streaming must be preserved (use generator runnable)

---

## 📊 Visual Diagram
```
 text ─► RunnableLambda(mask_pii) ─► prompt ─► llm ─► RunnableLambda(validate)
              │                                           │
        plain Python fn                              plain Python fn
 Router: RunnableLambda(x -> cheap_chain | full_chain)  # returns a Runnable
```

---

## 💰 Cost Impact
Lambdas are free but save money when they avoid LLM calls: regex extraction, cache lookup, routing by rule (cheap chain vs expensive chain), truncating context (`text[:3000]`) and PII stripping reduce tokens. Put such steps before the model.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RunnableLambda | Function as Runnable | Function को Runnable बनाना |
| @chain | Decorator version | Decorator रूप |
| Dynamic routing | Return a chain at run time | Run time पर chain चुनना |
| Glue code | Small helper steps | जोड़ने वाला code |
| run_name | Trace label | Trace का नाम |

---

## ⚡ 3-Line Summary
English: RunnableLambda turns any function into a Runnable with batch, async and tracing. It takes one input and can return a Runnable for dynamic routing. Prefer async functions and avoid blocking IO.
Hindi: RunnableLambda किसी भी function को batch, async और tracing वाला Runnable बनाता है। यह एक input लेता है और dynamic routing के लिए Runnable लौटा सकता है। Async functions लो और blocking IO से बचो।

---

## ➡️ Next Topic
**241. Document Loaders** — getting PDFs, CSVs, web pages into LangChain Documents.
