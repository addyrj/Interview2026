# 43. querystring Module
# हिंदी में: querystring Module — URL Query Strings Parse/Format करना

---

## 🔵 Simple Definition (English)
The **`querystring`** module (`require('querystring')`) parses and formats URL query strings — the part after `?` in a URL like `?name=rahul&age=25`. It converts between a query string and a plain JavaScript object: `parse()` string → object, `stringify()` object → string. It's a legacy module — modern code mostly uses the newer `URLSearchParams` (global, web-standard) instead.

## 🔵 सरल परिभाषा (Hindi)
**`querystring`** module URL के query string (जो `?` के बाद आता है, जैसे `?name=rahul&age=25`) को parse और format करता है। `parse()` string को object में बदलता है, `stringify()` object को string में। यह एक legacy module है — modern code ज़्यादातर नए `URLSearchParams` (global, web-standard) को use करता है।

---

## 🔴 Problem it Solves
Before any helper existed, developers had to manually split query strings on `&` and `=`, handle URL-encoding (`%20` for space, `%40` for `@`), and deal with arrays (`tags=a&tags=b`). This was error-prone — forgetting to decode `%` sequences led to broken data (`name=Rahul%20Kumar` showing as `Rahul%20Kumar` instead of `Rahul Kumar`). `querystring` standardized this parsing/encoding logic into the core runtime so every app didn't reinvent it.

## 🔴 यह क्यों बना? (Hindi)
पहले developers को manually `&` और `=` पर split करना पड़ता था, URL-encoding (`%20` space के लिए, `%40` `@` के लिए) handle करनी पड़ती थी, और arrays (`tags=a&tags=b`) को संभालना पड़ता था। यह error-prone था — `%` sequences decode करना भूल जाने से data टूट जाता था। `querystring` ने यह logic core runtime में standardize कर दिया।

---

## 🟢 How it Works — Step by Step

Step 1 → Import: `const qs = require('querystring');`
Step 2 → Parsing: `qs.parse('name=Rahul&age=25')` → splits on `&`, then each pair on `=`, URL-decodes each part → `{ name: 'Rahul', age: '25' }`.
Step 3 → Repeated keys become arrays: `qs.parse('tags=node&tags=js')` → `{ tags: ['node', 'js'] }`.
Step 4 → Stringifying: `qs.stringify({ name: 'Rahul Kumar' })` → URL-encodes values → `'name=Rahul%20Kumar'`.
Step 5 → `qs.escape()`/`qs.unescape()` do raw percent-encoding/decoding of individual strings (like `encodeURIComponent`/`decodeURIComponent`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Import करो: `const qs = require('querystring');`
Step 2 → Parsing: `qs.parse('name=Rahul&age=25')` `&` पर split करता है, फिर हर pair को `=` पर, और हर part को URL-decode करता है → `{ name: 'Rahul', age: '25' }`।
Step 3 → Repeated keys array बन जाती हैं: `qs.parse('tags=node&tags=js')` → `{ tags: ['node', 'js'] }`।
Step 4 → Stringify करना: `qs.stringify({ name: 'Rahul Kumar' })` → values URL-encode होती हैं → `'name=Rahul%20Kumar'`।
Step 5 → `qs.escape()`/`qs.unescape()` individual strings को percent-encode/decode करते हैं (जैसे `encodeURIComponent`/`decodeURIComponent`)।

---

## 🟡 Real World Example
**Flipkart's product search URL:** `https://flipkart.com/search?q=mobile+phone&price_range=10000-20000&brand=samsung&brand=apple`. The backend search service needs to parse `q`, `price_range`, and the repeated `brand` param. `querystring.parse(url.split('?')[1])` gives `{ q: 'mobile phone', price_range: '10000-20000', brand: ['samsung', 'apple'] }` — directly usable to build a database filter. When building the "next page" link, `querystring.stringify({ ...filters, page: 2 })` safely re-encodes everything.

## 🟡 Real Example Hindi mein
**Flipkart की product search URL:** `?q=mobile+phone&price_range=10000-20000&brand=samsung&brand=apple`। Backend search service को `q`, `price_range`, और repeated `brand` param parse करना है। `querystring.parse()` से मिलता है `{ q: 'mobile phone', ..., brand: ['samsung', 'apple'] }` — directly database filter बनाने में इस्तेमाल होता है।

---

## 💻 Code Example — Basic
```javascript
// querystring-basics.js
const qs = require('querystring'); // import built-in module

// 1. Parse a query string into an object
const parsed = qs.parse('name=Rahul&age=25&city=Delhi');
console.log(parsed); // { name: 'Rahul', age: '25', city: 'Delhi' }
console.log(typeof parsed.age); // 'string' -- querystring NEVER converts types

// 2. Parse repeated keys -> array
const multi = qs.parse('tags=node&tags=express&tags=js');
console.log(multi.tags); // [ 'node', 'express', 'js' ]

// 3. Stringify an object back into a query string
const str = qs.stringify({ name: 'Rahul Kumar', city: 'New Delhi' });
console.log(str); // 'name=Rahul%20Kumar&city=New%20Delhi' (space -> %20)

// 4. escape / unescape single values (like encodeURIComponent/decodeURIComponent)
console.log(qs.escape('hello world@123')); // 'hello%20world%4O123' style encoding
console.log(qs.unescape('hello%20world'));  // 'hello world'

// 5. Custom separators (rare, but supported)
const customSep = qs.parse('name:Rahul;city:Delhi', ';', ':');
console.log(customSep); // { name: 'Rahul', city: 'Delhi' }
```

## 💻 Code Example — Advanced
```javascript
// querystring-advanced.js -- production style usage with URL + validation
const qs = require('querystring');
const { URL } = require('url');

// Build a safe search URL for an e-commerce API (handles encoding automatically)
function buildSearchUrl(baseUrl, filters) {
  // Remove undefined/null filters before stringifying
  const cleanFilters = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== undefined && v !== null)
  );
  const query = qs.stringify(cleanFilters); // auto URL-encodes everything
  return `${baseUrl}?${query}`;
}

const url = buildSearchUrl('https://api.flipkart.com/search', {
  q: 'mobile phone & accessories', // contains special chars
  brand: ['samsung', 'apple'],     // array -> repeated key
  page: 1,
});
console.log(url);
// https://api.flipkart.com/search?q=mobile%20phone%20%26%20accessories&brand=samsung&brand=apple&page=1

// Parse incoming request query safely with defaults + type coercion
function parseSearchQuery(queryString) {
  const raw = qs.parse(queryString);
  return {
    q: raw.q || '',
    page: parseInt(raw.page, 10) || 1,              // querystring gives strings -> coerce
    brands: Array.isArray(raw.brand) ? raw.brand : (raw.brand ? [raw.brand] : []),
  };
}

console.log(parseSearchQuery('q=laptop&page=3&brand=hp&brand=dell'));
// { q: 'laptop', page: 3, brands: [ 'hp', 'dell' ] }

// Modern alternative using URLSearchParams (preferred in new code)
function parseWithURLSearchParams(fullUrl) {
  const u = new URL(fullUrl);
  return Object.fromEntries(u.searchParams.entries()); // simple, but loses dup keys unless using getAll
}
console.log(parseWithURLSearchParams('https://flipkart.com/search?q=tv&page=2'));
// { q: 'tv', page: '2' }
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const qs = require('querystring');
const app = express();

// Express parses req.query for you using its own query parser (qs library by default),
// but sometimes you need raw querystring parsing (e.g. reading req.url manually)
app.get('/search', (req, res) => {
  // req.query is already parsed by Express -- no need to call qs.parse() yourself
  console.log(req.query); // { q: 'mobile', brand: [ 'samsung', 'apple' ] }

  // Manual parsing example: extracting query from req.url directly
  const rawQuery = req.url.split('?')[1] || '';
  const manualParsed = qs.parse(rawQuery);
  console.log('Manual parse matches req.query:', manualParsed);

  res.json({ received: req.query });
});

// Building a redirect URL with querystring.stringify()
app.post('/apply-filter', (req, res) => {
  const filters = { category: req.body.category, sort: req.body.sort, page: 1 };
  const query = qs.stringify(filters);
  res.redirect(`/search?${query}`); // safe, URL-encoded redirect
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming parsed values keep their original types
```javascript
// Wrong
const { age } = qs.parse('age=25');
if (age === 25) console.log('adult'); // NEVER runs -- age is string '25', not number 25

// Right
const { age } = qs.parse('age=25');
if (parseInt(age, 10) === 25) console.log('adult'); // explicitly coerce type
```

❌ Mistake 2: Forgetting to encode special characters before building URLs manually
```javascript
// Wrong
const url = `/search?q=${req.body.query}`; // if query has spaces/& -> broken URL

// Right
const url = `/search?${qs.stringify({ q: req.body.query })}`; // auto-encoded, safe
```

---

## 🧠 Tricky Interview Question
```javascript
const qs = require('querystring');
console.log(qs.parse('a=1&a=2&b=3'));
console.log(qs.parse(''));
console.log(qs.stringify({ a: undefined, b: null, c: 1 }));
```
Answer: `qs.parse('a=1&a=2&b=3')` → `{ a: [ '1', '2' ], b: '3' }` (repeated key becomes an array, single key stays a string). `qs.parse('')` → `{}` (empty object, not null/undefined). `qs.stringify({ a: undefined, b: null, c: 1 })` → `'a=&b=&c=1'` — `undefined` and `null` are stringified as empty strings, NOT omitted from the output (unlike `JSON.stringify` which drops `undefined` keys).

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `querystring` module and `URLSearchParams`?
A1: `querystring` is Node-specific, older, and slightly faster for simple string<->object conversion. `URLSearchParams` is a web standard (also available in browsers), works with the `URL` class, supports iteration (`for...of`), and has methods like `.getAll()`, `.append()`, `.set()`. Modern Node.js code generally prefers `URLSearchParams` for new projects; `querystring` is kept for legacy compatibility.

Q2: Does `querystring.parse()` decode URL-encoded characters automatically?
A2: Yes. `qs.parse('name=Rahul%20Kumar')` automatically decodes `%20` to a space, giving `{ name: 'Rahul Kumar' }`. It uses `decodeURIComponent`-style decoding internally (with a custom, faster decoder for performance).

Q3: How does `querystring.parse()` handle duplicate keys?
A3: Duplicate keys are collected into an array in the order they appear: `qs.parse('tag=a&tag=b')` → `{ tag: ['a', 'b'] }`. A single occurrence stays a plain string, not a single-element array — this inconsistency is a common source of bugs (code must check `Array.isArray()` before using the value).

Q4: Why would Express.js code rarely call `querystring` directly?
A4: Express automatically parses the query string from the request URL into `req.query` using its own configurable query parser (`qs` npm package by default, which is a superset with nested-object support like `a[b]=1`). Developers only reach for the raw `querystring`/`URLSearchParams` modules when building outgoing URLs, working outside Express, or needing to manually inspect `req.url`.

Q5: What does `querystring.stringify()` do with array and object values?
A5: Arrays are stringified as repeated keys: `qs.stringify({ tags: ['a', 'b'] })` → `'tags=a&tags=b'`. Nested objects are NOT supported natively — they get coerced to strings like `[object Object]`, which is usually wrong; for nested data, use the `qs` npm package (`qs.stringify({ a: { b: 1 } })` → `'a%5Bb%5D=1'`) or send JSON in the body instead.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Working with raw query strings outside a framework (CLI tools, simple scripts)
- You need fast, dependency-free parsing of flat `key=value` pairs
- Maintaining legacy code that already uses `querystring`

❌ Avoid when:
- You need nested object support (`a[b][c]=1`) — use the `qs` npm package instead
- Building new code where `URLSearchParams` (web-standard, globally available) fits better
- Using Express — `req.query` is already parsed for you

---

## 📊 Visual Diagram
```
URL: https://flipkart.com/search?q=mobile&brand=samsung&brand=apple
                                  └──────────── query string ────────────┘

  qs.parse('q=mobile&brand=samsung&brand=apple')
        │
        ▼
  Split on '&' ──► ['q=mobile', 'brand=samsung', 'brand=apple']
        │
        ▼
  Split each on '=' + URL-decode
        │
        ▼
  { q: 'mobile', brand: ['samsung', 'apple'] }   <-- repeated key = array

  qs.stringify({ q: 'mobile', brand: ['samsung','apple'] })
        │
        ▼
  'q=mobile&brand=samsung&brand=apple'   <-- reverse operation
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| querystring | Part of URL after `?` | URL का `?` के बाद वाला हिस्सा |
| parse() | string → object | String को object में बदलना |
| stringify() | object → string | Object को string में बदलना |
| URL-encoding | Special chars as %XX | Special characters को %XX में बदलना |
| escape()/unescape() | Encode/decode single value | एक value को encode/decode करना |
| URLSearchParams | Modern web-standard alternative | नया web-standard विकल्प |

---

## ⚡ 3-Line Summary
English: `querystring` converts between URL query strings and JS objects via `parse()` and `stringify()`. All parsed values are strings (or arrays of strings for duplicate keys) — never auto-coerced to numbers/booleans. Modern code prefers `URLSearchParams`, but Express abstracts this entirely via `req.query`.

Hindi: `querystring` URL query strings और JS objects के बीच convert करता है `parse()` और `stringify()` से। सभी parsed values strings होती हैं (duplicate keys के लिए arrays) — number/boolean में auto-convert नहीं होतीं। Modern code `URLSearchParams` पसंद करता है, पर Express इसे `req.query` से पूरी तरह abstract कर देता है।

---

## ➡️ Next Topic
**44. crypto Module — Hashing + Encryption** — password hashing, HMAC, and symmetric encryption using Node's built-in crypto primitives.
