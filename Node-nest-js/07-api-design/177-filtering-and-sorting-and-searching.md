# 177. Filtering + Sorting + Searching
# हिंदी में: Filtering + Sorting + Searching — Query Params से Results Control करना

---

## 🔵 Simple Definition (English)
**Filtering**, **sorting**, and **searching** let API clients narrow down and order a collection of resources using query string parameters (`?category=electronics&sort=-price&q=phone`), instead of the server always returning the full dataset and letting the client figure it out. This reduces payload size, server load, and gives clients flexible control over what they see.

## 🔵 सरल परिभाषा (Hindi)
**Filtering**, **sorting**, और **searching** API clients को query string parameters (`?category=electronics&sort=-price&q=phone`) से resources की collection को narrow down और order करने देते हैं, ना कि server हमेशा पूरा dataset भेजे और client खुद figure out करे। यह payload size, server load कम करता है, और clients को flexible control देता है।

---

## 🔴 Problem it Solves
Without server-side filtering/sorting/searching:
```
GET /products  →  returns ALL 50,000 products
Client then: filters by category in JavaScript, sorts by price in JavaScript, searches by name in JavaScript
```
Problems: (1) Massive payload — downloading 50,000 products just to show 20 wastes bandwidth and time. (2) Slow on low-end mobile devices — filtering/sorting 50,000 JS objects client-side is CPU-heavy. (3) Can't paginate properly — you'd need the ENTIRE dataset before you can even show "page 1." Moving filtering/sorting/searching to the server (where the database can use indexes) solves all three — the client gets back exactly the 20 relevant, already-sorted items.

## 🔴 यह क्यों बना? (Hindi)
Server-side filtering/sorting/searching के बिना:
```
GET /products  →  सारे 50,000 products return होते हैं
Client फिर: category से JavaScript में filter करता है, price से sort करता है, name से search करता है
```
Problems: (1) Massive payload — सिर्फ 20 दिखाने के लिए 50,000 products download करना bandwidth/time waste। (2) Low-end mobile devices पर slow — 50,000 JS objects client-side filter/sort करना CPU-heavy है। (3) सही pagination नहीं हो सकती — "page 1" दिखाने के लिए भी पूरा dataset चाहिए। Filtering/sorting/searching को server पर move करने से (जहाँ database indexes use कर सकता है) तीनों problems solve होती हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Client sends query params: `?category=electronics&minPrice=1000&maxPrice=50000&sort=-price&q=phone&page=1&limit=20`.
Step 2 → Server parses these params and builds a dynamic database query/filter object — ONLY applying filters that are actually present.
Step 3 → For **sorting**, a `-` prefix (or `asc`/`desc` param) indicates direction: `sort=-price` means descending price; `sort=price` means ascending.
Step 4 → For **searching**, use a text/regex search on indexed fields (or a full-text search engine like Elasticsearch for complex relevance ranking at scale).
Step 5 → Combine filter + sort + search + pagination into ONE query, execute it, and return results with metadata (total count, applied filters) so the client can render UI state correctly.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client query params भेजता है: `?category=electronics&minPrice=1000&maxPrice=50000&sort=-price&q=phone&page=1&limit=20`।
Step 2 → Server इन params को parse करता है और dynamic database query/filter object बनाता है — सिर्फ actually present filters apply करता है।
Step 3 → **Sorting** के लिए, `-` prefix (या `asc`/`desc` param) direction बताता है: `sort=-price` मतलब descending price; `sort=price` मतलब ascending।
Step 4 → **Searching** के लिए, indexed fields पर text/regex search use करो (या बड़े scale पर relevance ranking के लिए Elasticsearch जैसा full-text search engine)।
Step 5 → Filter + sort + search + pagination को ONE query में combine करो, execute करो, और results को metadata (total count, applied filters) के साथ return करो।

---

## 🟡 Real World Example
**Flipkart's search/filter sidebar:** When a user searches "laptop" and then filters by "brand: Dell, HP" + "price: ₹30,000-₹60,000" + sorts by "Price: Low to High," ALL of this translates into ONE combined backend query: full-text search on `name`/`description` matching "laptop," `WHERE brand IN ('Dell','HP') AND price BETWEEN 30000 AND 60000`, `ORDER BY price ASC`, paginated to show 20 results. Flipkart's backend builds this dynamically based on which filter checkboxes the user has ticked — most filters are optional and only added to the query when present.

## 🟡 Real Example Hindi mein
**Flipkart का search/filter sidebar:** जब user "laptop" search करता है और फिर "brand: Dell, HP" + "price: ₹30,000-₹60,000" filter करता है + "Price: Low to High" से sort करता है, यह सब ONE combined backend query में translate होता है: `name`/`description` पर "laptop" का full-text search, `WHERE brand IN ('Dell','HP') AND price BETWEEN 30000 AND 60000`, `ORDER BY price ASC`, 20 results के लिए paginated। Flipkart का backend इसे dynamically बनाता है based on कौन से filter checkboxes user ने tick किये हैं।

---

## 💻 Code Example — Basic

```javascript
// basic-filter-sort-search.js
// Install: npm install express mongoose

const express = require('express');
const app = express();
const Product = require('./models/Product');

app.get('/products', async (req, res) => {
  const { category, minPrice, maxPrice, sort, q, page = 1, limit = 20 } = req.query;

  // Build filter object dynamically -- only add conditions that were actually provided
  const filter = {};
  if (category) filter.category = category;                 // exact match filter
  if (minPrice || maxPrice) {
    filter.price = {};
    if (minPrice) filter.price.$gte = Number(minPrice);       // price >= minPrice
    if (maxPrice) filter.price.$lte = Number(maxPrice);        // price <= maxPrice
  }
  if (q) filter.name = { $regex: q, $options: 'i' };          // case-insensitive partial match search

  // Build sort object: "-price" => { price: -1 }, "price" => { price: 1 }
  let sortObj = { _id: 1 }; // default sort
  if (sort) {
    const direction = sort.startsWith('-') ? -1 : 1;
    const field = sort.replace('-', '');
    sortObj = { [field]: direction };
  }

  const skip = (Number(page) - 1) * Number(limit);
  const [items, total] = await Promise.all([
    Product.find(filter).sort(sortObj).skip(skip).limit(Number(limit)),
    Product.countDocuments(filter),
  ]);

  res.json({ data: items, meta: { total, page: Number(page), limit: Number(limit) } });
});

app.listen(3000);
```

## 💻 Code Example — Advanced

```javascript
// advanced-filter-sort-search.js — whitelisting fields, multi-field sort, text index search

const express = require('express');
const app = express();
const Product = require('./models/Product');

// Only these fields are allowed to be filtered/sorted on -- prevents arbitrary/unsafe query injection
const ALLOWED_FILTER_FIELDS = ['category', 'brand', 'inStock'];
const ALLOWED_SORT_FIELDS = ['price', 'rating', 'createdAt'];

function buildFilter(query) {
  const filter = {};

  for (const field of ALLOWED_FILTER_FIELDS) {
    if (query[field] !== undefined) {
      // Support comma-separated multi-value filters: ?brand=Dell,HP -> { $in: ['Dell','HP'] }
      const values = String(query[field]).split(',');
      filter[field] = values.length > 1 ? { $in: values } : values[0];
    }
  }

  if (query.minPrice || query.maxPrice) {
    filter.price = {};
    if (query.minPrice) filter.price.$gte = Number(query.minPrice);
    if (query.maxPrice) filter.price.$lte = Number(query.maxPrice);
  }

  // Full-text search using a MongoDB text index (requires: schema.index({ name: 'text', description: 'text' }))
  if (query.q) {
    filter.$text = { $search: query.q };
  }

  return filter;
}

// Supports multiple sort fields: ?sort=-rating,price -> { rating: -1, price: 1 }
function buildSort(sortParam) {
  if (!sortParam) return { createdAt: -1 }; // default: newest first
  const sortObj = {};
  sortParam.split(',').forEach((part) => {
    const direction = part.startsWith('-') ? -1 : 1;
    const field = part.replace('-', '');
    if (ALLOWED_SORT_FIELDS.includes(field)) {
      sortObj[field] = direction; // only allow whitelisted fields -- security + predictability
    }
  });
  return Object.keys(sortObj).length ? sortObj : { createdAt: -1 };
}

app.get('/products', async (req, res, next) => {
  try {
    const filter = buildFilter(req.query);
    const sort = buildSort(req.query.sort);
    const page = Math.max(1, Number(req.query.page) || 1);
    const limit = Math.min(100, Number(req.query.limit) || 20); // cap limit to prevent abuse

    const projection = filter.$text ? { score: { $meta: 'textScore' } } : {}; // relevance score for text search
    let query = Product.find(filter, projection).sort(filter.$text ? { score: { $meta: 'textScore' } } : sort);

    const [items, total] = await Promise.all([
      query.skip((page - 1) * limit).limit(limit),
      Product.countDocuments(filter),
    ]);

    res.json({
      data: items,
      meta: { total, page, limit, appliedFilters: filter },
    });
  } catch (err) {
    next(err);
  }
});

module.exports = app;
```

---

## 🟠 Express.js Integration

```javascript
// Reusable query-parsing middleware shared across multiple resource routes
function parseListQuery(allowedFilters, allowedSorts) {
  return (req, res, next) => {
    req.listQuery = {
      filter: Object.fromEntries(
        Object.entries(req.query).filter(([key]) => allowedFilters.includes(key))
      ),
      sort: req.query.sort,
      page: Math.max(1, Number(req.query.page) || 1),
      limit: Math.min(100, Number(req.query.limit) || 20),
    };
    next();
  };
}

app.get('/orders', parseListQuery(['status', 'userId'], ['createdAt', 'total']), async (req, res) => {
  const { filter, page, limit } = req.listQuery;
  const orders = await Order.find(filter).skip((page - 1) * limit).limit(limit);
  res.json({ data: orders });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Directly passing raw `req.query` into the database query without whitelisting
✅ Correct: Whitelist allowed filter/sort fields — otherwise clients can filter/sort on unintended or sensitive fields, or even inject operators.

```javascript
// Wrong -- dangerous, allows clients to pass ANY MongoDB operator/field
const products = await Product.find(req.query);

// Right -- only apply explicitly allowed, type-checked fields
const filter = buildFilter(req.query); // whitelisted + validated
```

❌ Mistake 2: Using `$regex` search on unindexed fields at scale
✅ Correct: Regex searches without an index force a full collection scan, which is very slow on large datasets. Use a proper text index (`$text`) or a dedicated search engine (Elasticsearch, Algolia) for production-scale search.

```javascript
// Wrong at scale (slow full scan)
Product.find({ name: { $regex: q, $options: 'i' } });

// Right (uses text index)
Product.find({ $text: { $search: q } });
```

---

## 🧠 Tricky Interview Question

```javascript
// GET /products?sort=password&limit=99999
// What's wrong with this request if the server blindly applies req.query to the sort/limit?
```
Answer: Two issues: (1) **Unsafe sort field** — sorting by `password` (or any sensitive/unintended field) might not leak the field's VALUE directly, but it can leak information through side channels (e.g., inferring password hash ordering, or just exposing internal schema fields that shouldn't be sortable). The fix is a sort-field whitelist. (2) **Unbounded limit** — `limit=99999` could force the server to fetch and serialize a huge number of records, causing memory spikes or DoS-like slowdowns. The fix is capping `limit` server-side (e.g., `Math.min(100, requestedLimit)`) regardless of what the client requests.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between filtering and searching?
A1: **Filtering** narrows results by EXACT or range criteria on structured fields (`category=electronics`, `price between X and Y`) — deterministic, boolean match. **Searching** finds results by relevance/similarity on text content (`q=running shoes`), often with fuzzy matching, typo tolerance, and ranked results by relevance score — typically needs a text index or dedicated search engine for good quality at scale.

Q2: Why whitelist filter and sort fields instead of allowing any field from the query string?
A2: Security (prevent NoSQL/SQL injection via unexpected operators), predictability (avoid unindexed-field queries causing slow full scans), and API contract clarity (clients should only rely on documented, supported filters — not accidentally depend on internal/undocumented fields that might change).

Q3: How would you implement a combined AND/OR filter, e.g., "brand is Dell OR HP, AND price < 50000"?
A3: Build the query object with explicit `$and`/`$or` (MongoDB) or `AND`/`OR` (SQL) clauses based on parsed query params: e.g., `{ $and: [{ $or: [{brand:'Dell'},{brand:'HP'}] }, { price: {$lt: 50000} }] }`. Alternatively, support comma-separated values for implicit OR within one field (`?brand=Dell,HP` → `$in`) and treat different query params as implicit AND, covering the common 90% case without needing a full query DSL.

Q4: When should you move search to a dedicated engine like Elasticsearch instead of using your main database?
A4: When you need fuzzy/typo-tolerant matching, relevance ranking (TF-IDF/BM25 scoring), faceted search (aggregated filter counts), or search across millions of documents with sub-second latency. Elasticsearch is purpose-built for these; a general-purpose database's text search (`$text`, `LIKE`, basic full-text) works for simpler, smaller-scale needs but degrades in quality and speed at scale.

Q5: How do you return applied filters/sort info back to the client, and why is it useful?
A5: Include a `meta` object in the response showing `appliedFilters`, `sort`, `page`, `limit`, `total`. This helps clients (especially SPAs) sync UI state (which filter chips are "active," total result count for "Showing 1-20 of 532") without needing to separately track what was sent, and helps catch bugs where a filter param was silently ignored (e.g., typo in query param name).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any list/collection endpoint where the dataset can grow beyond what's reasonable to send in full.
- Building user-facing search/filter UIs (e-commerce, dashboards, admin panels).

❌ Avoid when:
- The dataset is tiny and fixed (e.g., a list of 5 configuration options) — server-side filtering adds unnecessary complexity.

---

## 📊 Visual Diagram
```
QUERY STRING                         SERVER-SIDE QUERY BUILDING
──────────────────────────────────────────────────────────────
?category=electronics       ──▶  filter.category = 'electronics'
&minPrice=1000&maxPrice=50000 ──▶  filter.price = { $gte:1000, $lte:50000 }
&q=phone                    ──▶  filter.$text = { $search: 'phone' }
&sort=-price                ──▶  sort = { price: -1 }
&page=1&limit=20            ──▶  skip=0, limit=20
                                        │
                                        ▼
                            ONE combined database query
                                        │
                                        ▼
                      { data: [...20 items], meta: { total, page } }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Filtering | Narrowing by exact/range match | Exact/range match से narrow करना |
| Sorting | Ordering results | Results order करना |
| Searching | Relevance-based text matching | Relevance-based text match |
| Whitelisting | Allowing only specific fields | सिर्फ specific fields allow करना |
| Text index | DB index for full-text search | Full-text search के लिए DB index |

---

## ⚡ 3-Line Summary
English:
1. Move filtering, sorting, and searching to the server/database so clients get small, relevant, pre-sorted result sets instead of the full dataset.
2. Always whitelist which fields can be filtered/sorted on, and cap the result limit server-side to prevent abuse.
3. Use regex/basic text search for small-scale needs; use a text index or dedicated engine (Elasticsearch) for relevance-ranked search at scale.

Hindi:
1. Filtering, sorting, searching को server/database पर move करो ताकि clients को पूरे dataset की जगह छोटा, relevant, pre-sorted result मिले।
2. हमेशा whitelist करो कि कौन से fields filter/sort हो सकते हैं, और abuse रोकने के लिए server-side limit cap करो।
3. छोटे scale के लिए regex/basic text search use करो; बड़े scale पर relevance-ranked search के लिए text index या dedicated engine (Elasticsearch) use करो।

---

## ➡️ Next Topic
**178. API Response Format Standard** — Consistent response envelope design for success responses।
