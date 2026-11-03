# 115. Design a URL Shortener Schema
# हिंदी में: URL Shortener का Schema Design

---

## 🔵 Simple Definition (English)
A **URL shortener** (bit.ly style) maps a short code like `abc123` to a long URL, redirects users instantly, counts clicks and optionally expires links. The interview problem tests whether you can pick the right **schema**, **unique index**, **code-generation strategy**, **atomic counters**, and a way to store **click analytics** without making the main collection huge.

## 🔵 सरल परिभाषा (Hindi)
**URL shortener** (bit.ly जैसा) एक छोटे code जैसे `abc123` को लंबे URL से map करता है, user को तुरंत redirect करता है, clicks गिनता है और चाहें तो links को expire करता है। यह interview problem जाँचती है कि आप सही **schema**, **unique index**, **code-generation strategy**, **atomic counters** और बिना main collection बड़ा किए **click analytics** रखने का तरीका चुन पाते हैं या नहीं।

---

## 🔴 Problem it Solves
Requirements: (1) `POST /shorten` returns a unique short code; (2) `GET /:code` must redirect in a few milliseconds (reads are 100x more than writes); (3) two users must never get the same code, even under concurrent writes; (4) count clicks and show per-day stats; (5) links may expire. A naive design (one big doc with an ever-growing `clicks: []` array) hits the 16 MB document limit, causes write contention on hot links, and a non-unique `code` field would redirect to the wrong site.

## 🔴 यह क्यों बना? (Hindi)
Requirements: (1) `POST /shorten` एक unique short code लौटाए; (2) `GET /:code` कुछ milliseconds में redirect करे (reads, writes से 100 गुना ज़्यादा); (3) concurrent writes में भी दो users को एक जैसा code न मिले; (4) clicks गिनो और per-day stats दिखाओ; (5) links expire हो सकें। Naive design (एक बड़ा doc जिसमें बढ़ता `clicks: []` array हो) 16 MB document limit तोड़ देता है, hot links पर write contention बनाता है, और non-unique `code` गलत site पर redirect करा देगा।

---

## 🟢 How it Works — Step by Step

Step 1 → **Collections**: `urls` (one doc per short link), `clicks` (one doc per click, append-only), `counters` (for sequence numbers).
Step 2 → **`urls` schema**: `{ code, long, userId, clicks, createdAt, expireAt }`. Keep `clicks` as a **number** (cheap `$inc`), not an array.
Step 3 → **Unique index** `{ code: 1 }` — the database, not app code, guarantees uniqueness. A duplicate insert fails with error **11000**.
Step 4 → **Generating the code** (two options): (a) *Random* 6-7 chars base62 — insert, and on `11000` just retry with a new random code (no coordination needed, but codes are guessable-resistant); (b) *Counter* — atomically `$inc` a `counters` doc, then base62-encode the number (short, sequential, predictable).
Step 5 → **Redirect**: `findOneAndUpdate({ code }, { $inc: { clicks: 1 } })` fetches the long URL and counts in ONE atomic round trip using the unique index.
Step 6 → **Analytics**: insert `{ code, ts, country }` into `clicks` (or use a time-series collection) and aggregate with `$group` by day. Index `{ code: 1, ts: 1 }`.
Step 7 → **Expiry**: TTL index on `expireAt` with `expireAfterSeconds: 0`; also check `expireAt > now` in the redirect query because the TTL monitor lags up to ~60 s.
Step 8 → **Scale**: cache hot codes in Redis, shard by hashed `code` (`{ code: "hashed" }`) to spread load evenly.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Collections**: `urls` (हर short link का एक doc), `clicks` (हर click का एक doc, सिर्फ append), `counters` (sequence numbers के लिए)।
Step 2 → **`urls` schema**: `{ code, long, userId, clicks, createdAt, expireAt }`। `clicks` को array नहीं **number** रखो (सस्ता `$inc`)।
Step 3 → **Unique index** `{ code: 1 }` — uniqueness की guarantee database देता है, app code नहीं। Duplicate insert **11000** error से fail होता है।
Step 4 → **Code generate करना** (दो तरीके): (a) *Random* 6-7 chars base62 — insert करो, `11000` आए तो नया random code लेकर retry (coordination नहीं चाहिए, codes का अंदाज़ा लगाना मुश्किल); (b) *Counter* — `counters` doc पर atomically `$inc`, फिर number को base62 में encode (छोटा, sequential, predictable)।
Step 5 → **Redirect**: `findOneAndUpdate({ code }, { $inc: { clicks: 1 } })` एक ही atomic round trip में long URL भी लाता है और count भी बढ़ाता है, unique index से।
Step 6 → **Analytics**: `clicks` में `{ code, ts, country }` insert करो (या time-series collection) और `$group` से दिन के हिसाब से aggregate करो। Index `{ code: 1, ts: 1 }`।
Step 7 → **Expiry**: `expireAt` पर TTL index (`expireAfterSeconds: 0`); redirect query में `expireAt > now` भी check करो क्योंकि TTL monitor ~60 s पीछे रह सकता है।
Step 8 → **Scale**: hot codes Redis में cache करो, load बराबर बाँटने के लिए hashed `code` (`{ code: "hashed" }`) पर shard करो।

---

## 🟡 Real World Example
**Razorpay payment links** and **Flipkart's share-this-product links** use short codes like `rzp.io/i/AbC12x`. A link sent over SMS is clicked by thousands of users within minutes (a hot key). Using a `clicks` counter with `$inc` keeps the `urls` document tiny, while each click also lands in an append-only `clicks` collection. Marketing then runs "clicks per day per country" on that collection. Payment links expire after 7 days via `expireAt`, so stale links disappear automatically.

## 🟡 Real Example Hindi mein
**Razorpay payment links** और **Flipkart के share-this-product links** `rzp.io/i/AbC12x` जैसे short codes इस्तेमाल करते हैं। SMS से भेजा गया link कुछ ही मिनटों में हज़ारों users क्लिक करते हैं (hot key)। `$inc` वाला `clicks` counter `urls` document को छोटा रखता है, जबकि हर click append-only `clicks` collection में भी जाता है। Marketing उसी collection पर "प्रति दिन प्रति देश clicks" चलाता है। Payment links 7 दिन बाद `expireAt` से अपने-आप गायब हो जाते हैं।

---

## 💻 Code Example — Basic

```javascript
// mongosh — tested on MongoDB 8.0.4
use("shortener");

// 1) Indexes: unique code (the guarantee), TTL for expiry
db.urls.createIndex({ code: 1 }, { unique: true });
db.urls.createIndex({ expireAt: 1 }, { expireAfterSeconds: 0 }); // delete at expireAt

// 2) Create a short link (expires in 30 days)
db.urls.insertOne({
  code: "abc123",                              // short code (base62)
  long: "https://flipkart.com/p/1",            // destination
  userId: 7,                                   // owner
  clicks: 0,                                   // numeric counter, NOT an array
  createdAt: new Date(),
  expireAt: new Date(Date.now() + 86400000 * 30) // 30 days
});

// 3) The unique index rejects a duplicate code
try { db.urls.insertOne({ code: "abc123", long: "x" }); }
catch (e) { print(e.code); }                   // Output: 11000 (DuplicateKey)

// 4) Redirect: fetch long URL AND count the click atomically
db.urls.findOneAndUpdate(
  { code: "abc123", expireAt: { $gt: new Date() } }, // ignore expired-but-not-yet-deleted
  { $inc: { clicks: 1 } },                           // atomic increment
  { returnDocument: "after", projection: { _id: 0, code: 1, long: 1, clicks: 1 } }
);
// Output: { code: 'abc123', long: 'https://flipkart.com/p/1', clicks: 1 }
```

## 💻 Code Example — Advanced

```javascript
// mongosh — counter-based codes + click analytics, tested on MongoDB 8.0.4
use("shortener");

// A) Counter strategy: atomic sequence (safe under concurrency)
db.counters.insertOne({ _id: "url", seq: 1000 });
const n = db.counters.findOneAndUpdate(
  { _id: "url" }, { $inc: { seq: 1 } }, { returnDocument: "after" }
).seq;                                          // Output: 1001 (each caller gets a different n)

// base62 encode the number into a short string (pure JS helper)
const A = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
function b62(x) { let s = ""; do { s = A[x % 62] + s; x = Math.floor(x / 62); } while (x > 0); return s; }
b62(1001);                                      // Output: 'g9'

// B) Random strategy with retry on duplicate key
function createLink(long) {
  for (let i = 0; i < 5; i++) {                 // bounded retries
    let code = ""; for (let k = 0; k < 7; k++) code += A[Math.floor(Math.random() * 62)];
    try { db.urls.insertOne({ code, long, clicks: 0, createdAt: new Date() }); return code; }
    catch (e) { if (e.code !== 11000) throw e; } // only retry for duplicate key
  }
  throw new Error("could not allocate code");
}

// C) Click events + per-day report
db.clicks.createIndex({ code: 1, ts: 1 });      // supports filter by code + time range
db.clicks.insertMany([
  { code: "abc123", ts: new Date("2026-01-01T10:00:00Z"), country: "IN" },
  { code: "abc123", ts: new Date("2026-01-01T11:00:00Z"), country: "IN" },
  { code: "abc123", ts: new Date("2026-01-02T11:00:00Z"), country: "US" }
]);
db.clicks.aggregate([
  { $match: { code: "abc123" } },                                           // uses the index
  { $group: { _id: { $dateToString: { format: "%Y-%m-%d", date: "$ts" } }, n: { $sum: 1 } } },
  { $sort: { _id: 1 } }
]);
// Output: [ { _id: '2026-01-01', n: 2 }, { _id: '2026-01-02', n: 1 } ]
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

const Url = mongoose.model('Url', new mongoose.Schema({
  code:     { type: String, required: true, unique: true }, // creates the unique index
  long:     { type: String, required: true },
  clicks:   { type: Number, default: 0 },
  expireAt: { type: Date, index: { expireAfterSeconds: 0 } },
}, { timestamps: true }));

const ALPHA = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
const rand = (n) => Array.from({ length: n }, () => ALPHA[Math.floor(Math.random() * 62)]).join('');

app.post('/shorten', async (req, res) => {
  // validate the URL so we never store javascript: or garbage links
  let u; try { u = new URL(req.body.url); } catch { return res.status(400).json({ error: 'bad url' }); }
  if (!['http:', 'https:'].includes(u.protocol)) return res.status(400).json({ error: 'bad protocol' });

  for (let i = 0; i < 5; i++) {
    try {
      const doc = await Url.create({ code: rand(7), long: u.href, expireAt: new Date(Date.now() + 30 * 864e5) });
      return res.status(201).json({ short: `https://sho.rt/${doc.code}` });
    } catch (e) { if (e.code !== 11000) throw e; } // duplicate code -> retry
  }
  res.status(503).json({ error: 'try again' });
});

app.get('/:code', async (req, res) => {
  const doc = await Url.findOneAndUpdate(
    { code: req.params.code, $or: [{ expireAt: null }, { expireAt: { $gt: new Date() } }] },
    { $inc: { clicks: 1 } }
  ).lean();
  if (!doc) return res.status(404).send('not found');
  res.redirect(302, doc.long); // 302 keeps analytics working (301 gets cached by browsers)
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Check-then-insert for uniqueness
```javascript
// Wrong — race condition: two requests both see "not found" and both insert
if (!(await Url.findOne({ code }))) await Url.create({ code, long });

// Right — let the unique index decide, catch error 11000 and retry
try { await Url.create({ code, long }); } catch (e) { if (e.code === 11000) /* retry */; }
```

❌ Mistake 2: Storing clicks as an array inside the URL document
✅ Correct: Use a numeric `clicks` with `$inc` and a separate `clicks` events collection. Unbounded arrays hit the 16 MB limit and make every click rewrite a bigger document.

❌ Mistake 3: Forgetting the index on `code` (full collection scan on every redirect) or using 301 redirects (browser caches them and your click counting stops).

---

## 🧠 Tricky Interview Question

```javascript
// Two servers run this at the same instant for the same new code "xyz":
if (!db.urls.findOne({ code: "xyz" })) db.urls.insertOne({ code: "xyz", long: A_or_B });
```
Answer: Without a unique index **both inserts can succeed**, giving two documents for `xyz`, so `findOne` later returns an arbitrary one — a user may be redirected to somebody else's site. With `createIndex({ code: 1 }, { unique: true })` the second insert fails with **E11000**, and you retry with a new code. Lesson: uniqueness must be enforced by the database, never by a read-before-write in the app.

---

## ⚫ Interview Questions + Answers

Q1: Random codes or a counter — which is better?
A1: Random base62 (7 chars = 62^7 ≈ 3.5 trillion) needs no shared state and is hard to enumerate, but needs a duplicate-retry loop. A counter gives short sequential codes with no collisions, but the `counters` doc is a hot spot, codes are guessable (privacy concern), and sharding needs ranges per server. Many systems pre-allocate counter ranges per app server.

Q2: How do you make redirects fast?
A2: Unique index on `code` (index lookup + one document), `findOneAndUpdate` to combine read and count, a Redis/in-memory cache for hot codes, and an update of the counter that can be batched or made async if it contends.

Q3: How do you store analytics without bloating `urls`?
A3: Append-only `clicks` events (or a time-series collection) keyed by `code` and `ts`, aggregated per day with `$group`; keep only a cheap `clicks` total on the URL doc. Use TTL on events if only recent data is needed.

Q4: How do you shard this?
A4: Shard `urls` on a hashed `code` (`{ code: "hashed" }`) so reads for a code go to a single shard and writes spread evenly. Note: a unique index must include the shard key, which `{code: 1}` unique does when sharding on code.

Q5: How do you expire links?
A5: Absolute-TTL: `expireAt` with `expireAfterSeconds: 0`. The TTL monitor runs about every 60 s, so also add `expireAt > now` to the redirect query for correctness.

---

## 🔷 When to Use + When Not to Use
✅ Use this design when:
- Reads massively outnumber writes and a lookup by a single key (code) dominates
- You need atomic counters and append-only analytics without joins

❌ Avoid when:
- You need analytics on billions of clicks with complex slicing — export to a warehouse (ClickHouse/BigQuery) or use a time-series collection
- You need codes that are sequential, and ranges across servers are hard (use pre-allocated ranges or ULIDs)

---

## 📊 Visual Diagram
```
URL SHORTENER
──────────────────────────────────────────────────────
 POST /shorten ──► generate code ──► urls.insertOne
                         │              (unique {code:1})
                         └─ E11000? ──► retry new code

 GET /abc123 ──► (cache?) ──► urls.findOneAndUpdate
                                {code, expireAt>now}
                                $inc clicks   ──► 302 Location: long
                                    │
                                    └──► clicks.insertOne {code, ts, country}

 urls                       clicks (append-only)
 ┌─────────────────┐        ┌───────────────────────┐
 │ code (unique)   │        │ code, ts   idx{code,ts}│
 │ long, clicks    │        │ country                │
 │ expireAt (TTL)  │        └───────────────────────┘
 └─────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Short code | Compact key for a long URL | Long URL की छोटी key |
| Unique index | DB-enforced uniqueness | DB द्वारा लागू uniqueness |
| E11000 | Duplicate key error | Duplicate key error |
| base62 | 0-9, a-z, A-Z encoding | 62 characters वाली encoding |
| $inc | Atomic numeric increment | Atomic number बढ़ाना |
| findOneAndUpdate | Atomic read+update | Atomic पढ़ना + update |
| Hashed shard key | Spreads data evenly | Data बराबर बाँटने वाली shard key |

---

## ⚡ 3-Line Summary
English:
1. Store one small `urls` doc per link with a unique `code`, a numeric `clicks`, and an `expireAt` TTL.
2. Generate codes randomly (retry on E11000) or from an atomic counter; never check-then-insert.
3. Redirect with `findOneAndUpdate` + `$inc`, and put click events in a separate append-only collection.

Hindi:
1. हर link के लिए एक छोटा `urls` doc रखो: unique `code`, numeric `clicks`, और `expireAt` TTL।
2. Codes random (E11000 पर retry) या atomic counter से बनाओ; कभी check-then-insert मत करो।
3. Redirect `findOneAndUpdate` + `$inc` से करो और click events अलग append-only collection में रखो।

---

## ➡️ Next Topic
**116. Design a Chat App Schema** — messages, rooms, pagination by timestamp and read receipts.
