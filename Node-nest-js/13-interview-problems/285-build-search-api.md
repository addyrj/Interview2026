# 285. Build Search API
# हिंदी में: Search API बनाना

---

## 🔵 Simple Definition (English)
A search API lets clients find relevant records by keyword, with support for filtering, ranking, and typo-tolerance — going beyond a simple SQL `LIKE '%term%'` query, which doesn't scale or rank results well. Production search typically layers full-text search (Postgres `tsvector`, MySQL `FULLTEXT`) or a dedicated search engine (Elasticsearch, Algolia, Meilisearch) behind a clean Node.js API.

## 🔵 सरल परिभाषा (Hindi)
Search API clients को keyword से relevant records ढूंढने देता है, filtering, ranking, और typo-tolerance के साथ — simple SQL `LIKE '%term%'` query से आगे, जो scale और rank नहीं करता अच्छे से। Production search आम तौर पर full-text search (Postgres `tsvector`) या dedicated search engine (Elasticsearch, Algolia, Meilisearch) को clean Node.js API के पीछे use करता है।

---

## 🔴 Problem it Solves
`WHERE name LIKE '%search term%'` is slow at scale (can't use a standard B-tree index effectively, forces a full table scan for leading-wildcard patterns), doesn't rank results by relevance (all matches are equally "found," regardless of how well they match), and doesn't handle typos, word stemming ("running" should match "run"), or multi-word relevance scoring. Dedicated full-text search solves all of this with inverted indexes, relevance scoring (TF-IDF/BM25), and fuzzy matching.

## 🔴 यह क्यों बना? (Hindi)
`LIKE '%term%'` scale पर slow है (leading-wildcard patterns के लिए full table scan), results को relevance से rank नहीं करता, typos handle नहीं करता, word stemming ("running" को "run" से match) नहीं करता। Dedicated full-text search ये सब inverted indexes, relevance scoring, fuzzy matching से solve करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Choose a search backend based on scale: PostgreSQL's built-in full-text search (`tsvector`/`tsquery` with a GIN index) for moderate scale/simplicity; Elasticsearch/OpenSearch for large-scale, feature-rich search (faceting, fuzzy matching, analytics); Algolia/Meilisearch for fast managed/hosted search with minimal ops overhead.
Step 2 → **Index** your searchable data — for Postgres, maintain a `tsvector` column (often via a trigger or application-level update on write) combining searchable fields; for Elasticsearch, documents are indexed into a separate search-optimized store, kept in sync with your primary DB.
Step 3 → Build the query endpoint: accept a search term plus optional filters (category, price range) and pagination params.
Step 4 → Parse the search term appropriately — sanitize/escape for the underlying engine's query syntax, support partial/prefix matching for "search as you type" UX.
Step 5 → Rank results by relevance score (how well they match) combined with business signals (popularity, recency) — pure text relevance alone often isn't the best user experience.
Step 6 → Return paginated results with total count and facet/filter counts (e.g. "42 results, 12 in Electronics category") for building filter UIs.
Step 7 → Keep the search index in sync with the primary database — via application-level dual-writes, database triggers, or change-data-capture pipelines for eventual consistency at scale.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Scale के हिसाब से search backend चुनो: Postgres full-text search, Elasticsearch, या Algolia/Meilisearch।
Step 2 → Searchable data **index** करो।
Step 3 → Query endpoint बनाओ: search term + filters + pagination।
Step 4 → Search term सावधानी से parse करो, sanitize करो, prefix matching support करो।
Step 5 → Results को relevance score + business signals से rank करो।
Step 6 → Paginated results, total count, facet counts return करो।
Step 7 → Search index को primary DB से sync रखो।

---

## 🟡 Real World Example
**Swiggy's** restaurant/dish search uses Elasticsearch behind the scenes: typing "biryani" returns restaurants ranked by a combination of text relevance, restaurant rating, delivery time, and distance — not just alphabetical/text-match order. The search index is kept in sync with the primary restaurant/menu database via a change-data-capture pipeline, so menu updates (new dish added, price changed) propagate to search within seconds without requiring the search service to query the primary DB on every search request.

## 🟡 Real Example Hindi mein
**Swiggy** का restaurant/dish search Elasticsearch use करता है: "biryani" type करने पर restaurants text relevance + rating + delivery time + distance के combination से ranked आते हैं, सिर्फ alphabetical order नहीं। Search index primary database से change-data-capture pipeline के through sync रहता है।

---

## 💻 Code Example — Basic

```javascript
// basic-search-postgres.js — PostgreSQL full-text search
// npm install pg
// Requires a Postgres table with a tsvector column:
//   ALTER TABLE products ADD COLUMN search_vector tsvector;
//   UPDATE products SET search_vector = to_tsvector('english', name || ' ' || description);
//   CREATE INDEX idx_products_search ON products USING GIN(search_vector);

const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

async function searchProducts(searchTerm) {
  // to_tsquery converts the search term into a tsquery; ts_rank scores relevance
  const result = await pool.query(
    `SELECT id, name, description,
            ts_rank(search_vector, to_tsquery('english', $1)) AS relevance
     FROM products
     WHERE search_vector @@ to_tsquery('english', $1)
     ORDER BY relevance DESC
     LIMIT 20`,
    [searchTerm.trim().split(/\s+/).join(' & ')] // join words with AND logic
  );
  return result.rows;
}

searchProducts('wireless mouse').then(console.log).catch(console.error);
```

## 💻 Code Example — Advanced

```javascript
// advanced-search-service.js — filters, pagination, prefix matching, sync strategy
// npm install pg

const { Pool } = require('pg');

class SearchService {
  constructor(pool) {
    this.pool = pool;
  }

  // Sanitize user input into a safe tsquery string, supporting prefix search ("laptop:*")
  buildTsQuery(searchTerm) {
    const words = searchTerm
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .map((w) => w.replace(/[^\w]/g, '') + ':*'); // :* enables prefix matching for "type-ahead"
    return words.join(' & '); // AND logic between words — all terms must partially match
  }

  async search({ query, category, minPrice, maxPrice, page = 1, limit = 20 }) {
    const tsQuery = this.buildTsQuery(query);
    const offset = (page - 1) * limit;

    const conditions = ['search_vector @@ to_tsquery($1)'];
    const params = [tsQuery];
    let paramIndex = 2;

    if (category) {
      conditions.push(`category = $${paramIndex++}`);
      params.push(category);
    }
    if (minPrice !== undefined) {
      conditions.push(`price >= $${paramIndex++}`);
      params.push(minPrice);
    }
    if (maxPrice !== undefined) {
      conditions.push(`price <= $${paramIndex++}`);
      params.push(maxPrice);
    }

    const whereClause = conditions.join(' AND ');

    // Main results query, ranked by relevance
    const resultsQuery = `
      SELECT id, name, description, price, category,
             ts_rank(search_vector, to_tsquery($1)) AS relevance
      FROM products
      WHERE ${whereClause}
      ORDER BY relevance DESC
      LIMIT $${paramIndex++} OFFSET $${paramIndex++}
    `;
    params.push(limit, offset);

    // Separate count query for total (needed for pagination metadata)
    const countQuery = `SELECT COUNT(*) FROM products WHERE ${whereClause}`;
    const countParams = params.slice(0, paramIndex - 3); // exclude limit/offset

    const [results, countResult] = await Promise.all([
      this.pool.query(resultsQuery, params),
      this.pool.query(countQuery, countParams),
    ]);

    return {
      data: results.rows,
      meta: {
        page,
        limit,
        total: Number(countResult.rows[0].count),
        totalPages: Math.ceil(Number(countResult.rows[0].count) / limit),
      },
    };
  }

  // Keep search_vector in sync when a product is created/updated
  async updateSearchVector(productId) {
    await this.pool.query(
      `UPDATE products
       SET search_vector = to_tsvector('english', name || ' ' || COALESCE(description, ''))
       WHERE id = $1`,
      [productId]
    );
  }
}

module.exports = SearchService;
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { Pool } = require('pg');
const SearchService = require('./advanced-search-service');

const app = express();
app.use(express.json());

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const searchService = new SearchService(pool);

app.get('/api/search', async (req, res) => {
  const { q, category, minPrice, maxPrice, page, limit } = req.query;

  if (!q || q.trim().length === 0) {
    return res.status(400).json({ error: 'Search query (q) is required' });
  }

  try {
    const results = await searchService.search({
      query: q,
      category,
      minPrice: minPrice ? Number(minPrice) : undefined,
      maxPrice: maxPrice ? Number(maxPrice) : undefined,
      page: page ? Number(page) : 1,
      limit: limit ? Number(limit) : 20,
    });
    res.json(results);
  } catch (err) {
    console.error('Search error:', err);
    res.status(500).json({ error: 'Search failed' });
  }
});

// Keep index in sync — call this whenever a product is created/updated
app.put('/api/products/:id', async (req, res) => {
  // ... update product fields in DB ...
  await searchService.updateSearchVector(req.params.id);
  res.json({ message: 'Product updated, search index refreshed' });
});

app.listen(3000, () => console.log('Search API on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `LIKE '%term%'` for search at any meaningful scale
✅ Correct: Leading-wildcard `LIKE` queries can't use a standard B-tree index efficiently, forcing a full table scan that gets slower linearly with table size. Use full-text search (`tsvector`) or a dedicated search engine instead.

```javascript
// Wrong: full table scan, no relevance ranking, breaks on typos/word variations
await pool.query(`SELECT * FROM products WHERE name LIKE $1`, [`%${searchTerm}%`]);

// Right: indexed full-text search with relevance ranking
await pool.query(
  `SELECT *, ts_rank(search_vector, to_tsquery($1)) AS relevance
   FROM products WHERE search_vector @@ to_tsquery($1) ORDER BY relevance DESC`,
  [tsQuery]
);
```

❌ Mistake 2: Interpolating raw user search input directly into a `to_tsquery()` call
✅ Correct: `to_tsquery` has its OWN query syntax (`&`, `|`, `!`, `:*`) — raw user input containing these characters can cause SQL errors or unexpected query behavior. Sanitize/escape before building the tsquery string, as shown in `buildTsQuery`.

```javascript
// Wrong: user types "cat & dog | (evil" — breaks the query or behaves unexpectedly
await pool.query(`SELECT * FROM products WHERE search_vector @@ to_tsquery($1)`, [userInput]);

// Right: sanitize to plain words before constructing the tsquery syntax
const safe = userInput.replace(/[^\w\s]/g, '').trim().split(/\s+/).join(' & ');
```

---

## 🧠 Tricky Interview Question

```javascript
// Why does this search index go stale, causing search results to miss recently added products?
async function createProduct(data) {
  const result = await db.query('INSERT INTO products (name, price) VALUES ($1, $2) RETURNING id', [data.name, data.price]);
  return result.rows[0];
  // search_vector column is never populated!
}
```
Answer: The `search_vector` column is only populated by an EXPLICIT update (`UPDATE ... SET search_vector = to_tsvector(...)`), which this `createProduct` function never calls — so newly inserted products have a `NULL` search_vector and are invisible to `WHERE search_vector @@ to_tsquery(...)` searches, despite existing in the table and being findable by direct ID lookup. This is a classic "search index out of sync with primary data" bug. Fixes: (1) Always call the sync step (`updateSearchVector`) immediately after every insert/update in application code — risky if a code path forgets to call it. (2) Use a database TRIGGER (`CREATE TRIGGER ... BEFORE INSERT OR UPDATE ... EXECUTE FUNCTION tsvector_update_trigger(...)`) so the database itself guarantees the column is always populated, regardless of which application code path wrote the row — the more robust, foolproof approach for critical search sync.

---

## ⚫ Interview Questions + Answers

Q1: When would you choose Elasticsearch over PostgreSQL's built-in full-text search?
A1: Postgres full-text search is sufficient for moderate scale (up to low millions of rows), simpler ops (no separate service to run), and when search needs are relatively basic (keyword matching, simple ranking). Elasticsearch becomes worth the added operational complexity when you need: advanced relevance tuning (custom scoring functions, boosting), faceted search/aggregations at scale, fuzzy/typo-tolerant matching out of the box, geo-spatial search, or search volume/data size that strains a single Postgres instance's full-text capabilities. Many companies start with Postgres FTS and migrate to Elasticsearch only once genuinely needed.

Q2: How do you keep a separate search index (Elasticsearch) in sync with your primary database?
A2: Common patterns: (1) **Dual-write**: application code writes to both the primary DB and the search index on every write — simple but risks inconsistency if one write succeeds and the other fails. (2) **Change Data Capture (CDC)**: tools like Debezium read the database's write-ahead log/binlog and stream changes to the search index asynchronously — more reliable (captures ALL changes, even from direct DB access bypassing the app) but adds infrastructure complexity. (3) **Periodic full reindex**: simplest but introduces staleness windows; often combined with one of the above as a fallback/repair mechanism.

Q3: How would you implement "search as you type" / autocomplete efficiently?
A3: Use prefix matching (`:*` suffix in Postgres tsquery, or an Elasticsearch `match_phrase_prefix`/edge-ngram-based field) rather than full-word matching, since the user hasn't finished typing. Debounce the client-side requests (wait ~200-300ms after the last keystroke before firing the API call) to avoid flooding the server with a request per keystroke. For very snappy autocomplete, a dedicated lightweight index (precomputed list of common search terms/product names) queried separately from the main full-text search can be faster than running the full ranked-search query on every keystroke.

Q4: Why is a separate COUNT query needed for pagination metadata, and what's its performance cost at scale?
A4: `LIMIT`/`OFFSET` alone tells you the current page of results but not the TOTAL number of matches (needed for "Page 3 of 47" UI or "1,234 results found"). A separate `COUNT(*)` query with the same WHERE clause gets this, but COUNT over a large filtered result set can itself be slow (requires scanning/counting all matches, not just the current page). Mitigations: cache the count for a few seconds if exact real-time accuracy isn't critical, use approximate counts (Postgres `pg_class.reltuples` for rough total-table estimates, or Elasticsearch's efficient aggregation counts), or simply omit total count and offer "load more" instead of numbered pagination when exact counts aren't essential.

Q5: How do you handle multi-field search where different fields should have different relevance weight (e.g. matching the product NAME should rank higher than matching the DESCRIPTION)?
A5: In Postgres, use `setweight()` when building the tsvector: `setweight(to_tsvector(name), 'A') || setweight(to_tsvector(description), 'B')` — weight 'A' contributes more to the final `ts_rank` score than weight 'B'. In Elasticsearch, use field boosting in the query (`{ match: { name: { query: term, boost: 3 } } }` vs description with boost 1) to achieve the same effect — ensuring a product whose NAME matches the search term ranks above one that only matches in its description.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- User-facing search over a meaningful dataset (products, articles, listings) where relevance and speed matter
- You need filtering/faceting combined with text search (category + price range + keyword)

❌ Avoid when:
- Simple exact-match lookups (searching by a known ID or exact code) — a plain indexed equality query is simpler and faster than full-text search machinery
- Extremely small, static datasets where even a naive `LIKE` query performs acceptably and the complexity of a dedicated search stack isn't justified

---

## 📊 Visual Diagram
```
CLIENT                    SEARCH API                          DATA STORE
──────                    ───────────                         ───────────
GET /api/search?q=laptop
  &category=electronics
  &page=1
        │
        ▼
  ┌──────────────┐
  │ Sanitize query │  "laptop" → "laptop:*" (tsquery syntax)
  └──────┬───────┘
         ▼
  ┌──────────────┐
  │ Build WHERE    │  search_vector @@ to_tsquery($1) AND category = $2
  │ with filters   │
  └──────┬───────┘
         ▼
  ┌──────────────┐          ┌─────────────────────┐
  │ Run ranked     │ ──────► │ Postgres / Elasticsearch│
  │ query + count  │ ◄────── │ (GIN index / inverted   │
  └──────┬───────┘          │  index for fast lookup)  │
         ▼                  └─────────────────────┘
  { data: [...ranked results...],
    meta: { page, total, totalPages } }
         ▼
     Response to client
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Full-Text Search | Indexed keyword search with relevance ranking | Relevance ranking वाली indexed keyword search |
| tsvector/tsquery | Postgres full-text search data types | Postgres full-text search के data types |
| GIN Index | Index type optimized for full-text search | Full-text search के लिए optimized index type |
| Relevance Score | Numeric measure of how well a result matches | Result कितना अच्छे से match करता है, इसका numeric measure |
| Change Data Capture | Streaming DB changes to keep systems in sync | DB changes को stream करके systems sync रखना |
| Faceted Search | Search combined with category/attribute filters | Category/attribute filters के साथ combined search |

---

## ⚡ 3-Line Summary
English: 1. Production search APIs use full-text search (Postgres tsvector/GIN index) or dedicated engines (Elasticsearch), not `LIKE '%term%'`, for speed and relevance ranking. 2. Sanitize user input before building engine-specific query syntax, and combine text relevance with business signals (rating, recency) for better results. 3. Keep the search index in sync with the primary database via explicit update calls, database triggers, or change-data-capture pipelines.
Hindi: 1. Production search APIs full-text search (Postgres tsvector/GIN index) या dedicated engines (Elasticsearch) use करती हैं, `LIKE '%term%'` नहीं, speed और relevance ranking के लिए। 2. Engine-specific query syntax बनाने से पहले user input sanitize करो, text relevance को business signals के साथ combine करो। 3. Search index को explicit update calls, triggers, या CDC pipelines से sync रखो।

---

## ➡️ Next Topic
**286. Build Pagination API** — offset-based और cursor-based pagination implement करना।
