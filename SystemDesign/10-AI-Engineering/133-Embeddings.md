# 133. Embeddings
# हिंदी में: Embeddings — text (या image) का अर्थ संख्याओं की एक लंबी सूची (vector) में बदलना, ताकि मिलते-जुलते अर्थ वाली चीज़ें पास-पास हों: semantic search, RAG, recommendations, duplicate पहचान, clustering

---

## 🔵 Simple Definition (English)
An **embedding** is a **dense numeric vector** (e.g., 512–3072 numbers) that represents the **meaning** of a piece of text, image or other data, produced by an **embedding model**. Similar meanings map to **nearby vectors**:
- "Where is my order?" ≈ "मेरा ऑर्डर कहाँ है?" ≈ "order kab aayega" (close vectors, even across languages with multilingual models)
- "Where is my order?" vs "How to make paneer tikka?" (far apart)
Similarity is measured with **cosine similarity** (most common), **dot product** or **Euclidean distance**.
Embeddings power:
- **semantic search** and **RAG retrieval** (Topic 137)
- **recommendations** ("similar restaurants/products")
- **deduplication** and clustering of tickets and reviews
- **classification** with few labels, anomaly detection
- **dynamic few-shot** example selection (Topic 130)
Models: OpenAI `text-embedding-3-small/large`, **Voyage AI** (recommended by Anthropic, since Anthropic doesn't offer its own embedding model), Cohere Embed (multilingual), and open-source (BGE, E5/multilingual-E5, sentence-transformers). Multimodal: CLIP-style image+text embeddings.

## 🔵 सरल परिभाषा (Hindi)
Embedding = किसी text/image के अर्थ को संख्याओं की लंबी सूची (vector, जैसे 512–3072 numbers) में बदलना, embedding model से; मिलते-जुलते अर्थ = पास-पास vectors — "Where is my order?", "मेरा ऑर्डर कहाँ है?" और "order kab aayega" पास-पास (multilingual model हो तो भाषाएँ अलग होने पर भी), जबकि "paneer tikka कैसे बनाएँ" दूर।
दूरी cosine similarity से नापते हैं। उपयोग: semantic search, RAG, "मिलते-जुलते restaurants", duplicate tickets ढूँढना, clustering, classification। Models: OpenAI, Voyage AI (Anthropic इसी की सलाह देता है), Cohere, open-source (BGE, E5)।

---

## 🔴 Problem it Solves
Traditional **keyword search** (SQL `LIKE`, BM25) matches **words, not meaning**:
- "refund nahi aaya" won't match a help article titled "When will I get my money back?"
- "spicy veg starter" won't find "Paneer 65" or "Chilli Mushroom" unless those words appear.
- Users write in Hindi, Hinglish or with typos, and synonyms ("cold drink" vs "soft drink") are missed.
Embeddings let systems compare **semantic similarity**, enabling search and retrieval that understands intent, cross-lingual matching (Hindi query → English docs), and grouping of similar content at scale (millions of reviews or tickets). They're the backbone of RAG, where an LLM needs the most relevant context out of millions of documents.

## 🔴 यह क्यों बना? (Hindi)
पुरानी keyword search (SQL LIKE, BM25) शब्द मिलाती है, अर्थ नहीं: "refund nahi aaya" से "पैसे कब वापस मिलेंगे?" वाला लेख नहीं मिलता; "spicy veg starter" से "Paneer 65" नहीं मिलता अगर शब्द न हों; हिंदी/Hinglish/typos और synonyms ("cold drink" बनाम "soft drink") छूट जाते हैं।
Embeddings अर्थ की समानता नापते हैं — इरादा समझने वाली search, हिंदी सवाल से अंग्रेज़ी documents, लाखों reviews/tickets को समूहों में बाँटना — और RAG की रीढ़, जहाँ करोड़ों documents में से सबसे सही संदर्भ चाहिए।

---

## 🟢 How it Works — Step by Step

### From text to vector to similarity

```
"Where is my order?"  ──embedding model──►  [0.012, -0.338, 0.071, …, 0.204]   (e.g., 1024 dims)
"order kab aayega"    ──embedding model──►  [0.018, -0.301, 0.066, …, 0.198]
cosine_similarity(a, b) = (a · b) / (|a| |b|)  → 0.89 (very similar)
"paneer tikka recipe" → cosine with "Where is my order?" → 0.12 (unrelated)
If vectors are L2-normalized, cosine similarity == dot product (faster)
```

### Using embeddings for semantic search (offline + online)

```
OFFLINE (indexing):
  documents → clean → chunk (Topic 136) → embed each chunk (batch) → store vector + metadata
  (doc_id, title, url, language, tenant, updated_at, embedding_model_version) in vector DB (Topic 134)
ONLINE (query):
  user query → embed (same model!, "query" input type if supported) → nearest neighbours (top-k)
  → (optional) filter by metadata, hybrid with keyword (Topic 138), rerank (Topic 139) → results / RAG context
```

### Choosing an embedding model

```
Quality on YOUR data (build a small retrieval eval: queries + relevant docs → recall@k, MRR)
Multilingual support (Hindi, Tamil, Hinglish, code-mixed) → test explicitly
Dimensions: higher = more expressive but more storage/memory & slower search
   (some models support shortening dims, e.g., OpenAI `dimensions` param, Matryoshka-style)
Max input length (tokens per text) → affects chunk size
Query vs document asymmetry: some models take input_type="query"/"document" → use correctly
Cost & latency per 1M tokens, rate limits; hosting (API vs self-hosted open model for data residency)
Domain: code embeddings, legal/finance, e-commerce → specialized models may win
```

### Operational concerns

```
- Model versioning: embeddings from different models are NOT comparable → store model name/version;
  changing models = re-embed corpus (backfill job) + dual-write during migration
- Batch embedding (hundreds per request), retries, rate limits; cache embeddings by content hash
- Normalize text (strip boilerplate, unify whitespace) before embedding; keep raw text for display
- Storage math: 10M chunks × 1024 dims × 4 bytes ≈ 41 GB (float32) → consider 512 dims or
  half-precision/quantization
- Privacy: embeddings can leak information about source text → protect like the data itself
```

### Limitations

```
Weak on exact identifiers & numbers (order IDs, SKU "SM-A146B", "₹199") → combine with keyword/filters
Negation & fine logic ("not spicy") may be poorly captured
Domain shift: generic models may confuse domain terms → evaluate, consider domain models / fine-tuning
Similar ≠ relevant: retrieval returns similar text that may not answer the question → rerankers help
```

## 🟢 कैसे काम करता है? (Hindi)
1. Model हर text को vector में बदलता है; दो vectors की cosine similarity (0 से 1 के आसपास) बताती है अर्थ कितना मिलता है; normalized vectors पर cosine = dot product (तेज़)।
2. Offline: documents साफ़ करो → टुकड़ों (chunks) में बाँटो → batch में embed → vector DB में metadata (doc, भाषा, tenant, model version) के साथ; Online: सवाल को उसी model से embed (query type) → सबसे पास के top-k → filter/hybrid/rerank → नतीजे या RAG संदर्भ।
3. Model चुनो अपने डेटा के eval से (recall@k), हिंदी/Hinglish की जाँच ज़रूर, dimensions बनाम storage, अधिकतम input लंबाई, query/document type, ख़र्च, data residency के लिए self-hosted विकल्प।
4. अलग models के embeddings आपस में तुलनीय नहीं — model version save करो, model बदलो तो पूरा corpus दोबारा embed; content hash से cache; 1 करोड़ chunks × 1024 dims ≈ 41 GB — dims कम करो या quantize।
5. कमज़ोरी: order ID, SKU, ₹ राशि जैसे सटीक शब्द और "spicy नहीं" जैसा निषेध — keyword search/filters और reranker साथ में।

---

## 🟡 Real World Example

**word2vec (2013) → sentence embeddings** — Google's word2vec popularized learned word vectors ("king − man + woman ≈ queen"). Sentence-BERT (2019) and modern embedding models extended this to whole sentences and passages, the basis of today's semantic search.

**Pinterest, Spotify, YouTube recommendations** — use learned embeddings of users and items (e.g., Pinterest's PinSage graph embeddings) to find similar content at massive scale, the same "nearest neighbours in vector space" idea used for RAG.

**Swiggy's neural search (2023)** — Swiggy announced AI-powered "neural search" so users can search conversationally ("something light and healthy for dinner") instead of exact dish names, an example of embeddings-based semantic retrieval in Indian consumer apps.

**Multilingual retrieval for Bharat** — initiatives like AI4Bharat research and multilingual embedding models make it possible to match Hindi or Tamil queries to content in English or other Indian languages, important for vernacular help centres and government information services.

## 🟡 Real Example Hindi में
Google के word2vec (2013) ने शब्दों के vectors लोकप्रिय किए ("king − man + woman ≈ queen"); Sentence-BERT (2019) और आज के models पूरे वाक्यों/अनुच्छेदों के embeddings बनाते हैं; Pinterest, Spotify, YouTube की recommendations भी users और items के embeddings से "पास वाले" ढूँढती हैं।
Swiggy ने 2023 में AI वाली "neural search" बताई — "रात के लिए कुछ हल्का और healthy" जैसे बातचीत वाले सवाल; multilingual embeddings से हिंदी/तमिल सवाल को अंग्रेज़ी content से जोड़ना vernacular help centres और सरकारी सेवाओं में अहम।

---

## 🟠 My Stack Example

### Python: embed with Voyage (query vs document) and compare
```python
# pip install voyageai numpy
import voyageai, numpy as np
vo = voyageai.Client()                                  # VOYAGE_API_KEY from env

docs = ["When will I get my refund? Refunds reach the original payment method in 5–7 working days.",
        "How to change delivery address after placing an order",
        "Paneer tikka recipe with tandoori masala"]
doc_vecs = np.array(vo.embed(docs, model="voyage-3.5", input_type="document").embeddings)
q_vec = np.array(vo.embed(["refund nahi aaya abhi tak"], model="voyage-3.5", input_type="query").embeddings[0])

def cosine(a, b): return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
print([round(cosine(q_vec, d), 3) for d in doc_vecs])   # refund doc should score highest
```

### OpenAI embeddings with reduced dimensions (storage savings)
```python
from openai import OpenAI
oai = OpenAI()
r = oai.embeddings.create(model="text-embedding-3-small", input=["Where is my order?", "मेरा ऑर्डर कहाँ है?"], dimensions=512)
vecs = [d.embedding for d in r.data]                     # 512-dim vectors (smaller index, slight quality trade-off)
```

### Batch embedding job with content-hash cache + model version (Postgres)
```sql
CREATE TABLE embedding_cache (content_hash TEXT, model TEXT, embedding vector(1024), PRIMARY KEY (content_hash, model));
```
```python
import hashlib
MODEL = "voyage-3.5"
def embed_documents(texts: list[str]) -> list[list[float]]:
    hashes = [hashlib.sha256(t.encode()).hexdigest() for t in texts]
    cached = {r["content_hash"]: r["embedding"] for r in db.fetch(
        "SELECT content_hash, embedding FROM embedding_cache WHERE model=$1 AND content_hash = ANY($2)", MODEL, hashes)}
    missing = [(h, t) for h, t in zip(hashes, texts) if h not in cached]
    for i in range(0, len(missing), 128):                 # batch requests
        batch = missing[i:i + 128]
        vecs = vo.embed([t for _, t in batch], model=MODEL, input_type="document").embeddings
        db.executemany("INSERT INTO embedding_cache VALUES ($1,$2,$3) ON CONFLICT DO NOTHING", [(h, MODEL, v) for (h, _), v in zip(batch, vecs)])
        cached.update({h: v for (h, _), v in zip(batch, vecs)})
    return [cached[h] for h in hashes]
```

### Use case: find duplicate / similar support tickets (clustering)
```python
from sklearn.cluster import AgglomerativeClustering
X = np.array(embed_documents(ticket_texts)); X /= np.linalg.norm(X, axis=1, keepdims=True)
labels = AgglomerativeClustering(n_clusters=None, distance_threshold=0.35, metric="cosine", linkage="average").fit_predict(X)
# Large clusters today → emerging incident ("UPI payments failing in Pune") → alert ops
```

### Node: embed queries in an API (OpenAI SDK)
```js
import OpenAI from 'openai';
const openai = new OpenAI();
export async function embedQuery(q) {
  const r = await openai.embeddings.create({ model: 'text-embedding-3-small', input: q.trim().slice(0, 2000) });
  return r.data[0].embedding;
}
```

### Retrieval eval (recall@k) to choose a model
```python
def recall_at_k(model, evalset, k=5):
    hits = 0
    for ex in evalset:                                     # {"query": "...", "relevant_doc_ids": [...]}
        results = search(embed_query(ex["query"], model), k=k)
        hits += any(r.doc_id in ex["relevant_doc_ids"] for r in results)
    return hits / len(evalset)
# Compare voyage vs openai vs open-source on Hinglish + Hindi + English queries before committing
```

---

## ⚫ Interview Questions + Answers

**Q1: What are embeddings and how are they used?**
A1: Embeddings are dense vectors produced by a model such that semantically similar inputs map to nearby points in vector space. Similarity is computed with cosine similarity or dot product. They're used for semantic search and RAG retrieval, recommendations (similar items or users), deduplication and clustering, classification with few labels, anomaly detection and dynamic example selection. Typically you embed a corpus offline, store vectors with metadata in a vector index, and embed queries online to retrieve nearest neighbours.

**Q2: Cosine similarity vs dot product vs Euclidean distance?**
A2: Cosine similarity measures the angle between vectors, ignoring magnitude, and is the default for text embeddings. Dot product equals cosine when vectors are L2-normalized and is cheaper to compute, so many systems normalize and use the inner product. Euclidean (L2) distance measures straight-line distance, and for normalized vectors it's monotonically related to cosine. Use the metric the embedding model was trained or recommended for, and configure the vector index consistently.

**Q3: How do you choose an embedding model?**
A3: Evaluate candidates on your own data with a retrieval benchmark (real queries with known relevant documents, measuring recall@k and MRR), covering your languages (Hindi, Hinglish, regional) and domain terms. Also weigh dimensions (storage and memory and speed), max input length, query/document input types, cost and rate limits, latency, and hosting constraints such as data residency or self-hosting. Public leaderboards (like MTEB) are a starting point, not the decision.

**Q4: What happens when you change embedding models?**
A4: Vectors from different models live in different spaces and aren't comparable, so you must re-embed the entire corpus with the new model. Do it as a backfill job into a new index or column, dual-write new documents to both during migration, run retrieval evals comparing old and new, switch query embedding and search to the new index atomically, then retire the old one. Store the model and version alongside every vector to avoid mixing.

**Q5: What are limitations of embedding-based search?**
A5: Embeddings capture general semantic similarity but can miss exact matches (IDs, SKUs, codes, specific numbers and prices), handle negation and fine-grained constraints poorly, drift on domain jargon, and return content that's similar but doesn't answer the query. They also need re-indexing on model changes. Mitigate with hybrid search (BM25 plus vectors), metadata filters, rerankers, query rewriting and domain evaluation.

---

## 🔷 Trade-offs
✅ Semantic & cross-lingual matching — ❌ misses exact tokens/numbers (use hybrid).
✅ Higher dimensions: quality — ❌ storage, memory, latency.
✅ API embedding models: quality, no infra — ❌ cost, data leaves your VPC; self-hosted: control — ❌ GPU ops.
✅ Re-embedding with better models: quality gains — ❌ backfill cost & migration effort.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Vector representing meaning | अर्थ का vector |
| Vector | List of numbers | संख्याओं की सूची |
| Dimension | Length of the vector | vector की लंबाई |
| Cosine similarity | Angle-based similarity | कोण से समानता |
| Normalization | Scale vector to unit length | vector को इकाई लंबाई |
| Semantic search | Search by meaning | अर्थ से खोज |
| Multilingual embedding | Same space for many languages | कई भाषाओं का एक space |
| Query/document type | Asymmetric embedding inputs | सवाल/document के लिए अलग |
| Re-embedding | Recompute with new model | नए model से दोबारा |
| recall@k | Relevant item in top k? | top k में सही मिला? |

---

## ⚡ 3-Line Summary
**English:**
1. Embeddings map text/images to vectors where similar meaning = nearby; compare with cosine/dot product; power search, RAG, recommendations, dedupe, clustering.
2. Choose models via your own retrieval evals (incl. Hindi/Hinglish), mind dimensions/cost/residency, use query vs document input types.
3. Version embeddings (re-embed on model change), batch + cache by content hash, and combine with keyword search & reranking for exact terms.

**Hindi:**
1. Embeddings = अर्थ के vectors; पास = मिलता-जुलता; search, RAG, recommendations, duplicate, clustering।
2. Model अपने evals से चुनो (हिंदी/Hinglish भी), dimensions/ख़र्च का ध्यान, query/document type सही।
3. Model version रखो (बदलने पर दोबारा embed), batch + cache, सटीक शब्दों के लिए keyword search और reranking।

---

## ➡️ Next Topic Suggestion
**134. Vector Databases** — Millions of embeddings need fast nearest-neighbour search. Next: how vector databases work (HNSW, IVF, quantization), filtering, multi-tenancy, scaling, and how to choose one.
