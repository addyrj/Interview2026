# 161. URL + URLSearchParams
# हिंदी में: URL + URLSearchParams — Web Address को Safely Parse और Build करना

---

## 🔵 Simple Definition (English)
`URL` is a built-in class that parses a web address into parts (protocol, host, pathname, search, hash), and `URLSearchParams` reads and writes the query string (`?key=value&...`). Both are available in browsers and in Node.js as globals, with no `require` needed.

## 🔵 सरल परिभाषा (Hindi)
`URL` एक built-in class है जो web address को हिस्सों (protocol, host, pathname, search, hash) में बाँटती है, और `URLSearchParams` query string (`?key=value&...`) को पढ़ती और लिखती है। ये दोनों browser और Node.js में global रूप से मिलते हैं, `require` की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
Before these classes, developers built URLs with string concatenation: `"/search?q=" + query + "&page=" + page`. This breaks when the query has spaces, `&`, `#` or Hindi text, and it creates injection bugs. Parsing with regular expressions was also fragile. Swiggy search, Flipkart filters and payment callback URLs all need correct encoding, so one wrong `&` can break the whole page.

## 🔴 यह क्यों बना? (Hindi)
इन classes से पहले developers string जोड़कर URL बनाते थे: `"/search?q=" + query + "&page=" + page`। यह तब टूटता था जब query में spaces, `&`, `#` या हिंदी text होता था, और injection bugs भी बनते थे। Regular expression से parsing भी नाज़ुक होती थी। Swiggy search, Flipkart filters और payment callback URLs को सही encoding चाहिए, एक गलत `&` पूरा page तोड़ सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `new URL(input, base)` parses the string. `base` is used when `input` is relative (like `/menu`)
Step 2 → Read parts: `url.protocol`, `url.host`, `url.pathname`, `url.search`, `url.hash`
Step 3 → `url.searchParams` is a live `URLSearchParams` object tied to the URL
Step 4 → `get(key)` returns the first value (or `null`); `getAll(key)` returns all values as an array
Step 5 → `set(key, value)` replaces, `append(key, value)` adds, `delete(key)` removes
Step 6 → Converting back with `url.href` or `url.toString()` gives the encoded address; values are percent-encoded automatically

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → `new URL(input, base)` string को parse करता है। अगर `input` relative है (जैसे `/menu`), तो `base` इस्तेमाल होता है
Step 2 → हिस्से पढ़ें: `url.protocol`, `url.host`, `url.pathname`, `url.search`, `url.hash`
Step 3 → `url.searchParams` एक live `URLSearchParams` object है, जो URL से जुड़ा रहता है
Step 4 → `get(key)` पहली value देता है (या `null`); `getAll(key)` सारी values array में देता है
Step 5 → `set(key, value)` बदलता है, `append(key, value)` जोड़ता है, `delete(key)` हटाता है
Step 6 → `url.href` या `url.toString()` से वापस encoded address मिलता है; values अपने आप percent-encode होती हैं

---

## 🟡 Real World Example
Swiggy restaurant search: the user types "biryani & kebab" in the search box. The app builds a URL such as `/search?query=biryani+%26+kebab&veg=false` using `URLSearchParams`, so the `&` inside the search term is encoded and does not split the query. Razorpay's payment callback reads `razorpay_payment_id` and `razorpay_signature` from the redirect URL with `searchParams.get`.

## 🟡 Real Example Hindi mein
Swiggy restaurant search: user search box में "biryani & kebab" लिखता है। App `URLSearchParams` से `/search?query=biryani+%26+kebab&veg=false` जैसा URL बनाता है, इसलिए search term के अंदर का `&` encode होता है और query को नहीं तोड़ता। Razorpay का payment callback redirect URL से `razorpay_payment_id` और `razorpay_signature` को `searchParams.get` से पढ़ता है।

---

## 💻 Code Example — Basic
> This runs in Node.js with no installs (`URL` and `URLSearchParams` are globals). Save as `url-basic.js` and run `node url-basic.js`. The same code also runs in every modern browser console.

```javascript
// url-basic.js — parse, read and build URLs (run: node url-basic.js)

// Build a full URL from a string
const url = new URL("https://www.swiggy.com/search?query=pizza&veg=true#results");
// Parse the whole address into parts

console.log(url.protocol);
// "https:" — the scheme including the colon
console.log(url.host);
// "www.swiggy.com" — hostname plus port if any
console.log(url.pathname);
// "/search" — path without query or hash
console.log(url.search);
// "?query=pizza&veg=true" — query string including "?"
console.log(url.hash);
// "#results" — fragment including "#"

// Read query values with searchParams
const q = url.searchParams.get("query");
// Get the value of "query"
console.log(q);
// "pizza"
console.log(url.searchParams.get("missing"));
// null — key does not exist

// Change a value
url.searchParams.set("veg", "false");
// Replace the value of "veg"
url.searchParams.append("city", "Delhi");
// Add a new key-value pair (duplicates allowed)
console.log(url.search);
// "?query=pizza&veg=false&city=Delhi"

// Special characters are encoded automatically
url.searchParams.set("query", "biryani & kebab");
// Contains spaces and an ampersand
console.log(url.search);
// "?query=biryani+%26+kebab&veg=false&city=Delhi" — space becomes "+", & becomes %26

// Build a relative URL against a base
const menu = new URL("/menu/123", "https://www.zomato.com");
// Absolute path relative to the base origin
console.log(menu.href);
// "https://www.zomato.com/menu/123"

// Iterate over all parameters
for (const [key, value] of url.searchParams) {
  // URLSearchParams is iterable as [key, value] pairs
  console.log(`${key} = ${value}`);
  // Print each pair
}
```

## 💻 Code Example — Advanced
> Production-style helpers: a safe `buildUrl` that skips empty filters, a strict `parseFilters` that validates types with defaults, and a `mergeQuery` that keeps unrelated parameters. Runs in Node: `node url-advanced.js`.

```javascript
// url-advanced.js — safe URL building and parsing (run: node url-advanced.js)

// Build a URL from a base path and an object of filters
function buildUrl(base, path, filters = {}) {
  // base is origin, path is the route, filters are optional query values
  const url = new URL(path, base);
  // Resolve path against the base origin
  for (const [key, value] of Object.entries(filters)) {
    // Loop through each filter the caller provided
    if (value === undefined || value === null || value === "") continue;
    // Skip empty filters so the URL stays clean
    if (Array.isArray(value)) {
      // Arrays become repeated keys: cuisine=indian&cuisine=chinese
      for (const v of value) url.searchParams.append(key, String(v));
      // Append each array item under the same key
    } else {
      url.searchParams.set(key, String(value));
      // Scalar values replace any existing value for that key
    }
  }
  return url;
  // Return the URL object (call .href when you need a string)
}

// Parse query values into typed, validated filters with defaults
function parseFilters(search) {
  // search can be a string like "?page=2" or a URLSearchParams object
  const params = new URLSearchParams(search);
  // Normalize input into a URLSearchParams object
  const page = Number.parseInt(params.get("page") ?? "1", 10);
  // Read page as a number, default to 1 when missing
  const limit = Math.min(Math.max(Number.parseInt(params.get("limit") ?? "20", 10), 1), 100);
  // Clamp limit between 1 and 100 to protect the server
  return {
    page: Number.isInteger(page) && page > 0 ? page : 1,
    // Fall back to page 1 if the value is not a positive integer
    limit,
    // Safe, clamped limit
    cuisines: params.getAll("cuisine"),
    // All repeated cuisine values as an array
    sort: ["price", "rating"].includes(params.get("sort")) ? params.get("sort") : "rating",
    // Whitelist sort values to block arbitrary input
  };
}

// Keep unrelated parameters while changing one value
function mergeQuery(currentHref, changes) {
  // currentHref is a full URL string; changes is an object of new values
  const url = new URL(currentHref);
  // Start from the current URL so host and path stay the same
  for (const [key, value] of Object.entries(changes)) {
    // Apply each change
    if (value === null) url.searchParams.delete(key);
    // null means remove this parameter
    else url.searchParams.set(key, String(value));
    // Otherwise set or replace it
  }
  return url.href;
  // Return the updated address as a string
}

// ---- demo ----
const link = buildUrl("https://www.swiggy.com", "/search", {
  query: "biryani & kebab",
  // Search term with special characters
  cuisine: ["indian", "mughlai"],
  // Two cuisines become two cuisine= pairs
  veg: "",
  // Empty value is skipped
});
console.log(link.href);
// https://www.swiggy.com/search?query=biryani+%26+kebab&cuisine=indian&cuisine=mughlai

console.log(parseFilters("?page=3&limit=500&cuisine=indian&cuisine=chinese&sort=price"));
// { page: 3, limit: 100, cuisines: ['indian','chinese'], sort: 'price' }  (limit clamped)

console.log(parseFilters("?page=-4&sort=hacked").page, parseFilters("?sort=hacked").sort);
// 1 rating  (bad page falls back, unknown sort falls back)

console.log(mergeQuery(link.href, { page: 2, veg: null }));
// Keeps query and cuisine, adds page=2, removes veg
```

---

## 🟠 Express.js Integration
Express gives you `req.query` already parsed (using the same query parser idea), but using `new URL` lets you build absolute links, such as pagination "next" links, and reuse the same URL logic on the client and server.

```javascript
// server.js — npm i express, then node server.js
const express = require("express");
// Import Express
const app = express();
// Create the app

const BASE = "http://localhost:3000";
// Public base used when building absolute links

app.get("/api/restaurants", (req, res) => {
  // Route handles search and pagination
  const current = new URL(req.originalUrl, BASE);
  // Rebuild the full URL of this request (originalUrl keeps the query string)
  const page = Number.parseInt(current.searchParams.get("page") ?? "1", 10);
  // Read the page number, default 1
  const safePage = Number.isInteger(page) && page > 0 ? page : 1;
  // Validate the value

  const next = new URL(current);
  // Copy the current URL so other filters stay
  next.searchParams.set("page", String(safePage + 1));
  // Point to the next page

  res.json({
    page: safePage,
    // Current page number
    items: [{ name: "Paneer Tikka" }],
    // Sample data
    next: next.href,
    // Absolute link to the next page, safe for clients to follow
  });
});

app.listen(3000, () => console.log("Try http://localhost:3000/api/restaurants?page=2&veg=true"));
// Start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building query strings with concatenation, so special characters break the URL.
✅ Correct: Use `searchParams.set` or `append`, which encode values automatically.

```javascript
// Wrong — "&" in the search term splits it into two parameters
const q = "biryani & kebab";
const bad = `https://x.com/search?query=${q}&veg=true`;
// The server sees query="biryani " and an extra parameter " kebab"

// Right — encoding is automatic
const good = new URL("https://x.com/search");
good.searchParams.set("query", q);
good.searchParams.set("veg", "true");
console.log(good.href); // ...?query=biryani+%26+kebab&veg=true
```

❌ Mistake 2: Using `new URL(path)` without a base when the path is relative, which throws.
✅ Correct: Give a base as the second argument, or use an absolute URL.

```javascript
// Wrong — throws TypeError: Invalid URL
const u1 = new URL("/menu");

// Right — provide the base
const u2 = new URL("/menu", "https://www.zomato.com");
console.log(u2.href); // "https://www.zomato.com/menu"
```

❌ Mistake 3: Assuming `get` returns a number or handling a missing value as an empty string.
✅ Correct: `get` returns a string or `null`. Convert and validate it.

```javascript
// Wrong — null + 1 is 1, and "2" + 1 is "21"
const p = new URL("https://x.com?page=2").searchParams.get("page");
console.log(p + 1); // "21" — string concatenation, a common bug

// Right — parse and default
const page = Number(new URL("https://x.com?page=2").searchParams.get("page") ?? 1);
console.log(page + 1); // 3
```

---

## 🧠 Tricky Interview Question
What is printed? This runs in Node.js (`node tricky-url.js`).

```javascript
// Tricky URL code
const base = "https://shop.example/items/";
// Note the trailing slash in the base path

console.log(new URL("tea", base).href);
// A: relative path with no leading slash
console.log(new URL("/tea", base).href);
// B: path with a leading slash

const p = new URLSearchParams("q=a+b&x=%E2%82%B9");
// Query with "+" and a percent-encoded rupee sign
console.log(p.get("q"), p.get("x"), p.has("y"));
// C: three values
```

Answer: Line A prints `https://shop.example/items/tea`. Without a leading slash, the path is resolved relative to the base directory, which is `/items/`. Line B prints `https://shop.example/tea`, because a leading slash means "from the origin root", which discards `/items/`. Line C prints `a b ₹ false`. In query strings, `+` decodes to a space, `%E2%82%B9` decodes to the rupee sign `₹`, and `has("y")` is `false` because the key does not exist. This is the reason to always use `URL` for resolving links instead of string joins.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `url.search` and `url.searchParams`?
A1: `url.search` is the raw string (`?a=1`). `url.searchParams` is a live object that parses and encodes the values for you.

Q2: What does `getAll` do?
A2: It returns every value for a repeated key as an array, for example `cuisine=indian&cuisine=chinese`.

Q3: Are `URL` and `URLSearchParams` available in Node.js?
A3: Yes. Since Node 10 they are globals, so you do not need `require("url")`.

Q4: Why does `new URL("/menu")` throw?
A4: Because a relative string has no scheme or host. You must pass a base URL as the second argument.

Q5: Does `URLSearchParams` encode a space as `%20`?
A5: In query strings, spaces are encoded as `+` by `URLSearchParams`. `%20` also works in query strings, but `+` is the form-encoding convention. Path segments use `%20`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You build or read any URL with query parameters
- You resolve links relative to a base (pagination, redirects)
- You validate and extract query values on server or client

❌ Avoid when:
- You need to parse a path with only a simple static string (a regex is fine)
- You build a URL for a value you already know is safe and static (a template literal is fine)
- You need to parse a non-URL string such as an email, where `URL` throws

---

## 📊 Visual Diagram
```
https://www.swiggy.com:443/search?query=biryani+%26+kebab&veg=false#results
\___/   \______________/ \__/ \____/ \_____________________________/ \______/
protocol      host      port  path              search (query)        hash

url.searchParams  ->  get("query") = "biryani & kebab"   (decoded)
                  ->  getAll("veg") = ["false"]

new URL("/menu", "https://www.zomato.com").href
                  -> "https://www.zomato.com/menu"   (base origin used)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| URL | Class that parses and builds addresses | Address को parse और बनाने वाली class |
| base | Address used to resolve relative URLs | Relative URL को पूरा करने वाला आधार |
| searchParams | Live query-string object of a URL | URL का live query-string object |
| URLSearchParams | Read and write query pairs | Query pairs पढ़ने और लिखने वाली class |
| Percent-encoding | Converts special chars to %XX | Special characters को %XX में बदलना |
| getAll | Returns all values for a repeated key | एक ही key की सारी values देता है |
| Origin | Scheme + host + port | Scheme + host + port का combo |

---

## ⚡ 3-Line Summary
English: `URL` parses addresses into parts, and `URLSearchParams` reads and writes query strings safely.
English: Values are encoded automatically, so never build query strings by concatenation.
English: Always pass a base for relative paths, and validate values with `get` plus defaults.
Hindi: `URL` address को हिस्सों में बाँटता है, और `URLSearchParams` query string को सुरक्षित रूप से पढ़ता व लिखता है।
Hindi: Values अपने आप encode होती हैं, इसलिए query string को concatenation से न बनाएँ।
Hindi: Relative path के लिए हमेशा base दें, और `get` के साथ default और validation रखें।

---

## ➡️ Next Topic
162. Fetch vs Axios: once you can build a correct URL, the next step is sending the request. `fetch` is the built-in API for HTTP calls in browsers and Node 18+, and Axios is the popular library alternative. Interviews often ask when to pick each one.
