---

# 229. RAG for Tariff System
# हिंदी में: Tariff System के लिए RAG

---

## 🔵 Simple Definition (English)
This note designs one complete RAG system for our Tariff Classification project: ingest customs documents, retrieve the right HS-code chunks, and have the LLM return a code with a justification and citations.

## 🔵 सरल परिभाषा (Hindi)
यह note हमारे Tariff Classification project का पूरा RAG design है: customs documents ingest करो, सही HS-code chunks retrieve करो, और LLM से citations के साथ code + कारण निकालो।

---

## 🔴 Problem it Solves
Classifying a product into an HS code (6-10 digits) by LLM memory alone is unreliable: codes change yearly, national lines (India 8-digit ITC-HS) differ, and the model invents codes. We need grounded answers from official tariff text with traceable sources.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ LLM की memory से HS code (6-10 digits) निकालना भरोसेमंद नहीं: codes हर साल बदलते हैं, देश के 8-digit lines अलग हैं, और model code गढ़ देता है। हमें official tariff text से grounded, source-सहित answers चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Ingest: parse Section/Chapter/Heading notes + tariff tables
Step 2 → Chunk by hierarchy: one chunk per heading/subheading + parent notes
Step 3 → Metadata: chapter, heading, hs_code, effective_date, country
Step 4 → Index: embeddings (dense) + BM25 (exact codes/terms)
Step 5 → Query: normalise product text; hybrid retrieve top-20
Step 6 → Rerank to top-5; filter by country/effective_date
Step 7 → LLM returns JSON: hs_code, confidence, reasoning, cited chunk ids
Step 8 → Validate: code exists in code list; low confidence -> human review
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Ingest: Section/Chapter/Heading notes + tariff tables parse
Step 2 → Hierarchy से chunk: हर heading/subheading + parent notes
Step 3 → Metadata: chapter, heading, hs_code, effective_date, country
Step 4 → Index: dense embeddings + BM25 (exact codes/terms के लिए)
Step 5 → Query normalise; hybrid retrieve top-20
Step 6 → Rerank top-5; country/date से filter
Step 7 → LLM JSON दे: hs_code, confidence, reasoning, cited ids
Step 8 → Validate: code सूची में है? कम confidence -> human review
```

---

## 🟡 Real World Example
Input: "Bluetooth wireless earbuds with charging case". Hybrid search hits Heading 8518 (microphones, headphones, earphones) and 8517 (apparatus for transmission of voice). The reranker puts 8518.30 first; Chapter 85 notes are attached as parent context. LLM answers `8518.30` with confidence 0.86 and cites chunk ids. A validator confirms 8518.30 exists in the code list. **Amazon** seller onboarding uses the same flow for product-category assignment.

## 🟡 Real Example Hindi mein
Input: "Charging case वाले Bluetooth wireless earbuds"। Hybrid search Heading 8518 (headphones/earphones) और 8517 लाता है। Reranker 8518.30 को ऊपर रखता है; Chapter 85 notes parent context के रूप में जुड़ते हैं। LLM confidence 0.86 के साथ `8518.30` और cited chunk ids देता है। Validator जाँचता है कि code सूची में है।

---

## 💻 Code Example — Basic
```python
# Offline tariff RAG: keyword retrieval + rule-based "LLM" + validator
import re
from dataclasses import dataclass

@dataclass
class Chunk:
    id: str
    hs: str
    text: str

CHUNKS: list[Chunk] = [
    Chunk("c1", "8518.30", "headphones earphones whether or not combined with microphone"),
    Chunk("c2", "8517.13", "smartphones telephones for cellular networks"),
    Chunk("c3", "6403.99", "footwear with outer soles of rubber leather uppers"),
]
VALID_CODES: set[str] = {c.hs for c in CHUNKS}  # official list

def tokenize(s: str) -> set[str]:
    return set(re.findall(r"[a-z]+", s.lower()))  # words only

def retrieve(q: str, k: int = 2) -> list[Chunk]:
    qt = tokenize(q)
    scored = sorted(CHUNKS, key=lambda c: -len(qt & tokenize(c.text)))  # overlap ranking
    return [c for c in scored[:k] if qt & tokenize(c.text)]  # drop zero-overlap

def classify(q: str) -> dict:
    hits = retrieve(q)
    if not hits:
        return {"hs_code": None, "needs_review": True, "reason": "no evidence"}
    best = hits[0]  # mock LLM picks top chunk
    conf = round(len(tokenize(q) & tokenize(best.text)) / max(len(tokenize(q)), 1), 2)
    ok = best.hs in VALID_CODES  # validator step
    return {"hs_code": best.hs, "confidence": conf, "sources": [c.id for c in hits],
            "needs_review": (not ok) or conf < 0.3}

print(classify("wireless headphones earphones"))
print(classify("space elevator"))
```

## 💻 Code Example — Advanced
```python
# Production tariff RAG: hybrid retrieval, structured output, validation, async
import asyncio
from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document

class Classification(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4}(\.\d{2}){0,2}$")  # 8518 / 8518.30 / 8518.30.00
    confidence: float = Field(ge=0, le=1)
    reasoning: str
    cited_ids: list[str]
    decision: Literal["auto", "review"] = "auto"

PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a customs classifier. Use ONLY the context. If unsure, lower confidence."),
    ("human", "Product: {product}\n\nContext:\n{context}"),
])

def build_retriever(docs: list[Document]) -> EnsembleRetriever:
    dense = FAISS.from_documents(docs, OpenAIEmbeddings(model="text-embedding-3-small")).as_retriever(search_kwargs={"k": 10})
    sparse = BM25Retriever.from_documents(docs); sparse.k = 10  # exact term matches
    return EnsembleRetriever(retrievers=[sparse, dense], weights=[0.4, 0.6])  # RRF merge

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Classification)
chain = PROMPT | llm

async def classify(product: str, retriever: EnsembleRetriever, valid_codes: set[str]) -> Classification:
    docs = (await retriever.ainvoke(product))[:5]  # top-5 after merge
    ctx = "\n".join(f"[{d.metadata['id']}] {d.metadata['hs']}: {d.page_content}" for d in docs)
    try:
        out: Classification = await asyncio.wait_for(chain.ainvoke({"product": product, "context": ctx}), timeout=20)
    except (asyncio.TimeoutError, Exception):
        return Classification(hs_code="0000", confidence=0.0, reasoning="LLM failure", cited_ids=[], decision="review")
    if out.hs_code not in valid_codes or out.confidence < 0.6:  # guardrail
        out.decision = "review"
    return out
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Tariff RAG")

class Req(BaseModel):
    product: str

@app.post("/classify", response_model=Classification)
async def classify_route(req: Req) -> Classification:
    if not req.product.strip():
        raise HTTPException(422, "product is empty")  # input validation
    return await classify(req.product, RETRIEVER, VALID_CODES)  # built at startup (lifespan)
```

---

## 🔗 LangChain / LangGraph Connection
A LangGraph workflow: `normalize -> retrieve -> rerank -> classify -> validate -> (review_queue | done)`. The conditional edge after `validate` routes low-confidence items to a human-in-the-loop interrupt.

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class S(TypedDict, total=False):
    product: str
    result: dict
    decision: str

g = StateGraph(S)
for name in ("normalize", "retrieve", "classify", "validate"):
    g.add_node(name, lambda s: {})  # real logic goes here
g.set_entry_point("normalize")
g.add_edge("normalize", "retrieve"); g.add_edge("retrieve", "classify"); g.add_edge("classify", "validate")
g.add_conditional_edges("validate", lambda s: END if s.get("decision") == "auto" else END)  # route to review in prod
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Pure vector search for codes
```python
# Wrong: dense only -> "8518.30" not found reliably
# Right: hybrid BM25 + dense so exact codes and terms match
```

❌ Mistake 2: Trusting the LLM's code without validation
```python
# Wrong: return llm_output.hs_code
# Right: if code not in VALID_CODES or confidence < 0.6: send to review
```

---

## 🧠 Tricky Interview Question
**Q**: "Accuracy is 92 percent in testing but customs rejects 15 percent in production. Why?"

**Answer**: Likely (1) stale index: tariff schedules and notifications changed, (2) test set leakage or too-clean product descriptions versus messy real ones, (3) correct 6-digit code but wrong 8-digit national line, (4) ignoring Section/Chapter notes that exclude items. Fixes: effective-date metadata and re-index pipeline, realistic eval set from rejected cases, hierarchical chunking with parent notes, and a human review queue.

---

## ⚫ Interview Questions + Answers

Q1: Why hierarchical chunking for tariffs? (Easy)
A1: Rules live in Section/Chapter notes that include or exclude headings; attaching parent notes prevents wrong classification.

Q2: Why hybrid search? (Easy)
A2: Codes and legal terms need exact matches (BM25); descriptions need semantics (dense).

Q3: How do you handle ambiguity like "smart watch"? (Medium)
A3: Retrieve competing headings, let LLM output top-2 candidates with reasons, ask a clarifying question or route to review.

Q4: How do you keep data fresh? (Medium)
A4: Store effective_date and version, incremental re-index on notifications, filter retrieval by date, run regression tests on a golden set after each update.

Q5: How would you measure the system end to end? (Hard)
A5: Offline: golden set accuracy at 4/6/8 digits, recall@k of the right chunk, faithfulness. Online: auto-approval rate, review rate, customs rejection rate, p95 latency, cost per classification. Tie alerts to rejection-rate drift.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Rules change often and answers need citations
- Large document corpus beyond context window

❌ Avoid when:
- A fixed lookup table or fine-tuned classifier on historical data is enough and cheaper

---

## 📊 Visual Diagram
```
 Customs PDFs ─► Parse ─► Hierarchical chunks (+parent notes, metadata)
                                   │
                     ┌─────────────┴──────────────┐
                     ▼                            ▼
                Dense index                   BM25 index
                     └─────────────┬──────────────┘
 Product text ─► Normalise ─► Hybrid retrieve (20) ─► Rerank (5)
                                   ▼
                     LLM (structured JSON + citations)
                                   ▼
               Validate code ─► auto ─► API response
                              └► low confidence ─► human review
```

---

## 💰 Cost Impact
Per classification: ~1,500 input tokens (5 chunks + prompt) + ~150 output = about $0.00032 on gpt-4o-mini; 100k classifications/month is roughly $32. Embedding the corpus is one-time (text-embedding-3-small, very cheap). Optimise: cache by normalised product text, rerank to 3-5 chunks, small model first and escalate to a bigger one only for low confidence, batch API for bulk uploads.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HS code | Harmonised System product code | Product का अंतरराष्ट्रीय code |
| Hybrid search | BM25 + dense | मिला-जुला search |
| Parent notes | Chapter/Section notes | ऊपरी नियम |
| Validator | Checks output is legal | Output जाँचने वाला |
| Human-in-the-loop | Manual review path | इंसानी review |

---

## ⚡ 3-Line Summary
English: The tariff RAG uses hierarchical chunks, hybrid search, reranking and structured output. A validator and review queue protect against wrong codes. Freshness metadata keeps answers current.
Hindi: Tariff RAG में hierarchical chunks, hybrid search, reranking और structured output होते हैं। Validator और review queue गलत codes से बचाते हैं। Freshness metadata answers को current रखता है।

---

## ➡️ Next Topic
**230. RAG Production Checklist** — what to verify before shipping any RAG system.
