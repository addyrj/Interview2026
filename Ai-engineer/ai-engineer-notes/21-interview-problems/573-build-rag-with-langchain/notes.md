---

# 573. Build RAG with LangChain
# हिंदी में: LangChain के साथ RAG बनाना

---

## 🔵 Simple Definition (English)
Building RAG with LangChain means composing ready-made parts (text splitter, embeddings, vector store, retriever, prompt, chat model, output parser) into one pipeline using LCEL, the `|` pipe syntax. You write about 20 lines instead of hundreds.

## 🔵 सरल परिभाषा (Hindi)
LangChain से RAG बनाने का मतलब तैयार हिस्सों (text splitter, embeddings, vector store, retriever, prompt, chat model, output parser) को LCEL की `|` pipe syntax से एक pipeline में जोड़ना है। सैकड़ों lines की जगह लगभग 20 lines लिखनी पड़ती हैं।

---

## 🔴 Problem it Solves
Hand-written RAG (572) repeats the same plumbing. LangChain gives swappable components (change OpenAI to another provider, or in-memory to Qdrant, by changing one line), plus streaming, async, batching and tracing for free. Interviewers check you know the pieces and their trade-offs, not just the imports.

## 🔴 यह क्यों बना? (Hindi)
Hand-written RAG (572) में वही plumbing बार-बार लिखनी पड़ती है। LangChain बदलने योग्य components देता है (provider या vector store एक line में बदलें), साथ में streaming, async, batching और tracing मुफ्त। Interviewer देखते हैं कि आप हिस्सों और उनके trade-offs को समझते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Document objects (text + metadata)
Step 2 → RecursiveCharacterTextSplitter makes chunks
Step 3 → Embeddings + VectorStore.add_documents indexes them
Step 4 → store.as_retriever(k=2) is a Runnable: question -> list[Document]
Step 5 → Format docs into one context string (with ids)
Step 6 → {"context": retriever | fmt, "question": RunnablePassthrough()} | prompt | llm | parser
Step 7 → chain.invoke / ainvoke / astream the question
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Document objects (text + metadata)
Step 2 → RecursiveCharacterTextSplitter chunks बनाता है
Step 3 → Embeddings + VectorStore.add_documents से index
Step 4 → store.as_retriever(k=2) एक Runnable है: सवाल -> Documents
Step 5 → Docs को ids के साथ एक context string में बदलो
Step 6 → {"context": retriever | fmt, "question": RunnablePassthrough()} | prompt | llm | parser
Step 7 → chain.invoke / ainvoke / astream से सवाल पूछो
```

---

## 🟡 Real World Example
**Tariff Classification System**: HS notes are loaded as `Document`s with metadata `{id, chapter, effective_date}`. The retriever uses a metadata filter for the current year. The chain returns an answer with `[hs-8517]` citations. In production the in-memory store becomes Qdrant and the model becomes `gpt-4o-mini`.

**Zomato-style**: Restaurant FAQ bot over menu and policy documents.

## 🟡 Real Example Hindi mein
**Tariff System**: HS notes `Document` बनकर आते हैं, metadata `{id, chapter, effective_date}` के साथ। Retriever मौजूदा साल का metadata filter लगाता है। Chain `[hs-8517]` citations के साथ जवाब देती है। Production में in-memory store की जगह Qdrant और model `gpt-4o-mini` होता है।

---

## 💻 Code Example — Basic
Full file: `main.py` (needs `pip install langchain-core langchain-text-splitters`; not installed in this environment, so I only syntax-checked it, I did not run it). Without `OPENAI_API_KEY` it uses `DeterministicFakeEmbedding` and `FakeListChatModel`: this proves wiring, but retrieval order is meaningless because fake embeddings carry no semantics.

```python
# Core chain (from main.py)
chain = (
    {"context": retriever | fmt, "question": RunnablePassthrough()}  # run retrieval and keep question
    | prompt                                                         # fill the template
    | llm                                                            # call the model
    | StrOutputParser()                                              # AIMessage -> str
)
print(chain.invoke("What is the duty on smartphones?"))              # sync call
```

## 💻 Code Example — Advanced
`main.py` adds: model selection by env (real OpenAI vs fakes), splitter with overlap, citation formatting from metadata, an async `ainvoke` demo, and a FastAPI `/ask` route with error mapping to 502. Production extras to add: `search_kwargs={"k": 4, "filter": ...}`, a reranker, `chain.with_retry()`, `.with_fallbacks([...])`, streaming with `astream`, and LangSmith tracing.

```python
# Excerpt: async route with error mapping (main.py)
@app.post("/ask")
async def ask(q: Q) -> dict[str, str]:
    try:
        return {"answer": await chain.ainvoke(q.question)}      # async LCEL call
    except Exception as exc:                                    # provider / retrieval failure
        raise HTTPException(status_code=502, detail=type(exc).__name__) from exc
```

---

## 🟠 FastAPI Integration
```python
# Build the chain ONCE at startup, reuse for every request (components are thread-safe to call)
chain = build_chain()          # heavy: loads index

@app.post("/ask")
async def ask(q: Q) -> dict[str, str]:
    return {"answer": await chain.ainvoke(q.question)}

# Streaming variant (SSE) would use: async for chunk in chain.astream(q.question): ...
```

---

## 🔗 LangChain / LangGraph Connection
This IS the LangChain connection. For agentic RAG, move to LangGraph: nodes `retrieve`, `grade_documents`, `generate`, and a conditional edge that rewrites the query when documents are irrelevant. Use LangSmith to trace each node's tokens and latency.

```python
# LangGraph sketch (illustrative; check current API names)
# graph.add_node("retrieve", retrieve); graph.add_node("generate", generate)
# graph.add_conditional_edges("retrieve", is_relevant, {"yes": "generate", "no": "rewrite_query"})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Rebuilding the index on every request
✅ Correct: Build at startup (or persist the vector store).
```python
# Wrong
@app.post("/ask")
async def ask(q: Q):
    chain = build_chain()          # re-embeds all docs per call: slow and costs money
# Right
chain = build_chain()              # once
```

❌ Mistake 2: Passing Document objects directly into the prompt
✅ Correct: Format to text (the default repr includes noisy metadata and wastes tokens).
```python
# Wrong: {"context": retriever}          -> list[Document] stringified
# Right: {"context": retriever | fmt}    -> clean "[id] text" lines
```

---

## 🧠 Tricky Interview Question
**Q**: "Your LangChain RAG is accurate on small tests but latency is 6 seconds in production. Where do you look?"

**Answer**: Trace it (LangSmith) to split time: embedding the query, vector search, reranker, LLM time-to-first-token and generation length. Typical fixes: smaller `k`, cap `max_tokens`, stream tokens so the user sees output sooner, async/parallel retrieval, cache query embeddings and frequent answers, move the vector DB near the app, use a faster model for simple questions. Do not guess; measure each stage.

---

## ⚫ Interview Questions + Answers

Q1: What is LCEL?
A1: LangChain Expression Language: composing Runnables with `|` into chains that support invoke, batch, stream and async.

Q2: What is a retriever?
A2: A Runnable that takes a query string and returns relevant `Document`s.

Q3: Why `RunnablePassthrough`?
A3: It forwards the original input (the question) unchanged alongside the retrieved context.

Q4: How do you add citations?
A4: Put ids from metadata into the context and instruct the model to cite; return `source_documents`/ids separately for the UI.

Q5: LangChain vs writing it yourself?
A5: LangChain speeds up and standardises (swap providers, streaming, tracing) but adds abstraction and version churn; for a tiny pipeline hand-written code may be clearer. Choose based on team size, need for integrations and observability.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want swappable components, tracing and streaming quickly
- Team already uses the LangChain ecosystem

❌ Avoid when:
- A 50-line custom pipeline is enough and dependency weight matters
- You need very fine control that abstractions hide

---

## 📊 Visual Diagram
```
 question ──┬────────────────────────────► RunnablePassthrough ─┐
            │                                                    ▼
            └─► retriever ─► fmt ─► context ─► ChatPromptTemplate ─► ChatModel ─► StrOutputParser ─► answer
                  ▲
          VectorStore (Qdrant/InMemory) ◄── splitter ◄── Documents
```

---

## 💰 Cost Impact
Same economics as any RAG: input tokens = prompt template + k chunks + question. LangChain itself adds no token cost, but careless chains do (re-sending large contexts, retries, agent loops). Track with callbacks or LangSmith. Optimise: k=3-4, trim chunk size, prompt caching for the static system message, `max_tokens`, cheap model for simple Q&A. Prices change; check the provider's pricing page.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LCEL | Pipe-based chain syntax | Pipe वाली chain syntax |
| Runnable | Any chain component | Chain का कोई भी हिस्सा |
| Retriever | Query to documents | Query से documents |
| VectorStore | Stores embeddings | Embeddings का भंडार |
| Document | Text + metadata | Text + metadata |
| Output parser | Converts model output | Model output बदलना |

---

## ⚡ 3-Line Summary
English: LangChain RAG composes splitter, embeddings, vector store, retriever, prompt, model and parser with LCEL. Build the chain once at startup and call it with `ainvoke` in FastAPI. Trace each stage to fix latency and cost.
Hindi: LangChain RAG splitter, embeddings, vector store, retriever, prompt, model और parser को LCEL से जोड़ता है। Chain startup पर एक बार बनाएँ और FastAPI में `ainvoke` से चलाएँ। Latency और cost सुधारने के लिए हर stage trace करें।

---

## ➡️ Next Topic
**574. Build RAG with LlamaIndex** — the same problem with a data-centric framework.
