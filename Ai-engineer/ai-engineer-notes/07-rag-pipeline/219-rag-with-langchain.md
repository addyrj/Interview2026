---

# 219. RAG with LangChain
# हिंदी में: RAG with LangChain

---

## 🔵 Simple Definition (English)
LangChain gives ready-made parts for RAG: document loaders, text splitters, embeddings, vector stores, retrievers, prompt templates, chat models and output parsers. You connect them with LCEL (the `|` pipe) into one runnable chain.

## 🔵 सरल परिभाषा (Hindi)
LangChain RAG के लिए तैयार parts देता है: document loaders, text splitters, embeddings, vector stores, retrievers, prompt templates, chat models और output parsers। आप इन्हें LCEL (`|` pipe) से एक runnable chain में जोड़ते हैं।

---

## 🔴 Problem it Solves
Writing RAG from scratch means gluing many SDKs, each with its own interface. LangChain gives a common interface (Runnable) so you can swap the vector DB, the model or the reranker with one line, and get streaming, batching, async and tracing for free.

## 🔴 यह क्यों बना? (Hindi)
RAG scratch से लिखने में कई SDKs जोड़ने पड़ते हैं, हर एक का अपना interface होता है। LangChain common interface (Runnable) देता है, इसलिए vector DB, model या reranker एक line में बदल सकते हैं, और streaming, batching, async व tracing मुफ़्त मिलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Load documents (PyPDFLoader, WebBaseLoader ...)
Step 2 → Split with RecursiveCharacterTextSplitter (chunk_size, overlap)
Step 3 → Embed with an Embeddings class and store in a VectorStore
Step 4 → retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
Step 5 → prompt = ChatPromptTemplate(system rules + {context} + {question})
Step 6 → chain = {"context": retriever | format_docs, "question": RunnablePassthrough()}
                 | prompt | llm | StrOutputParser()
Step 7 → await chain.ainvoke(question)  /  chain.astream(question)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Documents load करो (PyPDFLoader, WebBaseLoader ...)
Step 2 → RecursiveCharacterTextSplitter से split करो (chunk_size, overlap)
Step 3 → Embeddings class से embed करके VectorStore में रखो
Step 4 → retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
Step 5 → prompt = ChatPromptTemplate (system rules + {context} + {question})
Step 6 → chain = {"context": retriever | format_docs, "question": RunnablePassthrough()}
                 | prompt | llm | StrOutputParser()
Step 7 → await chain.ainvoke(question)  /  chain.astream(question)
```

---

## 🟡 Real World Example
**Tariff Classification System**: PDFs of the customs tariff are loaded with `PyPDFLoader`, split into 800-character chunks with overlap 100 and metadata `page`, embedded into Chroma/pgvector, and served through a retriever filtered by country. The same chain is traced in LangSmith to debug wrong HS codes. **Zomato**: FAQ chain. **Amazon**: product-doc chain with metadata filter on category.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs tariff के PDFs `PyPDFLoader` से load होते हैं, 800-character chunks (overlap 100) और metadata `page` के साथ split होते हैं, Chroma/pgvector में embed होते हैं और country filter वाले retriever से serve होते हैं। वही chain LangSmith में trace होती है ताकि गलत HS codes debug हो सकें। **Zomato**: FAQ chain। **Amazon**: category metadata filter वाली product-doc chain।

---

## 💻 Code Example — Basic
```python
# Basic LCEL RAG. Offline-friendly: uses fake embeddings + fake chat model from langchain_core.
# pip install langchain-core  (real use: langchain-openai, langchain-chroma ...)
from langchain_core.documents import Document  # document type
from langchain_core.embeddings import DeterministicFakeEmbedding  # fake embeddings for demo
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # fake LLM
from langchain_core.output_parsers import StrOutputParser  # to string
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_core.runnables import RunnablePassthrough  # pass question through
from langchain_core.vectorstores import InMemoryVectorStore  # simple store

docs = [  # knowledge base
    Document(page_content="Smartphones HS 8517.13 duty 20 percent.", metadata={"page": 412}),
    Document(page_content="Laptops HS 8471.30 duty 0 percent.", metadata={"page": 380}),
]
store = InMemoryVectorStore.from_documents(docs, DeterministicFakeEmbedding(size=64))  # embed + store
retriever = store.as_retriever(search_kwargs={"k": 1})  # top-1


def format_docs(items: list[Document]) -> str:
    """Join retrieved docs into one context string."""
    return "\n".join(f"[p.{d.metadata['page']}] {d.page_content}" for d in items)


prompt = ChatPromptTemplate.from_messages([  # system + human
    ("system", "Answer only from the context.\nContext:\n{context}"),
    ("human", "{question}"),
])
llm = FakeListChatModel(responses=["(fake LLM) See the cited context."])  # replace with ChatOpenAI
chain = {"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()

if __name__ == "__main__":
    print(chain.invoke("What is the duty on smartphones?"))  # run the chain
```

## 💻 Code Example — Advanced
```python
# Production: async chain returning answer + sources, with metadata filter, fallback model and error handling.
import logging  # logs
from operator import itemgetter  # pick keys

from langchain_core.documents import Document  # type
from langchain_core.output_parsers import StrOutputParser  # parser
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_core.runnables import RunnableLambda, RunnableParallel  # runnables
from langchain_openai import ChatOpenAI  # real model

logger = logging.getLogger("lc_rag")  # logger

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer ONLY from the context. Cite page numbers like [p.12]. If missing say NOT_FOUND.\n<context>\n{context}\n</context>"),
    ("human", "{question}"),
])
primary = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=400, timeout=20, max_retries=2)  # main model
backup = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=400)  # stronger fallback
llm = primary.with_fallbacks([backup])  # auto-fallback on exceptions


def format_docs(items: list[Document]) -> str:
    return "\n".join(f"[p.{d.metadata.get('page', '?')}] {d.page_content}" for d in items)


def build_chain(vectorstore, country: str):
    """Return a chain that outputs {'answer': str, 'sources': [Document]}."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4, "filter": {"country": country}})  # metadata filter (store-dependent syntax)
    answer_chain = prompt | llm | StrOutputParser()  # generation
    return (
        RunnableParallel(sources=itemgetter("question") | retriever, question=itemgetter("question"))  # retrieve once
        | RunnableParallel(
            answer=RunnableLambda(lambda x: {"context": format_docs(x["sources"]), "question": x["question"]}) | answer_chain,
            sources=itemgetter("sources"),
        )
    )


async def ask(chain, question: str) -> dict:
    try:  # runtime errors
        out = await chain.ainvoke({"question": question})  # async run
        return {"answer": out["answer"], "pages": [d.metadata.get("page") for d in out["sources"]]}
    except Exception as exc:  # provider or retrieval failure
        logger.exception("rag chain failed: %s", exc)  # log trace
        return {"answer": "Service temporarily unavailable", "pages": []}  # safe response
```

---

## 🟠 FastAPI Integration
Build the chain once at startup and call `ainvoke` or `astream` in routes.

```python
from contextlib import asynccontextmanager  # lifespan
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models


@asynccontextmanager
async def lifespan(app: FastAPI):
    vectorstore = ...  # connect Chroma/pgvector here
    app.state.chain = build_chain(vectorstore, country="IN")  # build once
    yield


app = FastAPI(lifespan=lifespan)  # app


class Q(BaseModel):
    question: str  # question


@app.post("/ask")  # route
async def ask_route(q: Q) -> dict:
    return await ask(app.state.chain, q.question)  # use shared chain
```

---

## 🔗 LangChain / LangGraph Connection
This is the LangChain connection. For control flow (retry retrieval when context is weak, route by question type, human review), move the same components into a LangGraph `StateGraph`: nodes `retrieve`, `grade`, `generate`; conditional edges decide the next step. The chain above becomes the `generate` node.

```python
from langgraph.graph import END, START, StateGraph  # graph API
from typing_extensions import TypedDict  # state typing


class State(TypedDict):
    question: str  # input
    docs: list  # retrieved
    answer: str  # output


# g = StateGraph(State)
# g.add_node("retrieve", retrieve_node); g.add_node("generate", generate_node)
# g.add_edge(START, "retrieve"); g.add_edge("retrieve", "generate"); g.add_edge("generate", END)
# app_graph = g.compile()
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the deprecated `RetrievalQA`/legacy chains in new code
✅ Correct: Use LCEL or `create_retrieval_chain` / LangGraph.

```python
# Wrong (legacy): RetrievalQA.from_chain_type(...)
# Right: LCEL pipe or langchain.chains.create_retrieval_chain(retriever, combine_docs_chain)
```

❌ Mistake 2: Rebuilding the vector store on every request
✅ Correct: Index once, load or connect at startup.

```python
# Wrong
store = Chroma.from_documents(docs, emb)   # re-embeds each call, slow and costly

# Right
store = Chroma(persist_directory="db", embedding_function=emb)   # reuse
```

---

## 🧠 Tricky Interview Question
**Q**: "Your LCEL chain retrieves documents twice (once for the prompt, once for returning sources) and doubles latency. Why, and how do you fix it?"

**Answer**: If you call `retriever` in two branches of the chain, each runs its own search. Retrieve once in a first step (`RunnableParallel(sources=retriever, question=...)`), then feed that same result to both the context formatter and the output, as in the advanced example. Alternatively use `create_retrieval_chain`, which returns `context` (documents) and `answer` together.

---

## ⚫ Interview Questions + Answers

Q1: What is LCEL?
A1: LangChain Expression Language: composing Runnables with `|` into chains that support invoke, batch, stream and async.

Q2: What does `RunnablePassthrough` do?
A2: It passes the input unchanged to the next step (used to forward the question next to the retrieved context).

Q3: What is a retriever in LangChain?
A3: A Runnable that takes a query string and returns a list of Documents; any vector store can create one via `as_retriever`.

Q4: How do you add a reranker?
A4: Wrap the base retriever in `ContextualCompressionRetriever` with a compressor such as `CohereRerank` or `CrossEncoderReranker`.

Q5: When would you move from a simple LCEL chain to LangGraph?
A5: When you need loops, branching, state, retries, human approval, or multiple agents: for example grade documents, rewrite the query when context is weak, and retry retrieval. LCEL is for linear flows; LangGraph is for stateful control flow with checkpoints.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want fast prototyping and swappable components
- You need tracing (LangSmith), streaming and async built in
- Team knows the ecosystem

❌ Avoid when:
- A tiny app where raw SDK calls are simpler
- You need very fine control over every request and want fewer abstractions
- Strict dependency minimalism

---

## 📊 Visual Diagram
```
 question ──┬──────────────────────────────┐
            │                              ▼
            ▼                       ┌────────────┐
      ┌───────────┐  docs  ┌────────►│   prompt   │──► LLM ──► parser ──► answer
      │ retriever │───────►│format   └────────────┘
      └───────────┘        │docs          ▲
            ▲              └──────────────┘
      vector store (Chroma / pgvector)       question passthrough
```

---

## 💰 Cost Impact
- Abstractions can hide tokens: check with callbacks/LangSmith. LangChain does not add tokens by itself, but defaults (like `k=4` and large chunks) decide your prompt size.
- Example: k=4 x 800-character chunks (about 200 tokens each) = about 800 context tokens plus 100 for rules.
- Optimise: tune `k` and chunk size, cache embeddings (`CacheBackedEmbeddings`), cache LLM calls (`set_llm_cache`), use `max_tokens`, fallback to a cheaper model first, and track usage via `usage_metadata` on AIMessage.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LCEL | Pipe syntax for chains | Chains जोड़ने की pipe syntax |
| Runnable | Common interface for steps | Steps का common interface |
| Retriever | Query to Documents | Query से Documents |
| VectorStore | DB of embeddings | Embeddings का database |
| Fallback | Backup model on failure | Failure पर backup model |

---

## ⚡ 3-Line Summary
English: LangChain wires loaders, splitters, vector stores, retrievers, prompts and models with LCEL. Build the chain once, use async, and retrieve only once per request. Move to LangGraph when you need loops and state.
Hindi: LangChain loaders, splitters, vector stores, retrievers, prompts और models को LCEL से जोड़ता है। Chain एक बार बनाओ, async use करो और हर request में retrieval सिर्फ़ एक बार करो। Loops और state चाहिए तो LangGraph पर जाओ।

---

## ➡️ Next Topic
**220. RAG with LlamaIndex** — the data-centric alternative framework, strong on indexing and query engines.
