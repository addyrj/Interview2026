# 42. url Module
# हिंदी में: url Module — URLs Parse और Build करना

---

## 🔵 Simple Definition (English)
The **`url`** module is Node's built-in API for parsing, constructing, and manipulating URLs. Modern Node uses the **WHATWG URL API** (`new URL(string)`, the same standard used in browsers), which replaced the older, legacy `url.parse()`/`url.format()` functions.

## 🔵 सरल परिभाषा (Hindi)
**`url`** module Node का built-in API है URLs parse, construct, और manipulate करने के लिए। Modern Node **WHATWG URL API** use करता है (`new URL(string)`, वही standard जो browsers में use होता है), जो older, legacy `url.parse()`/`url.format()` functions की जगह ले लिया है।

---

## 🔴 Problem it Solves
Every web server needs to extract information from request URLs — the path, query parameters, hash fragment, protocol, hostname — and every HTTP client needs to construct valid URLs with properly-encoded parameters. Manually parsing URL strings with regex or string splitting is error-prone (handling encoding, edge cases with special characters, malformed input). The `url` module (especially the modern WHATWG `URL` class) provides a standard, battle-tested, spec-compliant way to do this reliably, matching exactly how browsers interpret URLs.

## 🔴 यह क्यों बना? (Hindi)
हर web server को request URLs से information निकालनी होती है — path, query parameters, hash fragment, protocol, hostname — और हर HTTP client को properly-encoded parameters के साथ valid URLs बनानी होती हैं। URL strings को regex या string splitting से manually parse करना error-prone है (encoding handle करना, special characters के edge cases, malformed input)। `url` module (especially modern WHATWG `URL` class) इसे reliably करने का एक standard, battle-tested, spec-compliant तरीका देता है, exactly वैसे ही जैसे browsers URLs को interpret करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `const { URL, URLSearchParams } = require('url')` — though `URL` and `URLSearchParams` are also GLOBAL in Node (no require needed at all, same as in browsers).
Step 2 → `new URL(urlString, [base])` parses a URL string into an object with properties: `.protocol`, `.hostname`, `.port`, `.pathname`, `.search` (raw query string), `.searchParams` (a `URLSearchParams` object for easy query access), `.hash`.
Step 3 → The `base` parameter is used when `urlString` is RELATIVE — `new URL('/path', 'https://example.com')` resolves to `https://example.com/path`.
Step 4 → `.searchParams.get('key')` reads a query parameter; `.searchParams.set('key', 'value')` adds/updates one; `.searchParams.append()` adds without replacing (supports repeated keys); iterate with `for (const [key, value] of url.searchParams)`.
Step 5 → `URLSearchParams` can ALSO be used standalone (without a full URL) to build/parse just a query string: `new URLSearchParams('a=1&b=2')` or `new URLSearchParams({ a: 1, b: 2 })`.
Step 6 → The LEGACY API (`url.parse()`, `url.format()`, `url.resolve()`) is deprecated in favor of the WHATWG `URL` class — avoid it in new code; it has known inconsistencies with how browsers actually parse URLs.
Step 7 → For incoming Express/http requests, `req.url` is only the PATH+QUERY portion (no protocol/host) — to build a full `URL` object from it, you need to supply a base: `new URL(req.url, `http://${req.headers.host}`)`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `const { URL, URLSearchParams } = require('url')` — हालाँकि `URL` और `URLSearchParams` Node में GLOBAL भी हैं (कोई require नहीं चाहिए, browsers जैसे ही)।
Step 2 → `new URL(urlString, [base])` URL string को एक object में parse करता है जिसके properties हैं: `.protocol`, `.hostname`, `.port`, `.pathname`, `.search` (raw query string), `.searchParams` (easy query access के लिए `URLSearchParams` object), `.hash`।
Step 3 → `base` parameter तब use होता है जब `urlString` RELATIVE हो — `new URL('/path', 'https://example.com')` `https://example.com/path` में resolve होता है।
Step 4 → `.searchParams.get('key')` एक query parameter पढ़ता है; `.searchParams.set('key', 'value')` add/update करता है; `.searchParams.append()` बिना replace किए add करता है (repeated keys support करता है); `for (const [key, value] of url.searchParams)` से iterate करो।
Step 5 → `URLSearchParams` standalone भी use हो सकता है (पूरी URL के बिना) सिर्फ एक query string build/parse करने के लिए: `new URLSearchParams('a=1&b=2')` या `new URLSearchParams({ a: 1, b: 2 })`।
Step 6 → LEGACY API (`url.parse()`, `url.format()`, `url.resolve()`) WHATWG `URL` class के favor में deprecated है — नए code में avoid करो; browsers actually URLs कैसे parse करते हैं उससे known inconsistencies हैं।
Step 7 → Incoming Express/http requests के लिए, `req.url` केवल PATH+QUERY हिस्सा है (कोई protocol/host नहीं) — इससे पूरा `URL` object बनाने के लिए, एक base supply करना होता है: `new URL(req.url, `http://${req.headers.host}`)`।

---

## 🟡 Real World Example
**Flipkart's product-search API gateway:** Incoming requests like `/search?category=electronics&minPrice=1000&maxPrice=50000&sort=price_asc` need robust query parameter parsing. The gateway uses `new URL(req.url, baseUrl).searchParams` to safely extract `category`, `minPrice`, `maxPrice`, `sort` — correctly handling URL-encoded special characters in search terms (e.g., `category=home%20%26%20kitchen` decodes to `"home & kitchen"` automatically), something manual string splitting on `&`/`=` would get wrong for encoded ampersands and special characters.

## 🟡 Real Example Hindi mein
**Flipkart का product-search API gateway:** Incoming requests जैसे `/search?category=electronics&minPrice=1000&maxPrice=50000&sort=price_asc` को robust query parameter parsing चाहिए। Gateway `new URL(req.url, baseUrl).searchParams` use करके safely `category`, `minPrice`, `maxPrice`, `sort` निकालता है — URL-encoded special characters को search terms में correctly handle करता है (जैसे `category=home%20%26%20kitchen` automatically `"home & kitchen"` में decode होता है), जो manual string splitting `&`/`=` पर encoded ampersands और special characters के लिए गलत होता।

---

## 💻 Code Example — Basic

```javascript
// urlBasics.js — the modern WHATWG URL API
const { URL } = require('url'); // also available globally, this require is optional

const myUrl = new URL('https://api.example.com:8080/products/search?category=electronics&sort=price#results');

console.log('protocol:', myUrl.protocol);   // "https:"
console.log('hostname:', myUrl.hostname);    // "api.example.com"
console.log('port:', myUrl.port);             // "8080"
console.log('pathname:', myUrl.pathname);     // "/products/search"
console.log('search:', myUrl.search);         // "?category=electronics&sort=price"
console.log('hash:', myUrl.hash);             // "#results"

// Working with query parameters via searchParams
console.log('category:', myUrl.searchParams.get('category')); // "electronics"
console.log('sort:', myUrl.searchParams.get('sort'));           // "price"

// Modifying the URL
myUrl.searchParams.set('page', '2'); // add a new query param
console.log('Updated URL:', myUrl.toString());
// → "https://api.example.com:8080/products/search?category=electronics&sort=price&page=2#results"
```

## 💻 Code Example — Advanced

```javascript
// urlAdvanced.js — production patterns: parsing requests, building query strings
const { URL, URLSearchParams } = require('url');

// ─── 1. Parsing an incoming request's URL (Express/http req.url is PATH-ONLY) ──
function parseRequestUrl(reqUrl, host) {
  // req.url from http/Express has no protocol/host — must supply a base
  const fullUrl = new URL(reqUrl, `http://${host}`);
  return {
    pathname: fullUrl.pathname,
    query: Object.fromEntries(fullUrl.searchParams), // convert searchParams to a plain object
  };
}

// ─── 2. Building a query string from a plain object (e.g., for an outbound API call) ──
function buildQueryString(params) {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (Array.isArray(value)) {
      value.forEach((v) => searchParams.append(key, v)); // repeated keys for arrays
    } else if (value !== undefined && value !== null) {
      searchParams.set(key, value);
    }
  }
  return searchParams.toString(); // automatically URL-encodes everything correctly
}

// ─── 3. Validating and normalizing user-supplied URLs (e.g., webhook registration) ──
function validateWebhookUrl(urlString) {
  try {
    const parsed = new URL(urlString);
    if (parsed.protocol !== 'https:') {
      throw new Error('Webhook URL must use HTTPS');
    }
    return parsed.toString(); // normalized, canonical form
  } catch (err) {
    throw new Error(`Invalid webhook URL: ${err.message}`);
  }
}

// ─── Usage ───────────────────────────────────────────────────────────────────
const parsed = parseRequestUrl('/search?category=books&minPrice=100', 'api.flipkart.com');
console.log('Parsed request:', parsed);
// { pathname: '/search', query: { category: 'books', minPrice: '100' } }

const qs = buildQueryString({ category: 'electronics', tags: ['sale', 'new'], page: 2 });
console.log('Query string:', qs);
// "category=electronics&tags=sale&tags=new&page=2"

try {
  console.log(validateWebhookUrl('https://partner.example.com/webhook'));
} catch (err) {
  console.error(err.message);
}
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express app using URL/URLSearchParams for robust query handling
const express = require('express');
const { URL } = require('url');

const app = express();

// Note: Express ALREADY parses req.query for you via its own router —
// this example shows the UNDERLYING mechanism and manual usage for non-Express contexts
app.get('/search', (req, res) => {
  // req.query is Express's own convenience (built internally using similar URL parsing logic)
  const { category, minPrice, maxPrice } = req.query;
  res.json({ category, minPrice, maxPrice });
});

// Building outbound API call URLs with correct encoding
app.get('/proxy-search', async (req, res) => {
  const targetUrl = new URL('https://partner-api.example.com/products');
  targetUrl.searchParams.set('q', req.query.q || '');          // safely encodes special characters
  targetUrl.searchParams.set('limit', req.query.limit || '20');

  console.log('Calling:', targetUrl.toString());
  // Proceed to fetch targetUrl.toString() using https/fetch/axios...
  res.json({ calledUrl: targetUrl.toString() });
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the deprecated legacy `url.parse()` in new code
```javascript
// Wrong — legacy API, deprecated, has known inconsistencies with browser URL parsing
const url = require('url');
const parsed = url.parse('https://example.com/path?a=1'); // deprecated since Node 11
console.log(parsed.query); // "a=1" — a raw STRING, not parsed key-values!

// Right — use the modern WHATWG URL class
const { URL } = require('url');
const parsed2 = new URL('https://example.com/path?a=1');
console.log(parsed2.searchParams.get('a')); // "1" — properly parsed
```

❌ Mistake 2: Forgetting that `new URL()` requires a FULL or base-relative string, not a bare path
```javascript
// Wrong — throws TypeError: Invalid URL, because a bare path has no protocol/host
const parsed = new URL('/search?q=shoes'); // TypeError: Invalid URL

// Right — supply a base URL when parsing a path-only string (common for req.url)
const parsed2 = new URL('/search?q=shoes', 'https://example.com');
console.log(parsed2.pathname); // "/search"
```

---

## 🧠 Tricky Interview Question

```javascript
const { URL } = require('url');

const myUrl = new URL('https://example.com/search?tag=a&tag=b&tag=c');
console.log(myUrl.searchParams.get('tag'));       // ?
console.log(myUrl.searchParams.getAll('tag'));     // ?
console.log(Object.fromEntries(myUrl.searchParams)); // ?
```
Answer: `.get('tag')` returns **`"a"`** (only the FIRST matching value — `.get()` never returns multiple values, even if the key is repeated). `.getAll('tag')` returns **`["a", "b", "c"]`** (ALL values for that repeated key, as an array). `Object.fromEntries(myUrl.searchParams)` returns **`{ tag: "c" }`** — this is a subtle trap: `Object.fromEntries` iterates the entries and, since a plain object can only have ONE value per key, each subsequent `tag` entry OVERWRITES the previous one, leaving only the LAST value (`"c"`), silently losing `"a"` and `"b"`. This demonstrates why naively converting `URLSearchParams` with repeated keys to a plain object loses data — you must use `.getAll()` explicitly when a parameter can legitimately repeat (e.g., multi-select filters).

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between the legacy `url.parse()` and the modern WHATWG `URL` class?
A1: `url.parse()` (legacy, deprecated since Node 11) returns a plain object with a RAW, unparsed query string (`.query` is just a string like `"a=1&b=2"` unless you pass a second `true` argument to parse it, which then uses the older `querystring` module internally). The WHATWG `URL` class is the modern, spec-compliant, browser-matching standard — it provides `.searchParams` as a proper `URLSearchParams` object with built-in get/set/getAll methods, consistent encoding/decoding behavior, and is the recommended approach for all new code.

Q2: Why does `new URL('/path')` throw an error, and how do you fix it?
A2: The WHATWG `URL` constructor requires a string that's either a FULLY QUALIFIED URL (with protocol and host) or a relative string ACCOMPANIED by a `base` argument to resolve against. A bare path like `/path` has no way to determine protocol/host on its own, so `new URL('/path')` throws `TypeError: Invalid URL`. The fix: `new URL('/path', 'https://example.com')`, supplying an appropriate base — this is the standard pattern for parsing `req.url` from an incoming HTTP request, which only contains path+query, never protocol+host.

Q3: How do `URLSearchParams.get()` and `.getAll()` differ when a query parameter is repeated?
A3: `.get('key')` returns ONLY the first occurrence's value as a single string, silently ignoring any additional repeated values. `.getAll('key')` returns an ARRAY of ALL values for that key, in order. This matters for query strings like `?color=red&color=blue` (common in multi-select filter UIs) — using `.get()` here would silently lose the second value, while `.getAll()` correctly captures both.

Q4: How would you safely build a URL with user-supplied values that might contain special characters (spaces, `&`, `=`, non-ASCII)?
A4: Use `URLSearchParams.set()`/`.append()` rather than manually concatenating strings — `URLSearchParams` automatically handles percent-encoding for ALL special characters correctly (spaces become `%20` or `+`, `&`/`=` within values get escaped so they don't corrupt the query string structure, non-ASCII characters are UTF-8 percent-encoded). Manual string concatenation (`'?q=' + userInput`) risks producing malformed or exploitable URLs if `userInput` contains characters with special meaning in URL syntax.

Q5: Is `req.url` in an Express/http handler a full URL or just a path?
A5: Just the PATH and QUERY STRING portion (e.g., `/search?q=shoes`) — it never includes the protocol, hostname, or port, because that information is implicit from the connection the client already established to reach the server. To construct a full `URL` object from it (e.g., for logging the complete requested URL, or building an absolute link), you must supply a base derived from `req.headers.host`: `new URL(req.url, \`http://${req.headers.host}\`)`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Parsing or constructing any URL — incoming request URLs, outbound API call URLs, webhook URLs, redirect targets.
- Safely handling query parameters, especially with special characters or repeated keys.
- Validating user-supplied URLs (e.g., checking protocol, hostname) before using them.

❌ Avoid when:
- Using the legacy `url.parse()`/`url.format()`/`url.resolve()` functions in new code — always prefer the WHATWG `URL`/`URLSearchParams` classes.
- Manually string-concatenating query parameters instead of using `URLSearchParams`, which handles encoding correctly and avoids injection-style bugs.

---

## 📊 Visual Diagram
```
WHATWG URL STRUCTURE:
──────────────────────────────────────────────────────────

  https://user:pass@api.example.com:8080/products/search?category=books&page=2#results
  └─┬──┘ └───┬────┘ └──────┬───────┘└┬─┘└──────┬───────┘└───────┬──────────┘└──┬──┘
  protocol  auth       hostname    port     pathname         search (query)   hash

  myUrl.protocol  → "https:"
  myUrl.hostname  → "api.example.com"
  myUrl.port      → "8080"
  myUrl.pathname  → "/products/search"
  myUrl.search    → "?category=books&page=2"
  myUrl.searchParams → URLSearchParams { category: 'books', page: '2' }
  myUrl.hash      → "#results"

  req.url (Express/http) = pathname + search ONLY — no protocol/host/port!
  → must supply base: new URL(req.url, `http://${req.headers.host}`)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| URL class | WHATWG standard URL parser | WHATWG standard URL parser |
| URLSearchParams | Query string parsing/building helper | Query string parse/build करने वाला helper |
| pathname | Path portion of a URL | URL का path हिस्सा |
| search | Raw query string (with ?) | Raw query string (? के साथ) |
| searchParams.get/getAll | Read one/all values for a key | एक/सभी values पढ़ना |
| Legacy url.parse() | Deprecated older parsing API | Deprecated पुराना parsing API |

---

## ⚡ 3-Line Summary
English: The modern WHATWG `URL`/`URLSearchParams` classes (global in Node, also via `require('url')`) are the standard, spec-compliant way to parse and build URLs, replacing the deprecated legacy `url.parse()`/`url.format()` functions. `req.url` from HTTP/Express handlers is path+query only, requiring a `base` argument when constructing a full `URL` object from it. Always use `URLSearchParams` for query string handling to get correct encoding and proper support for repeated keys via `.getAll()`.
Hindi: Modern WHATWG `URL`/`URLSearchParams` classes (Node में global, `require('url')` से भी) URLs parse और build करने का standard, spec-compliant तरीका हैं, deprecated legacy `url.parse()`/`url.format()` functions की जगह लेते हैं। HTTP/Express handlers से `req.url` केवल path+query होता है, इससे पूरा `URL` object बनाने के लिए `base` argument चाहिए। Query string handling के लिए हमेशा `URLSearchParams` use करो correct encoding और `.getAll()` से repeated keys की proper support पाने के लिए।

---

## ➡️ Next Topic
**43. querystring Module (Legacy)** — the older query-string parsing utility and why `URLSearchParams` has largely replaced it.
