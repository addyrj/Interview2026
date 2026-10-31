---

# 247. MultiQueryRetriever
# हिंदी में: MultiQueryRetriever (एक सवाल, कई रूप)

---

## 🔵 Simple Definition (English)
`MultiQueryRetriever` uses an LLM to rewrite the user's question into several different versions (default 3), runs the retriever for each version, and returns the **unique union** of all results. It fixes the weakness that one badly-worded query may miss the right chunk.

## 🔵 सरल परिभाषा (Hindi)
`MultiQueryRetriever` LLM से user के सवाल को कई अलग तरीकों (default 3) में दोबारा लिखवाता है, हर version के लिए retriever चलाता है और सभी results का **unique union** लौटाता है। इससे वह कमज़ोरी ठीक होती है जहाँ एक खराब शब्दों वाली query सही chunk को miss कर देती है।

---

## 🔴 Problem it Solves
Vector search is sensitive to wording. A user types "mobile charger HS code" but the tariff note says "portable power supply units for telephones". The embeddings may be far apart, so the right chunk is not in the top-k. Users cannot be trained to write perfect queries.

## 🔴 यह क्यों बना? (Hindi)
Vector search शब्दों के प्रति sensitive है। User "mobile charger HS code" लिखता है, पर tariff note में "portable power supply units for telephones" लिखा है। Embeddings दूर हो सकते हैं और सही chunk top-k में नहीं आता। हम users को perfect query लिखना नहीं सिखा सकते, इसलिए LLM query के कई रूप बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User question: "mobile charger HS code"
Step 2 → LLM prompt: "Generate 3 different versions of this question"
Step 3 → LLM returns lines:  "HS code for phone charging adapters"
                             "Tariff heading for portable power supply"
                             "Customs classification of USB chargers"
Step 4 → An output parser splits the text by newline into 3 queries
Step 5 → retriever.invoke() runs for EACH query (original optional via include_original)
Step 6 → Results are merged and de-duplicated (by document content)
Step 7 → Unique documents go to the RAG prompt
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User सवाल: "mobile charger HS code"
Step 2 → LLM से कहा जाता है: "इस सवाल के 3 अलग versions बनाओ"
Step 3 → LLM तीन lines लौटाता है
Step 4 → Output parser newline से split करके 3 queries बनाता है
Step 5 → हर query के लिए retriever चलता है
Step 6 → Results merge होते हैं और duplicates हटते हैं
Step 7 → Unique documents RAG prompt में जाते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs officers write short, informal product names ("charger", "wall adapter"). MultiQuery expands it to "AC/DC power adapter", "static converter", "battery charger heading 8504". Heading 8504 ("static converters") is retrieved even though the user never used that word. Measure recall@k on your own labelled queries to confirm the gain.

**Zomato AI**: "something light for dinner" → "salad", "soup", "low-calorie meals" — three searches, one richer result list.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs officer छोटे, informal नाम लिखते हैं ("charger", "wall adapter")। MultiQuery इसे "AC/DC power adapter", "static converter", "battery charger heading 8504" में बदलता है। Heading 8504 मिल जाती है, भले user ने "static converter" शब्द कभी न लिखा हो। (Recall के numbers हर dataset पर अलग होते हैं, खुद measure करो।)

**Zomato AI**: "डिनर के लिए कुछ हल्का" → "salad", "soup", "low-calorie meals" — तीन searches, एक बेहतर list।

---

## 💻 Code Example — Basic
```python
# Basic: MultiQueryRetriever with a fake LLM (offline, no API key)
# pip install langchain-core langchain-classic
from langchain_core.documents import Document                          # Document type
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # scripted fake LLM
from langchain_core.retrievers import BaseRetriever                    # retriever base
from langchain_classic.retrievers import MultiQueryRetriever           # the star of this note


class KeywordRetriever(BaseRetriever):                                 # simple keyword retriever
    docs: list[Document]                                               # corpus
    k: int = 1                                                         # only 1 result per query

    def _get_relevant_documents(self, query: str, *, run_manager) -> list[Document]:
        words = set(query.lower().split())                             # query words
        scored = [(len(words & set(d.page_content.lower().split())), d) for d in self.docs]
        scored.sort(key=lambda p: p[0], reverse=True)                  # best first
        return [d for s, d in scored[: self.k] if s > 0]               # top-k with a match


corpus = [                                                             # tiny corpus
    Document(page_content="heading 8504 static converters battery chargers adapters"),
    Document(page_content="heading 8507 lithium power banks accumulators"),
    Document(page_content="heading 0901 coffee"),
]
base = KeywordRetriever(docs=corpus)                                   # base retriever
print("plain  :", [d.page_content[:12] for d in base.invoke("charger")])  # plain query finds one doc

fake_llm = FakeListChatModel(responses=[                               # LLM answer = 3 lines
    "wall adapter\nstatic converters\nlithium power banks"
])
mq = MultiQueryRetriever.from_llm(retriever=base, llm=fake_llm)        # wrap base with query generation
docs = mq.invoke("charger")                                            # runs 3 queries, merges results
print("multi  :", [d.page_content[:12] for d in docs])                 # more unique documents
```

## 💻 Code Example — Advanced
```python
# Production: custom prompt, include_original, tracing, async, error handling
# pip install langchain-core langchain-classic langchain-openai
import asyncio                                                         # async
import logging                                                         # logs
from langchain_core.documents import Document                          # doc type
from langchain_core.language_models import BaseChatModel               # llm type
from langchain_core.prompts import PromptTemplate                       # custom prompt
from langchain_core.retrievers import BaseRetriever                    # retriever type
from langchain_classic.retrievers import MultiQueryRetriever           # wrapper

logging.getLogger("langchain_classic.retrievers.multi_query").setLevel(logging.INFO)  # see generated queries
logger = logging.getLogger("tariff.multiquery")                        # our logger

TARIFF_PROMPT = PromptTemplate(                                        # domain-specific rewriting prompt
    input_variables=["question"],
    template=(
        "You help customs officers. Rewrite the product description below into 3 "
        "different search queries using official tariff vocabulary. "
        "One query per line, no numbering.\nProduct: {question}"
    ),
)


def build_multiquery(base: BaseRetriever, llm: BaseChatModel) -> MultiQueryRetriever:
    """Create retriever that also keeps the ORIGINAL query (safer: never worse than base)."""
    return MultiQueryRetriever.from_llm(
        retriever=base, llm=llm, prompt=TARIFF_PROMPT, include_original=True
    )


async def search(mq: MultiQueryRetriever, base: BaseRetriever, query: str) -> list[Document]:
    """Try multi-query; if the LLM step fails, fall back to the plain retriever."""
    try:
        return await asyncio.wait_for(mq.ainvoke(query), timeout=8.0)  # extra LLM call adds latency
    except Exception:                                                  # LLM down / timeout / parse error
        logger.exception("multiquery failed, falling back")            # keep traceback
        return await base.ainvoke(query)                               # degrade gracefully
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI                                   # FastAPI
from pydantic import BaseModel, Field                                  # schemas
from langchain_classic.retrievers import MultiQueryRetriever

app = FastAPI()                                                        # app


def get_mq() -> MultiQueryRetriever:
    raise NotImplementedError                                          # create once at startup


class Q(BaseModel):                                                    # request
    product: str = Field(min_length=2, max_length=300)


@app.post("/classify/candidates")                                      # candidate headings endpoint
async def candidates(q: Q, mq: MultiQueryRetriever = Depends(get_mq)) -> list[dict]:
    docs = await mq.ainvoke(q.product)                                 # async: LLM + N searches
    return [{"text": d.page_content, "meta": d.metadata} for d in docs]  # return evidence to the UI
```
Tip: expose the generated queries in debug logs; it makes poor results easy to explain.

---

## 🔗 LangChain / LangGraph Connection
```python
# In LCEL, MultiQueryRetriever is just another retriever in the context map:
chain = {"context": mq | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()

# In LangGraph, you may implement the same idea as explicit nodes:
#   node "rewrite"   -> llm creates N queries  (state["queries"])
#   node "retrieve"  -> runs retriever for each query (parallel / Send API)
#   node "dedupe"    -> merge by doc id
# This gives more control (budget limits, per-query logging) than the prebuilt class.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not de-duplicating / returning too many documents
```python
# Wrong — 3 queries x k=4 = up to 12 docs go to the LLM (3x tokens):
mq = MultiQueryRetriever.from_llm(retriever=store.as_retriever(search_kwargs={"k": 4}), llm=llm)

# Correct — lower base k, then cap the final list:
base = store.as_retriever(search_kwargs={"k": 2})
mq = MultiQueryRetriever.from_llm(retriever=base, llm=llm)
docs = mq.invoke(q)[:5]
```

❌ Mistake 2: Using an expensive model for rewriting
```python
# Wrong: gpt-4o just to paraphrase a question
mq = MultiQueryRetriever.from_llm(retriever=base, llm=ChatOpenAI(model="gpt-4o"))

# Correct: small, fast model with temperature 0
mq = MultiQueryRetriever.from_llm(retriever=base, llm=ChatOpenAI(model="gpt-4o-mini", temperature=0))
```

❌ Mistake 3: Custom prompt that does not output one query per line
```python
# Wrong — the default parser splits on newlines; numbered JSON breaks it:
template = "Return JSON list of queries for {question}"

# Correct — one query per line, no numbering (or pass a custom parser chain).
```

---

## 🧠 Tricky Interview Question

**Q**: "After adding MultiQueryRetriever, answers got worse for exact HS-code questions like 'What is 8507.60?'. Why?"

**Answer**: The LLM paraphrases the query and may drop or change the exact code ("lithium batteries heading", "rechargeable accumulators"). The paraphrases pull semantically similar but different chunks, pushing out the exact match. Fixes: use `include_original=True`, write a prompt that says "keep codes and numbers unchanged", route code-like queries to a keyword/BM25 path (EnsembleRetriever, topic 248), and evaluate per query type. Query expansion helps vague natural-language questions, not exact lookups.

---

## ⚫ Interview Questions + Answers

Q1: What does MultiQueryRetriever do? (Easy)
A1: Uses an LLM to generate several rephrasings of the user query, retrieves for each, and returns the unique union of documents.

Q2: Why does it improve recall? (Easy)
A2: Embedding search depends on wording. Different phrasings land near different chunks, so the union covers more relevant chunks than a single query.

Q3: What are the extra costs? (Medium)
A3: One extra LLM call (small) per question, N vector searches instead of 1, and more documents reaching the final prompt (more input tokens). Latency also increases by the LLM call time.

Q4: How can you see which queries were generated? (Medium)
A4: Set the logger `langchain_classic.retrievers.multi_query` (older: `langchain.retrievers.multi_query`) to INFO, or use LangSmith tracing / a callback handler.

Q5: How is it different from HyDE and from step-back prompting? (Hard)
A5: MultiQuery makes several paraphrases of the *question*. HyDE generates a hypothetical *answer* and embeds that (closer to document style). Step-back asks a more general question to fetch background context. They can be combined; choose with offline evaluation on your query set, since each helps different failure modes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users write vague, short or differently-worded queries
- Recall is the bottleneck (right chunk exists but is not retrieved)
- Corpus vocabulary differs from user vocabulary (domain jargon)

❌ Avoid when:
- Queries are exact lookups (IDs, codes) — use keyword search
- Latency or cost budgets are very strict
- The base retriever already has high recall

---

## 📊 Visual Diagram
```
                      "mobile charger HS code"
                                │
                                ▼
                       LLM (rewrite x3)
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
        "phone adapter"  "static converters"  "USB charger tariff"
              │                 │                  │
              ▼                 ▼                  ▼
          Retriever         Retriever          Retriever
              │                 │                  │
              └──────────┬──────┴──────────────────┘
                         ▼
               Unique union (dedupe)
                         ▼
                      RAG prompt
```

---

## 💰 Cost Impact
Extra rewrite call: ~80 input + ~60 output tokens on gpt-4o-mini ≈ $0.000048 — tiny. The real cost is more context: 3 queries × k=4 can mean up to 12 chunks × 500 tokens = 6,000 input tokens vs 2,000 (3x). On gpt-4o-mini that is $0.0009 vs $0.0003 per query; at 100K queries/day, +$60/day.

Optimise: lower base `k` to 2, cap final docs, combine with compression (topic 246), cache generated queries for repeated questions, and use a small model for rewriting.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Query expansion | Generating more query variants | Query के कई रूप बनाना |
| Union | Merge of all results | सभी results का मेल |
| De-duplication | Remove identical docs | Duplicate हटाना |
| `include_original` | Keep user's query too | असली query भी रखना |
| Recall | Fraction of relevant docs found | कितने सही docs मिले |
| HyDE | Embed a hypothetical answer | काल्पनिक जवाब से search |

---

## ⚡ 3-Line Summary
English: MultiQueryRetriever asks an LLM for several rephrasings, searches with each, and merges unique results. It boosts recall for vague queries but adds one LLM call and more context tokens. Keep the original query and avoid it for exact-code lookups.
Hindi: MultiQueryRetriever LLM से कई rephrasings बनवाता है, हर एक से search करता है और unique results मिलाता है। इससे vague queries पर recall बढ़ता है, पर एक extra LLM call और ज़्यादा tokens लगते हैं। Original query रखो और exact-code lookups में इसे मत लगाओ।

---

## ➡️ Next Topic
**248. EnsembleRetriever** — combine keyword (BM25) and vector search so both exact codes and meaning-based queries work.
