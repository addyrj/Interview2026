# 53a. Search Engines (Elasticsearch / OpenSearch) ⭐
# हिंदी में: Search Engine — टेक्स्ट में तेज़ खोज (full-text search), typo सहन करना, relevance के हिसाब से नतीजे देना — जैसे "biryani near me"

---

## 🔵 Simple Definition (English)
A **search engine** like **Elasticsearch** (or its open-source fork **OpenSearch**) is a distributed datastore built for **full-text search**, **filtering**, **relevance ranking** and **aggregations** at scale. Its core is the **inverted index**: a map from each **word (term)** → the list of **documents** containing it. It's used **alongside** your primary DB (Postgres), not instead of it.
Alternatives: Algolia, Typesense, Meilisearch (simpler), Solr, Postgres full-text search (for smaller needs).

## 🔵 सरल परिभाषा (Hindi)
Elasticsearch एक search इंजन है जो "inverted index" बनाता है — हर शब्द से उन documents की सूची जिनमें वो शब्द है (जैसे किताब के पीछे का index)।
इससे लाखों रेस्टोरेंट/products में तुरंत खोज, typo सहन करना, filters और सबसे relevant नतीजे पहले — सब होता है। यह Postgres के साथ चलता है, उसकी जगह नहीं।

---

## 🔴 Problem it Solves
SQL is bad at search:
```sql
SELECT * FROM restaurants WHERE name ILIKE '%biryani%' OR description ILIKE '%biryani%';
```
- `LIKE '%x%'` can't use B-tree indexes → **full scan** of millions of rows.
- No **relevance ranking** (which result is best?), no **typo tolerance** ("biriyani"), no **synonyms** ("veg" = "vegetarian"), no **stemming** ("burgers" = "burger"), no **autocomplete**.
- Faceted filters + counts ("Cuisine: North Indian (120), Chinese (85)") are expensive in SQL.

Search engines are built exactly for this: **millisecond full-text search over millions or billions of documents**, with ranking, fuzziness, facets and geo.

## 🔴 यह क्यों बना? (Hindi)
SQL का `LIKE '%biryani%'` पूरी टेबल पढ़ता है, ranking नहीं करता, "biriyani" जैसी typo नहीं समझता, "burgers" और "burger" को एक नहीं मानता।
Search engine इसी के लिए बना है — करोड़ों documents में milliseconds में खोज, सही ranking, typo, synonyms, filters और counts के साथ।

---

## 🟢 How it Works — Step by Step

### Inverted index

```
Documents:
  1: "Hyderabadi Chicken Biryani"
  2: "Veg Biryani and Raita"
  3: "Chicken Tikka Masala"

Analyze (lowercase, tokenize, stem) → terms → inverted index:
  biryani    → [1, 2]
  chicken    → [1, 3]
  hyderabadi → [1]
  veg        → [2]
  raita      → [2]
  tikka      → [3]
  masala     → [3]

Query "chicken biryani" → postings: chicken[1,3] ∩/∪ biryani[1,2] → doc 1 best match (both terms)
Lookup = O(terms), not O(documents) ⚡
```

### Analysis pipeline

```
"Burgers & FRIES near Andheri!"
  → character filters (strip html)
  → tokenizer:  [Burgers] [FRIES] [near] [Andheri]
  → token filters: lowercase → stop words → stemming → synonyms
  → [burger] [fri] [andheri]   (near removed as stop word)
Same analyzer applied to the query → matching works.
Also: n-grams / edge n-grams for autocomplete ("bir" → biryani), phonetic, language analyzers (Hindi too)
```

### Relevance scoring (BM25)
```
Score higher when:
  - term appears more in the document (term frequency, with saturation)
  - term is RARE across all docs (inverse document frequency) — "hyderabadi" > "chicken"
  - field is shorter (match in title > match in long description)
Then boost with business signals: rating, distance, popularity, is_open, sponsored
  → function_score / rescore / learning-to-rank
```

### Distributed architecture

```
Cluster
 ├── Node 1: [P0] [R1]
 ├── Node 2: [P1] [R2]
 └── Node 3: [P2] [R0]
Index "restaurants" = 3 primary shards (P) + 1 replica each (R)
Write → routed to primary shard (hash(_id) % shards) → replicated
Search → coordinator sends query to one copy of EVERY shard → each returns top N → merge → top N
(scatter-gather; replicas add read throughput & HA)
Each shard = a Lucene index made of immutable segments (merged in background)
Near-real-time: new docs searchable after "refresh" (default 1s)
```

### Keep it in sync with Postgres (Postgres = source of truth)

```
❌ Dual write in API (write PG, then ES) → if ES call fails, out of sync forever
✅ Outbox / CDC:
   Postgres ──(outbox table or Debezium reading WAL)──► Kafka ──► Indexer ──► Elasticsearch
   - retries, ordering per entity, re-index from scratch possible
✅ Small scale: background job "reindex changed rows WHERE updated_at > last_run"
Full reindex strategy: build new index (restaurants_v2) → backfill → switch ALIAS → delete old
```

### When to use what

```
Postgres full-text (tsvector + GIN) / pg_trgm  → < few million rows, simple search, no extra infra
Elasticsearch / OpenSearch                     → large scale, complex ranking, facets, geo, logs
Algolia / Typesense / Meilisearch              → instant search UX, typo tolerance, less ops
ES is also the "E" in ELK: logs & observability search (Topic 100)
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर document के टेक्स्ट को छोटे शब्दों (terms) में तोड़ा जाता है — lowercase, stemming, synonyms।
2. Inverted index बनता है: शब्द → उन documents की सूची। खोज में सिर्फ़ उन शब्दों की सूचियाँ देखी जाती हैं।
3. BM25 से score: शब्द ज़्यादा बार और दुर्लभ हो तो score ज़्यादा; फिर rating, दूरी, popularity से boost।
4. डेटा shards में बँटा होता है; search सब shards पर चलकर नतीजे जोड़ती है।
5. Postgres सच का स्रोत है; बदलाव CDC/outbox → Kafka → indexer से Elasticsearch तक पहुँचते हैं (dual write नहीं)।

---

## 🟡 Real World Example

**Swiggy / Zomato search** — "paneer near me" searches restaurants and dishes with typo tolerance, Hindi or Hinglish synonyms, geo-distance filters, open-now filters, and ranking by relevance plus rating plus distance plus personalization. Search clusters are fed by change streams from the primary DBs.

**Flipkart / Amazon product search** — inverted indexes over hundreds of millions of products, facets (brand, price range, rating), autocomplete and learning-to-rank models trained on click and purchase data.

**GitHub code search, Wikipedia, Uber Eats, Netflix** — all use Elasticsearch/Lucene-based or custom inverted-index search.

**Logs (ELK / OpenSearch)** — most companies store application logs in Elasticsearch or OpenSearch and query them in Kibana or OpenSearch Dashboards.

## 🟡 Real Example Hindi में
Swiggy/Zomato में "paneer near me" — typo, Hinglish synonyms, दूरी, अभी खुला है या नहीं, rating — सब search इंजन से होता है, जिसे primary DB से बदलाव लगातार मिलते रहते हैं।
Flipkart की product search में करोड़ों products, brand/price filters, autocomplete और click-डेटा से सीखी ranking होती है।

---

## 🟠 My Stack Example

### Index mapping for restaurants
```json
PUT restaurants_v1
{
  "settings": {
    "number_of_shards": 3, "number_of_replicas": 1,
    "analysis": {
      "filter": { "food_synonyms": { "type": "synonym", "synonyms": ["veg, vegetarian", "biryani, biriyani, biriani"] },
                  "autocomplete": { "type": "edge_ngram", "min_gram": 2, "max_gram": 15 } },
      "analyzer": {
        "food":       { "tokenizer": "standard", "filter": ["lowercase", "food_synonyms", "porter_stem"] },
        "food_ac":    { "tokenizer": "standard", "filter": ["lowercase", "autocomplete"] }
      }
    }
  },
  "mappings": {
    "properties": {
      "name":     { "type": "text", "analyzer": "food", "fields": { "ac": { "type": "text", "analyzer": "food_ac", "search_analyzer": "food" } } },
      "dishes":   { "type": "text", "analyzer": "food" },
      "cuisines": { "type": "keyword" },
      "location": { "type": "geo_point" },
      "rating":   { "type": "float" },
      "is_open":  { "type": "boolean" },
      "city_id":  { "type": "keyword" }
    }
  }
}
POST _aliases { "actions": [{ "add": { "index": "restaurants_v1", "alias": "restaurants" } }] }
```

### Node.js search API (@elastic/elasticsearch)
```js
import { Client } from '@elastic/elasticsearch';
const es = new Client({ node: process.env.ES_URL });

app.get('/api/v1/search', async (req, res) => {
  const { q, lat, lng, cuisine } = req.query;
  const r = await es.search({
    index: 'restaurants',
    size: 20,
    query: {
      function_score: {
        query: {
          bool: {
            must: [{ multi_match: { query: q, fields: ['name^3', 'name.ac^2', 'dishes'], fuzziness: 'AUTO' } }],
            filter: [
              { term: { is_open: true } },
              { geo_distance: { distance: '5km', location: { lat: +lat, lon: +lng } } },
              ...(cuisine ? [{ term: { cuisines: cuisine } }] : []),
            ],
          },
        },
        functions: [
          { field_value_factor: { field: 'rating', modifier: 'log1p', missing: 3 } },
          { gauss: { location: { origin: { lat: +lat, lon: +lng }, scale: '2km' } } },
        ],
        boost_mode: 'multiply',
      },
    },
    aggs: { cuisines: { terms: { field: 'cuisines', size: 10 } } },      // facets with counts
  });
  res.json({ results: r.hits.hits.map((h) => ({ id: h._id, score: h._score, ...h._source })),
             facets: r.aggregations.cuisines.buckets });
});
```

### Indexer worker (consume change events → ES), idempotent by _id
```js
consumer.on('restaurant.changed', async ({ id }) => {
  const row = await repo.getRestaurantForIndex(id);           // join PG tables into one document
  if (!row || row.deleted) return es.delete({ index: 'restaurants', id, refresh: false }).catch(() => {});
  await es.index({ index: 'restaurants', id: String(id), document: row });
});
// bulk API for backfills: es.helpers.bulk({ datasource: rows, onDocument: (d) => ({ index: { _index: 'restaurants_v2', _id: d.id } }) })
```

### Postgres full-text (when ES is overkill)
```sql
ALTER TABLE restaurants ADD COLUMN search tsvector
  GENERATED ALWAYS AS (setweight(to_tsvector('simple', coalesce(name,'')), 'A') ||
                       setweight(to_tsvector('simple', coalesce(dishes_text,'')), 'B')) STORED;
CREATE INDEX idx_rest_search ON restaurants USING GIN (search);
SELECT id, name, ts_rank(search, q) AS rank
FROM restaurants, plainto_tsquery('simple', 'chicken biryani') q
WHERE search @@ q ORDER BY rank DESC LIMIT 20;
-- typo tolerance: pg_trgm similarity(name, 'biriyani') > 0.3
```

### Docker Compose (local)
```yaml
opensearch:
  image: opensearchproject/opensearch:2.15.0
  environment: { discovery.type: single-node, DISABLE_SECURITY_PLUGIN: "true", OPENSEARCH_JAVA_OPTS: "-Xms1g -Xmx1g" }
  ports: ["9200:9200"]
```
AWS: **Amazon OpenSearch Service**. Elastic Cloud for Elasticsearch.

### React Native / Next.js search UX
```tsx
// debounce keystrokes (250ms), cancel stale requests, show autocomplete from name.ac
const [q, setQ] = useState('');
const debounced = useDebounce(q, 250);
const { data } = useQuery({ queryKey: ['search', debounced, lat, lng], enabled: debounced.length >= 2,
  queryFn: ({ signal }) => api.get('/api/v1/search', { params: { q: debounced, lat, lng }, signal }).then(r => r.data) });
```

---

## ⚫ Interview Questions + Answers

**Q1: What is an inverted index and why is it fast for search?**
A1: A mapping from each term to the list of documents (and positions) containing it, built after text analysis (tokenizing, lowercasing, stemming). A query only reads the postings lists of its terms and combines them, so cost depends on the number of query terms and matches, not on scanning every document. Relevance scores (BM25) are computed from term statistics stored in the index.

**Q2: Why not just use SQL LIKE for search?**
A2: `LIKE '%term%'` can't use normal B-tree indexes and scans the table. It has no relevance ranking, typo tolerance, synonyms, stemming, phrase or proximity matching, language analysis or efficient facet counts. Postgres full-text search and trigram indexes help at moderate scale. Dedicated engines handle large scale, complex ranking, autocomplete, geo and aggregations much better.

**Q3: How do you keep Elasticsearch in sync with your primary database?**
A3: Treat the DB as the source of truth and ES as a derived index. Avoid dual writes from the API. Use the transactional outbox or CDC (Debezium reading the Postgres WAL) to publish changes to Kafka, and have an indexer service build denormalized documents and upsert them by ID (idempotent, retryable, ordered per entity). For mapping changes or recovery, build a new index, backfill, then switch the alias atomically. Monitor lag and run periodic reconciliation.

**Q4: How does Elasticsearch scale and stay available?**
A4: An index is split into primary shards (fixed at creation, routed by document ID hash) distributed across nodes, each with replica shards on other nodes. Writes go to the primary and are replicated. Searches scatter to one copy of each shard and gather the top results. More nodes and replicas give more read throughput and fault tolerance. Use enough shards for growth, but not too many small ones (overhead), index lifecycle management for time-based indices (logs), and dedicated master nodes for cluster stability.

**Q5: How would you design search for a food delivery app?**
A5: Index restaurants and dishes as denormalized documents (name, dishes, cuisines, geo_point, rating, open hours, price, delivery zones) using analyzers with synonyms (Hinglish), edge n-grams for autocomplete, and fuzziness for typos. Queries filter by serviceability (geo or zone, is_open), match text, and rank with function_score combining BM25, rating, distance, popularity and personalization, with facets for cuisines. Feed updates via CDC from Postgres, cache popular queries briefly, debounce on the client, and log clicks to improve ranking (learning-to-rank).

---

## 🔷 Trade-offs
✅ Advantages:
- Fast full-text search, relevance ranking, fuzzy/typo, synonyms, autocomplete, facets, geo.
- Horizontally scalable; great for logs/analytics search too.

❌ Disadvantages:
- Another distributed system to run (memory-hungry JVM, shard tuning, upgrades).
- Not a primary store (no ACID transactions); eventual consistency with DB (refresh/indexing lag).
- Sync pipeline complexity; relevance tuning is an ongoing effort.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Inverted index | Term → documents map | शब्द → documents की सूची |
| Analyzer | Text processing pipeline | टेक्स्ट को शब्दों में बदलने की प्रक्रिया |
| Tokenizer | Splits text into tokens | टेक्स्ट को टुकड़ों में तोड़ना |
| Stemming | Reduce words to root | शब्द को मूल रूप में |
| BM25 | Relevance scoring formula | relevance score का सूत्र |
| Shard / Replica | Index partition / copy | index का हिस्सा / copy |
| Facet / Aggregation | Grouped counts for filters | filters के लिए गिनती |
| Fuzziness | Typo tolerance | typo सहन करना |
| Alias | Pointer name to an index | index का दूसरा नाम |
| Refresh | Make new docs searchable | नए documents खोजने लायक बनाना |

---

## ⚡ 3-Line Summary
**English:**
1. Search engines use an inverted index (term → docs) + analyzers + BM25 ranking for fast, relevant full-text search.
2. Elasticsearch/OpenSearch scale with shards/replicas and add fuzzy search, autocomplete, facets, geo.
3. Keep the DB as source of truth and sync via outbox/CDC → Kafka → indexer; use Postgres FTS for small needs.

**Hindi:**
1. Search engine = inverted index + analyzer + BM25 ranking → तेज़ और सही full-text खोज।
2. Elasticsearch shards/replicas से स्केल करता है; typo, autocomplete, filters, geo देता है।
3. DB ही सच का स्रोत; sync outbox/CDC → Kafka → indexer से; छोटी ज़रूरत में Postgres FTS काफ़ी।

---

## ➡️ Next Topic Suggestion
**🎉 Databases + Caching complete!** Next: **54. JWT Authentication** in `03-Auth-Security-API/`. You know how data is stored; now learn how users prove who they are: the structure of a JWT, signing, access vs refresh tokens, and secure storage on web and mobile.
