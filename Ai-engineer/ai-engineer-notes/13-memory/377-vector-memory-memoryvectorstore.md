---

# 377. Vector Memory (MemoryVectorStore)
# हिंदी में: Vector Memory (MemoryVectorStore)

---

## 🔵 Simple Definition (English)
Vector memory saves each memory (a past message or fact) as an embedding vector. When a new question arrives, you embed it and fetch the top-k most similar memories. `MemoryVectorStore` (LangChain.js) and `InMemoryVectorStore` (Python `langchain_core`) keep these vectors in RAM.

## 🔵 सरल परिभाषा (Hindi)
Vector memory हर memory (पुराना message या fact) को embedding vector के रूप में save करती है। नया सवाल आने पर उसे embed करके सबसे similar top-k memories निकाली जाती हैं। `MemoryVectorStore` (LangChain.js) और `InMemoryVectorStore` (Python `langchain_core`) ये vectors RAM में रखते हैं।

---

## 🔴 Problem it Solves
Sliding windows forget old turns; entity memory needs exact names. Users ask in different words ("duty on laptops" vs "HS code for notebooks"). Vector memory recalls by meaning, from thousands of past items, without sending them all to the LLM.

## 🔴 यह क्यों बना? (Hindi)
Sliding window पुरानी बातें भूल जाती है; entity memory को exact नाम चाहिए। Users अलग शब्दों में पूछते हैं ("laptops पर duty" बनाम "notebooks का HS code")। Vector memory meaning से, हज़ारों पुरानी memories में से, बिना सब LLM को भेजे recall करती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Turn finishes; decide what is worth remembering
Step 2 → Embed the memory text (e.g. text-embedding-3-small)
Step 3 → Store (vector, text, metadata like user_id, time)
Step 4 → New query arrives; embed it
Step 5 → Cosine similarity against stored vectors
Step 6 → Take top-k (k = 3-5) above a score threshold
Step 7 → Put those texts into the prompt
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Turn खत्म होता है; तय करो क्या याद रखना है
Step 2 → Memory text को embed करो (जैसे text-embedding-3-small)
Step 3 → (vector, text, metadata जैसे user_id, time) store करो
Step 4 → नया query आता है; उसे embed करो
Step 5 → Stored vectors से cosine similarity निकालो
Step 6 → Threshold से ऊपर वाले top-k (k = 3-5) लो
Step 7 → उन texts को prompt में डालो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Past resolved cases are saved: "Bluetooth speaker classified under 8518.22, ruling dated 2024". A new user asks "wireless audio box duty?" - no shared keywords, but the embedding is close, so the earlier ruling is recalled. **Amazon-style**: remember "user bought a size-42 running shoe" and recall it when they ask "good sneakers for me?".

## 🟡 Real Example Hindi mein
**Tariff System**: पुराने solved cases save हैं: "Bluetooth speaker 8518.22 में classify हुआ, 2024 ruling"। नया user पूछता है "wireless audio box पर duty?" - शब्द मिलते नहीं, पर embedding पास है, इसलिए पुराना ruling recall हो जाता है। **Amazon-style**: "user ने size-42 running shoe खरीदा" याद रखो और "मेरे लिए अच्छे sneakers?" पर recall करो।

---

## 💻 Code Example — Basic
```python
# Pure Python vector memory with a toy bag-of-words "embedding" - runs offline
import math                                              # for sqrt in cosine similarity
from collections import Counter                          # word counts

def embed(text: str) -> Counter:
    """Toy embedding: word-count vector (real apps use an embedding model)."""
    return Counter(text.lower().split())                 # word -> count

def cosine(a: Counter, b: Counter) -> float:
    """Cosine similarity between two sparse vectors."""
    dot = sum(a[w] * b[w] for w in a if w in b)          # dot product on shared words
    na = math.sqrt(sum(v * v for v in a.values()))       # length of a
    nb = math.sqrt(sum(v * v for v in b.values()))       # length of b
    return dot / (na * nb) if na and nb else 0.0         # avoid divide by zero

class VectorMemory:
    def __init__(self) -> None:
        self.items: list[tuple[Counter, str]] = []       # (vector, original text)

    def add(self, text: str) -> None:
        self.items.append((embed(text), text))           # store vector + text

    def search(self, query: str, k: int = 2) -> list[str]:
        q = embed(query)                                 # embed the query
        scored = sorted(self.items, key=lambda it: cosine(q, it[0]), reverse=True)   # best first
        return [text for _, text in scored[:k]]          # top-k texts

mem = VectorMemory()                                     # new memory
mem.add("bluetooth speaker classified under 8518.22")    # past case 1
mem.add("cotton t-shirt classified under 6109.10")       # past case 2
print(mem.search("duty on bluetooth speaker", k=1))      # finds the speaker case
```

## 💻 Code Example — Advanced
```python
# Production: async embeddings, threshold, per-user filter, error handling
import asyncio                                           # async runtime
import logging                                           # log problems
import numpy as np                                       # fast vector math
from openai import AsyncOpenAI, OpenAIError              # openai>=1 client

log = logging.getLogger("vector_memory")                 # logger

class AsyncVectorMemory:
    def __init__(self, model: str = "text-embedding-3-small") -> None:
        self.client = AsyncOpenAI()                      # needs OPENAI_API_KEY
        self.model = model                               # embedding model
        self.vectors: list[np.ndarray] = []              # normalised vectors
        self.rows: list[dict[str, str]] = []             # text + metadata per vector

    async def _embed(self, texts: list[str]) -> list[np.ndarray]:
        resp = await self.client.embeddings.create(model=self.model, input=texts)   # one batched call
        vecs = [np.array(d.embedding, dtype=np.float32) for d in resp.data]         # to numpy
        return [v / np.linalg.norm(v) for v in vecs]     # normalise so dot = cosine

    async def add(self, text: str, user_id: str) -> None:
        try:
            (vec,) = await self._embed([text])           # embed one memory
        except OpenAIError as exc:                       # API failure
            log.error("embed failed: %s", exc)           # log it
            return                                       # skip, do not crash the chat
        self.vectors.append(vec)                         # save vector
        self.rows.append({"text": text, "user_id": user_id})   # save payload

    async def search(self, query: str, user_id: str, k: int = 3, min_score: float = 0.3) -> list[str]:
        if not self.vectors:                             # nothing stored yet
            return []
        try:
            (q,) = await self._embed([query])            # embed query
        except OpenAIError as exc:
            log.error("query embed failed: %s", exc)
            return []                                    # degrade gracefully
        scores = np.stack(self.vectors) @ q              # cosine for all memories at once
        order = np.argsort(-scores)                      # best first
        out: list[str] = []                              # results
        for i in order:                                  # walk by score
            if self.rows[i]["user_id"] != user_id or scores[i] < min_score:   # filter user + threshold
                continue
            out.append(self.rows[i]["text"])             # keep it
            if len(out) == k:                            # enough results
                break
        return out

async def main() -> None:
    m = AsyncVectorMemory()                              # create
    await m.add("Speaker ruling 8518.22", "u1")          # store
    print(await m.search("wireless audio box", "u1"))    # recall

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI                              # web framework
from pydantic import BaseModel                           # request models

app = FastAPI()                                          # app
memory = AsyncVectorMemory()                             # one shared instance (use pgvector/Qdrant in prod)

class MemIn(BaseModel):
    user_id: str                                         # owner
    text: str                                            # memory or query

@app.post("/memory")
async def save(body: MemIn) -> dict[str, str]:
    await memory.add(body.text, body.user_id)            # embed + store
    return {"status": "saved"}                           # ack

@app.post("/recall")
async def recall(body: MemIn) -> dict[str, list[str]]:
    return {"memories": await memory.search(body.text, body.user_id)}   # top-k for this user
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.vectorstores import InMemoryVectorStore   # Python "MemoryVectorStore"
from langchain_openai import OpenAIEmbeddings                 # embedding model wrapper

store = InMemoryVectorStore(OpenAIEmbeddings(model="text-embedding-3-small"))   # RAM store
store.add_texts(["Speaker ruling 8518.22"], metadatas=[{"user_id": "u1"}])      # save memory
retriever = store.as_retriever(search_kwargs={"k": 3})        # retriever for LCEL chains
docs = retriever.invoke("wireless audio box")                  # recall by meaning
# LangGraph: call retriever in a "recall" node and write results into state["memories"].
# JS equivalent: new MemoryVectorStore(new OpenAIEmbeddings()).
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No user filter - one user sees another's memories
✅ Correct: always filter by `user_id` (metadata filter).

```python
# Wrong
store.similarity_search(q, k=3)
# Right
store.similarity_search(q, k=3, filter=lambda d: d.metadata["user_id"] == uid)
```

❌ Mistake 2: Using an in-memory store in production (lost on restart)
✅ Correct: use pgvector, Qdrant, Chroma or Pinecone for persistence.

```python
# Wrong - vanishes on deploy
store = InMemoryVectorStore(emb)
# Right - persistent
# store = PGVector(embeddings=emb, connection=DB_URL, collection_name="memory")
```

---

## 🧠 Tricky Interview Question
**Q**: "Vector memory returns an old, wrong fact ('origin China') though the user later said 'Vietnam'. Why?"

**Answer**: Similarity has no notion of time or truth - both memories are similar to the query. Fix: store timestamps and re-rank by recency, supersede/delete old memories when a conflicting fact is saved, or store facts as updatable entity attributes and use vectors only for fuzzy lookup.

---

## ⚫ Interview Questions + Answers

Q1: What is stored in vector memory? (Easy)
A1: Embedding vector plus original text plus metadata for each memory.

Q2: Is `MemoryVectorStore` production-safe? (Easy)
A2: No. It lives in RAM and is lost on restart; use a persistent vector DB.

Q3: How do you choose k and the score threshold? (Medium)
A3: Start with k=3-5, threshold around 0.3-0.5 for normalised cosine, then tune on real queries; too high loses recall, too low adds noise tokens.

Q4: How is it different from RAG? (Medium)
A4: Same mechanism, different source: RAG searches a document corpus; vector memory searches the conversation's own saved memories and is written to at runtime.

Q5: How do you scale and keep it fresh? (Hard)
A5: ANN index (HNSW) in pgvector/Qdrant, partition by user, recency-weighted scoring, dedupe by similarity before insert, TTL or importance-based eviction, and periodic consolidation of similar memories into one.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many past items, queries phrased differently
- Fuzzy recall by meaning is acceptable

❌ Avoid when:
- Exact facts required (use entity/key-value)
- Tiny history (just send it)
- Strict latency with no embedding budget

---

## 📊 Visual Diagram
```
 save:   text ──embed──► vector ──► [ store: vec | text | user_id ]
 recall: query ─embed─► qvec ──cosine──► top-k ──► prompt
```

---

## 💰 Cost Impact
text-embedding-3-small costs about $0.02 per 1M tokens, so embedding a 50-token memory is about $0.000001 - almost free. The real saving is prompt size: 3 recalled memories (about 100 tokens) replace thousands of history tokens. Optimise: embed only important turns, batch embeddings, cache query embeddings, cap k.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Number vector capturing meaning | meaning का number vector |
| Cosine similarity | Angle-based closeness | vectors की समानता |
| top-k | Best k matches | सबसे अच्छे k results |
| Threshold | Minimum score to accept | न्यूनतम score |
| ANN | Approximate nearest neighbour search | तेज़ approximate search |

---

## ⚡ 3-Line Summary
English: Vector memory stores memories as embeddings and recalls the closest ones by meaning. The in-memory store is for demos; production needs a persistent vector DB with user filters. Add recency and conflict handling.
Hindi: Vector memory memories को embeddings में रखती है और meaning से सबसे पास वाली recall करती है। In-memory store सिर्फ़ demo के लिए है; production में persistent vector DB और user filter चाहिए। Recency और conflict handling जोड़ो।

---

## ➡️ Next Topic
**378. Zep Memory Server** - a managed memory service that automates extraction, summaries and retrieval.
