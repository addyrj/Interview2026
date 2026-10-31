---

# 235. LCEL — LangChain Expression Language
# हिंदी में: LCEL — LangChain Expression Language

---

## 🔵 Simple Definition (English)
LCEL is the declarative way to build chains in LangChain: connect Runnables with the pipe `|` (`prompt | model | parser`). The result is also a Runnable with built-in `invoke`, `ainvoke`, `stream`, `batch`, retries, fallbacks and tracing.

## 🔵 सरल परिभाषा (Hindi)
LCEL LangChain में chains बनाने का declarative तरीका है: Runnables को pipe `|` से जोड़ो (`prompt | model | parser`)। नतीजा भी एक Runnable होता है जिसमें `invoke`, `ainvoke`, `stream`, `batch`, retries, fallbacks और tracing अपने-आप मिलते हैं।

---

## 🔴 Problem it Solves
Legacy chains (`LLMChain`, `SequentialChain`) were class-heavy, hard to stream, hard to make async, and hid what was sent to the LLM. Every new feature (streaming, batching, parallelism) needed code per chain class. LCEL gives these for free to any composition.

## 🔴 यह क्यों बना? (Hindi)
पुराने chains (`LLMChain`, `SequentialChain`) class-heavy थे, streaming और async कठिन थे, और LLM को क्या भेजा जा रहा है यह छिपा रहता था। हर नई feature के लिए हर chain class में code लिखना पड़ता था। LCEL किसी भी composition को ये सब मुफ्त देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Each component is a Runnable (prompt, model, parser, retriever, function)
Step 2 → A | B creates RunnableSequence([A, B]); output of A -> input of B
Step 3 → A dict {"x": r1, "y": r2} becomes RunnableParallel (runs r1, r2 together)
Step 4 → A plain function in a chain is auto-wrapped as RunnableLambda
Step 5 → chain.invoke(input) runs sync; ainvoke async; stream yields chunks
Step 6 → chain.batch([...]) runs many inputs concurrently
Step 7 → .with_retry / .with_fallbacks / .with_config add resilience + tracing
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर component Runnable है (prompt, model, parser, retriever, function)
Step 2 → A | B = RunnableSequence([A, B]); A का output -> B का input
Step 3 → dict {"x": r1, "y": r2} = RunnableParallel (दोनों साथ चलते हैं)
Step 4 → chain में सादा function अपने-आप RunnableLambda बनता है
Step 5 → invoke sync; ainvoke async; stream chunks देता है
Step 6 → batch([...]) कई inputs concurrently चलाता है
Step 7 → .with_retry / .with_fallbacks / .with_config से resilience + tracing
```

---

## 🟡 Real World Example
**Tariff Classification System**:
`{"context": retriever | format_docs, "product": RunnablePassthrough()} | prompt | llm | parser`. The same chain serves a normal API call (`ainvoke`), a streaming UI (`astream`), and a nightly bulk job (`abatch`) with no code change. **Zomato AI**: streaming tokens to the chat UI for a "recommend dinner" chain.

## 🟡 Real Example Hindi mein
**Tariff System**: `{"context": retriever | format_docs, "product": RunnablePassthrough()} | prompt | llm | parser`। यही chain normal API call (`ainvoke`), streaming UI (`astream`) और रात की bulk job (`abatch`) तीनों में बिना code बदले चलती है।

---

## 💻 Code Example — Basic
```python
# Runs offline (langchain-core only): a full LCEL chain with a fake model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("Context: {context}\nQuestion: {question}")  # 2 variables

def fake_retriever(q: str) -> str:
    return "HS 8518: headphones and earphones"  # pretend retrieval

def fake_llm(p) -> str:
    return "Answer: 8518.30 (based on) " + p.to_string().splitlines()[0]  # pretend LLM

chain = (
    {"context": RunnableLambda(fake_retriever), "question": RunnablePassthrough()}  # parallel dict
    | prompt  # fills template
    | RunnableLambda(fake_llm)  # model step
    | StrOutputParser()  # string out
)

print(chain.invoke("HS code for earbuds?"))  # sync
print(chain.batch(["earbuds?", "shoes?"]))  # batch of two
for chunk in chain.stream("earbuds?"):  # streaming works (single chunk here)
    print("chunk:", chunk)
```

## 💻 Code Example — Advanced
```python
# Production LCEL: retrieval + structured output + retry + fallback + async + token logging
import asyncio
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_openai import ChatOpenAI

class Answer(BaseModel):
    hs_code: str
    confidence: float = Field(ge=0, le=1)
    sources: list[str]

def format_docs(docs) -> str:
    return "\n\n".join(f"[{d.metadata.get('id','?')}] {d.page_content}" for d in docs)  # docs -> text

def build(retriever) -> RunnableLambda:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Use only the context. Cite ids."),
        ("human", "Context:\n{context}\n\nProduct: {question}"),
    ])
    main = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    backup = ChatOpenAI(model="gpt-4o", temperature=0)  # stronger fallback
    llm = main.with_retry(stop_after_attempt=3).with_fallbacks([backup])  # resilience
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm.with_structured_output(Answer)  # typed output
    )

async def run(chain, product: str) -> tuple[Answer | None, dict]:
    usage = UsageMetadataCallbackHandler()  # collects token usage
    try:
        ans = await chain.ainvoke(product, config={"callbacks": [usage], "tags": ["tariff"]})
        return ans, usage.usage_metadata  # tokens per model name
    except Exception as exc:
        print("chain failed:", exc)
        return None, {}
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()
text_chain = ...  # prompt | llm | StrOutputParser() built at startup

@app.get("/stream")
async def stream(q: str) -> StreamingResponse:
    async def gen():
        async for chunk in text_chain.astream(q):  # LCEL gives streaming for free
            yield chunk  # send token pieces
    return StreamingResponse(gen(), media_type="text/plain")
```

---

## 🔗 LangChain / LangGraph Connection
LCEL chains are Runnables, so they plug straight into LangGraph as nodes. Use LCEL for linear, stateless pipelines, and LangGraph when you need loops, branching, or state. `chain.get_graph().print_ascii()` shows the structure (needs `grandalf`).

```python
# graph.add_node("classify", chain)   # LCEL chain as a LangGraph node
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing a str where the prompt needs a dict
```python
# Wrong
(prompt | llm).invoke("earbuds")     # prompt expects {"product": ...}
# Right
(prompt | llm).invoke({"product": "earbuds"})
```

❌ Mistake 2: Blocking calls inside async chains
```python
# Wrong: RunnableLambda(lambda x: requests.get(...).text)   # blocks event loop
# Right: async def fetch(x): ... ; RunnableLambda(fetch)   # or use httpx.AsyncClient
```

---

## 🧠 Tricky Interview Question
**Q**: "`{'a': r1, 'b': r2} | prompt` - is it sequential or parallel, and why does it matter?"

**Answer**: The dict becomes `RunnableParallel`: r1 and r2 run concurrently (threads for sync, `asyncio.gather` for async), both receive the same input, and the outputs are merged into one dict. It matters for latency (retriever + another lookup in parallel) and for correctness: neither branch can see the other's output.

---

## ⚫ Interview Questions + Answers

Q1: What does `|` do? (Easy)
A1: Calls `Runnable.__or__` to create a `RunnableSequence` where each output feeds the next input.

Q2: What methods does every LCEL chain have? (Easy)
A2: `invoke`, `ainvoke`, `stream`, `astream`, `batch`, `abatch`, plus `astream_events` and `astream_log`.

Q3: How is a Python function used in a chain? (Medium)
A3: Wrap with `RunnableLambda` (or put it in a chain and LCEL coerces it). Use `@chain` decorator for custom runnables.

Q4: How do you add retries and fallbacks? (Medium)
A4: `.with_retry(stop_after_attempt=3)` and `.with_fallbacks([other])` on any Runnable.

Q5: When is LCEL the wrong tool? (Hard)
A5: When you need cycles, durable state, human approval, or dynamic routing across many steps: use LangGraph. Very dynamic control flow in LCEL becomes unreadable; LCEL excels at DAG-shaped, stateless pipelines.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Linear pipelines: prompt -> model -> parser, RAG
- You want streaming, batch, async for free

❌ Avoid when:
- Loops, complex state, agents (use LangGraph)

---

## 📊 Visual Diagram
```
 input ─► {"context": retriever|fmt , "question": passthrough}
                      │  (RunnableParallel)
                      ▼
                   prompt ─► llm ─► parser ─► output
 Same object supports: invoke / ainvoke / stream / batch
```

---

## 💰 Cost Impact
LCEL does not add tokens by itself. It helps cost by: `batch` with `max_concurrency` (control rate), caching (`set_llm_cache`), streaming for perceived speed, and fallbacks that use a cheap model first. Watch for retries: each retry resends the full prompt, so cap `stop_after_attempt`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LCEL | Pipe-style chain syntax | Pipe वाली chain syntax |
| RunnableSequence | A | B | B | क्रम में चलने वाला chain |
| RunnableParallel | Dict of runnables | साथ चलने वाले runnables |
| astream | Async token stream | Async streaming |
| Fallback | Backup runnable | बैकअप |

---

## ⚡ 3-Line Summary
English: LCEL composes Runnables with `|` into chains that automatically support sync, async, streaming and batch. Dicts run branches in parallel. Add retries and fallbacks with one method call.
Hindi: LCEL `|` से Runnables जोड़ता है और chain में sync, async, streaming, batch अपने-आप आते हैं। Dict की branches parallel चलती हैं। Retries और fallbacks एक method call से जुड़ते हैं।

---

## ➡️ Next Topic
**236. Runnable Interface** — the common contract behind every LCEL component.
