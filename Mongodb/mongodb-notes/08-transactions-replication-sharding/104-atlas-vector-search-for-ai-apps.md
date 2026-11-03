# 104. Atlas Vector Search for AI Apps
# हिंदी में: AI Apps के लिए Atlas Vector Search

---

## 🔵 Simple Definition (English)
**Vector Search** finds documents by **meaning** instead of exact words. An embedding model (OpenAI, Voyage AI, Cohere, a local model) turns text or images into a list of numbers (a **vector**, e.g. 1536 floats). Similar meanings produce nearby vectors. **Atlas Vector Search** stores those vectors in a normal document field, builds an approximate-nearest-neighbour (ANN) index (HNSW) over them, and lets you query with the `$vectorSearch` aggregation stage. It is the retrieval half of **RAG** (Retrieval-Augmented Generation): fetch the most relevant chunks, then give them to an LLM as context.

## 🔵 सरल परिभाषा (Hindi)
**Vector Search** documents को exact शब्दों की जगह **मतलब** से खोजता है। Embedding model (OpenAI, Voyage AI, Cohere, local model) text या image को numbers की list (**vector**, जैसे 1536 floats) में बदलता है। मिलते-जुलते मतलब के vectors पास-पास होते हैं। **Atlas Vector Search** इन vectors को normal document field में रखता है, उन पर approximate-nearest-neighbour (ANN) index (HNSW) बनाता है, और `$vectorSearch` aggregation stage से query करने देता है। यह **RAG** (Retrieval-Augmented Generation) का retrieval हिस्सा है: सबसे relevant chunks लाओ, फिर LLM को context की तरह दो।

---

## 🔴 Problem it Solves
Keyword search fails on meaning. A user asks "my food arrived cold, how do I get my money back?" and the help article is titled "Refund policy for delivery issues". No shared keywords, so `$text` returns nothing. LLMs also hallucinate when they do not know your private data (policies, product docs, tickets) and cannot read millions of documents in one prompt.

Vector search finds the right article by meaning, and RAG feeds only those few passages to the LLM so it answers from your data. Keeping vectors in MongoDB (instead of a separate vector DB) means one database, one backup, transactional updates of text and embedding together, and metadata filters in the same query.

## 🔴 यह क्यों बना? (Hindi)
Keyword search मतलब पर fail होता है। User पूछता है "मेरा खाना ठंडा आया, पैसे वापस कैसे मिलेंगे?" और help article का title है "Refund policy for delivery issues"। कोई common शब्द नहीं, तो `$text` कुछ नहीं लौटाता। LLM भी तब hallucinate करते हैं जब उन्हें आपका private data (policies, product docs, tickets) पता नहीं, और वे एक prompt में लाखों documents नहीं पढ़ सकते।

Vector search सही article को मतलब से ढूँढता है, और RAG सिर्फ वही कुछ passages LLM को देता है ताकि वह आपके data से जवाब दे। Vectors को MongoDB में रखने (अलग vector DB की जगह) का मतलब: एक database, एक backup, text और embedding का साथ में transactional update, और उसी query में metadata filters।

---

## 🟢 How it Works — Step by Step

Step 1 → **Chunk** your content (e.g. 300 to 500 tokens per chunk) so each piece has one idea.
Step 2 → **Embed**: call an embedding model per chunk; store the returned float array in a field, e.g. `embedding`, next to `text` and metadata (`source`, `category`, `tenantId`).
Step 3 → **Create a vector index** on `embedding`: `type: "vectorSearch"`, with `numDimensions` (must equal the model's output size) and `similarity` (`cosine`, `euclidean` or `dotProduct`). Add `filter` fields for pre-filtering.
Step 4 → At query time **embed the user question** with the SAME model.
Step 5 → Run `$vectorSearch` with `queryVector`, `path`, `numCandidates` (how many neighbours HNSW examines, e.g. 100 to 200) and `limit` (how many to return, e.g. 5). Optional `filter` narrows by metadata before ranking.
Step 6 → Project the text and `{ $meta: "vectorSearchScore" }` (0 to 1 for cosine).
Step 7 → **Generate**: put the top chunks into the LLM prompt ("answer only from the context below") and return the answer plus sources.
Step 8 → Keep it fresh: re-embed when the source text changes; index updates follow automatically.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Content को **chunk** करो (जैसे 300 से 500 tokens प्रति chunk) ताकि हर टुकड़े में एक ही idea हो।
Step 2 → **Embed**: हर chunk के लिए embedding model call करो; मिली float array को field (जैसे `embedding`) में `text` और metadata (`source`, `category`, `tenantId`) के साथ रखो।
Step 3 → `embedding` पर **vector index** बनाओ: `type: "vectorSearch"`, `numDimensions` (model के output size के बराबर होना ज़रूरी) और `similarity` (`cosine`, `euclidean` या `dotProduct`)। Pre-filtering के लिए `filter` fields जोड़ो।
Step 4 → Query के समय **user का सवाल** उसी model से embed करो।
Step 5 → `$vectorSearch` चलाओ: `queryVector`, `path`, `numCandidates` (HNSW कितने neighbours जाँचे, जैसे 100 से 200) और `limit` (कितने लौटाने, जैसे 5)। Optional `filter` ranking से पहले metadata से छाँटता है।
Step 6 → Text और `{ $meta: "vectorSearchScore" }` project करो (cosine के लिए 0 से 1)।
Step 7 → **Generate**: top chunks को LLM prompt में डालो ("सिर्फ नीचे के context से जवाब दो") और जवाब के साथ sources लौटाओ।
Step 8 → ताज़ा रखो: source text बदले तो फिर से embed करो; index अपने-आप update होता है।

---

## 🟡 Real World Example
**Razorpay's support assistant.** Razorpay-style docs (settlement timelines, refund rules, API errors) are chunked into ~400-token pieces and stored in `kb_chunks` with `{ text, embedding, product: "payments", lang: "en" }`. A merchant types "money not credited after settlement day". The backend embeds the question, runs `$vectorSearch` with `filter: { product: "payments" }` and `limit: 4`, and passes the four chunks to an LLM. The answer cites "Settlements > Delays" chunk and links the doc. Because tickets and docs sit in the same cluster, a nightly job also embeds resolved tickets so "similar past tickets" can be suggested to support agents.

## 🟡 Real Example Hindi mein
**Razorpay जैसा support assistant।** Docs (settlement timelines, refund rules, API errors) ~400-token टुकड़ों में बँटकर `kb_chunks` में `{ text, embedding, product: "payments", lang: "en" }` के साथ रखे जाते हैं। Merchant लिखता है "settlement day के बाद भी पैसा credit नहीं हुआ"। Backend सवाल को embed करता है, `filter: { product: "payments" }` और `limit: 4` के साथ `$vectorSearch` चलाता है, और चारों chunks LLM को देता है। जवाब में "Settlements > Delays" chunk का हवाला और doc का link आता है। Tickets और docs एक ही cluster में हैं, इसलिए रात का job resolved tickets भी embed करता है ताकि support agents को "मिलते-जुलते पुराने tickets" दिखें।

---

## 💻 Code Example — Basic

```javascript
// Atlas Vector Search basics. Requires Atlas (or Atlas CLI local deployment); NOT runnable on
// Community mongod. Syntax-checked against current docs. A tiny 3-dim vector is used for readability.

// 1) Store documents WITH their embedding (real models give 384 / 768 / 1024 / 1536 numbers)
db.kb_chunks.insertMany([
  { text: "Refunds are processed in 5-7 days", product: "payments", embedding: [0.9, 0.1, 0.0] },
  { text: "How to rotate your API key",        product: "dev",      embedding: [0.0, 0.2, 0.9] },
  { text: "Settlement delayed on bank holiday", product: "payments", embedding: [0.8, 0.3, 0.1] },
]);

// 2) Create the vector index (mongosh on Atlas)
db.kb_chunks.createSearchIndex(
  "vec_idx",                                  // index name
  "vectorSearch",                             // index TYPE (not a normal search index)
  {
    fields: [
      { type: "vector",                       // the embedding field
        path: "embedding",
        numDimensions: 3,                     // MUST equal your model's output size (e.g. 1536)
        similarity: "cosine" },               // cosine | euclidean | dotProduct
      { type: "filter", path: "product" },    // fields usable in $vectorSearch.filter
    ],
  }
);

// 3) Query: queryVector is the embedding of the user's question (same model!)
db.kb_chunks.aggregate([
  { $vectorSearch: {
      index: "vec_idx",                       // which vector index
      path: "embedding",                      // field holding vectors
      queryVector: [0.85, 0.2, 0.05],         // embedded question
      numCandidates: 100,                     // ANN candidates to examine (>= limit, ~10-20x)
      limit: 2,                               // results returned
      filter: { product: "payments" },        // pre-filter on a filter field
  } },
  { $project: { _id: 0, text: 1, score: { $meta: "vectorSearchScore" } } }, // expose similarity
]);
// Expected shape on Atlas (scores illustrative, not verified):
// [ { text: 'Refunds are processed in 5-7 days', score: 0.99 },
//   { text: 'Settlement delayed on bank holiday', score: 0.97 } ]
```

## 💻 Code Example — Advanced

```javascript
// Full RAG pipeline in Node.js. Needs: Atlas cluster, OPENAI_API_KEY, `npm i mongodb openai`.
// Syntax-checked only (external services); model names change often, check provider docs.
const { MongoClient } = require('mongodb');
const OpenAI = require('openai');

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const client = new MongoClient(process.env.ATLAS_URI);
const chunks = client.db('support').collection('kb_chunks');

// Embed any text with ONE fixed model; dimensions must match the index
async function embed(text) {
  const r = await openai.embeddings.create({ model: 'text-embedding-3-small', input: text }); // 1536 dims
  return r.data[0].embedding;                       // array of 1536 floats
}

// INGEST: chunk -> embed -> store (batch in real life to save API calls)
async function ingest(doc) {                         // doc = { text, product, source }
  await chunks.insertOne({ ...doc, embedding: await embed(doc.text), createdAt: new Date() });
}

// RETRIEVE: embed the question, ask Atlas for the nearest chunks
async function retrieve(question, product) {
  return chunks.aggregate([
    { $vectorSearch: {
        index: 'vec_idx', path: 'embedding',
        queryVector: await embed(question),
        numCandidates: 200, limit: 4,
        filter: { product },                          // multi-tenant / topic isolation
    } },
    { $project: { _id: 0, text: 1, source: 1, score: { $meta: 'vectorSearchScore' } } },
    { $match: { score: { $gte: 0.75 } } },            // drop weak matches (tune on real data)
  ]).toArray();
}

// GENERATE: stuff retrieved text into the prompt
async function answer(question, product) {
  const ctx = await retrieve(question, product);
  if (ctx.length === 0) return { answer: "I don't know. Contacting support.", sources: [] };
  const prompt = `Answer ONLY from the context.\n\nContext:\n${ctx.map(c => '- ' + c.text).join('\n')}\n\nQuestion: ${question}`;
  const out = await openai.chat.completions.create({
    model: 'gpt-4o-mini', messages: [{ role: 'user', content: prompt }],
  });
  return { answer: out.choices[0].message.content, sources: ctx.map(c => c.source) };
}

// Hybrid tip: combine $vectorSearch and $search with $rankFusion / $unionWith + reciprocal rank
// fusion when you need both exact keywords (SKU, error code) and meaning. (Recent Atlas versions.)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose model with an embedding array + a RAG route. Atlas required; syntax-checked only.
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

const Chunk = mongoose.model('Chunk', new mongoose.Schema({
  text: { type: String, required: true },
  product: { type: String, index: true },
  embedding: { type: [Number], select: false },        // select:false -> never ship 1536 floats to clients
}), 'kb_chunks');

app.post('/ask', async (req, res) => {
  const { question, product } = req.body;
  if (typeof question !== 'string' || question.length > 500) return res.status(400).json({ error: 'bad question' });
  const queryVector = await embed(question);            // embed() as defined above
  const hits = await Chunk.aggregate([
    { $vectorSearch: { index: 'vec_idx', path: 'embedding', queryVector, numCandidates: 150, limit: 4,
                       filter: { product: String(product) } } },
    { $project: { text: 1, score: { $meta: 'vectorSearchScore' } } },   // embedding excluded by default
  ]);
  res.json({ hits });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Dimension or model mismatch
```javascript
// Wrong: index numDimensions: 1536, but queryVector made by a 768-dim model -> no/invalid results
// Wrong: indexing with model A, querying with model B -> vectors live in different spaces
// Right: ONE model per index; store model name + version with each chunk so you can re-embed on upgrade
```

❌ Mistake 2: `numCandidates` too small or `limit` > `numCandidates`
```javascript
// Wrong: ANN may miss the true best matches
{ $vectorSearch: { /* ... */ numCandidates: 5, limit: 5 } }
// Right: numCandidates about 10x to 20x limit (cap 10000); raise it if recall looks poor
{ $vectorSearch: { /* ... */ numCandidates: 100, limit: 5 } }
```

❌ Mistake 3: Filtering with `$match` AFTER `$vectorSearch` and expecting full results
✅ Correct: `$match` after `$vectorSearch` only trims the already-limited top-N, so you may get 0 rows. Declare the field as `type: "filter"` in the index and use `$vectorSearch.filter` so filtering happens during the search.

---

## 🧠 Tricky Interview Question

**Q:** Vector search with cosine similarity returns the top-5 chunks, but the answer is still wrong. Name three non-LLM reasons.

**Answer:** (1) **Bad chunking**: chunks too large dilute meaning, too small lose context, so the right fact is split across two chunks. (2) **Recall limits of ANN**: HNSW is approximate; too low `numCandidates` can miss the true nearest chunk. (3) **Semantic is not lexical**: queries with exact identifiers ("error E4021", SKU numbers) embed poorly, so combine with `$search` (hybrid, reciprocal rank fusion). Others: stale embeddings after a doc edit, mixing models, no score threshold so irrelevant chunks are passed to the LLM, and missing metadata filters (wrong tenant/language).

---

## ⚫ Interview Questions + Answers

Q1: What is an embedding and what does `similarity: "cosine"` mean?
A1: An embedding is a fixed-length numeric vector that represents the meaning of text/image. Cosine similarity measures the angle between two vectors (1 = same direction, 0 = unrelated), ignoring magnitude. Use `dotProduct` for normalised vectors (fastest) and `euclidean` when magnitude matters.

Q2: ANN vs exact (ENN) search in Atlas?
A2: Default `$vectorSearch` is approximate (HNSW graph): very fast but may miss a few true neighbours. Setting `exact: true` (instead of `numCandidates`) does a full scan for exact results; it is slow, so use it for small filtered sets or to measure recall.

Q3: Why store vectors in MongoDB instead of a separate vector database?
A3: One system to run, secure and back up; text, metadata and embedding are updated together; the same query can pre-filter on metadata and join other stages; no sync pipeline. Trade-off: very large or very specialised vector workloads may prefer a dedicated engine.

Q4: How do you handle multi-tenant RAG?
A4: Put `tenantId` on every chunk, declare it as a `filter` field in the vector index, and ALWAYS add `filter: { tenantId }` from the server (derived from the auth token, never from the client). Skipping it leaks one customer's documents into another's answers.

Q5: How big can the vectors be and how do you reduce storage?
A5: Atlas supports up to 8192 dimensions. Reduce cost with a smaller-dimension model (Matryoshka/`dimensions` parameter), or enable scalar/binary quantisation in the index definition (`quantization: "scalar" | "binary"`), which cuts RAM sharply with small recall loss.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Semantic search, recommendations ("similar items"), RAG chatbots, duplicate detection
- You already store operational data in MongoDB and want metadata filters in the same query
- You need real-time index freshness without a separate ETL

❌ Avoid when:
- Exact lookups, filters and aggregates (plain indexes are faster and exact)
- Keyword-heavy search such as SKUs and codes (use Atlas Search or hybrid)
- You cannot use Atlas or a `mongot`-enabled deployment (Community `mongod` has no `$vectorSearch`)

---

## 📊 Visual Diagram
```
RAG WITH ATLAS VECTOR SEARCH
──────────────────────────────────────────────────────────────
INGEST:   docs ─► chunk ─► embedding model ─► { text, embedding, meta } ─► MongoDB
                                                       │
                                            vectorSearch index (HNSW)

QUERY:    question ─► embedding model ─► queryVector
                                              │
             $vectorSearch { filter, numCandidates, limit }
                                              │  top-k chunks + score
                                              ▼
                      prompt = "Answer ONLY from context" + chunks + question
                                              │
                                              ▼
                                            LLM ─► answer + sources
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Numeric vector for meaning | Meaning का numeric vector |
| Vector index | HNSW index on a vector field | Vector field पर HNSW index |
| `numDimensions` | Vector length, must match the model | Vector की लंबाई, model से match |
| Cosine similarity | Angle-based closeness score | Angle पर आधारित closeness score |
| ANN / HNSW | Approximate nearest neighbour graph | अनुमानित nearest-neighbour graph |
| `numCandidates` | Neighbours examined before `limit` | `limit` से पहले जाँचे गए neighbours |
| RAG | Retrieve context, then generate | Context लाओ, फिर जवाब बनाओ |
| Chunking | Splitting docs into small passages | Docs को छोटे हिस्सों में बाँटना |

---

## ⚡ 3-Line Summary
English:
1. Embeddings turn meaning into vectors; `$vectorSearch` finds the nearest ones using an HNSW index inside MongoDB Atlas.
2. RAG = chunk and embed your data, retrieve top-k by similarity (with metadata filters), then give them to an LLM.
3. Match model and dimensions, tune `numCandidates`, filter by tenant, and note it needs Atlas, not plain Community `mongod`.

Hindi:
1. Embeddings मतलब को vectors में बदलते हैं; `$vectorSearch` MongoDB Atlas के अंदर HNSW index से सबसे नज़दीकी vectors खोजता है।
2. RAG = अपने data को chunk और embed करो, similarity (और metadata filters) से top-k लाओ, फिर LLM को दो।
3. Model और dimensions match रखो, `numCandidates` tune करो, tenant से filter करो, और याद रखो इसके लिए Atlas चाहिए, plain Community `mongod` नहीं।

---

## ➡️ Next Topic
**105. MongoDB Authentication + RBAC** — who can connect, and what they are allowed to do.

---
> Not verified against a live system: `$vectorSearch`, vector index definitions, embedding/LLM calls are syntax-checked only (Atlas and API keys needed). Output scores shown are illustrative.
