# 138. Hybrid Search (BM25 + Vector)
# हिंदी में: Hybrid Search — keyword वाली खोज (BM25 — सटीक शब्द, IDs, codes) और vector वाली खोज (अर्थ, synonyms, दूसरी भाषा) दोनों को साथ चलाकर नतीजे मिलाना (fusion, जैसे RRF), ताकि दोनों की कमियाँ ढक जाएँ

---

## 🔵 Simple Definition (English)
**Hybrid search** runs **lexical (keyword) search**, typically **BM25**, and **semantic (vector) search** in parallel and **fuses** their ranked results:
- **BM25** scores documents by term matches, weighting rare terms higher (IDF) and normalizing by document length. It excels at **exact tokens**: order IDs, SKUs ("SM-A146B"), error codes ("UPI-U30"), names, numbers and rare jargon.
- **Vector search** excels at **meaning**: paraphrases, synonyms, typos and cross-lingual queries ("refund nahi aaya" ↔ "money not returned").
Fusion methods:
- **Reciprocal Rank Fusion (RRF)**: `score = Σ 1/(k + rank_i)` with k≈60. Simple, robust and doesn't need score normalization.
- **Weighted score combination**: normalize BM25 and cosine scores, then use `α·vector + (1−α)·bm25`.
- **Sparse-dense vectors**: learned sparse (SPLADE) or BM25 sparse vectors combined with dense vectors in one index (e.g., Pinecone, Qdrant, Weaviate, OpenSearch).
Hybrid retrieval followed by **reranking** (139) is the default best practice for RAG and site search.

## 🔵 सरल परिभाषा (Hindi)
Hybrid search = keyword खोज (BM25) और vector खोज साथ-साथ चलाकर नतीजे मिलाना: BM25 सटीक शब्दों में माहिर (order ID, SKU "SM-A146B", error code "UPI-U30", नाम, नंबर, दुर्लभ शब्द — दुर्लभ शब्द को ज़्यादा वज़न); vector अर्थ में माहिर (दूसरे शब्दों में कहा, synonyms, typos, दूसरी भाषा — "refund nahi aaya" ↔ "money not returned")।
मिलाने के तरीके: RRF (`1/(60 + rank)` जोड़ो — आसान और भरोसेमंद), weighted (scores normalize करके α से जोड़ना), sparse-dense vectors (एक ही index में)। Hybrid + reranking RAG और site search का सबसे अच्छा default।

---

## 🔴 Problem it Solves
Each method alone fails in predictable ways:
- **Vector-only** misses exact matches. "Error UPI-U30 while paying" may retrieve generic payment-failure articles instead of the one about U30. "iPhone 16 Pro 256GB" might return iPhone 15 pages (semantically similar). Numbers, codes, names and new jargon are weak spots.
- **Keyword-only** misses meaning. "Paise wapas kab milenge?" won't match "Refund timelines", and "cheap phone with good camera" won't match "budget smartphone with 50MP sensor". Typos and synonyms break it.
Real user queries (especially in India, mixing Hinglish, product codes and colloquial phrases) contain **both** kinds of signals. Hybrid search consistently improves **recall and robustness**, which matters because RAG answers can only be as good as what's retrieved.

## 🔴 यह क्यों बना? (Hindi)
अकेले हर तरीका अपने तरीके से fail होता है: सिर्फ़ vector — "Error UPI-U30" पर U30 वाले लेख की जगह आम payment failure लेख; "iPhone 16 Pro 256GB" पर iPhone 15 (अर्थ में मिलता-जुलता); नंबर, codes, नाम, नए शब्द कमज़ोर। सिर्फ़ keyword — "Paise wapas kab milenge?" से "Refund timelines" नहीं मिलता; "अच्छे camera वाला सस्ता फ़ोन" से "50MP sensor वाला budget phone" नहीं; typos/synonyms तोड़ देते हैं।
असली भारतीय सवालों में Hinglish, product codes और बोलचाल — दोनों तरह के संकेत; hybrid recall और मज़बूती बढ़ाता है — RAG का जवाब उतना ही अच्छा जितना retrieval।

---

## 🟢 How it Works — Step by Step

### BM25 in one minute

```
score(D, Q) = Σ_{term t in Q} IDF(t) · ( f(t,D) · (k1 + 1) ) / ( f(t,D) + k1 · (1 − b + b · |D|/avgdl) )
IDF: rare terms (U30, SKU) weigh more than common ones ("payment", "the")
f(t,D): term frequency in doc (saturates via k1 ≈ 1.2–2.0)
b ≈ 0.75: length normalization (long docs don't win just by size)
Needs: tokenization/analyzers (lowercase, stemming, stopwords; language-specific — Hindi analyzers,
       transliteration handling), inverted index (Postgres FTS, Elasticsearch/OpenSearch, Tantivy)
```

### Hybrid flow

```
Query "UPI-U30 error refund kab aayega"
   ├─► BM25 / full-text  → top 50 (strong on "U30", "UPI")
   └─► Vector (embedding) → top 50 (strong on "refund kab aayega" ≈ refund timeline)
            │ (same metadata filters on both: tenant, ACL, product, lang)
            ▼
   FUSION (RRF): for each doc d: RRF(d) = Σ_lists 1 / (60 + rank_list(d))
            ▼
   top 30–50 fused → RERANK (cross-encoder, Topic 139) → top 5–8 → LLM
```

### Why RRF is popular

```
- Uses ranks, not raw scores → no need to normalize incomparable BM25 vs cosine scales
- Robust default (k=60 from the original RRF paper), easy to implement, works with any number of lists
- Weighted variants: multiply each list's contribution by a weight if one retriever is more reliable
```

### Weighted score fusion (alternative)

```
norm_bm25 = (bm25 − min) / (max − min) per query ; norm_vec = cosine (already 0–1-ish)
final = α · norm_vec + (1 − α) · norm_bm25 ; tune α on eval set (e.g., 0.5–0.7)
Sensitive to score distributions → recheck when corpus or model changes
```

### Query-aware routing

```
Detect identifier-heavy queries (regex: order IDs, SKUs, error codes, phone/PIN) → weight BM25 higher
Natural-language / vernacular queries → weight vector higher
Exact-match filters for structured fields (order_id = …) instead of fuzzy search when possible
```

### Implementation options

```
Postgres: tsvector + GIN index (BM25-like ts_rank_cd; or pg_search/ParadeDB BM25 extension) + pgvector → fuse in SQL
OpenSearch/Elasticsearch: BM25 native + k-NN vectors + hybrid query with normalization/RRF pipelines
Pinecone/Qdrant/Weaviate: sparse-dense (BM25/SPLADE sparse vectors + dense) hybrid queries
Multilingual: index both native script & transliteration; language analyzers; synonyms dictionary
```

## 🟢 कैसे काम करता है? (Hindi)
1. BM25: सवाल के हर शब्द का document में मिलना गिनता है — दुर्लभ शब्द (U30, SKU) को ज़्यादा वज़न (IDF), बार-बार आने का असर सीमित (k1), लंबे document को फ़ायदा नहीं (b); इसके लिए tokenizer/analyzer (हिंदी, transliteration) और inverted index (Postgres FTS, Elasticsearch)।
2. Hybrid: एक ही सवाल पर BM25 के top 50 और vector के top 50 (दोनों पर वही filters — tenant, ACL, भाषा) → RRF से मिलाओ → 30–50 को rerank → 5–8 LLM को।
3. RRF: हर list में rank के हिसाब से `1/(60 + rank)` जोड़ो — scores normalize करने की ज़रूरत नहीं, आसान और भरोसेमंद; ज़रूरत हो तो किसी list को ज़्यादा वज़न।
4. Weighted fusion: दोनों scores 0–1 में लाकर α से जोड़ो (eval से α तय); सवाल देखकर routing — IDs/SKU/error codes वाले सवाल पर BM25 ज़्यादा, बोलचाल/हिंदी पर vector ज़्यादा; order_id जैसे fields के लिए सीधा exact filter।
5. लागू करने के तरीके: Postgres (tsvector + GIN + pgvector, SQL में fusion), OpenSearch/Elasticsearch (BM25 + k-NN + hybrid pipeline), Pinecone/Qdrant/Weaviate (sparse-dense); हिंदी के लिए native script + transliteration दोनों index, synonyms।

---

## 🟡 Real World Example

**RRF origin (Cormack et al., 2009)** — Reciprocal Rank Fusion was shown to outperform individual rankers and more complex fusion methods. It's now built into Elasticsearch, OpenSearch and many vector databases as the default hybrid strategy.

**Anthropic Contextual Retrieval (2024)** — combining contextual embeddings with **contextual BM25** reduced retrieval failures more than embeddings alone, and adding reranking improved further. That's strong evidence for hybrid plus rerank in RAG.

**E-commerce search (Flipkart, Amazon, Myntra)** — production search combines lexical matching (brand, model numbers, sizes) with semantic and learned ranking (intent, synonyms, vernacular queries), essentially hybrid retrieval with learning-to-rank on top.

**Support search for payments (Razorpay/Paytm/bank help centres)** — users paste error codes and transaction IDs alongside natural-language complaints, the classic case where BM25 catches the code and vectors catch the intent.

## 🟡 Real Example Hindi में
RRF (Cormack et al., 2009) ने अकेले rankers और जटिल तरीकों से बेहतर नतीजे दिखाए — आज Elasticsearch, OpenSearch और कई vector DBs का default; Anthropic के Contextual Retrieval (2024) में contextual embeddings + contextual BM25 से failures अकेले embeddings से ज़्यादा घटे, reranking से और।
Flipkart/Amazon/Myntra की search brand, model number, size जैसे सटीक शब्दों और अर्थ/vernacular सवालों दोनों को मिलाती है; Razorpay/Paytm/बैंक help centres में यूज़र error code और transaction ID के साथ शिकायत लिखते हैं — BM25 code पकड़ता है, vector इरादा।

---

## 🟠 My Stack Example

### Postgres: full-text + pgvector in one table, fused with RRF in SQL
```sql
ALTER TABLE kb_chunks ADD COLUMN fts tsvector
  GENERATED ALWAYS AS (to_tsvector('simple', coalesce(title,'') || ' ' || content)) STORED;   -- 'simple' keeps codes like U30 intact
CREATE INDEX kb_fts ON kb_chunks USING gin (fts);

-- $1 = query embedding, $2 = query text, $3 = tenant_id
WITH vec AS (
  SELECT id, row_number() OVER (ORDER BY embedding <=> $1) AS r
  FROM kb_chunks WHERE tenant_id = $3 ORDER BY embedding <=> $1 LIMIT 50
), kw AS (
  SELECT id, row_number() OVER (ORDER BY ts_rank_cd(fts, q) DESC) AS r
  FROM kb_chunks, websearch_to_tsquery('simple', $2) q
  WHERE tenant_id = $3 AND fts @@ q ORDER BY ts_rank_cd(fts, q) DESC LIMIT 50
)
SELECT c.id, c.title, c.url, c.content,
       COALESCE(1.0 / (60 + vec.r), 0) + COALESCE(1.0 / (60 + kw.r), 0) AS rrf
FROM kb_chunks c
LEFT JOIN vec ON vec.id = c.id LEFT JOIN kw ON kw.id = c.id
WHERE vec.id IS NOT NULL OR kw.id IS NOT NULL
ORDER BY rrf DESC LIMIT 40;
```

### Python helper: RRF over any number of ranked lists + query-aware weights
```python
import re
from collections import defaultdict

ID_PATTERN = re.compile(r"\b([A-Z]{2,}-?[A-Z0-9]{2,}|\d{6,})\b")      # error codes, SKUs, long numeric IDs

def rrf(ranked_lists: list[list[str]], weights: list[float] | None = None, k: int = 60) -> list[tuple[str, float]]:
    weights = weights or [1.0] * len(ranked_lists)
    scores = defaultdict(float)
    for w, lst in zip(weights, ranked_lists):
        for rank, doc_id in enumerate(lst, start=1):
            scores[doc_id] += w / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

async def hybrid_search(query: str, tenant_id: int, acl: list[str], k: int = 40):
    vec_ids = await vector_search(embed_query(query), tenant_id, acl, limit=50)       # list of ids
    kw_ids = await keyword_search(query, tenant_id, acl, limit=50)
    has_ids = bool(ID_PATTERN.search(query))
    fused = rrf([vec_ids, kw_ids], weights=[0.7, 1.3] if has_ids else [1.0, 1.0])  # identifier-heavy → favour BM25
    return await load_chunks([doc_id for doc_id, _ in fused[:k]])
```

### OpenSearch hybrid query (BM25 + k-NN) with a normalization pipeline
```json
PUT /_search/pipeline/hybrid-norm
{ "phase_results_processors": [ { "normalization-processor": {
    "normalization": { "technique": "min_max" },
    "combination": { "technique": "arithmetic_mean", "parameters": { "weights": [0.4, 0.6] } } } } ] }

GET /kb/_search?search_pipeline=hybrid-norm
{ "query": { "hybrid": { "queries": [
    { "match": { "content": "UPI-U30 error refund kab aayega" } },
    { "knn": { "embedding": { "vector": [0.01, -0.33, "..."], "k": 50 } } } ] } },
  "post_filter": { "term": { "tenant_id": 42 } } }
```

### Transliteration-aware indexing for Hindi/Hinglish
```python
def index_text(doc_text: str) -> str:
    # store native + romanized forms so "paneer" and "पनीर" both match lexically
    return doc_text + "\n" + transliterate_to_latin(doc_text) if has_devanagari(doc_text) else doc_text
```

---

## ⚫ Interview Questions + Answers

**Q1: Why use hybrid search instead of vector search alone?**
A1: Vector search captures semantic similarity (paraphrases, synonyms, cross-lingual matches) but is weak on exact tokens such as IDs, SKUs, error codes, names, numbers and rare jargon. BM25 keyword search nails exact terms but misses meaning, synonyms and typos. Real queries mix both signals, so running both and fusing the results improves recall and robustness across query types, which directly improves RAG answer quality, especially when followed by a reranker.

**Q2: Explain Reciprocal Rank Fusion.**
A2: RRF combines multiple ranked lists by summing, for each document, 1/(k + rank) across the lists where it appears, with k typically 60. It relies only on ranks, so it doesn't need score normalization between incomparable scoring systems like BM25 and cosine similarity. Documents ranked highly by several retrievers rise to the top. It's simple, robust, parameter-light, supports weights per list, and is widely implemented in search engines.

**Q3: How does BM25 work?**
A3: BM25 scores a document for a query by summing over query terms the term's inverse document frequency (rare terms weigh more) multiplied by a saturating function of the term's frequency in the document (controlled by k1), normalized by document length relative to the average (controlled by b). It requires an inverted index and analyzers for tokenization, case folding, stemming and stopwords, which must suit the languages involved.

**Q4: How would you implement hybrid search in Postgres?**
A4: Store a tsvector column (generated from title and content, with an appropriate text search configuration; 'simple' preserves codes) with a GIN index, alongside a pgvector embedding column with an HNSW index. Run both queries with the same tenant and ACL filters, each returning ranked top-N IDs (CTEs with row_number), then fuse with RRF in SQL or application code and pass the top results to a reranker. For true BM25 scoring, use an extension like ParadeDB's pg_search, or a search engine such as OpenSearch.

**Q5: How do you tune hybrid search?**
A5: Build a labelled retrieval eval set covering query types (natural language, Hinglish, identifier-heavy, typos). Measure recall@k and MRR for vector-only, BM25-only and hybrid configurations, then tune candidate depth per retriever, fusion method and weights (RRF k or score weights, α), analyzers (stemming, transliteration, synonyms), and query-aware routing that boosts BM25 for identifier queries. Re-run the evals when the corpus, embedding model or analyzers change.

---

## 🔷 Trade-offs
✅ Hybrid: best recall across query types — ❌ two indexes to maintain, slightly more latency.
✅ RRF: simple, robust — ❌ ignores score magnitudes (confidence).
✅ Weighted score fusion: uses confidence — ❌ requires normalization & tuning.
✅ Sparse-dense single index: one system — ❌ vendor-specific features.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hybrid search | Keyword + vector combined | keyword + vector साथ |
| BM25 | Classic keyword ranking function | keyword ranking का सूत्र |
| IDF | Rarity weight of a term | शब्द कितना दुर्लभ |
| Inverted index | Term → documents map | शब्द → documents सूची |
| Analyzer | Tokenization & normalization rules | शब्द तोड़ने के नियम |
| RRF | Reciprocal rank fusion | rank से मिलाना |
| Score normalization | Bring scores to same scale | scores एक पैमाने पर |
| Sparse vector | Mostly-zero term-weight vector | ज़्यादातर शून्य वाला vector |
| Dense vector | Embedding | embedding |
| Transliteration | Script conversion for matching | लिपि बदलकर मिलान |

---

## ⚡ 3-Line Summary
**English:**
1. BM25 catches exact terms (IDs, SKUs, codes, names); vectors catch meaning (paraphrase, synonyms, cross-lingual) — real queries need both.
2. Run both with identical filters, fuse with RRF (k≈60, optional weights) or normalized weighted scores, then rerank the top candidates.
3. Implement in Postgres (tsvector + pgvector), OpenSearch hybrid pipelines or sparse-dense vector DBs; tune analyzers, weights and routing with a retrieval eval set.

**Hindi:**
1. BM25 सटीक शब्द (ID, SKU, codes) पकड़ता है; vector अर्थ — असली सवालों को दोनों चाहिए।
2. दोनों एक जैसे filters के साथ, RRF से मिलाओ, फिर top उम्मीदवारों को rerank।
3. Postgres (tsvector + pgvector), OpenSearch या sparse-dense DBs में लागू; analyzers, वज़न और routing को eval से tune।

---

## ➡️ Next Topic Suggestion
**139. Reranking** — Hybrid retrieval gets good candidates. A reranker then picks the truly best few. Next: cross-encoders, LLM rerankers, latency budgets and how reranking boosts RAG precision.
