---

# 392. sentence-transformers
# हिंदी में: sentence-transformers (text को embeddings में बदलना)

---

## 🔵 Simple Definition (English)
`sentence-transformers` (SBERT) is a Python library that turns sentences into fixed-size number vectors (embeddings) where similar meanings are close together. Install: `pip install sentence-transformers`. Typical model: `all-MiniLM-L6-v2` (384 dimensions, max 256 tokens).

## 🔵 सरल परिभाषा (Hindi)
`sentence-transformers` (SBERT) वाक्यों को fixed-size number vectors (embeddings) में बदलती है, जहाँ मिलते-जुलते अर्थ वाले वाक्य vector space में पास होते हैं। Install: `pip install sentence-transformers`। आम model: `all-MiniLM-L6-v2` (384 dimensions, अधिकतम 256 tokens)।

---

## 🔴 Problem it Solves
Keyword search fails when words differ: "how long for money back?" has no word in common with "Refunds take 5 business days". Embeddings capture meaning, so semantic search, duplicate detection, clustering and RAG retrieval work on meaning instead of exact words, and you can run the model locally for free.

## 🔴 यह क्यों बना? (Hindi)
Keyword search तब फेल होती है जब शब्द अलग हों: "how long for money back?" और "Refunds take 5 business days" में कोई common शब्द नहीं। Embeddings अर्थ पकड़ते हैं, इसलिए semantic search, duplicate detection, clustering और RAG retrieval अर्थ पर चलते हैं, और model local में मुफ़्त चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → SentenceTransformer("all-MiniLM-L6-v2") loads a pretrained transformer + pooling
Step 2 → model.encode(texts) tokenizes and runs the model in batches
Step 3 → Token vectors are pooled (mean) into ONE vector per sentence (384 numbers)
Step 4 → Compare vectors with cosine similarity (1.0 same meaning, ~0 unrelated)
Step 5 → Semantic search: encode corpus once, encode query, take top-k most similar
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → SentenceTransformer("all-MiniLM-L6-v2") pretrained model load करता है
Step 2 → model.encode(texts) batches में tokenize करके model चलाता है
Step 3 → Token vectors को pool करके हर वाक्य का एक vector (384 numbers) बनता है
Step 4 → Cosine similarity से तुलना (1.0 मतलब एक जैसा अर्थ, ~0 मतलब असंबंधित)
Step 5 → Corpus एक बार encode, query encode, top-k सबसे पास वाले चुनो
```

---

## 🟡 Real World Example
A Swiggy-style help center: embed all 5,000 FAQ answers once and store the vectors. When a user types "paisa wapas kab aayega", embed the query, find the closest FAQ vectors, and show the top 3 (or pass them to an LLM for RAG). The same idea finds duplicate listings or groups similar complaints.

## 🟡 Real Example Hindi mein
Swiggy जैसे help center में 5,000 FAQ answers को एक बार embed करके vectors सेव कर लें। User "paisa wapas kab aayega" लिखे तो query को embed करें, सबसे पास वाले FAQ vectors खोजें और top 3 दिखाएँ (या RAG के लिए LLM को दें)। इसी तरह duplicate listings और मिलती-जुलती शिकायतें भी मिलती हैं।

---

## 💻 Code Example — Basic
```python
# VERIFIED: ran with sentence-transformers 6.3.0 + torch 2.15 (model ~90 MB downloaded on first run, internet needed).
# Install: pip install sentence-transformers
from typing import List  # type hints

from sentence_transformers import SentenceTransformer, util  # model + similarity helpers

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # downloads once, then cached

sentences: List[str] = [  # three sentences to compare
    "How do I reset my password?",
    "I forgot my login password",
    "Best biryani in Hyderabad",
]
emb = model.encode(sentences, normalize_embeddings=True)  # numpy array, one row per sentence
print(emb.shape, emb.dtype)  # Output: (3, 384) float32

similar: float = util.cos_sim(emb[0], emb[1]).item()  # same topic (password)
different: float = util.cos_sim(emb[0], emb[2]).item()  # unrelated topic
print(round(similar, 2), round(different, 2))  # Output: 0.78 0.01   (exact digits can vary slightly)
print(model.get_sentence_embedding_dimension(), model.max_seq_length)  # Output: 384 256
```

## 💻 Code Example — Advanced
```python
# VERIFIED: ran on CPU with sentence-transformers 6.3.0, Python 3.13.
# Production style: encode corpus once, reuse for many queries, top-k search, input validation.
from typing import List, Tuple

import numpy as np  # for the norm check
from sentence_transformers import SentenceTransformer, util  # library

MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"  # small, fast, good quality


class SemanticSearch:
    """Tiny semantic search over a list of documents."""

    def __init__(self, docs: List[str], model_name: str = MODEL_NAME) -> None:
        if not docs:  # nothing to search
            raise ValueError("docs must not be empty")
        self.docs: List[str] = docs  # keep original texts
        self.model = SentenceTransformer(model_name)  # load once
        self.emb = self.model.encode(  # encode corpus once (the expensive part)
            docs, convert_to_tensor=True, normalize_embeddings=True, batch_size=32
        )

    def search(self, query: str, top_k: int = 2) -> List[Tuple[str, float]]:
        """Return the top_k most similar documents with scores."""
        if not query.strip():  # validate
            raise ValueError("query must not be empty")
        q = self.model.encode(query, convert_to_tensor=True, normalize_embeddings=True)  # 1 vector
        hits = util.semantic_search(q, self.emb, top_k=top_k)[0]  # list of dicts for first query
        return [(self.docs[h["corpus_id"]], round(float(h["score"]), 2)) for h in hits]


corpus: List[str] = [
    "Refunds take 5 business days",
    "Delivery is free above Rs 499",
    "You can reset your password from settings",
    "Biryani is a rice dish",
]
engine = SemanticSearch(corpus)  # build the index
print(engine.search("how long for money back?"))
# Output: [('Refunds take 5 business days', 0.67), ('You can reset your password from settings', 0.09)]

vecs = engine.model.encode(corpus)  # plain numpy output
print(type(vecs).__name__, vecs.shape)  # Output: ndarray (4, 384)
print(bool(np.allclose(np.linalg.norm(vecs, axis=1), 1, atol=1e-3)))  # Output: True
# all-MiniLM-L6-v2 already includes a Normalize layer, so its vectors have length 1.
# Other models may not, so pass normalize_embeddings=True if you rely on dot product == cosine.
```

---

## 🟠 JavaScript vs Python Comparison
In JS you would use Transformers.js (`feature-extraction` pipeline) or an embeddings API.

```python
# Python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
vec = model.encode("hello world")          # numpy array of 384 floats
```
```javascript
// JavaScript (Transformers.js)
import { pipeline } from "@huggingface/transformers";
const extractor = await pipeline("feature-extraction", "Xenova/all-MiniLM-L6-v2");
const out = await extractor("hello world", { pooling: "mean", normalize: true });
const vec = Array.from(out.data);           // 384 numbers
```

Key differences: Python gives a one-line `encode()` with batching, GPU support and utilities like `semantic_search`. In JS you configure pooling and normalization yourself. For similarity in JS you write dot-product code or use a vector DB.

---

## 🟠 FastAPI Connection
Load the model at startup, precompute the corpus embeddings, and expose a `/search` endpoint. Use `def` (not `async def`) because `encode()` is CPU-heavy and blocking.

```python
# FastAPI semantic search (structure shown; model loads ~90 MB at startup)
from contextlib import asynccontextmanager  # lifespan
from typing import Any, AsyncIterator, Dict, List
from fastapi import FastAPI, Query  # web + query validation
from sentence_transformers import SentenceTransformer, util  # embeddings

DOCS: List[str] = ["Refunds take 5 business days", "Delivery is free above Rs 499"]
state: Dict[str, Any] = {}  # model + embeddings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # load once
    state["model"] = model
    state["emb"] = model.encode(DOCS, convert_to_tensor=True, normalize_embeddings=True)  # precompute
    yield
    state.clear()


app = FastAPI(lifespan=lifespan)


@app.get("/search")
def search(q: str = Query(min_length=2, max_length=200), k: int = Query(2, ge=1, le=10)) -> List[Dict[str, Any]]:
    qv = state["model"].encode(q, convert_to_tensor=True, normalize_embeddings=True)  # embed query
    hits = util.semantic_search(qv, state["emb"], top_k=k)[0]  # best matches
    return [{"text": DOCS[h["corpus_id"]], "score": round(float(h["score"]), 3)} for h in hits]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Re-encoding the corpus for every query
```python
# Wrong: slow, wasteful
for q in queries:
    emb = model.encode(corpus + [q])

# Right: encode the corpus once, encode only the query each time
corpus_emb = model.encode(corpus)
```

❌ Mistake 2: Comparing embeddings from different models
```python
# Wrong: vectors from model A and model B live in different spaces (even dimensions can differ)
# Right: index and query with the SAME model name (store it with the index)
```

❌ Mistake 3: Ignoring the max sequence length
```python
# Wrong: all-MiniLM-L6-v2 silently truncates to 256 tokens, so the tail of long text is ignored
vec = model.encode(long_document)

# Right: split long text into chunks (e.g. 150-200 words) and embed each chunk
```

❌ Mistake 4: Using Euclidean distance or raw dot product on unnormalized vectors
```python
# Wrong: scores depend on vector length
# Right: cosine similarity (util.cos_sim) or normalize_embeddings=True and then dot product
```

---

## 🧠 Tricky Interview Question

**Q**: Why does `util.cos_sim(a, b)` of two unrelated sentences sometimes give a small negative number, and why can two opposite sentences ("I love it" / "I hate it") score high?

**Answer**: Cosine similarity ranges from -1 to 1, so unrelated texts land near 0 and can dip slightly below. Embedding models learn topical/semantic closeness, not logical truth, so sentences about the same subject with opposite sentiment still sit near each other. If sentiment or negation matters, add a cross-encoder or a classifier on top; do not trust bi-encoder similarity alone for contradictions.

---

## ⚫ Interview Questions + Answers

Q1: Bi-encoder vs cross-encoder?
A1: A bi-encoder (SentenceTransformer) embeds each text separately, so you can precompute corpus vectors and search fast. A cross-encoder reads the pair together (more accurate but slow). Common pattern: bi-encoder for top 50, cross-encoder to re-rank.

Q2: What is cosine similarity?
A2: The cosine of the angle between two vectors: dot(a, b) / (|a| |b|). With normalized vectors it equals the dot product.

Q3: What dimension are the vectors and why does it matter?
A3: all-MiniLM-L6-v2 gives 384 numbers. Dimension decides vector DB storage/RAM (4 bytes x dim per vector) and must match the index definition.

Q4: How do you search millions of vectors?
A4: Use an approximate nearest neighbor index (FAISS, pgvector, Qdrant, Pinecone, Chroma) instead of brute force.

Q5: How do you support Hindi/multilingual text?
A5: Use a multilingual model such as `paraphrase-multilingual-MiniLM-L12-v2` or a newer multilingual embedding model. English-only models handle Hindi poorly.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Semantic search, FAQ matching, recommendations, duplicate detection
- RAG retrieval with a free local embedder
- Clustering or classifying text by meaning

❌ Avoid when:
- Exact keyword/ID lookup (use SQL or full-text search)
- You cannot afford the model memory or latency (use a hosted embeddings API)
- You need precise logic such as negation (add a cross-encoder or LLM)

---

## 📊 Visual Diagram

```
"how long for money back?"                 corpus (encoded once)
        │ encode                            ┌ "Refunds take 5 business days"   -> [0.12, ...]
        ▼                                   ├ "Delivery is free above Rs 499"  -> [-0.4, ...]
   [0.10, -0.03, ... 384 numbers]           └ ...
        │
        └── cosine similarity with each ──► scores 0.67, 0.09, ...
                                            top_k = best documents
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Meaning as a vector | अर्थ का vector |
| Cosine similarity | Angle-based closeness | कोण पर आधारित समानता |
| Pooling | Combine token vectors | token vectors को मिलाना |
| Bi-encoder | Encode texts separately | texts अलग-अलग encode करना |
| Cross-encoder | Score a pair together | जोड़ी को साथ में score करना |
| Top-k | Best k results | सबसे अच्छे k नतीजे |

---

## ⚡ 3-Line Summary
English: sentence-transformers converts text to vectors where meaning is distance. Encode your corpus once, encode each query, and rank by cosine similarity. Chunk long text and use the same model for indexing and querying.
Hindi: sentence-transformers text को ऐसे vectors में बदलती है जहाँ दूरी अर्थ बताती है। Corpus एक बार encode करें, हर query encode करें और cosine similarity से rank करें। लंबा text chunk करें और index व query में एक ही model रखें।

---

## ➡️ Next Topic
**393. ChromaDB** (already written) to store these embeddings, then **398. TensorFlow Basics**.
