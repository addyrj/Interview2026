---

# 263. LCEL RAG Chain
# हिंदी में: LCEL RAG Chain (Pipe वाला RAG)

---

## 🔵 Simple Definition (English)
An LCEL RAG chain builds a full RAG pipeline with LangChain Expression Language pipes: `{"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()`. It is transparent, supports streaming, async, batching and tracing by default, and is the modern way to write RAG in LangChain.

## 🔵 सरल परिभाषा (Hindi)
LCEL RAG chain पूरा RAG pipeline LangChain Expression Language के pipes से बनाती है: `{"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()`। ये पारदर्शी है, और streaming, async, batching, tracing अपने आप देती है। LangChain में RAG लिखने का आधुनिक तरीका यही है।

---

## 🔴 Problem it Solves
- Legacy RetrievalQA hid the prompt, the context formatting, and the steps.
- Hard to add sources, streaming, or custom steps.
- Different chain classes had different input and output keys.
- LCEL gives one composable interface (`Runnable`) for every step.

## 🔴 यह क्यों बना? (Hindi)
- Legacy RetrievalQA ने prompt, context formatting और steps छिपा रखे थे।
- Sources, streaming या custom steps जोड़ना कठिन था।
- अलग chain classes की input/output keys अलग थीं।
- LCEL हर step के लिए एक ही composable interface (`Runnable`) देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Input: the question string
Step 2 → RunnableParallel builds a dict: context (retriever → format) and question (passthrough)
Step 3 → retriever returns Documents; format_docs joins them into text (with source tags)
Step 4 → ChatPromptTemplate fills {context} and {question}
Step 5 → ChatModel generates the answer
Step 6 → StrOutputParser turns the AIMessage into a plain string
Step 7 → chain.invoke / ainvoke / stream / batch all work with no extra code
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Input: सवाल (string)
Step 2 → RunnableParallel dict बनाता है: context (retriever → format) और question (passthrough)
Step 3 → retriever Documents देता है; format_docs उन्हें (source tags के साथ) text में जोड़ता है
Step 4 → ChatPromptTemplate {context} और {question} भरता है
Step 5 → ChatModel जवाब generate करता है
Step 6 → StrOutputParser AIMessage को सादी string बनाता है
Step 7 → chain.invoke / ainvoke / stream / batch बिना अतिरिक्त code के चलते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: The whole `/ask` endpoint is one chain: retrieve 4 tariff chunks, format them with `[source: tariff_2024.pdf p.12]`, answer with citations, and stream tokens to the UI.
**Zomato AI**: "Best dessert places near me" retrieves restaurant reviews and answers; streaming makes the chat feel fast.

## 🟡 Real Example Hindi mein
**Tariff System**: पूरा `/ask` endpoint एक chain है: 4 tariff chunks retrieve करो, उन्हें `[source: tariff_2024.pdf p.12]` के साथ format करो, citations के साथ जवाब दो, और tokens UI पर stream करो।
**Zomato AI**: "पास के सबसे अच्छे dessert places" पर restaurant reviews retrieve होते हैं और जवाब बनता है; streaming से chat तेज़ लगती है।

---

## 💻 Code Example — Basic
```python
# Basic: LCEL-style pipes in pure Python (a tiny Runnable clone, runnable offline)
from typing import Any, Callable, Dict, List

class Step:
    """Minimal Runnable: wraps a function and supports the | operator."""
    def __init__(self, fn: Callable[[Any], Any]) -> None:
        self.fn = fn
    def __or__(self, other: "Step") -> "Step":
        return Step(lambda x: other.fn(self.fn(x)))        # run self, feed result to other
    def invoke(self, x: Any) -> Any:
        return self.fn(x)

DOCS = ["Lithium batteries: HS 8507.60, duty 10%.", "Speakers: HS 8518.22, duty 20%."]

retriever = Step(lambda q: [d for d in DOCS if any(w in d.lower() for w in q.lower().split())])
format_docs = Step(lambda docs: "\n".join(docs))           # join docs into one string
to_prompt = Step(lambda ctx: f"Context:\n{ctx}\nAnswer briefly.")   # fill the prompt
fake_llm = Step(lambda p: p.splitlines()[1] if len(p.splitlines()) > 1 else "not found")

chain = retriever | format_docs | to_prompt | fake_llm     # same shape as LCEL

if __name__ == "__main__":
    print(chain.invoke("speakers duty"))                   # Speakers: HS 8518.22, duty 20%.
    # Real LCEL: chain = {"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
```

## 💻 Code Example — Advanced
```python
# Production LCEL RAG: sources returned, streaming, async, error handling
import asyncio
from operator import itemgetter
from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

def format_docs(docs: list[Document]) -> str:
    """Join chunks and tag each with its source so the model can cite it."""
    return "\n\n".join(f"[{d.metadata.get('source', 'unknown')}] {d.page_content}" for d in docs)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer ONLY from the context. Cite sources in [brackets]. "
               "If the answer is not in the context, say 'not found'.\n\nContext:\n{context}"),
    ("human", "{question}"),
])
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=300)

def build_chain(retriever: Any) -> Any:
    answer_chain = (
        RunnablePassthrough.assign(context=lambda x: format_docs(x["docs"]))   # text for the prompt
        | prompt | llm | StrOutputParser()
    )
    # RunnableParallel keeps the docs AND the answer so the API can return sources
    return (
        RunnableParallel(docs=itemgetter("question") | retriever,    # retrieve once
                         question=itemgetter("question"))
        .assign(answer=answer_chain)                                 # add the generated answer
    )

async def ask(chain: Any, question: str) -> dict[str, Any]:
    try:
        out = await chain.ainvoke({"question": question})            # {"docs", "question", "answer"}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    return {"answer": out["answer"], "sources": [d.metadata.get("source") for d in out["docs"]]}

async def stream_answer(chain: Any, question: str) -> None:
    async for chunk in chain.astream({"question": question}):        # dict chunks
        if "answer" in chunk:
            print(chunk["answer"], end="", flush=True)                # print tokens as they arrive

async def demo() -> None:
    store = InMemoryVectorStore(OpenAIEmbeddings(model="text-embedding-3-small"))
    store.add_documents([
        Document(page_content="Lithium batteries: HS 8507.60, duty 10%.", metadata={"source": "tariff.pdf p1"}),
        Document(page_content="Speakers: HS 8518.22, duty 20%.", metadata={"source": "tariff.pdf p2"}),
    ])
    chain = build_chain(store.as_retriever(search_kwargs={"k": 2}))
    print(await ask(chain, "What is the duty on speakers?"))

if __name__ == "__main__":
    asyncio.run(demo())   # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
Build the chain once; expose both a JSON endpoint and an SSE streaming endpoint.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI()
rag_chain: Any = None          # rag_chain = build_chain(retriever) at startup

class Q(BaseModel):
    question: str = Field(min_length=3, max_length=1000)

@app.post("/ask")
async def ask_route(q: Q) -> dict:
    return await ask(rag_chain, q.question)

@app.post("/ask/stream")
async def ask_stream(q: Q) -> StreamingResponse:
    async def gen():
        async for chunk in rag_chain.astream({"question": q.question}):
            if "answer" in chunk:                         # only forward answer tokens
                yield f"data: {chunk['answer']}\n\n"      # Server-Sent Events format
    return StreamingResponse(gen(), media_type="text/event-stream")
```

---

## 🔗 LangChain / LangGraph Connection
LCEL is the core of modern LangChain; every `Runnable` can become a **LangGraph node**. When the flow needs loops (retry retrieval), conditional routing, or human approval, wrap the same pieces in a `StateGraph`. LangSmith traces each LCEL step automatically.

```python
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

class S(TypedDict, total=False):
    question: str
    docs: list
    answer: str

def retrieve_node(s: S) -> S:
    return {"docs": retriever.invoke(s["question"])}              # same retriever as LCEL
def generate_node(s: S) -> S:
    ans = (prompt | llm | StrOutputParser()).invoke(
        {"context": format_docs(s["docs"]), "question": s["question"]})
    return {"answer": ans}

g = StateGraph(S)
g.add_node("retrieve", retrieve_node); g.add_node("generate", generate_node)
g.add_edge(START, "retrieve"); g.add_edge("retrieve", "generate"); g.add_edge("generate", END)
graph = g.compile()
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Passing the retriever's raw documents into the prompt (prints `Document(...)` objects).
✅ Correct: Format docs into a string.

```python
# Wrong
{"context": retriever, "question": RunnablePassthrough()} | prompt | llm
# Right
{"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm
```

❌ Mistake 2: Retrieving twice (once for the answer, once for sources).
✅ Correct: Retrieve once and carry the docs (RunnableParallel + assign).

❌ Mistake 3: Using a sync retriever or `invoke` inside async routes (blocks the event loop).
✅ Correct: Use `ainvoke` / `astream`.

---

## 🧠 Tricky Interview Question
**Q**: "In your LCEL RAG chain the input is a string, but you now need to pass `question` and `language`. The chain breaks with 'expected string'. Why?"

**Answer**: `RunnablePassthrough()` forwards the whole input. When input becomes a dict, `retriever` receives a dict instead of a string. Use `itemgetter("question") | retriever` for retrieval and `itemgetter("language")` for the prompt variable. LCEL passes exactly what the previous step outputs, so the shape of data at each pipe must be tracked. Use `chain.get_graph().print_ascii()` or LangSmith traces to inspect.

---

## ⚫ Interview Questions + Answers

Q1: What is LCEL?
A1: LangChain Expression Language: compose `Runnable`s using the `|` operator into chains with built-in sync/async/stream/batch.

Q2: What does `RunnablePassthrough` do?
A2: Passes its input through unchanged, often used to keep the original question beside retrieved context.

Q3: How do you return sources with an LCEL RAG chain?
A3: Use `RunnableParallel` (or `.assign`) to keep `docs` next to the generated answer, then return metadata from the docs.

Q4: How does streaming work in LCEL RAG?
A4: `chain.astream(...)` yields output chunks as the LLM generates them; `StrOutputParser` supports streaming, so you can forward tokens to the client.

Q5: How would you make an LCEL RAG chain production-ready?
A5: Build once at startup; use async; add timeouts, `.with_retry()` and `.with_fallbacks()` (cheaper or backup model); score-threshold retrieval with empty-context handling; strict citation prompt; caching; LangSmith tracing; evaluation sets for faithfulness; token and latency metrics; and rate limits per user.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Straight pipelines: retrieve, prompt, generate
- You need streaming, async, batch for free
- Teams want readable, debuggable chains

❌ Avoid when:
- Flows need loops, retries by state, or human steps (use LangGraph)
- Heavy branching logic (graphs are clearer)

---

## 📊 Visual Diagram
```
                  ┌─► retriever ─► format_docs ─┐
 question ────────┤                             ├─► prompt ─► LLM ─► StrOutputParser ─► answer
                  └─► RunnablePassthrough ──────┘
                        (RunnableParallel builds {"context", "question"})
```

---

## 💰 Cost Impact
- One LLM call per question: input = prompt (~80 tokens) + k chunks (e.g. 4 x 300) + question; output capped by `max_tokens`.
- About 1300 input + 150 output tokens = ~$0.0003 on gpt-4o-mini.
- Optimise: smaller `k` with a reranker, chunk compression, `max_tokens`, response caching (`set_llm_cache`), semantic cache for repeated questions, fallback to a cheaper model for simple queries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LCEL | Pipe-based chain language | Pipe वाली chain भाषा |
| Runnable | Standard component interface | मानक component interface |
| RunnablePassthrough | Forwards input unchanged | Input जस का तस आगे भेजता है |
| RunnableParallel | Runs branches, returns dict | शाखाएँ चलाकर dict देता है |
| format_docs | Turns Documents into text | Documents को text बनाना |
| StrOutputParser | Message to string | Message को string बनाना |

---

## ⚡ 3-Line Summary
English: An LCEL RAG chain pipes retriever, prompt, model and parser into one transparent Runnable. It gives streaming, async, batching and tracing for free, and can return sources via RunnableParallel. Move to LangGraph when you need loops or complex routing.
Hindi: LCEL RAG chain retriever, prompt, model और parser को एक पारदर्शी Runnable में जोड़ती है। Streaming, async, batching और tracing मुफ़्त मिलते हैं, और RunnableParallel से sources भी लौटते हैं। Loops या जटिल routing चाहिए तो LangGraph पर जाओ।

---

## ➡️ Next Topic
**264. Callbacks in LangChain**: hook into chain events to log, trace, and count tokens.
