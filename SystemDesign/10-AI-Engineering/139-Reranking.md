# 139. Reranking
# हिंदी में: Reranking — पहली खोज (hybrid retrieval) से मिले 30–100 उम्मीदवारों को एक ज़्यादा समझदार model से दोबारा क्रम देना, ताकि सबसे सही 3–8 टुकड़े ही LLM तक पहुँचें — cross-encoders, LLM rerankers, MMR विविधता और latency budget

---

## 🔵 Simple Definition (English)
**Reranking** is a second-stage ranking step. A fast **first-stage retriever** (BM25, vector or hybrid) fetches many candidates (e.g., top 50), then a slower but more accurate **reranker** scores each candidate's relevance **to the specific query** and reorders them, so only the best few go to the LLM or user.
- **Bi-encoders** (embedding models) encode query and document **separately**, which is fast for retrieval over millions but less precise.
- **Cross-encoders / rerankers** take **(query, document) together** and output a relevance score. They're much more accurate because they read both jointly, but too slow to run over the whole corpus, so they're used only on candidates. Examples: Cohere Rerank, Voyage rerankers, Jina, BGE-reranker (open source, multilingual), ms-marco MiniLM.
- **LLM rerankers**: prompt an LLM to score or order passages (pointwise or listwise). Flexible but costlier.
- **Diversity reranking (MMR)**: avoid five near-duplicate chunks and keep relevant **and** diverse results.
Reranking typically gives one of the **largest quality gains per effort** in RAG.

## 🔵 सरल परिभाषा (Hindi)
Reranking = दूसरे चरण की ranking: पहले तेज़ retriever (BM25/vector/hybrid) 50 जैसे उम्मीदवार लाता है, फिर धीमा पर ज़्यादा सटीक reranker हर उम्मीदवार को उसी सवाल के हिसाब से score देकर दोबारा क्रम देता है — सिर्फ़ सबसे अच्छे कुछ LLM तक।
Bi-encoder (embedding) सवाल और document अलग-अलग पढ़ता है — करोड़ों पर तेज़, पर कम सटीक; cross-encoder (query, document) एक साथ पढ़कर score देता है — बहुत सटीक, पर सिर्फ़ उम्मीदवारों पर (Cohere Rerank, BGE-reranker, Jina); LLM reranker — लचीला पर महँगा; MMR — 5 लगभग एक जैसे chunks की जगह सही और विविध। RAG में मेहनत के हिसाब से सबसे बड़ा सुधार।

---

## 🔴 Problem it Solves
First-stage retrieval is optimized for **speed and recall**, not precision:
- Embedding similarity finds "related" text. For "What's the refund time for UPI?", the top results may include "UPI payment failures", "Refund policy for cards" and "How to add UPI ID", all similar but not answering the question.
- BM25 may rank a chunk higher just because it repeats "refund" many times.
- With top-k = 5 and no reranking, the actual answer chunk may sit at rank 9 and never reach the LLM, which then says "I don't know" or hallucinates.
- Sending 20 chunks "just in case" increases cost and latency and distracts the model.
A reranker **reads query and candidate together**, understanding nuances like "UPI vs card", negation and specificity, so the top 3–8 are truly relevant. Answers become more accurate with **fewer context tokens**.

## 🔴 यह क्यों बना? (Hindi)
पहली खोज तेज़ी और recall के लिए बनी है, सटीकता के लिए नहीं: "UPI refund में कितना समय?" पर ऊपर "UPI payment failure", "card की refund policy", "UPI ID कैसे जोड़ें" — सब मिलते-जुलते पर जवाब नहीं; BM25 किसी chunk को सिर्फ़ इसलिए ऊपर रखे कि उसमें "refund" बार-बार है; top-5 में reranking नहीं तो असली जवाब 9वें नंबर पर रह जाए और LLM "पता नहीं" कहे या गढ़े; "सुरक्षा के लिए" 20 chunks भेजो तो ख़र्च, देर और भटकाव।
Reranker सवाल और उम्मीदवार साथ पढ़कर बारीकियाँ (UPI बनाम card, निषेध) समझता है — कम tokens में ज़्यादा सही जवाब।

---

## 🟢 How it Works — Step by Step

### Two-stage retrieval

```
Corpus (millions of chunks)
   │  Stage 1: RETRIEVE (fast, high recall): hybrid BM25 + vector → top 50–100   ~30–100 ms
   ▼
Candidates (50)
   │  Stage 2: RERANK (accurate): cross-encoder scores each (query, chunk) pair → sort  ~100–300 ms
   ▼
Top 5–8 (+ diversity filter, score threshold) → LLM context
```

### Bi-encoder vs cross-encoder

```
Bi-encoder:   vec(q) ·  vec(d)       → d embeddings precomputed → millisecond search over millions
              (q and d never "see" each other → misses fine interactions)
Cross-encoder: model([q ; d]) → score  → full attention between query & doc tokens → precise
              cost ∝ number of candidates (can't precompute) → only for top-N
LLM reranker: "Rate relevance 0–3 of each passage to the question" or "Return passage IDs in order"
              → strong & flexible (multilingual, instructions like 'prefer latest policy'), but slower/costlier
```

### Choosing and tuning

```
Candidate depth N: larger N → higher recall ceiling, more rerank latency/cost (typical 30–100)
Output K: 3–8 chunks for RAG context (based on token budget)
Score threshold: drop candidates below a calibrated relevance score → enables "I don't know"
Multilingual: pick rerankers trained on many languages (Hindi/Hinglish) — evaluate!
Latency: batch pairs, GPU for self-hosted cross-encoders, truncate long chunks (e.g., 512 tokens), cache
         (query, doc) scores for frequent queries
Metrics: nDCG@k, MRR, precision@k on labelled pairs; end-to-end answer faithfulness/correctness
```

### Diversity: Maximal Marginal Relevance (MMR)

```
Problem: top-5 are near-duplicates (same FAQ copied across 3 articles)
MMR picks next doc maximizing: λ · relevance(d, q) − (1 − λ) · max_similarity(d, already_selected)
λ ≈ 0.7 → mostly relevance, some diversity; dedupe by doc_id/section too
```

### Business-aware reranking signals

```
Combine relevance with: recency (latest policy version), source authority (official policy > forum),
user context (product line, city, membership), popularity/click feedback → learning-to-rank for search
(But keep permission filtering BEFORE reranking — never rerank unauthorized docs)
```

## 🟢 कैसे काम करता है? (Hindi)
1. दो चरण: पहले hybrid (BM25 + vector) से करोड़ों में से 50–100 उम्मीदवार (~30–100 ms), फिर cross-encoder हर (सवाल, chunk) जोड़ी को score देकर क्रम (~100–300 ms) → top 5–8 + विविधता + score threshold → LLM।
2. Bi-encoder में सवाल और document एक-दूसरे को "देखते" नहीं (embeddings पहले से) — तेज़ पर बारीकी कम; cross-encoder दोनों को साथ पढ़ता है — सटीक पर सिर्फ़ उम्मीदवारों पर; LLM reranker निर्देश भी मान सकता है ("नई नीति को प्राथमिकता") पर धीमा/महँगा।
3. Tuning: उम्मीदवार N (30–100), output K (3–8), score threshold (कमज़ोर हटाओ ताकि "पता नहीं" कह सके), हिंदी/Hinglish वाले reranker की जाँच, लंबे chunks काटो, batch/GPU/cache; नाप: nDCG, MRR और अंत में जवाब की गुणवत्ता।
4. MMR: ऊपर के 5 लगभग एक जैसे न हों — relevance में से पहले चुने गए से समानता घटाकर अगला चुनो (λ ≈ 0.7); doc/section से भी dedupe।
5. Business संकेत जोड़ सकते हो: नई नीति, आधिकारिक स्रोत, यूज़र का product/शहर, clicks — पर permission filter reranking से पहले, अनधिकृत documents कभी rerank न हों।

---

## 🟡 Real World Example

**MS MARCO and BERT cross-encoders (2019)** — research showed that BERT-based cross-encoder rerankers on top of BM25 dramatically improved passage ranking on MS MARCO. That established the "retrieve then rerank" paradigm used in modern search.

**Cohere Rerank, Voyage and Jina rerankers** — hosted reranking APIs, including multilingual models, are widely used in RAG stacks because they add large precision gains with one API call. Open-source BGE-rerankers offer self-hosted multilingual alternatives.

**Anthropic Contextual Retrieval (2024)** — reported that adding reranking on top of contextual embeddings and BM25 reduced retrieval failures further, to about a 67% reduction in their tests versus the baseline.

**Web and e-commerce search** — Google, Bing, Amazon and Flipkart all use multi-stage ranking: cheap candidate generation, then progressively heavier ML rankers. RAG reranking is the same pattern applied to LLM context selection.

## 🟡 Real Example Hindi में
2019 में MS MARCO पर research ने दिखाया कि BM25 के ऊपर BERT cross-encoder reranker से passage ranking बहुत सुधरती है — "पहले ढूँढो, फिर rerank" का तरीका यहीं से; Cohere Rerank, Voyage, Jina (और open-source BGE-reranker) RAG में आम हैं — multilingual भी।
Anthropic के Contextual Retrieval (2024) में reranking जोड़ने से failures और घटे (~67% कमी); Google, Bing, Amazon, Flipkart सब कई चरणों वाली ranking करते हैं — सस्ते उम्मीदवार, फिर भारी ML rankers।

---

## 🟠 My Stack Example

### Hosted reranker (Cohere) on hybrid candidates (Python)
```python
import cohere
co = cohere.ClientV2()                                        # CO_API_KEY from env

async def rerank(query: str, candidates: list[Chunk], top_n: int = 6, threshold: float = 0.15) -> list[Chunk]:
    if not candidates: return []
    docs = [f"{c.title}\n{c.text[:2000]}" for c in candidates]          # include title; truncate long chunks
    res = co.rerank(model="rerank-v3.5", query=query, documents=docs, top_n=min(top_n * 2, len(docs)))
    ranked = [(candidates[r.index], r.relevance_score) for r in res.results]
    ranked = [(c, s) for c, s in ranked if s >= threshold]               # calibrated cut-off → enables "I don't know"
    for c, s in ranked: c.score = s
    return mmr_dedupe([c for c, _ in ranked], k=top_n)
```

### Self-hosted multilingual cross-encoder (sentence-transformers)
```python
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("BAAI/bge-reranker-v2-m3", max_length=512)   # multilingual (incl. Hindi); run on GPU in prod

def rerank_local(query: str, candidates: list[Chunk], top_n=6):
    scores = reranker.predict([(query, c.text) for c in candidates], batch_size=32)
    order = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [c for c, _ in order[:top_n]]
```

### MMR + doc-level dedupe
```python
import numpy as np
def mmr_dedupe(chunks: list[Chunk], k: int = 6, lam: float = 0.7):
    selected, seen_sections = [], set()
    pool = [c for c in chunks]
    vecs = {c.id: np.array(c.embedding) for c in pool}
    while pool and len(selected) < k:
        def mmr_score(c):
            sim = max((float(vecs[c.id] @ vecs[s.id]) for s in selected), default=0.0)
            return lam * c.score - (1 - lam) * sim
        best = max(pool, key=mmr_score); pool.remove(best)
        key = (best.doc_id, best.section)
        if key in seen_sections: continue                                 # one chunk per section
        seen_sections.add(key); selected.append(best)
    return selected
```

### LLM listwise reranker (when you need instruction-following, e.g., "prefer latest policy")
```python
def llm_rerank(query, candidates, k=5):
    listing = "\n".join(f'<p id="{i}" updated="{c.updated_at}">{c.text[:800]}</p>' for i, c in enumerate(candidates[:20]))
    r = client.messages.create(model="claude-haiku-5-5", max_tokens=60, temperature=0,
        system="Rank passages by how well they answer the question. Prefer the most recent policy when passages conflict. "
               "Return only a JSON array of the best passage ids, most relevant first.",
        messages=[{"role": "user", "content": f"<question>{query}</question>\n<passages>\n{listing}\n</passages>"}])
    ids = json.loads(r.content[0].text)[:k]
    return [candidates[i] for i in ids if isinstance(i, int) and 0 <= i < len(candidates)]
```

### Measure the gain (nDCG@5 with vs without reranking)
```python
def ndcg_at_k(ranked_ids, relevant: dict, k=5):
    dcg = sum(relevant.get(d, 0) / np.log2(i + 2) for i, d in enumerate(ranked_ids[:k]))
    ideal = sum(v / np.log2(i + 2) for i, v in enumerate(sorted(relevant.values(), reverse=True)[:k]))
    return dcg / ideal if ideal else 0.0
# Run on labelled queries: hybrid-only vs hybrid+rerank → keep reranker if nDCG & answer accuracy improve enough for its latency
```

---

## ⚫ Interview Questions + Answers

**Q1: Why add a reranker after retrieval?**
A1: First-stage retrievers (bi-encoder vectors, BM25) are built for speed and recall over huge corpora, so their top results contain related but non-answering passages. A cross-encoder reranker jointly reads the query with each candidate and scores true relevance, capturing nuances like product variants, negation and specificity. Reranking the top 30–100 candidates and keeping the best 3–8 raises precision, so the LLM gets better context with fewer tokens, improving answer accuracy, reducing hallucinations and cutting cost.

**Q2: Bi-encoder vs cross-encoder — what's the difference?**
A2: A bi-encoder embeds queries and documents independently into vectors, so document vectors can be precomputed and searched with ANN in milliseconds, but query-document interactions are limited to vector similarity. A cross-encoder processes the concatenated query and document through the model with full attention between them, producing a much more accurate relevance score. It can't be precomputed and costs one model pass per candidate, so it's used only on a small candidate set.

**Q3: How do you choose the number of candidates and outputs?**
A3: Candidate depth N sets the recall ceiling: the answer must be in the retrieved set for the reranker to surface it. Measure recall@N of first-stage retrieval and pick N where recall plateaus within the reranker's latency budget (often 30–100). Output K depends on the LLM's context budget and typical answer needs (often 3–8 chunks). Apply a calibrated score threshold so weak candidates are dropped, enabling "I don't know" behaviour. Tune both on a labelled eval set.

**Q4: When would you use an LLM as a reranker?**
A4: When you need ranking criteria beyond pure semantic relevance that are easy to express in instructions (prefer the latest policy version, prefer official sources, match the user's product or plan), when no good multilingual cross-encoder exists for your languages, or for low-volume, high-value queries. The trade-offs are higher latency and cost and the need to parse and validate structured outputs. A cheap fast model with listwise ranking of around 20 candidates is a common compromise.

**Q5: What is MMR and why use it?**
A5: Maximal Marginal Relevance selects results iteratively, maximizing a weighted combination of relevance to the query minus similarity to already-selected results. It prevents filling the context with near-duplicate chunks (the same FAQ copied across articles, or overlapping chunks), improving coverage of different relevant aspects and using the token budget efficiently. Combine it with simple dedupe by document or section.

---

## 🔷 Trade-offs
✅ Cross-encoder reranking: big precision gains — ❌ +100–300 ms, compute/API cost.
✅ Larger candidate depth: higher recall ceiling — ❌ more rerank latency.
✅ LLM rerankers: flexible criteria — ❌ slowest/costliest, output validation needed.
✅ MMR diversity: better coverage — ❌ may drop a slightly more relevant duplicate.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reranking | Second-stage reordering | दूसरे चरण में क्रम |
| First-stage retrieval | Fast candidate generation | तेज़ उम्मीदवार खोज |
| Bi-encoder | Separate query/doc embeddings | अलग-अलग embeddings |
| Cross-encoder | Joint query-doc scoring model | साथ पढ़कर score |
| Candidate depth | Number of candidates reranked | कितने उम्मीदवार |
| Relevance threshold | Minimum score to keep | रखने का न्यूनतम score |
| MMR | Relevance + diversity selection | प्रासंगिक + विविध चुनाव |
| nDCG / MRR | Ranking quality metrics | ranking गुणवत्ता नाप |
| Listwise reranking | Model orders a list at once | पूरी सूची एक साथ क्रम |
| Learning-to-rank | ML ranking with many signals | कई संकेतों से ML ranking |

---

## ⚡ 3-Line Summary
**English:**
1. Retrieve many (hybrid, top 30–100) fast, then rerank with a cross-encoder (or LLM) that reads query + candidate together; keep the best 3–8 for the LLM.
2. Tune candidate depth, output K and a calibrated threshold; use MMR/dedupe for diversity; pick multilingual rerankers for Indian languages.
3. Measure with nDCG/MRR and end-to-end answer quality; budget ~100–300 ms; apply permission filters before reranking.

**Hindi:**
1. पहले तेज़ी से 30–100 उम्मीदवार, फिर cross-encoder/LLM से rerank; LLM को सबसे अच्छे 3–8।
2. उम्मीदवार संख्या, K और threshold tune करो; MMR से विविधता; भारतीय भाषाओं के लिए multilingual reranker।
3. nDCG/MRR और जवाब की गुणवत्ता से नापो; ~100–300 ms budget; permission filter reranking से पहले।

---

## ➡️ Next Topic Suggestion
**140. Tool Use / Function Calling** — RAG answers from documents. Tools let the model check live data and take actions ("Where is my order?", "Raise a refund"). Next: defining tools, the tool-call loop, safety and design best practices.
