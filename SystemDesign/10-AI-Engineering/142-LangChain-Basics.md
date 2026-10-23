# 142. LangChain Basics
# हिंदी में: LangChain — LLM ऐप बनाने का लोकप्रिय framework (Python/JS): models, prompts, output parsers, retrievers, tools और उन्हें जोड़ने का तरीका (LCEL `|` से chains) — तेज़ prototype, ढेरों integrations; पर कब इसकी ज़रूरत है और कब सीधे SDK बेहतर

---

## 🔵 Simple Definition (English)
**LangChain** is an open-source framework (Python and JavaScript/TypeScript) providing **standard interfaces and integrations** for building LLM applications:
- **Chat models**: one interface across providers (`ChatAnthropic`, `ChatOpenAI`, Bedrock, local models), with `.invoke`, `.stream`, `.batch`, async variants and `.bind_tools` / `.with_structured_output`.
- **Prompt templates**: `ChatPromptTemplate` with variables and message placeholders.
- **Output parsers / structured output**: strings, JSON or Pydantic objects.
- **Document loaders, text splitters, embeddings, vector stores, retrievers**: the RAG building blocks, with hundreds of integrations (pgvector, Pinecone, Qdrant, OpenSearch…).
- **Tools**: the `@tool` decorator turns Python functions into tool schemas.
- **LCEL (LangChain Expression Language)**: compose **Runnables** with the pipe `|` (`prompt | model | parser`), plus `RunnableParallel`, `RunnablePassthrough`, fallbacks and retries. Streaming, async and batching come for free.
- **Callbacks and tracing**: integrates with **LangSmith** (Topic 147).
For **agents and stateful workflows**, the ecosystem uses **LangGraph** (Topic 143). LangChain's agent APIs are built on LangGraph in current versions.

## 🔵 सरल परिभाषा (Hindi)
LangChain एक open-source framework (Python और JS/TS) है जो LLM ऐप के हिस्सों के लिए एक जैसे interfaces और ढेरों integrations देता है: chat models (सब providers के लिए एक तरीका — invoke, stream, batch, tools, structured output), prompt templates, output parsers (JSON/Pydantic), document loaders, text splitters, embeddings, vector stores, retrievers (RAG के blocks — pgvector, Pinecone…), `@tool` से functions को tools बनाना, और LCEL — `prompt | model | parser` जैसे `|` से जोड़कर chains (streaming, async, batch अपने-आप); LangSmith से tracing।
Agents और stateful workflows के लिए LangGraph (अगला topic)।

---

## 🔴 Problem it Solves
Building LLM apps from scratch means writing the same glue repeatedly:
- Switching providers means rewriting request and response handling.
- Every RAG app needs loaders (PDF, web, Notion), splitters, embedding calls, vector store clients and retriever logic.
- Prompts with variables, chat history placeholders, structured output parsing and retries are re-implemented each time.
- Streaming, async, batching, fallbacks and tracing need extra plumbing.
LangChain provides **reusable, swappable components** and a **composition language**, so prototypes and many production apps can be assembled quickly. It's also a common interview topic, since many teams use it.
Teams must also understand its **trade-offs**: an abstraction layer over fast-moving APIs, version churn, and debugging through layers. Many experienced teams use it selectively (integrations, loaders) or prefer direct SDKs for core paths.

## 🔴 यह क्यों बना? (Hindi)
शुरू से LLM ऐप बनाना = बार-बार वही glue code: provider बदलो तो request/response संभालना दोबारा; हर RAG ऐप में loaders (PDF, web, Notion), splitters, embeddings, vector store client, retriever; variables वाले prompts, history, structured output parsing, retries; streaming, async, batching, fallbacks, tracing की अलग मेहनत।
LangChain दोबारा इस्तेमाल होने वाले, बदलने लायक हिस्से और जोड़ने की भाषा देता है — prototypes और कई production ऐप जल्दी बनते हैं (और इंटरव्यू में अक्सर पूछा जाता है); पर trade-offs भी समझो — तेज़ी से बदलते APIs पर abstraction, versions का बदलना, परतों में debugging; अनुभवी टीमें इसे चुनकर इस्तेमाल करती हैं।

---

## 🟢 How it Works — Step by Step

### Core abstractions

```
Runnable (everything composable): .invoke(x) .batch([x]) .stream(x) .ainvoke(x) .astream(x)
   ├─ ChatPromptTemplate     : dict → messages
   ├─ ChatModel              : messages → AIMessage (text / tool_calls)
   ├─ OutputParser           : AIMessage → str / dict / Pydantic
   ├─ Retriever              : query → [Document(page_content, metadata)]
   ├─ Tool                   : args → result (schema from function signature + docstring)
   └─ RunnableLambda         : wrap any Python function
Compose with LCEL:
   chain = prompt | model | parser                          (sequential)
   RunnableParallel(context=retriever, question=RunnablePassthrough())   (fan-out)
   model.with_fallbacks([backup_model]); chain.with_retry(stop_after_attempt=3)
```

### A RAG chain in LCEL (mental model)

```
question ──┬──► retriever (pgvector / Pinecone) ──► format_docs ──► {context}
           └──────────────────────────────────────────────────────► {question}
                                  ▼
                        ChatPromptTemplate (system rules + context + question)
                                  ▼
                        ChatAnthropic(model="claude-sonnet-5-5")
                                  ▼
                        StrOutputParser  ──► answer (streamable token by token)
```

### Ecosystem map

```
langchain-core        : base abstractions (Runnables, messages, prompts)
langchain             : chains/agents helpers (agents built on LangGraph in current versions)
langchain-anthropic, langchain-openai, langchain-aws, langchain-google-genai : provider packages
langchain-postgres (PGVector), langchain-pinecone, langchain-qdrant : vector stores
langchain-community   : many community integrations (loaders, tools)
langchain-text-splitters : splitters (recursive, Markdown header, token)
LangGraph             : stateful agents & workflows (Topic 143)
LangSmith             : tracing, evals, prompt hub (Topic 147)
```

### When to use LangChain vs direct SDKs

```
Use LangChain when:                              Prefer direct SDKs when:
✓ fast prototyping, many integrations needed     ✓ core production path needs full control/perf
✓ swapping providers/vector stores often         ✓ using newest provider features immediately
✓ team standardizes on LangGraph + LangSmith     ✓ simple app (one model, one retriever)
✓ loaders/splitters save real effort             ✓ debugging/latency through layers is a concern
Common hybrid: LangChain loaders/splitters for ingestion + direct SDK or LangGraph for runtime
```

### Practical tips

```
- Pin versions (fast-moving library); read migration notes on upgrades
- Use with_structured_output(PydanticModel) instead of fragile regex parsing
- Keep prompts in code/registry with versions; log chain inputs/outputs via LangSmith or your tracer
- Use async (.ainvoke/.astream) in FastAPI; batch embeddings; set timeouts on models
- Don't hide authz in chains — tools must still enforce permissions server-side
```

## 🟢 कैसे काम करता है? (Hindi)
1. सब कुछ Runnable है — `.invoke`, `.batch`, `.stream` और async रूप; prompt template (dict → messages), chat model (messages → जवाब/tool calls), output parser (जवाब → str/dict/Pydantic), retriever (सवाल → documents), tool, और कोई भी function (RunnableLambda)।
2. LCEL से जोड़ो: `prompt | model | parser` क्रम से; `RunnableParallel` से एक साथ (retriever + सवाल); `with_fallbacks` (backup model), `with_retry`।
3. RAG chain: सवाल → retriever (pgvector/Pinecone) → docs format → prompt (नियम + context + सवाल) → ChatAnthropic → parser → token-दर-token stream।
4. Packages: langchain-core, provider packages (anthropic, openai, aws), vector stores (postgres, pinecone), text-splitters, community; agents/workflows के लिए LangGraph, tracing/evals के लिए LangSmith।
5. कब इस्तेमाल: तेज़ prototype, बहुत integrations, providers बदलना; कब सीधा SDK: मुख्य production रास्ते पर पूरा नियंत्रण, नए features तुरंत, सरल ऐप; सुझाव: versions pin करो, `with_structured_output`, async, timeouts, और अनुमति tools में ख़ुद लागू करो।

---

## 🟡 Real World Example

**Rapid adoption (2023)** — LangChain, created by Harrison Chase in late 2022, became one of the fastest-growing open-source projects of 2023 as developers rushed to build RAG and agent prototypes. Its integration ecosystem (models, vector stores, loaders) was the main draw.

**Evolution toward LCEL and LangGraph** — early LangChain "chains" and "agents" were criticized for being too abstract and hard to debug. The project moved to LCEL composition and LangGraph for explicit, controllable agent graphs, a lesson in framework design that interviewers like to discuss.

**Enterprise usage** — many companies use LangChain and LangGraph with LangSmith for tracing and evaluation. Others use only loaders and splitters for ingestion and call provider SDKs directly at runtime, a common pragmatic split.

**Hackathons and Indian startup prototypes** — "chat with your PDF/website" and WhatsApp bot MVPs are commonly built in a day using LangChain loaders plus a vector store plus Claude or OpenAI, then hardened (or partially rewritten) for production.

## 🟡 Real Example Hindi में
LangChain (Harrison Chase, 2022 के आख़िर में) 2023 के सबसे तेज़ बढ़ने वाले open-source projects में रहा — RAG और agent prototypes की होड़ में; बड़ा आकर्षण integrations।
शुरुआती "chains/agents" को ज़्यादा abstract और debug में कठिन कहा गया, इसलिए project LCEL और LangGraph (साफ़, नियंत्रित graphs) की ओर गया; कई कंपनियाँ LangChain/LangGraph + LangSmith इस्तेमाल करती हैं, कुछ सिर्फ़ loaders/splitters और runtime पर सीधा SDK; hackathons में "PDF से बात करो"/WhatsApp bot MVP एक दिन में।

---

## 🟠 My Stack Example

### LCEL RAG chain with pgvector + Claude + streaming (Python)
```python
# pip install langchain-core langchain-anthropic langchain-postgres langchain-voyageai psycopg[binary]
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_postgres import PGVector
from langchain_voyageai import VoyageAIEmbeddings

embeddings = VoyageAIEmbeddings(model="voyage-3.5")
store = PGVector(embeddings=embeddings, collection_name="help_kb",
                 connection="postgresql+psycopg://app:***@db:5432/app", use_jsonb=True)
retriever = store.as_retriever(search_kwargs={"k": 5, "filter": {"tenant_id": 42}})

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer ONLY from the context. If not found, say you don't know. Cite [S#]. Reply in the user's language.\n\n{context}"),
    ("human", "{question}"),
])
model = ChatAnthropic(model="claude-sonnet-5-5", temperature=0.1, max_tokens=500, timeout=60)
backup = ChatAnthropic(model="claude-haiku-5-5", temperature=0.1, max_tokens=500)

def format_docs(docs):
    return "\n".join(f'<source id="S{i+1}" url="{d.metadata.get("url")}">{d.page_content}</source>' for i, d in enumerate(docs))

rag_chain = (
    RunnableParallel(context=retriever | format_docs, question=RunnablePassthrough())
    | prompt
    | model.with_fallbacks([backup])
    | StrOutputParser()
)

for token in rag_chain.stream("UPI refund kab tak aayega?"):
    print(token, end="", flush=True)
```

### Structured output in one line
```python
from pydantic import BaseModel
from typing import Literal
class Triage(BaseModel):
    category: Literal["DELIVERY_DELAY", "FOOD_QUALITY", "PAYMENT", "REFUND", "OTHER"]
    urgency: Literal["low", "medium", "high"]

triage = ChatAnthropic(model="claude-haiku-5-5", temperature=0).with_structured_output(Triage)
print(triage.invoke("Paise kat gaye, order nahi aaya, 2 ghante ho gaye!"))   # Triage(category='PAYMENT', urgency='high')
```

### Tools with @tool and bind_tools
```python
from langchain_core.tools import tool

@tool
def get_order_status(order_id: str) -> dict:
    """Get live status and ETA for one of the current user's orders."""
    return orders_api.status_for_current_user(order_id)        # authz enforced inside the API (current user from context)

llm_with_tools = ChatAnthropic(model="claude-sonnet-5-5").bind_tools([get_order_status])
ai_msg = llm_with_tools.invoke("Where is order 4521?")
print(ai_msg.tool_calls)        # [{'name': 'get_order_status', 'args': {'order_id': '4521'}, 'id': '...'}]
# Execute and loop — or use LangGraph's prebuilt ToolNode/agent (Topic 143)
```

### Ingestion with loaders + splitters
```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
docs = PyPDFLoader("refund_policy.pdf").load()                               # one Document per page (metadata: page)
chunks = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150).split_documents(docs)
for c in chunks: c.metadata.update({"tenant_id": 42, "doc_id": "refund-policy", "lang": "en"})
store.add_documents(chunks, ids=[f"refund-policy#{i}" for i in range(len(chunks))])
```

### FastAPI streaming endpoint with the chain
```python
@app.get("/api/ask")
async def ask(q: str):
    async def gen():
        async for tok in rag_chain.astream(q):
            yield f"data: {json.dumps({'delta': tok})}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
```

### LangChain.js equivalent (TypeScript)
```ts
import { ChatAnthropic } from '@langchain/anthropic';
import { ChatPromptTemplate } from '@langchain/core/prompts';
import { StringOutputParser } from '@langchain/core/output_parsers';
const chain = ChatPromptTemplate.fromMessages([['system', 'Be concise.'], ['human', '{q}']])
  .pipe(new ChatAnthropic({ model: 'claude-haiku-5-5', temperature: 0 }))
  .pipe(new StringOutputParser());
const answer = await chain.invoke({ q: 'Explain UPI autopay in one line' });
```

---

## ⚫ Interview Questions + Answers

**Q1: What is LangChain and what problems does it solve?**
A1: LangChain is a framework offering standardized interfaces and many integrations for LLM application components: chat models across providers, prompt templates, output parsers and structured output, document loaders, text splitters, embeddings, vector stores, retrievers and tools. With LCEL you compose them into chains that support streaming, async, batching, retries and fallbacks. It speeds up prototyping and makes components swappable. LangGraph handles stateful agents, and LangSmith handles tracing and evaluation.

**Q2: What is LCEL?**
A2: The LangChain Expression Language is a declarative way to compose Runnables using the pipe operator, e.g. `prompt | model | parser`, plus constructs like `RunnableParallel` for fan-out, `RunnablePassthrough` to forward inputs, and `RunnableLambda` for custom functions. Every composed chain is itself a Runnable with `invoke`, `batch`, `stream` and async methods, and supports `with_retry` and `with_fallbacks`, giving consistent streaming and tracing across the pipeline.

**Q3: What are the downsides of using LangChain?**
A3: Abstraction overhead can obscure what prompts and requests are actually sent, making debugging and performance tuning harder. The library evolves quickly, causing breaking changes and dependency sprawl. New provider features may lag behind direct SDKs, and complex chains can become hard to reason about. Mitigations are pinning versions, using tracing (LangSmith), keeping chains simple, and using direct SDKs or LangGraph for core logic while using LangChain integrations where they save real effort.

**Q4: How would you build a RAG app with LangChain?**
A4: For ingestion, load documents with loaders, split them with recursive or Markdown splitters, add metadata (tenant, doc ID, URL, language) and add them to a vector store like PGVector or Pinecone with stable IDs. At runtime, create a retriever with filters, compose `RunnableParallel(context=retriever | format_docs, question=passthrough) | prompt | chat_model | StrOutputParser()`, stream the output through an API endpoint, add fallbacks and retries, trace with LangSmith, and evaluate retrieval and answers with an eval set. For conversational or agentic behaviour, move orchestration to LangGraph.

**Q5: LangChain vs LangGraph — when to use which?**
A5: Use LangChain components and LCEL for linear or simple branching pipelines like a RAG chain, extraction or summarization, where data flows one way. Use LangGraph when you need explicit state, loops (agents calling tools repeatedly), conditional routing, persistence and checkpointing across turns, human-in-the-loop approvals, or multi-agent coordination, i.e. controllable, durable workflows. They interoperate: LangGraph nodes often use LangChain models, retrievers and tools.

---

## 🔷 Trade-offs
✅ Fast prototyping, huge integration ecosystem, provider-agnostic — ❌ abstraction overhead, churn, harder low-level debugging.
✅ LCEL streaming/async/batching built-in — ❌ learning curve for Runnable semantics.
✅ Standardization across team — ❌ lock-in to framework patterns; direct SDKs may be simpler for small apps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LangChain | LLM app framework | LLM ऐप framework |
| Runnable | Composable unit with invoke/stream | जुड़ने वाली इकाई |
| LCEL | Pipe-based composition language | `\|` से जोड़ने की भाषा |
| ChatPromptTemplate | Templated chat messages | template वाले संदेश |
| Output parser | Converts model output | output बदलने वाला |
| Retriever | Fetches relevant documents | documents लाने वाला |
| Vector store | Embedding storage integration | vector संग्रह |
| Document loader | Reads sources into Documents | स्रोत पढ़ने वाला |
| Text splitter | Chunks documents | टुकड़े करने वाला |
| bind_tools | Attach tools to a model | model से tools जोड़ना |

---

## ⚡ 3-Line Summary
**English:**
1. LangChain standardizes models, prompts, parsers, loaders, splitters, embeddings, vector stores, retrievers and tools with many integrations.
2. LCEL composes Runnables (`prompt | model | parser`, parallel, passthrough) with streaming, async, batching, retries and fallbacks.
3. Great for prototyping and integrations; pin versions, trace everything, keep authz in tools, and use LangGraph (or direct SDKs) for complex/controlled runtime logic.

**Hindi:**
1. LangChain models, prompts, parsers, loaders, splitters, vector stores, retrievers, tools को एक जैसा बनाता है।
2. LCEL से `prompt | model | parser` जैसे chains — streaming, async, retries, fallbacks के साथ।
3. Prototype और integrations के लिए बढ़िया; versions pin, tracing, अनुमति tools में; जटिल logic के लिए LangGraph या सीधा SDK।

---

## ➡️ Next Topic Suggestion
**143. LangGraph** — For agents and workflows that loop, branch, persist and pause for human approval, you need explicit state machines. Next: LangGraph's state, nodes, edges, checkpointers and interrupts.
