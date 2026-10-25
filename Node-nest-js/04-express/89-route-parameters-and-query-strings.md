# 89. Route Parameters + Query Strings
# हिंदी में: Route Parameters और Query Strings

---

## 🔵 Simple Definition (English)
**Route parameters** (`req.params`) are named placeholders in the URL path itself (e.g., `/users/:id` → `/users/42`). **Query strings** (`req.query`) are key-value pairs appended after `?` in the URL (e.g., `?page=2&sort=asc`). Both let clients pass dynamic data to the server, but params identify a specific resource while query strings filter/modify a request.

## 🔵 सरल परिभाषा (Hindi)
**Route parameters** (`req.params`) URL path में ही named placeholders होते हैं (जैसे `/users/:id` → `/users/42`)। **Query strings** (`req.query`) URL में `?` के बाद key-value pairs होते हैं (जैसे `?page=2&sort=asc`)। दोनों client को server को dynamic data भेजने देते हैं, पर params एक specific resource identify करते हैं जबकि query strings request को filter/modify करते हैं।

---

## 🔴 Problem it Solves
```
WITHOUT STRUCTURED PARAMS/QUERY:
  // Everything crammed into the path or parsed manually
  app.get('/getUserTransactionsPageTwoSortedByDate', handler);  // unscalable!

  // Or manual string splitting:
  app.get('/*', (req, res) => {
    const parts = req.url.split('/');       // fragile, breaks easily
    const query = req.url.split('?')[1];    // manual query string parsing
    const params = new URLSearchParams(query);
  });

WITH EXPRESS:
  app.get('/users/:userId/transactions', (req, res) => {
    const { userId } = req.params;                     // clean, from path
    const { page = 1, sort = 'date' } = req.query;      // clean, from query
  });
  // GET /users/42/transactions?page=2&sort=date
```

## 🔴 यह क्यों बना? (Hindi)
बिना structured params/query के, dynamic data को URL path में hardcode करना पड़ता या manually `req.url` split करना पड़ता था — यह fragile और unmaintainable था। Express ने route pattern syntax (`:param`) और automatic query string parsing (`req.query`) देकर इसे clean और declarative बना दिया।

---

## 🟢 How it Works — Step by Step

Step 1 → Route pattern like `/users/:id/posts/:postId` is compiled into a regex that captures named groups
Step 2 → When a request `/users/5/posts/10` arrives, Express extracts `{ id: '5', postId: '10' }` into `req.params`
Step 3 → The query string portion (`?key=value&key2=value2`) is parsed separately using Node's `querystring`/`qs` library into `req.query`
Step 4 → Both are plain JS objects available on `req` by the time your route handler runs — no extra middleware needed for basic cases
Step 5 → Arrays and nested objects in query strings (`?tags[]=a&tags[]=b`) are parsed by the `qs` library Express uses internally

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Route pattern जैसे `/users/:id/posts/:postId` एक regex में compile होता है जो named groups capture करता है
Step 2 → Request `/users/5/posts/10` आने पर Express `{ id: '5', postId: '10' }` को `req.params` में extract करता है
Step 3 → Query string भाग (`?key=value&key2=value2`) को Node की `querystring`/`qs` library से parse करके `req.query` में डाला जाता है
Step 4 → ये दोनों plain JS objects हैं जो handler चलने तक तैयार होते हैं — basic case में extra middleware नहीं चाहिए
Step 5 → Query strings में arrays और nested objects (`?tags[]=a&tags[]=b`) Express के internal `qs` library से parse होते हैं

---

## 🟡 Real World Example
**Flipkart product search:** `GET /api/products/electronics/mobiles?brand=samsung&minPrice=10000&maxPrice=50000&sort=price_asc&page=2` — `req.params` gives `{ category: 'electronics', subcategory: 'mobiles' }` (from route `/api/products/:category/:subcategory`), while `req.query` gives `{ brand: 'samsung', minPrice: '10000', maxPrice: '50000', sort: 'price_asc', page: '2' }` — used to build the MongoDB/SQL filter query.

## 🟡 Real Example Hindi mein
**Flipkart product search:** `GET /api/products/electronics/mobiles?brand=samsung&minPrice=10000&maxPrice=50000&sort=price_asc&page=2` — `req.params` देता है `{ category: 'electronics', subcategory: 'mobiles' }` (route `/api/products/:category/:subcategory` से), जबकि `req.query` देता है `{ brand: 'samsung', minPrice: '10000', ... }` — यह MongoDB/SQL filter query बनाने में use होता है।

---

## 💻 Code Example — Basic

```javascript
// params-query-basic.js
const express = require('express');
const app = express();

// Single route param
app.get('/users/:id', (req, res) => {
  res.json({ userId: req.params.id });
});

// Multiple route params
app.get('/users/:userId/orders/:orderId', (req, res) => {
  res.json({
    userId: req.params.userId,
    orderId: req.params.orderId,
  });
});

// Query string parsing
app.get('/search', (req, res) => {
  // GET /search?q=laptop&category=electronics
  const { q, category } = req.query;
  res.json({ searchTerm: q, category });
});

// Query string array syntax: ?tags=js&tags=node → req.query.tags = ['js', 'node']
app.get('/filter', (req, res) => {
  const tags = req.query.tags;  // could be string (one value) or array (multiple)
  const tagArray = Array.isArray(tags) ? tags : [tags].filter(Boolean);
  res.json({ tags: tagArray });
});

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// params-query-advanced.js — validation, defaults, nested query objects

const express = require('express');
const app = express();

// Middleware: validate route param format BEFORE handler runs
const validateMongoId = (req, res, next) => {
  const { id } = req.params;
  const isValidId = /^[0-9a-fA-F]{24}$/.test(id);  // MongoDB ObjectId pattern
  if (!isValidId) {
    return res.status(400).json({ error: `Invalid ID format: ${id}` });
  }
  next();
};

app.get('/api/products/:id', validateMongoId, (req, res) => {
  res.json({ id: req.params.id, valid: true });
});

// Pagination + filtering + sorting — a common real-world query handler
app.get('/api/products', (req, res) => {
  // Defaults + type coercion for query params (always strings by default!)
  const page = Math.max(1, parseInt(req.query.page, 10) || 1);
  const limit = Math.min(100, parseInt(req.query.limit, 10) || 20);  // cap at 100
  const sort = ['price_asc', 'price_desc', 'newest'].includes(req.query.sort)
    ? req.query.sort
    : 'newest';  // whitelist valid sort values

  // Nested query object: ?price[min]=100&price[max]=500 → req.query.price = { min: '100', max: '500' }
  const priceMin = req.query.price?.min ? Number(req.query.price.min) : undefined;
  const priceMax = req.query.price?.max ? Number(req.query.price.max) : undefined;

  res.json({
    page, limit, sort,
    filters: { priceMin, priceMax },
    skip: (page - 1) * limit,  // useful for DB pagination
  });
});

// Route param with regex constraint directly in the path (Express supports this)
app.get('/orders/:id(\\d+)', (req, res) => {
  // Only matches if :id is purely digits — /orders/abc won't match this route
  res.json({ orderId: Number(req.params.id) });
});

app.listen(3000);
```

---

## 🟠 Express.js Integration

```javascript
// Real-world: Zomato restaurant search with params + query
const express = require('express');
const app = express();

app.get('/api/cities/:city/restaurants', (req, res) => {
  const { city } = req.params;                         // from path
  const {
    cuisine,                                            // ?cuisine=italian
    minRating = 0,                                      // ?minRating=4
    isOpenNow,                                          // ?isOpenNow=true
    page = 1,
    limit = 10,
  } = req.query;

  const filters = {
    city,
    cuisine: cuisine || undefined,
    minRating: Number(minRating),
    openNow: isOpenNow === 'true',
  };

  // simulate DB query with filters
  res.json({
    filters,
    page: Number(page),
    limit: Number(limit),
    restaurants: [],  // would come from DB
  });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using route params for optional filter-like data
```javascript
// WRONG: forcing filters into the path makes routes rigid
app.get('/products/:category/:minPrice/:maxPrice/:sort', handler);
// What if sort is not needed? URL becomes awkward: /products/shoes/0/0/none

// CORRECT: use query strings for optional/filter data, params for resource identity
app.get('/products/:category', (req, res) => {
  const { minPrice, maxPrice, sort } = req.query;  // all optional via ?key=value
});
```

❌ **Mistake 2:** Not validating/sanitizing route params before using in a DB query
```javascript
// WRONG: trusting req.params blindly (can cause errors or injection in raw queries)
app.get('/users/:id', async (req, res) => {
  const user = await db.query(`SELECT * FROM users WHERE id = ${req.params.id}`); // ❌ SQL injection!
});

// CORRECT: validate type + use parameterized queries
app.get('/users/:id', async (req, res) => {
  if (!/^\d+$/.test(req.params.id)) return res.status(400).json({ error: 'Invalid ID' });
  const user = await db.query('SELECT * FROM users WHERE id = ?', [req.params.id]);
});
```

---

## 🧠 Tricky Interview Question

```javascript
// Route: app.get('/search', handler)
// Request: GET /search?tags=node&tags=express&tags=js
app.get('/search', (req, res) => {
  console.log(typeof req.query.tags, req.query.tags);
});
// What prints if the SAME query key appears once vs multiple times?
```
Answer: If `tags` appears once (`?tags=node`), `req.query.tags` is the string `'node'` (`typeof` → `'string'`). If it appears MULTIPLE times (`?tags=node&tags=express&tags=js`), Express's underlying `qs` parser automatically converts it into an ARRAY: `['node', 'express', 'js']` (`typeof` → `'object'`). This inconsistency is a classic gotcha — always normalize with `Array.isArray(req.query.tags) ? req.query.tags : [req.query.tags]` before processing.

---

## ⚫ Interview Questions + Answers

Q1: What's the fundamental difference between route params and query strings, and when do you use each?
A1: Route params (`:id`) identify a SPECIFIC resource and are typically REQUIRED for the route to make sense (`/users/:id` without an id doesn't identify any user). Query strings are for OPTIONAL filtering, sorting, pagination — data that modifies HOW you fetch something, not WHAT you're fetching. Rule of thumb: if removing it breaks the concept of the route, it's a param; if it's optional/for filtering, it's a query string.

Q2: Why are all values in `req.query` and `req.params` strings, even for numeric-looking data?
A2: HTTP URLs are plain text — there's no type information in a URL (`?page=2` is literally the three characters `'2'`). Express/Node has no way to know if you meant a number, boolean, or string, so it always gives you strings. You must explicitly convert with `Number()`, `parseInt()`, or `=== 'true'` for booleans.

Q3: How does Express handle the SAME query key appearing multiple times (e.g., `?tag=a&tag=b`)?
A3: Express (via the `qs` library) converts repeated keys into an array automatically: `req.query.tag` becomes `['a', 'b']`. But if the key appears only ONCE, it stays a plain string, not a single-element array. This inconsistency means you should always normalize: `const tags = [].concat(req.query.tag || [])`.

Q4: Can you add constraints directly in a route pattern, like requiring a param to be numeric?
A4: Yes, Express supports inline regex per param: `app.get('/orders/:id(\\d+)', handler)` only matches if `:id` consists purely of digits. This is less common in modern code (validation middleware or libraries like `express-validator`/Zod are preferred for readability and reusable error messages), but it's a quick way to prevent a route from matching invalid formats at the routing layer itself.

Q5: How would you parse a nested query string like `?price[min]=100&price[max]=500`?
A5: Express's default query parser (`qs`) handles this automatically — `req.query.price` becomes `{ min: '100', max: '500' }` without any extra code. This is different from Node's built-in `querystring` module, which does NOT support nested objects — Express uses `qs` specifically because it's more feature-rich (nested objects, arrays, etc.).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Route params: identifying a specific resource (`/orders/:id`, `/users/:userId/posts/:postId`)
- Query strings: optional filters, search terms, pagination, sorting (`?page=2&sort=price`)

❌ Avoid when:
- Putting large or structured data (like a full JSON object) into query strings — use a POST body instead
- Using route params for data that should be optional — it forces awkward URL structures

---

## 📊 Visual Diagram
```
  URL: /users/42/orders?status=pending&page=2&sort=date
         └──┬──┘           └──────────┬───────────────┘
         ROUTE PATH              QUERY STRING
         (with param)
            │                        │
            ▼                        ▼
  Route pattern:              Parsed by `qs` library:
  /users/:id/orders           req.query = {
            │                   status: 'pending',
            ▼                   page: '2',
  req.params = { id: '42' }     sort: 'date'
                                }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Route param | Named segment in URL path | URL path में named segment |
| Query string | Key-value pairs after `?` | `?` के बाद key-value pairs |
| `qs` library | Express's query string parser | Express का query string parser |
| Type coercion | Converting string → number/boolean | String को number/boolean में convert करना |
| Whitelisting | Allowing only known-safe values | सिर्फ known-safe values allow करना |

---

## ⚡ 3-Line Summary
English: 1. Route params (`:id`) identify specific resources; query strings (`?key=value`) handle optional filters/pagination/sorting. 2. All values from both are strings — always explicitly convert types before comparing or using numerically. 3. Repeated query keys become arrays automatically via Express's `qs` parser — normalize before use.
Hindi: 1. Route params (`:id`) specific resources identify करते हैं; query strings (`?key=value`) optional filters/pagination/sorting handle करते हैं। 2. दोनों के values strings होते हैं — numeric use से पहले हमेशा explicitly convert करो। 3. Repeated query keys automatically arrays बन जाते हैं — use से पहले normalize करो।

---

## ➡️ Next Topic
**90. HTTP Methods (GET, POST, PUT, PATCH, DELETE)** — Semantics and correct usage of each HTTP verb in REST APIs.
