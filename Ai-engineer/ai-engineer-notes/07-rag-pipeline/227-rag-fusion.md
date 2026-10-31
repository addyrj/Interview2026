---

# 227. RAG Fusion
# हिंदी में: RAG Fusion (कई queries + rank मिलाना)

---

## 🔵 Simple Definition (English)
RAG Fusion generates several rewrites of the user question, retrieves for each, and merges the ranked lists using Reciprocal Rank Fusion (RRF). Chunks that appear high in many lists win.

## 🔵 सरल परिभाषा (Hindi)
RAG Fusion user के सवाल के कई rewrites बनाता है, हर एक के लिए retrieve करता है, फिर Reciprocal Rank Fusion (RRF) से lists मिलाता है। जो chunks कई lists में ऊपर आते हैं वे जीतते हैं।

---

## 🔴 Problem it Solves
A single user query is often vague or phrased differently from the document ("phone import tax" vs "BCD on telephone sets"). One query = one embedding = one narrow view, so relevant chunks are missed. Multiple perspectives plus a robust merge raise recall without training anything.

## 🔴 यह क्यों बना? (Hindi)
User का एक query अक्सर अस्पष्ट होता है या document से अलग शब्दों में ("phone import tax" बनाम "telephone sets पर BCD")। एक query = एक embedding = सीमित नज़र, इसलिए relevant chunks छूट जाते हैं। कई नज़रिए + मज़बूत merge से बिना training के recall बढ़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → LLM writes N query variants (e.g., 4) from the original
Step 2 → Run retrieval for each variant (parallel)
Step 3 → Each run gives a ranked list of chunk IDs
Step 4 → RRF score per chunk = sum over lists of 1 / (k + rank), k = 60
Step 5 → Sort by RRF score, keep top-m
Step 6 → Optionally rerank with a cross-encoder
Step 7 → Generate the answer from the top-m chunks
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → LLM original से N query variants बनाता है (जैसे 4)
Step 2 → हर variant के लिए retrieval (parallel)
Step 3 → हर run से chunk IDs की ranked list मिलती है
Step 4 → RRF score = सभी lists में 1/(k+rank) का जोड़, k = 60
Step 5 → RRF score से sort करके top-m रखो
Step 6 → चाहें तो cross-encoder से rerank
Step 7 → Top-m chunks से answer generate करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: User types "tax on importing a phone". Variants: "basic customs duty smartphones", "HS code 8517 import duty", "IGST rate on mobile handsets", "customs tariff telephone sets". Each finds different chunks (duty table, HS notes, GST notification). RRF puts the HS 8517 chunk on top because it appears in 3 lists. **Zomato**: "cheap veg biryani near me" expands to "budget vegetarian biryani", "pure veg dum biryani under 200".

## 🟡 Real Example Hindi mein
**Tariff System**: User लिखता है "phone import पर tax"। Variants: "smartphones पर basic customs duty", "HS 8517 import duty", "mobile handsets पर IGST", "telephone sets customs tariff"। हर variant अलग chunks ढूँढता है। HS 8517 वाला chunk 3 lists में है इसलिए RRF में ऊपर आता है।

---

## 💻 Code Example — Basic
```python
# Reciprocal Rank Fusion in pure Python (runs offline)
from collections import defaultdict

def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Merge several ranked lists of IDs into one list using RRF."""
    scores: dict[str, float] = defaultdict(float)  # id -> fused score
    for ranked in rankings:  # each retrieval run
        for rank, doc_id in enumerate(ranked, start=1):  # rank starts at 1
            scores[doc_id] += 1.0 / (k + rank)  # RRF formula
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)  # best first

# Mock results from 3 query variants:
runs: list[list[str]] = [
    ["hs8517", "duty_table", "gst_note"],
    ["duty_table", "hs8517", "chapter85"],
    ["hs8517", "chapter85", "other"],
]
for doc_id, score in rrf(runs):
    print(f"{doc_id:12s} {score:.4f}")  # hs8517 should be first
```

## 💻 Code Example — Advanced
```python
# Async RAG Fusion with LangChain: query generation + parallel retrieval + RRF
import asyncio
from collections import defaultdict
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

gen_prompt = ChatPromptTemplate.from_template(
    "Write {n} different search queries (one per line, no numbering) for: {q}"
)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)  # some diversity is wanted here
query_chain = gen_prompt | llm | StrOutputParser()  # LCEL chain

async def expand(q: str, n: int = 4) -> list[str]:
    try:
        text = await query_chain.ainvoke({"q": q, "n": n})  # LLM call
    except Exception:
        return [q]  # fall back to the original query
    variants = [line.strip() for line in text.splitlines() if line.strip()][:n]
    return [q, *variants]  # always include the original

def fuse(results: list[list[Document]], k: int = 60, top: int = 5) -> list[Document]:
    scores: dict[str, float] = defaultdict(float)  # key -> score
    by_key: dict[str, Document] = {}  # key -> document
    for docs in results:
        for rank, d in enumerate(docs, start=1):
            key = d.metadata.get("id") or d.page_content[:80]  # stable identity
            scores[key] += 1.0 / (k + rank)
            by_key[key] = d
    ordered = sorted(scores, key=scores.get, reverse=True)  # best first
    return [by_key[x] for x in ordered[:top]]

async def rag_fusion(q: str, retriever) -> list[Document]:
    queries = await expand(q)  # Step 1
    results = await asyncio.gather(*(retriever.ainvoke(x) for x in queries), return_exceptions=True)  # Step 2
    ok = [r for r in results if not isinstance(r, Exception)]  # skip failed runs
    return fuse(ok) if ok else []  # Steps 4-5
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Q(BaseModel):
    question: str

@app.post("/tariff/fusion-search")
async def fusion_search(body: Q) -> dict:
    docs = await rag_fusion(body.question, retriever)  # advanced code above
    return {"chunks": [{"text": d.page_content, "meta": d.metadata} for d in docs]}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain offers `MultiQueryRetriever` (query variants) and `EnsembleRetriever` (uses weighted RRF across retrievers such as BM25 + vectors). RAG Fusion = MultiQuery + RRF.

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# bm25 = BM25Retriever.from_documents(docs); dense = vectorstore.as_retriever()
# ensemble = EnsembleRetriever(retrievers=[bm25, dense], weights=[0.4, 0.6])  # RRF inside
# In LangGraph: make "expand_queries" a node and "fuse" a node before "generate".
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Fusing raw similarity scores
```python
# Wrong: score_a + score_b  (different scales/metrics, not comparable)
# Right: fuse ranks with RRF, which ignores score scale
scores[doc_id] += 1.0 / (60 + rank)
```

❌ Mistake 2: Too many variants
```python
# Wrong: n=15 -> 15 retrievals, 3x latency, noisy drift
# Right: n=3-5 and keep the original query in the list
```

---

## 🧠 Tricky Interview Question
**Q**: "RAG Fusion improved recall but answer quality dropped. Why?"

**Answer**: Variants can drift from the intent, pulling in off-topic chunks that RRF promotes if they show up in several lists. Also the final context may contain more noise tokens. Fixes: instruct the LLM to stay on intent, keep the original query with a higher weight, rerank with a cross-encoder after fusion, and cut top-m.

---

## ⚫ Interview Questions + Answers

Q1: What is RRF? (Easy)
A1: A rank-merging formula: score = sum of 1/(k+rank) across lists. Documents ranked high in multiple lists score highest.

Q2: Why k=60? (Easy)
A2: A smoothing constant from the original RRF paper; it dampens the dominance of rank 1 versus rank 2 and works well without tuning.

Q3: RAG Fusion vs HyDE? (Medium)
A3: Fusion rewrites into several real queries; HyDE writes a hypothetical answer and embeds that. They can be combined.

Q4: Where does latency come from and how to cut it? (Medium)
A4: One LLM call for variants plus N retrievals. Run retrievals in parallel, use a small model, cache variants for repeated queries.

Q5: How do you evaluate fusion fairly? (Hard)
A5: Use a labelled set; compare recall@k, MRR, and end-to-end faithfulness for baseline vs fusion at equal latency budget. Segment by query type: fusion usually helps vague queries and may hurt precise ID lookups (e.g., exact HS code).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users write vague or short queries
- Vocabulary mismatch between users and documents

❌ Avoid when:
- Exact lookups (HS code, order ID)
- Tight latency budgets with no caching

---

## 📊 Visual Diagram
```
 Original Q ─► LLM ─► Q1, Q2, Q3, Q4
                         │
          ┌──────┬───────┼───────┬──────┐
          ▼      ▼       ▼       ▼      ▼
        list0  list1   list2   list3  list4   (retrieval)
          └──────┴───────┼───────┴──────┘
                         ▼
                 RRF: sum 1/(60+rank)
                         ▼
                  Top-m ─► (rerank) ─► LLM
```

---

## 💰 Cost Impact
Extra tokens: variant generation ~150 input + ~80 output tokens per query (about $0.00006 on gpt-4o-mini). Embedding N queries is tiny. Main cost is the bigger context if you keep more chunks. Optimise: cache variants, use top-m of 4-5, rerank to shrink context, use small model for expansion.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RRF | Reciprocal Rank Fusion | Rank मिलाने का फ़ॉर्मूला |
| Query expansion | Generate variants | Query के रूप बढ़ाना |
| Recall | Fraction of relevant found | कितने relevant मिले |
| MultiQueryRetriever | LangChain variants retriever | कई-query retriever |
| Ensemble | Combine retrievers | Retrievers का मेल |

---

## ⚡ 3-Line Summary
English: RAG Fusion creates multiple query variants and retrieves for each. RRF merges the ranked lists so consistently high chunks win. It boosts recall for vague queries at small extra cost.
Hindi: RAG Fusion कई query variants बनाकर हर एक के लिए retrieve करता है। RRF ranked lists मिलाता है ताकि बार-बार ऊपर आने वाले chunks जीतें। Vague queries पर recall बढ़ता है, cost थोड़ी बढ़ती है।

---

## ➡️ Next Topic
**228. Multi-Modal RAG** — retrieving over images, tables and PDFs, not just text.
