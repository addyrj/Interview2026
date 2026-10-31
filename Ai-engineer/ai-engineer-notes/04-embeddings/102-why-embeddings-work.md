---

# 102. Why Embeddings Work
# हिंदी में: Embeddings क्यों काम करते हैं

---

## 🔵 Simple Definition (English)
Embeddings work because a neural network is trained so that texts used in similar contexts get similar vectors. The idea comes from linguistics: "You shall know a word by the company it keeps" (the distributional hypothesis). After training on huge text, "earbuds" and "headphones" appear in similar sentences, so their vectors end up close together, and "banana" ends up far away.

## 🔵 सरल परिभाषा (Hindi)
Embeddings इसलिए काम करते हैं क्योंकि neural network को इस तरह train किया जाता है कि समान context में आने वाले texts के vectors समान हों। यह idea linguistics से आया है: "किसी शब्द को उसकी संगति से पहचानो" (distributional hypothesis)। बहुत सारे text पर training के बाद "earbuds" और "headphones" एक जैसे वाक्यों में आते हैं, इसलिए उनके vectors पास-पास आ जाते हैं, और "banana" दूर रहता है।

---

## 🔴 Problem it Solves
Keyword search matches letters, not meaning. Searching "wireless audio device for ears" finds nothing if the tariff text says "earphones, Bluetooth". Computers need a way to measure meaning similarity with numbers. Embeddings turn the fuzzy concept of meaning into geometry: closeness equals similarity.

## 🔴 यह क्यों बना? (Hindi)
Keyword search अक्षर match करता है, मतलब नहीं। "wireless audio device for ears" खोजने पर कुछ नहीं मिलता अगर tariff text में "earphones, Bluetooth" लिखा है। Computers को मतलब की समानता को numbers में नापने का तरीका चाहिए। Embeddings मतलब की धुंधली अवधारणा को geometry बना देते हैं: नज़दीकी यानी समानता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect a huge amount of text (billions of sentences)
Step 2 → Create a training task that needs meaning:
         predict a masked word, or pull matching pairs together
         (query <-> relevant passage) and push random pairs apart (contrastive learning)
Step 3 → The network turns each text into a vector (e.g. 1536 numbers)
Step 4 → Loss function: similar texts must have high cosine similarity, different texts low
Step 5 → Gradient descent adjusts weights millions of times
Step 6 → Result: directions in the vector space capture features (topic, sentiment, category)
Step 7 → At use time: embed text, compare vectors with cosine similarity, nearest = most similar meaning
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → बहुत बड़ी मात्रा में text जमा करो (अरबों वाक्य)
Step 2 → ऐसा training task बनाओ जिसमें मतलब चाहिए:
         masked शब्द predict करना, या matching pairs को पास लाना
         (query <-> relevant passage) और random pairs को दूर करना (contrastive learning)
Step 3 → Network हर text को vector में बदलता है (जैसे 1536 numbers)
Step 4 → Loss function: समान texts की cosine similarity ज़्यादा, अलग texts की कम
Step 5 → Gradient descent लाखों बार weights ठीक करता है
Step 6 → नतीजा: vector space की दिशाएँ features पकड़ती हैं (topic, sentiment, category)
Step 7 → Use के समय: text embed करो, cosine similarity से vectors compare करो, सबसे नज़दीकी = सबसे समान मतलब
```

---

## 🟡 Real World Example
**Tariff Classification System**: User writes "noise cancelling over-ear cans". The tariff database says "Headphones and earphones, whether or not combined with a microphone" (HS 8518.30). There is almost no word overlap, but the embedding vectors are close because both appear in similar contexts (audio, listening, electronics). Retrieval finds the right code, which a keyword search would miss.

**Amazon-style**: Searching "something to keep my coffee hot" returns thermos flasks and mug warmers.

## 🟡 Real Example Hindi mein
**Tariff System**: User लिखता है "noise cancelling over-ear cans"। Tariff database में है "Headphones and earphones, whether or not combined with a microphone" (HS 8518.30)। शब्द लगभग मेल नहीं खाते, पर embedding vectors पास हैं क्योंकि दोनों समान context में आते हैं (audio, सुनना, electronics)। Retrieval सही code ढूँढ लेता है जिसे keyword search चूक जाता।

**Amazon-style**: "something to keep my coffee hot" खोजने पर thermos flasks और mug warmers मिलते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny "learned from context" embedding built from co-occurrence counts.
# This demonstrates the SAME principle real models use, with pure Python (no libraries).
import math
from collections import defaultdict

corpus: list[str] = [                                   # tiny training text
    "wireless earbuds play music", "bluetooth headphones play music",
    "wireless headphones play audio", "earbuds play audio",
    "ripe banana tastes sweet", "ripe mango tastes sweet",
    "sweet banana is fruit", "mango is fruit",
]

# Step 1: count which words appear in the same sentence as which (the "company it keeps")
cooc: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
for sentence in corpus:
    words = sentence.split()
    for w in words:
        for c in words:
            if w != c:
                cooc[w][c] += 1                         # w appeared with context word c

vocab: list[str] = sorted({c for ctx in cooc.values() for c in ctx} | set(cooc))   # fixed dimension order

def vector(word: str) -> list[float]:
    """Embedding = counts of context words (one dimension per vocab word)."""
    return [float(cooc[word].get(c, 0)) for c in vocab]

def cosine(a: list[float], b: list[float]) -> float:
    """cos(angle) between vectors: 1 = same direction, 0 = unrelated."""
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0        # guard against zero vectors

for x, y in [("earbuds", "headphones"), ("banana", "mango"), ("earbuds", "banana")]:
    print(f"{x:>10} vs {y:<10} similarity = {cosine(vector(x), vector(y)):.2f}")
# Expect: earbuds~headphones high, banana~mango high, earbuds~banana low (meaning learned from context)
```

## 💻 Code Example — Advanced
```python
# Production: semantic search over tariff descriptions with OpenAI embeddings (async, batched).
import asyncio
import math
from typing import Optional
from openai import AsyncOpenAI, OpenAIError

client = AsyncOpenAI()
MODEL = "text-embedding-3-small"                        # 1536 dims, cheap

TARIFF_TEXTS: dict[str, str] = {
    "8518.30": "Headphones and earphones, whether or not combined with a microphone",
    "0803.90": "Bananas, fresh or dried",
    "6403.99": "Footwear with outer soles of rubber and uppers of leather",
}

def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))

async def embed(texts: list[str]) -> list[list[float]]:
    """One batched API call for many texts (cheaper and faster than one by one)."""
    response = await client.embeddings.create(model=MODEL, input=texts)
    return [d.embedding for d in response.data]          # order matches `texts`

async def search(query: str, top_k: int = 2) -> Optional[list[tuple[str, float]]]:
    """Return the best-matching HS codes for a free-text query."""
    try:
        codes = list(TARIFF_TEXTS)
        vectors = await embed([TARIFF_TEXTS[c] for c in codes] + [query])   # docs + query together
    except OpenAIError as exc:
        print("embedding failed:", exc)
        return None
    doc_vecs, q_vec = vectors[:-1], vectors[-1]
    scored = sorted(((c, cosine(q_vec, v)) for c, v in zip(codes, doc_vecs)),
                    key=lambda t: t[1], reverse=True)
    return scored[:top_k]

if __name__ == "__main__":
    print(asyncio.run(search("noise cancelling over-ear cans")))   # needs API key; expect 8518.30 first
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/search")
async def search_route(q: str, k: int = 3) -> dict:
    hits = await search(q, top_k=k)                      # embedding-based retrieval
    if hits is None:
        raise HTTPException(status_code=502, detail="embedding service unavailable")
    return {"query": q, "matches": [{"hs_code": c, "score": round(s, 3)} for c, s in hits]}
# In production: embed the tariff table ONCE at startup (or in a vector DB), embed only the query per request.
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

emb = OpenAIEmbeddings(model="text-embedding-3-small")
store = InMemoryVectorStore(embedding=emb)               # swap for Chroma/pgvector/Pinecone
store.add_texts(list(TARIFF_TEXTS.values()), metadatas=[{"hs": c} for c in TARIFF_TEXTS])
docs = store.similarity_search("noise cancelling over-ear cans", k=2)
# LangGraph: a "retrieve" node calls the store and writes docs to state for the "decide" node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking embeddings "understand" or store facts
✅ Correct: They capture similarity of usage; they can place opposites close (hot/cold appear in similar contexts) and are not a knowledge base.

```python
# Wrong: assume top-1 similarity = correct answer
# Right: retrieve top-K, then let an LLM/validator decide, and measure recall@K
```

❌ Mistake 2: Mixing vectors from different embedding models
✅ Correct: Query and documents must use the same model (same space and dimensions).

```python
# Wrong: docs embedded with text-embedding-3-small, query with text-embedding-3-large
# Right: one MODEL constant used for both
```

---

## 🧠 Tricky Interview Question

**Q**: "Why do 'The movie was good' and 'The movie was not good' often have very high cosine similarity, and why can that hurt a classifier?"

**Answer**: Embeddings are trained on context overlap and topical similarity; both sentences share the same words, topic and structure, so vectors are close even though the sentiment is opposite. Negation is a subtle signal. For tasks sensitive to polarity, use a cross-encoder/reranker or an LLM to check the final candidates, fine-tune the embedding on polarity-aware pairs, or combine embeddings with keyword/rule checks.

---

## ⚫ Interview Questions + Answers

Q1: What is the distributional hypothesis?
A1: Words used in similar contexts have similar meanings; the basis for learning embeddings.

Q2: What is cosine similarity?
A2: The cosine of the angle between two vectors; 1 means same direction (very similar), 0 unrelated, -1 opposite. It ignores vector length.

Q3: How are modern text embeddings trained?
A3: Transformer encoders trained with contrastive learning: matching pairs (query-passage, paraphrases) are pulled together, in-batch negatives are pushed apart.

Q4: Why do embeddings find synonyms keyword search misses?
A4: They compare meaning-in-context, not spelling, so "cans" near "headphones" can match.

Q5: What are the limits of embeddings?
A5: Weak on negation, exact identifiers (codes, SKUs), numbers and rare jargon; domain mismatch; fixed context length; language bias. Mitigate with hybrid search (BM25 + vectors), reranking, domain fine-tuning and evaluation on your own data.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Semantic search, recommendations, clustering, deduplication
- RAG retrieval

❌ Avoid when:
- Exact matching of IDs or codes (use keyword/SQL)
- Tiny datasets where simple rules work

---

## 📊 Visual Diagram
```
 Training pulls similar meanings together:

   "wireless earbuds"  ●──●  "bluetooth headphones"
                          \
                           ●  "noise cancelling cans"

   "ripe banana"  ■──■  "sweet mango"          (another region)

 Query vector ★ lands near ● cluster ─► nearest neighbours = relevant HS codes
 Similarity: cos(★, ●) high, cos(★, ■) low
```

---

## 💰 Cost Impact
Embedding calls are very cheap compared with chat models: `text-embedding-3-small` costs about $0.02 per 1M tokens (check current pricing). Embedding a 1M-token tariff manual costs cents; the main cost is storage and vector search infrastructure.
Optimise: embed documents once and store them, batch requests, embed only the query at runtime, cache query embeddings, choose smaller dimensions (the `dimensions` parameter on v3 models) to cut storage and search time.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Vector representing meaning | मतलब का vector |
| Distributional hypothesis | Similar context, similar meaning | समान context, समान मतलब |
| Cosine similarity | Angle-based similarity | Angle पर आधारित समानता |
| Contrastive learning | Pull similar, push different | समान पास, अलग दूर |
| Hybrid search | Keywords + vectors | Keywords + vectors साथ |
| Reranker | Re-scores top candidates | Top results को फिर जाँचना |

---

## ⚡ 3-Line Summary
English: Embeddings work because models learn that similar contexts mean similar meanings and encode this as closeness in vector space. Cosine similarity then finds related text even without shared words. They are great for retrieval but weak on negation and exact IDs.
Hindi: Embeddings इसलिए काम करते हैं क्योंकि models सीखते हैं कि समान context का मतलब समान अर्थ है और इसे vector space की नज़दीकी में encode करते हैं। Cosine similarity समान शब्दों के बिना भी संबंधित text ढूँढती है। Retrieval के लिए बढ़िया, पर negation और exact IDs में कमजोर।

---

## ➡️ Next Topic
**103. Vector Space — Visual Explanation** — seeing embeddings as points in space: distance, direction and clusters.
