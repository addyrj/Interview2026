---

# 207. Cross-Encoder Reranking
# हिंदी में: Cross-Encoder Reranking

---

## 🔵 Simple Definition (English)
A cross-encoder is a transformer that takes the query and a chunk together as one input and outputs one relevance score. Because every query word can attend to every chunk word, it is much more accurate than comparing two separate embeddings.

## 🔵 सरल परिभाषा (Hindi)
Cross-encoder एक transformer है जो query और chunk को एक साथ एक input में लेकर एक relevance score देता है। हर query word हर chunk word को देख पाता है, इसलिए यह दो अलग embeddings की तुलना से ज़्यादा accurate है।

---

## 🔴 Problem it Solves
Bi-encoders (normal embeddings) compress a chunk into one vector without knowing the query. Subtle cases like negation ("not eligible"), numbers, and exact entities get lost. A cross-encoder reads both together and catches these details. The trade-off: you cannot precompute anything, so it only runs on the small candidate set.

## 🔴 यह क्यों बना? (Hindi)
Bi-encoder chunk को query जाने बिना एक vector में compress कर देता है। Negation ("not eligible"), numbers और exact entities जैसी बारीकियाँ खो जाती हैं। Cross-encoder दोनों को साथ पढ़कर ये पकड़ लेता है। Trade-off: कुछ भी precompute नहीं हो सकता, इसलिए यह सिर्फ़ छोटे candidate set पर चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Take query q and candidate chunk d
Step 2 → Build one input: [CLS] q [SEP] d [SEP]
Step 3 → Transformer runs full self-attention across q and d tokens together
Step 4 → [CLS] vector goes to a small linear head -> one score (logit)
Step 5 → Repeat for all N candidates (batched on GPU)
Step 6 → Sort by score, keep top-K
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Query q और candidate chunk d लो
Step 2 → एक input बनाओ: [CLS] q [SEP] d [SEP]
Step 3 → Transformer q और d के tokens पर साथ में self-attention चलाता है
Step 4 → [CLS] vector एक linear head से एक score देता है
Step 5 → सभी N candidates के लिए दोहराओ (GPU पर batch में)
Step 6 → Score से sort करो, top-K रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Query: "HS code for LED TV not exceeding 32 inch". Chunk A: "LED televisions above 32 inch: 8528.72 ...". Chunk B: "LED televisions up to 32 inch: 8528.72 ...". A bi-encoder scores both nearly the same. The cross-encoder reads "not exceeding" with "above" and "up to", and ranks B first. **Zomato AI**: matches "no onion no garlic dishes" against menu descriptions. **Amazon**: ranks answers to "does this fit 15 inch laptop".

## 🟡 Real Example Hindi mein
**Tariff System**: Query: "32 inch से ज़्यादा नहीं वाले LED TV का HS code"। Chunk A: "32 inch से ऊपर", Chunk B: "32 inch तक"। Bi-encoder दोनों को लगभग बराबर score देता है। Cross-encoder "not exceeding" को "above" और "up to" के साथ पढ़कर B को पहले रखता है। **Zomato**: "बिना प्याज़ लहसुन" को menu descriptions से match करता है। **Amazon**: "15 inch laptop में fit होगा?" के answers rank करता है।

---

## 💻 Code Example — Basic
```python
# Basic: scoring with a toy cross-encoder (pure Python) so it runs anywhere.
# Real usage is shown in comments below (needs sentence-transformers).
from typing import List, Tuple  # type hints

# Real model (optional, heavy download):
#   from sentence_transformers import CrossEncoder
#   model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
#   scores = model.predict([(query, doc) for doc in docs])


class ToyCrossEncoder:
    """Looks at query and doc TOGETHER (joint features), like a real cross-encoder."""

    def predict(self, pairs: List[Tuple[str, str]]) -> List[float]:
        scores: List[float] = []  # one score per pair
        for q, d in pairs:  # each (query, doc) pair
            qw, dw = q.lower().split(), d.lower().split()  # tokenise both
            s = float(sum(1 for w in qw if w in dw))  # word overlap
            if "not exceeding" in q.lower() and "up to" in d.lower():  # joint rule
                s += 3.0  # semantic match of the two phrases
            if "not exceeding" in q.lower() and "above" in d.lower():  # contradiction
                s -= 3.0  # penalise
            scores.append(s)  # store
        return scores  # list of floats


if __name__ == "__main__":
    query = "LED TV not exceeding 32 inch"  # query
    docs = [  # candidates
        "LED televisions above 32 inch HS 8528.72",
        "LED televisions up to 32 inch HS 8528.72",
    ]
    model = ToyCrossEncoder()  # build model
    scores = model.predict([(query, d) for d in docs])  # score all pairs
    for s, d in sorted(zip(scores, docs), reverse=True):  # best first
        print(f"{s:+.1f} {d}")  # display
```

## 💻 Code Example — Advanced
```python
# Production: batched, async-safe cross-encoder (runs the sync model in a thread).
import asyncio  # to_thread
import logging  # logging
from typing import Sequence  # typing

logger = logging.getLogger("cross_encoder")  # logger


class CrossEncoderReranker:
    """Lazy-loaded sentence-transformers CrossEncoder with batching and truncation."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
                 max_length: int = 512, batch_size: int = 32) -> None:
        self.model_name = model_name  # HF model id
        self.max_length = max_length  # tokens per pair (model limit)
        self.batch_size = batch_size  # pairs per forward pass
        self._model = None  # loaded on first use

    def _load(self):
        if self._model is None:  # load once
            from sentence_transformers import CrossEncoder  # heavy import, delayed
            self._model = CrossEncoder(self.model_name, max_length=self.max_length)  # load weights
        return self._model  # cached model

    def _score_sync(self, query: str, docs: Sequence[str]) -> list[float]:
        model = self._load()  # get model
        pairs = [(query, d) for d in docs]  # build pairs
        scores = model.predict(pairs, batch_size=self.batch_size)  # numpy array
        return [float(s) for s in scores]  # plain floats

    async def score(self, query: str, docs: Sequence[str]) -> list[float]:
        if not docs:  # nothing to do
            return []  # empty result
        try:  # model errors should not crash the request
            return await asyncio.to_thread(self._score_sync, query, docs)  # do not block the event loop
        except Exception as exc:  # OOM, missing package, etc.
            logger.exception("cross-encoder failed: %s", exc)  # log trace
            raise  # let caller use fallback (see topic 206)
```

---

## 🟠 FastAPI Integration
Load the model once at startup (lifespan), not per request. Run it in a thread so other requests keep flowing.

```python
from contextlib import asynccontextmanager  # lifespan helper
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

reranker: CrossEncoderReranker  # global, set at startup


@asynccontextmanager
async def lifespan(app: FastAPI):
    global reranker  # assign module variable
    reranker = CrossEncoderReranker()  # build
    await reranker.score("warmup", ["warmup"])  # warm up (loads weights)
    yield  # app runs here


app = FastAPI(lifespan=lifespan)  # attach lifespan


class RerankReq(BaseModel):
    query: str  # query
    documents: list[str]  # candidates
    top_k: int = 5  # keep


@app.post("/rerank")  # POST /rerank
async def rerank_route(req: RerankReq) -> list[dict]:
    scores = await reranker.score(req.query, req.documents)  # score
    ranked = sorted(zip(scores, req.documents), reverse=True)[: req.top_k]  # sort
    return [{"score": s, "text": d} for s, d in ranked]  # response
```

---

## 🔗 LangChain / LangGraph Connection
`langchain.retrievers.document_compressors.CrossEncoderReranker` accepts a `HuggingFaceCrossEncoder` from `langchain_community.cross_encoders`.

```python
from langchain.retrievers import ContextualCompressionRetriever  # wrapper
from langchain.retrievers.document_compressors import CrossEncoderReranker  # compressor
from langchain_community.cross_encoders import HuggingFaceCrossEncoder  # model wrapper

# model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")  # open-source reranker
# compressor = CrossEncoderReranker(model=model, top_n=5)  # keep 5
# retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=base)
# docs = retriever.invoke("HS code LED TV up to 32 inch")  # reranked docs
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Loading the model inside the request handler
✅ Correct: Load once at startup.

```python
# Wrong: 2-5 seconds per request
@app.post("/r")
async def r(q: str):
    m = CrossEncoder("BAAI/bge-reranker-base")  # reload every call
    return m.predict([(q, "x")])

# Right: global instance from lifespan (see above)
```

❌ Mistake 2: Ignoring max length truncation
✅ Correct: Chunk to fit (e.g. under 400 tokens) or the end of the chunk is silently cut.

```python
# Wrong: 1500-token chunk, only first 512 tokens are scored
scores = model.predict([(q, long_chunk)])

# Right: keep chunks small, or split long chunks and take max score
parts = [long_chunk[i:i + 1500] for i in range(0, len(long_chunk), 1500)]
score = max(model.predict([(q, p) for p in parts]))
```

---

## 🧠 Tricky Interview Question
**Q**: "A cross-encoder is more accurate than a bi-encoder. Why not use it for the whole retrieval over 5 million chunks?"

**Answer**: A cross-encoder needs one forward pass per (query, chunk) pair at query time, nothing can be precomputed. For 5M chunks that is 5M transformer runs per query, minutes of GPU time. A bi-encoder precomputes chunk vectors once and uses ANN search in milliseconds. So bi-encoder gives recall over millions, and cross-encoder gives precision over the top 30-100.

---

## ⚫ Interview Questions + Answers

Q1: What does a cross-encoder output?
A1: One relevance score (logit) for a (query, document) pair.

Q2: Can you store cross-encoder embeddings in a vector DB?
A2: No. It has no standalone document embedding; scoring needs the query at runtime.

Q3: Name some popular cross-encoder rerankers.
A3: `cross-encoder/ms-marco-MiniLM-L-6-v2` (small, fast), `BAAI/bge-reranker-base` and `bge-reranker-large`, `mixedbread-ai/mxbai-rerank` models.

Q4: How do you reduce cross-encoder latency?
A4: Smaller model, GPU, fp16, batching, fewer candidates (N=20-30), shorter chunks, ONNX/quantisation, and caching.

Q5: How would you fine-tune a cross-encoder on tariff data?
A5: Collect (query, relevant chunk, hard negatives) triples from user logs or labelled classifications. Mine hard negatives from the stage-1 retriever (similar but wrong HS codes). Train with a pairwise or listwise loss using sentence-transformers, evaluate NDCG@10 and recall on a held-out set, and compare against the off-the-shelf model before shipping.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need high precision on top-5
- You can host a small model (CPU okay for small N, GPU better)
- Data stays private (no external API)

❌ Avoid when:
- N is huge (hundreds) and latency is tight
- Documents are long and cannot be chunked
- You cannot maintain model infrastructure (consider a hosted API like Cohere)

---

## 📊 Visual Diagram
```
 Bi-encoder                      Cross-encoder
 ──────────                      ─────────────
 query ─► [Enc] ─► vq            [CLS] query [SEP] chunk [SEP]
 chunk ─► [Enc] ─► vd                      │
        cosine(vq, vd)             ┌───────▼────────┐
   (no interaction)                │  Transformer   │ full attention
                                   └───────┬────────┘
                                           ▼
                                      score = 7.3
```

---

## 💰 Cost Impact
- Open-source: no per-token API fee, but GPU/CPU hosting cost (a small MiniLM on CPU handles about 20-50 pairs per second per core, GPU much more).
- Saves LLM tokens by shrinking context (e.g. 10 chunks to 4).
- Optimise: N=20-30, truncate to 256-512 tokens, batch, quantise, cache by (query, chunk id).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cross-encoder | Joint query+doc transformer | साथ में पढ़ने वाला model |
| Logit | Raw score before sigmoid | कच्चा score |
| Hard negative | Similar but wrong example | मिलता-जुलता पर गलत उदाहरण |
| max_length | Max tokens per pair | प्रति pair token सीमा |
| Batch | Many pairs per forward pass | एक साथ कई pairs |

---

## ⚡ 3-Line Summary
English: A cross-encoder reads the query and chunk together and outputs one score, giving high precision. It is too slow for the whole corpus, so use it only on the top 20-100 candidates. Load once, batch, and watch the token limit.
Hindi: Cross-encoder query और chunk को साथ पढ़कर एक score देता है, जिससे precision ज़्यादा मिलती है। पूरे corpus पर यह बहुत धीमा है, इसलिए सिर्फ़ top 20-100 पर चलाओ। एक बार load करो, batch करो और token limit का ध्यान रखो।

---

## ➡️ Next Topic
**208. Cohere Reranker** — a hosted reranking API, so you get cross-encoder-quality without running your own model.
