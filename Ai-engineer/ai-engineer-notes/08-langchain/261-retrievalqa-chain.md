---

# 261. RetrievalQA Chain
# हिंदी में: RetrievalQA Chain (Legacy RAG Chain)

---

## 🔵 Simple Definition (English)
`RetrievalQA` is a legacy LangChain chain that does simple RAG in one object: take a question, fetch documents with a retriever, stuff them into a prompt, and ask the LLM. It returns `result` and, optionally, `source_documents`. The modern replacement is `create_retrieval_chain` with `create_stuff_documents_chain`, or plain LCEL.

## 🔵 सरल परिभाषा (Hindi)
`RetrievalQA` LangChain की legacy chain है जो एक ही object में simple RAG करती है: सवाल लो, retriever से documents लाओ, उन्हें prompt में डालो और LLM से पूछो। ये `result` और चाहें तो `source_documents` लौटाती है। आधुनिक विकल्प है `create_retrieval_chain` + `create_stuff_documents_chain`, या सादा LCEL।

---

## 🔴 Problem it Solves
- Every RAG app repeated: retrieve, format context, prompt, generate.
- Beginners needed a quick way to ask questions over their documents.
- RetrievalQA packaged this into one call with four `chain_type` options.

## 🔴 यह क्यों बना? (Hindi)
- हर RAG app यही दोहराता था: retrieve, context format, prompt, generate।
- नए लोगों को अपने documents पर सवाल पूछने का तेज़ तरीका चाहिए था।
- RetrievalQA ने इसे एक call में बाँधा और चार `chain_type` विकल्प दिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a retriever: vectorstore.as_retriever(search_kwargs={"k": 4})
Step 2 → qa = RetrievalQA.from_chain_type(llm, retriever=retriever, chain_type="stuff")
Step 3 → qa.invoke({"query": "..."})
Step 4 → Retriever returns top-k Documents
Step 5 → "stuff": all documents pasted into ONE prompt (others: map_reduce, refine, map_rerank)
Step 6 → LLM answers using the context
Step 7 → Output: {"query", "result", "source_documents"} (if return_source_documents=True)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Retriever बनाओ: vectorstore.as_retriever(search_kwargs={"k": 4})
Step 2 → qa = RetrievalQA.from_chain_type(llm, retriever=retriever, chain_type="stuff")
Step 3 → qa.invoke({"query": "..."})
Step 4 → Retriever top-k Documents देता है
Step 5 → "stuff": सारे documents एक ही prompt में चिपकते हैं (दूसरे: map_reduce, refine, map_rerank)
Step 6 → LLM context से जवाब देता है
Step 7 → Output: {"query", "result", "source_documents"} (अगर return_source_documents=True)
```

---

## 🟡 Real World Example
**Tariff Classification System**: "What is the duty on lithium batteries?" The retriever pulls the 4 closest tariff chunks; the stuff chain puts them in one prompt; the answer cites chunk sources. A good fit for a simple first version.
**Amazon AI**: answer "does this product have a warranty?" from the product manual.

## 🟡 Real Example Hindi mein
**Tariff System**: "Lithium batteries पर duty कितनी है?" Retriever 4 सबसे पास के tariff chunks लाता है; stuff chain उन्हें एक prompt में रखती है; जवाब chunk sources के साथ आता है। पहले version के लिए अच्छा विकल्प।
**Amazon AI**: product manual से "क्या इसमें warranty है?" का जवाब।

---

## 💻 Code Example — Basic
```python
# Basic: what RetrievalQA (chain_type="stuff") does, in pure Python (runnable offline)
from typing import Dict, List

DOCS: List[Dict[str, str]] = [
    {"id": "d1", "text": "Lithium batteries (HS 8507.60) carry 10% duty."},
    {"id": "d2", "text": "Speakers (HS 8518.22) carry 20% duty."},
    {"id": "d3", "text": "Cotton shirts (HS 6205.20) carry 12% duty."},
]

def retrieve(query: str, k: int = 2) -> List[Dict[str, str]]:
    words = set(query.lower().split())
    # Score each doc by number of shared words (stand-in for vector similarity)
    scored = sorted(DOCS, key=lambda d: -len(words & set(d["text"].lower().split())))
    return scored[:k]

def stuff_prompt(question: str, docs: List[Dict[str, str]]) -> str:
    context = "\n".join(d["text"] for d in docs)          # "stuff" = paste all docs together
    return f"Use only this context.\n{context}\n\nQuestion: {question}\nAnswer:"

def fake_llm(prompt: str) -> str:
    # Pretend LLM: return the first context line mentioning duty
    for line in prompt.splitlines():
        if "duty" in line and "Question" not in line:
            return line
    return "I don't know"

def retrieval_qa(query: str) -> Dict[str, object]:
    docs = retrieve(query)                                 # step 4
    answer = fake_llm(stuff_prompt(query, docs))           # steps 5-6
    return {"query": query, "result": answer, "source_documents": [d["id"] for d in docs]}

if __name__ == "__main__":
    print(retrieval_qa("duty on lithium batteries"))
```

## 💻 Code Example — Advanced
```python
# Legacy RetrievalQA with custom prompt + sources, and its modern replacement (async, typed)
import asyncio
import warnings
from typing import Any

from langchain.chains import RetrievalQA                              # legacy
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain         # modern helper
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI

warnings.filterwarnings("ignore", category=DeprecationWarning)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=300)

def build(retriever: Any) -> tuple[Any, Any]:
    # ---------- LEGACY ----------
    legacy_prompt = PromptTemplate.from_template(
        "Answer using ONLY the context. If missing, say 'not found'.\n"
        "Context:\n{context}\n\nQuestion: {question}\nAnswer:")
    legacy = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True,                 # include the docs used
        chain_type_kwargs={"prompt": legacy_prompt},  # custom prompt
    )
    # ---------- MODERN ----------
    modern_prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer using ONLY the context. If missing, say 'not found'.\n\n{context}"),
        ("human", "{input}"),
    ])
    qa_chain = create_stuff_documents_chain(llm, modern_prompt)
    modern = create_retrieval_chain(retriever, qa_chain)   # returns {"input","context","answer"}
    return legacy, modern

async def ask(legacy: Any, modern: Any, question: str) -> dict[str, Any]:
    try:
        old = await legacy.ainvoke({"query": question})        # keys: query/result/source_documents
        new = await modern.ainvoke({"input": question})        # keys: input/context/answer
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    return {
        "legacy_answer": old["result"],
        "modern_answer": new["answer"],
        "sources": [d.metadata.get("source") for d in new["context"]],
    }

# retriever = your_vectorstore.as_retriever(search_kwargs={"k": 4})
# legacy, modern = build(retriever)
# print(asyncio.run(ask(legacy, modern, "Duty on lithium batteries?")))   # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
Build the chain once at startup (not per request) and call it asynchronously.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

state: dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # retriever = load_vectorstore().as_retriever(search_kwargs={"k": 4})
    # state["legacy"], state["modern"] = build(retriever)
    yield

app = FastAPI(lifespan=lifespan)

class Q(BaseModel):
    question: str = Field(min_length=3, max_length=1000)

@app.post("/ask")
async def ask_route(q: Q) -> dict:
    result = await state["modern"].ainvoke({"input": q.question})
    if not result.get("answer"):
        raise HTTPException(status_code=502, detail="empty answer")
    return {"answer": result["answer"],
            "sources": [d.metadata.get("source") for d in result["context"]]}
```

---

## 🔗 LangChain / LangGraph Connection
RetrievalQA is deprecated; LangChain docs migrate it to `create_retrieval_chain` or custom LCEL (see 263). For retrieval with branching (grade the docs, rewrite the query, retry) build a LangGraph `StateGraph` with `retrieve`, `grade`, `generate` nodes: this is the base of corrective and agentic RAG.

```python
# LCEL form (no helpers needed)
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser

def fmt(docs: list) -> str:
    return "\n\n".join(d.page_content for d in docs)

lcel = (
    {"context": itemgetter("input") | retriever | fmt, "input": itemgetter("input")}
    | modern_prompt | llm | StrOutputParser()
)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Wrong input key.
✅ Correct: RetrievalQA wants `query`; `create_retrieval_chain` wants `input`.

```python
# Wrong
qa.invoke({"question": "Duty?"})        # KeyError / missing 'query'
# Right
qa.invoke({"query": "Duty?"})
```

❌ Mistake 2: Using `chain_type="stuff"` with a large `k` and big chunks (context overflow).
✅ Correct: Limit `k`, chunk size, or use `map_reduce` for many documents.

❌ Mistake 3: Custom prompt without `{context}` and `{question}` variables.
✅ Correct: The prompt must contain both names.

---

## 🧠 Tricky Interview Question
**Q**: "RetrievalQA gives confident answers even when the document has no answer. How do you stop this?"

**Answer**: The LLM fills gaps from its own knowledge. Add a strict prompt ("answer only from context, otherwise say 'not found'"), temperature 0, and check retrieval relevance: use `similarity_score_threshold` retrievers so weak matches return nothing, and handle empty context before calling the LLM. Return `source_documents` so users can verify, and evaluate with unanswerable questions. For stronger control, use a graph that grades documents first (Corrective RAG).

---

## ⚫ Interview Questions + Answers

Q1: What does RetrievalQA return?
A1: A dict with `query`, `result`, and `source_documents` if `return_source_documents=True`.

Q2: Name the `chain_type` options.
A2: `stuff` (all docs in one prompt), `map_reduce` (answer per doc, then combine), `refine` (iteratively improve the answer), `map_rerank` (score each answer, pick best).

Q3: When is `stuff` a bad choice?
A3: When retrieved documents exceed the context window or you want to reduce cost with many chunks.

Q4: Why is RetrievalQA deprecated?
A4: Opaque, limited customization, no chat history, inconsistent keys, weak streaming. `create_retrieval_chain` and LCEL are explicit and composable.

Q5: How do you add source citations and streaming when migrating?
A5: With `create_retrieval_chain`, the output already includes `context` (the documents) so you can list sources. Stream with `chain.astream`, which yields partial dicts containing `answer` chunks. Add `metadata` (file, page) during indexing so citations are meaningful.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Maintaining an old app
- Quick one-turn Q&A demo

❌ Avoid when:
- New projects (use `create_retrieval_chain`/LCEL)
- You need chat history, grading, or routing
- You need fine control over streaming and retries

---

## 📊 Visual Diagram
```
 {"query"} ──► Retriever ──► top-k Documents
                                   │
                    ┌──────────────▼───────────────┐
                    │ stuff: system + context + Q  │──► LLM ──► result
                    └──────────────────────────────┘
 Output: {"query": ..., "result": ..., "source_documents": [...]}
```

---

## 💰 Cost Impact
- Input tokens = prompt template (~60) + k chunks x chunk size + question. Example: 4 chunks x 300 tokens = ~1260 tokens in, ~150 out. On gpt-4o-mini that is about $0.00028 per query.
- `map_reduce` and `refine` make one LLM call per document: cost and latency multiply.
- Optimise: smaller `k`, smaller chunks, rerank then keep the best 3, compress context, `max_tokens`, cache frequent questions.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RetrievalQA | Legacy retrieve + answer chain | पुरानी retrieve + answer chain |
| chain_type | How docs are combined | Documents जोड़ने का तरीका |
| stuff | All docs in one prompt | सब docs एक prompt में |
| map_reduce | Per-doc answers, then merged | हर doc पर जवाब, फिर मिलाना |
| source_documents | Docs used for the answer | जवाब में इस्तेमाल हुए docs |
| create_retrieval_chain | Modern replacement | आधुनिक विकल्प |

---

## ⚡ 3-Line Summary
English: RetrievalQA is the legacy one-call RAG chain: retriever, stuff documents in a prompt, answer with sources. It is deprecated in favour of create_retrieval_chain and LCEL. Use strict prompts and score thresholds to avoid made-up answers.
Hindi: RetrievalQA legacy एक-call RAG chain है: retriever, documents को prompt में डालना, sources के साथ जवाब। इसकी जगह create_retrieval_chain और LCEL आ गए हैं। बनावटी जवाबों से बचने के लिए सख़्त prompt और score threshold रखो।

---

## ➡️ Next Topic
**262. ConversationalRetrievalChain**: RetrievalQA plus chat history for follow-up questions.
