# 15. Query Filters — equality and projection
# हिंदी में: Query Filters — equality और projection

---

## 🔵 Simple Definition (English)
A **query filter** is a document describing which documents to match. `{ city: "Pune" }` means equality (`city == "Pune"`); several fields are combined with implicit AND. **Dot notation** reaches into embedded documents (`"address.state"`), and a plain value against an array field matches if **any element** equals it. A **projection** (2nd argument of `find`) chooses which fields to return: `1` includes, `0` excludes.

## 🔵 सरल परिभाषा (Hindi)
**Query filter** एक document है जो बताता है कौन से documents match करने हैं। `{ city: "Pune" }` का मतलब equality है; कई fields implicit AND से जुड़ते हैं। **Dot notation** embedded documents के अंदर जाता है (`"address.state"`), और array field पर साधारण value तब match होती है जब **कोई भी element** बराबर हो। **Projection** (`find` का दूसरा argument) तय करता है कौन से fields लौटें: `1` शामिल, `0` बाहर।

---

## 🔴 Problem it Solves
Without filters you would fetch whole collections and filter in application code, wasting network and CPU. Without projection you would send big fields (a 50 KB description, an image URL list, password hashes) when the screen needs only the name. Filters push work to the database where indexes make it fast; projections cut payload size and can even let an index answer the query alone (a "covered query").

## 🔴 यह क्यों बना? (Hindi)
Filters के बिना पूरी collection लाकर application code में filter करना पड़ता, network और CPU बर्बाद होते। Projection के बिना बड़े fields (50 KB description, image URLs की list, password hash) भेजने पड़ते जबकि screen को सिर्फ़ name चाहिए। Filters काम database को देते हैं जहाँ indexes उसे तेज़ बनाते हैं; projection payload घटाता है और index अकेले query का जवाब दे सकता है ("covered query")।

---

## 🟢 How it Works — Step by Step

Step 1 → Each key in the filter is a field path; the value is what it must equal. `{ a: 1, b: 2 }` = `a == 1 AND b == 2`.
Step 2 → Dot notation `"address.state": "DL"` walks into the embedded document.
Step 3 → If the field is an array, `{ skills: "mongo" }` matches arrays containing `"mongo"`; `{ skills: ["java"] }` matches only an array that is EXACTLY `["java"]` in that order.
Step 4 → An embedded document used as a value (`{ address: { pin: "110001" } }`) must match the WHOLE subdocument exactly, including field order.
Step 5 → `{ field: null }` matches documents where the field is null OR missing.
Step 6 → Projection is applied after matching: `{name:1}` returns `_id` + name (`_id` is included unless you say `_id: 0`). You cannot mix include and exclude (except `_id`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Filter की हर key एक field path है; value वो है जिसके बराबर होना चाहिए। `{ a: 1, b: 2 }` = `a == 1 AND b == 2`।
Step 2 → Dot notation `"address.state": "DL"` embedded document के अंदर जाता है।
Step 3 → Field array हो तो `{ skills: "mongo" }` उन arrays से match होता है जिनमें `"mongo"` है; `{ skills: ["java"] }` सिर्फ़ उस array से जो ठीक `["java"]` हो।
Step 4 → Embedded document को value देने पर (`{ address: { pin: "110001" } }`) पूरा subdocument ठीक वैसा ही होना चाहिए, field order समेत।
Step 5 → `{ field: null }` उन documents से match करता है जहाँ field null है या मौजूद ही नहीं।
Step 6 → Projection match के बाद लगता है: `{name:1}` `_id` + name देता है (`_id` तब तक आता है जब तक `_id: 0` न लिखो)। Include और exclude मिला नहीं सकते (`_id` को छोड़कर)।

---

## 🟡 Real World Example
**Razorpay's merchant dashboard** lists payments. The filter is `{ merchantId: "m_42", "card.network": "VISA", status: "captured" }` using dot notation into the embedded `card` object. The list screen needs only `{ amount: 1, status: 1, createdAt: 1 }`, so the API projects just those fields rather than shipping the full payment document with card metadata and gateway logs. Smaller payload, faster dashboard.

## 🟡 Real Example Hindi mein
**Razorpay के merchant dashboard** में payments की list दिखती है। Filter है `{ merchantId: "m_42", "card.network": "VISA", status: "captured" }`, जो embedded `card` object में dot notation से जाता है। List screen को सिर्फ़ `{ amount: 1, status: 1, createdAt: 1 }` चाहिए, इसलिए API सिर्फ़ वही fields project करती है, पूरा payment document (card metadata, gateway logs) नहीं भेजती। Payload छोटा, dashboard तेज़।

---

## 💻 Code Example — Basic

Verified on MongoDB 8.0.4. Collection `users`: Asha (Pune, 28, address MH, skills js/mongo), Ravi (Delhi, 34, address DL, skills java), Meera (Pune, 22, no address, skills mongo/python).

```javascript
use("shop");

// Equality on one field + projection (name only; _id comes by default)
db.users.find({ city: "Pune" }, { name: 1 });
// Output: [ { _id: 1, name: 'Asha' }, { _id: 3, name: 'Meera' } ]

// Several fields = implicit AND; $gt is a comparison operator
db.users.find({ city: "Pune", age: { $gt: 25 } }, { name: 1 });
// Output: [ { _id: 1, name: 'Asha' } ]

// Dot notation into an embedded document (quotes are required)
db.users.find({ "address.state": "DL" }, { name: 1 });
// Output: [ { _id: 2, name: 'Ravi' } ]

// Array field: matches if ANY element equals "mongo"
db.users.find({ skills: "mongo" }, { name: 1, _id: 0 });
// Output: [ { name: 'Asha' }, { name: 'Meera' } ]
```

## 💻 Code Example — Advanced

```javascript
// Exact array match: order and contents must be identical
db.users.find({ skills: ["java"] }, { name: 1, _id: 0 });
// Output: [ { name: 'Ravi' } ]    ("skills: ['mongo']" would NOT match Asha)

// Whole-subdocument match: address must be EXACTLY { pin: "110001" }
db.users.find({ address: { pin: "110001" } }).toArray().length;
// Output: 0   (Ravi's address also has state: "DL", so exact match fails!)
// Right way: db.users.find({ "address.pin": "110001" })  -> matches Ravi

// null matches null OR missing field
db.users.find({ address: null }, { name: 1, _id: 0 });
// Output: [ { name: 'Meera' } ]   (Meera has no address field)

// Projection variants
db.users.find({ _id: 1 }, { name: 1, city: 1 });
// Output: [ { _id: 1, name: 'Asha', city: 'Pune' } ]
db.users.find({ _id: 1 }, { skills: 0, address: 0 });          // exclusion form
// Output: [ { _id: 1, name: 'Asha', city: 'Pune', age: 28 } ]
db.users.find({ _id: 1 }, { "address.pin": 1, _id: 0 });       // nested projection
// Output: [ { address: { pin: '411001' } } ]

// Mixing include and exclude is an ERROR
try { db.users.find({}, { name: 1, city: 0 }).toArray(); }
catch (e) { print(e.message); }
// Output: Cannot do exclusion on field city in inclusion projection
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// GET /users?city=Pune&skill=mongo
app.get("/users", async (req, res) => {
  const filter = {};                                  // build the filter only from known params
  if (req.query.city)  filter.city = String(req.query.city);   // String() blocks {$ne:..} injection
  if (req.query.skill) filter.skills = String(req.query.skill);

  const users = await User.find(filter)
    .select("name city -_id")        // Mongoose projection string: include name, city; drop _id
    .lean();                         // plain objects
  res.json(users);
});
```

Security note: if you pass `req.query` straight into `find`, a client can send `?city[$ne]=x` and Express parses it into `{ city: { $ne: "x" } }` (NoSQL injection). Cast values with `String()` or use Mongoose's `sanitizeFilter: true`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Matching an embedded document with the whole object
```javascript
db.users.find({ address: { pin: "110001" } });   // Wrong — 0 results (exact subdoc match)
db.users.find({ "address.pin": "110001" });      // Right — dot notation
```

❌ Mistake 2: Mixing inclusion and exclusion in a projection
✅ Correct: use all `1`s or all `0`s (only `_id: 0` may be combined with inclusions).

❌ Mistake 3: Forgetting quotes around dotted paths
```javascript
db.users.find({ address.state: "DL" });   // Wrong — syntax error
db.users.find({ "address.state": "DL" }); // Right
```

---

## 🧠 Tricky Interview Question

```javascript
db.users.find({ address: null }, { name: 1, _id: 0 })
```
Answer: It returns Meera, whose document has NO `address` field at all. `{ field: null }` matches both an explicit `null` value and a missing field. To match only explicit nulls use `{ field: { $type: "null" } }`; to match only missing, `{ field: { $exists: false } }`.

---

## ⚫ Interview Questions + Answers

Q1: How do you query a field inside an embedded document?
A1: Use dot notation in quotes: `{ "address.state": "DL" }`. It works at any depth and also through arrays of subdocuments (`"items.sku": "A1"`).

Q2: How does equality work on an array field?
A2: A scalar value matches if any element equals it. An array value matches only an identical array (same elements, same order), or an element that is itself that array. Use `$all` for "contains all in any order".

Q3: Is `_id` returned when you project `{ name: 1 }`?
A3: Yes. `_id` is included by default. Add `_id: 0` to remove it.

Q4: What is a covered query?
A4: A query where all filter fields and projected fields are in one index and `_id` is excluded (or indexed). MongoDB answers from the index alone without fetching documents; `explain()` shows `totalDocsExamined: 0`.

Q5: Why is `find(req.query)` dangerous?
A5: Operators can be injected (`?password[$ne]=1`). Whitelist fields, cast to strings/numbers, or enable `sanitizeFilter`.

---

## 🔷 When to Use + When Not to Use
✅ Use equality filters + dot notation for most lookups; always project when documents are large or contain sensitive fields.

❌ Avoid whole-subdocument matching and exact array matching unless you really want exactness; avoid returning password hashes or internal fields by forgetting to exclude them.

---

## 📊 Visual Diagram
```
 find( FILTER , PROJECTION )
        │            │
        ▼            ▼
 {city:"Pune",     {name:1, _id:0}
  "address.state":"MH",
  skills:"mongo"}      
        │
 match each doc:  city==Pune AND address.state==MH AND "mongo" IN skills
        │
        ▼
 matched docs ──► keep only chosen fields ──► client
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Filter | Document describing matches | Match की शर्त वाला document |
| Equality match | Field equals a value | Field value के बराबर |
| Dot notation | `"a.b"` path into subdocument | Subdocument के अंदर path |
| Projection | Choose returned fields | लौटने वाले fields चुनना |
| Covered query | Answered from index alone | सिर्फ़ index से जवाब |
| NoSQL injection | Operators sneaked into filters | Filter में operators घुसाना |

---

## ⚡ 3-Line Summary
English:
1. A filter is a document of field/value pairs (implicit AND); use dot notation for embedded fields and plain values for array membership.
2. Whole-subdocument and exact-array matches are strict; `null` matches missing fields too.
3. Projection uses all-1 or all-0 (plus `_id`), shrinking payloads and hiding sensitive fields.

Hindi:
1. Filter field/value जोड़ों का document है (implicit AND); embedded fields के लिए dot notation और array membership के लिए साधारण value इस्तेमाल करो।
2. पूरा-subdocument और exact-array match सख़्त होते हैं; `null` missing fields से भी match करता है।
3. Projection में सब 1 या सब 0 (और `_id`), इससे payload छोटा और sensitive fields छिपे रहते हैं।

---

## ➡️ Next Topic
**16. Sorting, limit, skip** — Ordering results and paginating them.
