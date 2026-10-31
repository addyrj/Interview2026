---

# 238. RunnablePassthrough
# हिंदी में: RunnablePassthrough

---

## 🔵 Simple Definition (English)
`RunnablePassthrough` returns its input unchanged. It is used inside a dict (RunnableParallel) to carry the original user input forward next to computed values, and `RunnablePassthrough.assign(...)` adds new keys to a dict while keeping existing ones.

## 🔵 सरल परिभाषा (Hindi)
`RunnablePassthrough` अपना input जैसा है वैसा लौटा देता है। इसे dict (RunnableParallel) के अंदर इस्तेमाल करते हैं ताकि मूल user input computed values के साथ आगे जाए। `RunnablePassthrough.assign(...)` dict में नई keys जोड़ता है और पुरानी रखता है।

---

## 🔴 Problem it Solves
In RAG, the prompt needs both `context` (computed by retriever) and the `question` (original input). Pipes pass only ONE value. Without passthrough, the question is lost after retrieval. Passthrough keeps the original while other branches compute.

## 🔴 यह क्यों बना? (Hindi)
RAG में prompt को `context` (retriever से) और `question` (मूल input) दोनों चाहिए। Pipe सिर्फ एक value आगे ले जाता है। Passthrough के बिना retrieval के बाद question खो जाता है। Passthrough मूल value रखता है जबकि बाकी branches compute करती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Input arrives:  "HS code for earbuds?"
Step 2 → Dict {"context": retriever, "question": RunnablePassthrough()}
Step 3 → Both branches get the SAME input and run in parallel
Step 4 → retriever branch -> docs; passthrough branch -> original string
Step 5 → Result dict {"context": docs, "question": "HS code..."} goes to prompt
Step 6 → .assign(new=fn) on a dict input: returns input + {"new": fn(input)}
Step 7 → Chain steps can keep adding keys: assign(a=..).assign(b=..)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Input आता है: "HS code for earbuds?"
Step 2 → Dict {"context": retriever, "question": RunnablePassthrough()}
Step 3 → दोनों branches को वही input मिलता है और parallel चलती हैं
Step 4 → retriever branch -> docs; passthrough branch -> मूल string
Step 5 → {"context": docs, "question": "..."} prompt में जाता है
Step 6 → dict input पर .assign(new=fn): input + {"new": fn(input)}
Step 7 → assign(a=..).assign(b=..) से keys बढ़ती रहती हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: the final API response should include the retrieved sources next to the answer. `RunnablePassthrough.assign(context=retriever_chain).assign(answer=prompt|llm|parser)` returns `{"question":..., "context":[docs], "answer":...}` so the API can return citations. **Zomato**: keep `user_id` flowing through all steps while computing `menu_items`.

## 🟡 Real Example Hindi mein
**Tariff System**: API response में answer के साथ retrieved sources भी चाहिए। `RunnablePassthrough.assign(context=retriever_chain).assign(answer=prompt|llm|parser)` लौटाता है `{"question":..., "context":[docs], "answer":...}` ताकि API citations दे सके। **Zomato**: `user_id` सभी steps में बहता रहे जबकि `menu_items` compute हों।

---

## 💻 Code Example — Basic
```python
# Runs offline
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# 1) Plain passthrough:
print(RunnablePassthrough().invoke("same"))  # same

# 2) Next to a computed branch:
fake_retriever = RunnableLambda(lambda q: ["HS 8518 headphones"])  # returns a list of docs
step = {"context": fake_retriever, "question": RunnablePassthrough()}  # parallel
print(step | RunnableLambda(lambda d: d)) if False else None  # (dict needs a Runnable partner to pipe)
from langchain_core.runnables import RunnableParallel
print(RunnableParallel(step).invoke("earbuds?"))  # {'context': [...], 'question': 'earbuds?'}

# 3) assign: keep existing keys + add new ones
chain = RunnablePassthrough.assign(
    length=lambda d: len(d["text"]),  # new key from function
    upper=lambda d: d["text"].upper(),  # another new key
)
print(chain.invoke({"text": "tariff"}))  # {'text': 'tariff', 'length': 6, 'upper': 'TARIFF'}
```

## 💻 Code Example — Advanced
```python
# RAG that returns answer + sources, async, using assign
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template("Context:\n{context}\n\nQ: {question}\nAnswer briefly with ids.")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def fmt(docs) -> str:
    return "\n".join(f"[{d.metadata.get('id')}] {d.page_content}" for d in docs)  # docs -> text

def build(retriever):
    return (
        {"question": RunnablePassthrough()}                      # input is a plain string
        | RunnablePassthrough.assign(docs=itemgetter("question") | retriever)   # add docs
        | RunnablePassthrough.assign(
            answer=(
                RunnableLambda(lambda d: {"context": fmt(d["docs"]), "question": d["question"]})
                | prompt | llm | StrOutputParser()
            )
        )
        | RunnableLambda(lambda d: {  # final shape for the API
            "answer": d["answer"],
            "sources": [x.metadata.get("id") for x in d["docs"]],
        })
    )

async def ask(chain, q: str) -> dict:
    try:
        return await chain.ainvoke(q)
    except Exception as exc:
        return {"answer": None, "sources": [], "error": str(exc)}
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Q(BaseModel):
    question: str

@app.post("/rag")
async def rag(body: Q) -> dict:
    return await ask(app.state.chain, body.question)  # {"answer":..., "sources":[...]}
```

---

## 🔗 LangChain / LangGraph Connection
Standard LCEL RAG recipes use passthrough. In LangGraph, state already carries all keys, so passthrough is less needed: each node returns only the keys it updates and other keys persist automatically.

```python
# LangGraph: def retrieve(state): return {"docs": retriever.invoke(state["question"])}  # question stays in state
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Losing the question after retrieval
```python
# Wrong
chain = retriever | prompt | llm      # prompt needs {question} too
# Right
chain = {"context": retriever | fmt, "question": RunnablePassthrough()} | prompt | llm
```

❌ Mistake 2: Using `assign` on a non-dict input
```python
# Wrong: RunnablePassthrough.assign(x=...).invoke("text")   # input must be a dict
# Right: first wrap: {"question": RunnablePassthrough()} | RunnablePassthrough.assign(...)
```

---

## 🧠 Tricky Interview Question
**Q**: "In `{'context': retriever, 'question': RunnablePassthrough()}` does the retriever run before or after the passthrough?"

**Answer**: Neither: dict branches are a RunnableParallel, executing concurrently with the same input. Passthrough does no work, so effectively the retriever dominates latency. Do not assume branch order or that one branch can see another's output; use `assign` sequentially when the second needs the first.

---

## ⚫ Interview Questions + Answers

Q1: What does RunnablePassthrough do? (Easy)
A1: Returns its input unchanged.

Q2: Why use it in RAG? (Easy)
A2: To pass the original question to the prompt alongside retrieved context.

Q3: What does `.assign()` do? (Medium)
A3: For dict inputs, runs given runnables on the dict and merges the results as new keys with the original keys.

Q4: `itemgetter` vs lambda? (Medium)
A4: `itemgetter("k")` is a fast, readable key extractor that LCEL coerces into a Runnable; lambdas work too but are opaque in traces.

Q5: How do you return both sources and answer from RAG? (Hard)
A5: Start with `{"question": RunnablePassthrough()}`, `assign(docs=...)`, `assign(answer=...)`, then map to the final response shape; the docs flow forward since assign preserves keys.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need the original input and computed values together
- Returning intermediate results (sources) with the final answer

❌ Avoid when:
- LangGraph state already holds everything

---

## 📊 Visual Diagram
```
                 "earbuds?"
                     │
        ┌────────────┴─────────────┐
        ▼                          ▼
   retriever ─► docs        RunnablePassthrough ─► "earbuds?"
        └────────────┬─────────────┘
                     ▼
     {"context": docs, "question": "earbuds?"} ─► prompt ─► llm
```

---

## 💰 Cost Impact
Passthrough is free (no tokens). It enables patterns that save money: returning cached `docs` for reuse in follow-up steps instead of re-retrieving, and avoiding a second LLM call just to restate the question. But careful: carrying big `docs` through many steps can accidentally enter prompts, so select only needed keys before the prompt.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Passthrough | Return input unchanged | Input जस का तस |
| assign | Add keys to dict | Dict में keys जोड़ना |
| itemgetter | Pick a dict key | Key निकालना |
| RunnableParallel | Run branches together | Branches साथ-साथ |
| Context | Retrieved text | Retrieve किया text |

---

## ⚡ 3-Line Summary
English: RunnablePassthrough forwards its input unchanged, typically beside a retriever branch. `.assign()` adds computed keys while keeping existing ones. Together they let RAG return answer plus sources.
Hindi: RunnablePassthrough input को जस का तस आगे भेजता है, आमतौर पर retriever के साथ। `.assign()` पुरानी keys रखकर नई जोड़ता है। दोनों से RAG answer के साथ sources भी लौटाता है।

---

## ➡️ Next Topic
**239. RunnableParallel** — running independent branches concurrently.
