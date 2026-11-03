# 14. find and findOne
# हिंदी में: find और findOne

---

## 🔵 Simple Definition (English)
**`find(filter, projection)`** returns a **cursor** over all documents matching the filter; **`findOne(filter, projection)`** returns the **first matching document itself** (or `null`). A cursor is a lazy pointer: the server sends results in batches (the first batch is up to 101 documents or 16 MB, later batches up to 16 MB) while you iterate.

## 🔵 सरल परिभाषा (Hindi)
**`find(filter, projection)`** filter से match करने वाले सभी documents पर एक **cursor** लौटाता है; **`findOne(filter, projection)`** **पहला matching document सीधे** लौटाता है (या `null`)। Cursor एक lazy pointer है: जब तुम iterate करते हो, server results batches में भेजता है।

---

## 🔴 Problem it Solves
Reading data is the most common operation. Returning a million matching documents in one response would blow up memory and network. The cursor model streams results in batches, so the client processes a few at a time. `findOne` solves the "I only need one" case (get user by email) without creating a cursor yourself, and returns `null` instead of an error when nothing matches, which is easy to check.

## 🔴 यह क्यों बना? (Hindi)
Data पढ़ना सबसे आम operation है। दस लाख matching documents एक ही response में भेजने से memory और network फट जाएँगे। Cursor model results को batches में stream करता है, client एक बार में थोड़े ही process करता है। `findOne` उस case के लिए है जहाँ सिर्फ़ एक चाहिए (email से user), और कुछ न मिले तो error की जगह `null` देता है जिसे check करना आसान है।

---

## 🟢 How it Works — Step by Step

Step 1 → You call `find({ city: "Pune" })`. Nothing is sent to the server yet in the Node driver; it just builds a cursor (lazy).
Step 2 → When you iterate (`toArray()`, `for await`, `next()`), the driver sends the `find` command.
Step 3 → The server's query planner picks an index (or a collection scan), runs the filter and returns the first batch plus a cursor id.
Step 4 → As you consume the batch, the driver issues `getMore` commands to fetch the next ones.
Step 5 → When exhausted (or idle for 10 minutes) the cursor is closed. `findOne` is `find().limit(1)` that returns the first element or `null`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → तुम `find({ city: "Pune" })` call करते हो। Node driver में अभी server को कुछ नहीं जाता; बस cursor बनता है (lazy)।
Step 2 → जब तुम iterate करते हो (`toArray()`, `for await`, `next()`) तब driver `find` command भेजता है।
Step 3 → Server का query planner index (या collection scan) चुनता है, filter चलाता है और पहला batch व cursor id लौटाता है।
Step 4 → जैसे-जैसे batch खत्म होता है, driver अगले batches के लिए `getMore` भेजता है।
Step 5 → खत्म होने पर (या 10 मिनट idle रहने पर) cursor बंद हो जाता है। `findOne` असल में `find().limit(1)` है जो पहला element या `null` देता है।

---

## 🟡 Real World Example
**Swiggy's order-history screen**: the app shows the last 10 orders for a user, so the backend runs `find({ userId }).sort({ placedAt: -1 }).limit(10)` and returns a list. When the user taps one order, the backend runs `findOne({ _id: orderId, userId })` to fetch that single order (also checking it belongs to the user). The list uses a cursor + batching; the detail screen uses `findOne`.

## 🟡 Real Example Hindi mein
**Swiggy की order-history screen** में app user के आखिरी 10 orders दिखाता है, तो backend `find({ userId }).sort({ placedAt: -1 }).limit(10)` चलाता है। User एक order पर tap करे तो backend `findOne({ _id: orderId, userId })` से वो एक order लाता है (और जाँचता है कि वो उसी user का है)। List cursor + batching इस्तेमाल करती है; detail screen `findOne`।

---

## 💻 Code Example — Basic

Verified on MongoDB 8.0.4. Collection `products` has `{_id:1 Mouse 499}`, `{_id:2 Keyboard 1299 tags:[usb]}`, `{_id:3 Monitor 8999}`.

```javascript
use("shop");

// findOne: returns ONE document object (not a cursor)
db.products.findOne({ name: "Mouse" });
// Output: { _id: 1, name: 'Mouse', price: 499 }

// findOne with no match returns null (NOT an error)
db.products.findOne({ name: "zzz" });
// Output: null

// find: returns a CURSOR. mongosh prints the first 20 docs automatically
db.products.find({ price: { $lt: 2000 } });
// Output: [ { _id: 1, name: 'Mouse', price: 499 },
//           { _id: 2, name: 'Keyboard', price: 1299, tags: [ 'usb' ] } ]

// Convert the cursor to an array to use it in code
const arr = db.products.find({ price: { $lt: 2000 } }).toArray(); // pulls ALL into memory
print(arr.length); // 2
```

## 💻 Code Example — Advanced

```javascript
// Manual cursor iteration: memory-friendly for big result sets
const c = db.products.find();       // cursor object
print(c.constructor.name);          // Cursor
print(JSON.stringify(c.next()));    // {"_id":1,"name":"Mouse","price":499}  (first doc)
print(c.hasNext());                 // true (more docs remain)

// forEach processes one by one without building a giant array
db.products.find().forEach(d => print(d.name)); // Mouse, Keyboard, Monitor

// Tune the batch size (documents fetched per round trip)
db.products.find().batchSize(500);

// A cursor can be consumed only ONCE; run find() again to re-read.
// Prefer findOne over find().limit(1)[0]: same thing, clearer intent.
```

Node.js driver (v7.x):

```javascript
const col = client.db("shop").collection("products");

// find() returns a FindCursor; the options object holds projection/sort/limit
const cursor = col.find({ price: { $lt: 2000 } }, { projection: { name: 1, _id: 0 } });

// Best for big data: async iteration pulls batches lazily
for await (const doc of cursor) {
  console.log(doc); // { name: 'Mouse' }  then { name: 'Keyboard' }
}

// findOne returns a Promise of a doc or null
const one = await col.findOne({ name: "Mouse" });
if (!one) throw new Error("not found"); // handle null explicitly
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const mongoose = require("mongoose");
const User = mongoose.model("User", new mongoose.Schema({ name: String, age: Number }));

// GET /users  -> list
app.get("/users", async (req, res) => {
  // .lean() returns plain JS objects (faster, less memory than Mongoose documents)
  const users = await User.find({ age: { $gte: 18 } }).lean();
  res.json(users);
});

// GET /users/:id -> single document
app.get("/users/:id", async (req, res) => {
  if (!mongoose.isValidObjectId(req.params.id))     // avoid CastError on bad ids
    return res.status(400).json({ error: "bad id" });
  const u = await User.findById(req.params.id).lean(); // = findOne({ _id: id })
  if (!u) return res.status(404).json({ error: "not found" }); // null -> 404
  res.json(u);
});
```

Verified in Mongoose 9: `User.find({age:{$gte:18}}).select('name -_id').sort('-age').limit(5).lean()` returned `[ { name: 'Asha' } ]`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Treating `find()` result as an array
```javascript
const r = db.collection("p").find({});   // Wrong — this is a cursor
console.log(r.length);                   // undefined
const arr = await db.collection("p").find({}).toArray(); // Right
```

❌ Mistake 2: Not handling `null` from `findOne`
```javascript
const u = await col.findOne({ email });
console.log(u.name);          // Wrong — TypeError if no user
console.log(u?.name ?? "n/a"); // Right
```

❌ Mistake 3: `toArray()` on a huge collection
✅ Correct: use `for await (const d of cursor)` or add `limit` so you never load millions of documents into memory.

---

## 🧠 Tricky Interview Question

```javascript
const cursor = db.products.find();
cursor.toArray();
print(cursor.hasNext());
```
Answer: `false`. `toArray()` exhausts the cursor, and a cursor can only be traversed once. To read again you must call `find()` again. Also note that in the Node driver, `find()` itself does not hit the server until you iterate (lazy), so a `find()` without `await`/`toArray()` does nothing.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `find` and `findOne`?
A1: `find` returns a cursor to all matches; `findOne` returns the first matching document (or `null`). `findOne` internally uses a limit of 1, so it stops scanning once one match is found.

Q2: What does `findOne({})` return and in which order?
A2: It returns the first document in natural order (usually insertion order, but not guaranteed). If order matters, use `find().sort(...).limit(1)`.

Q3: What is a cursor timeout?
A3: A server cursor idle for about 10 minutes is closed automatically, and further `getMore` calls fail with a "cursor not found" error. Process results promptly or use `noCursorTimeout` carefully.

Q4: How many documents are in the first batch?
A4: By default the first batch has up to 101 documents (or 16 MB), after that batches are up to 16 MB each; `batchSize()` can tune it.

Q5: Why use `.lean()` in Mongoose?
A5: `find` returns full Mongoose documents with getters, setters and change tracking. `.lean()` skips that and returns plain objects, which is much cheaper for read-only API responses.

---

## 🔷 When to Use + When Not to Use
✅ Use `find` for lists and streams; use `findOne` for lookups by unique key (email, `_id`).

❌ Avoid `find().toArray()` without a limit on large collections; avoid `findOne` when you need a deterministic "latest/first" without a sort.

---

## 📊 Visual Diagram
```
 app: find({city:"Pune"})
   │  (lazy: build cursor)
   ▼
 iterate ──► server: find cmd ──► batch 1 (<=101 docs) + cursorId
   │                                   │
   └── batch used up ──► getMore ──────┘──► batch 2 ... ──► exhausted -> closed

 findOne(filter) == find(filter).limit(1) -> doc | null
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cursor | Lazy pointer to query results | Query results का lazy pointer |
| find | Returns cursor of matches | सब matches का cursor |
| findOne | Returns first match or null | पहला match या null |
| batchSize | Docs per round trip | एक round trip में docs |
| getMore | Command to fetch next batch | अगला batch लाने की command |
| lean | Plain objects in Mongoose | Mongoose में plain objects |

---

## ⚡ 3-Line Summary
English:
1. `find` returns a lazy, one-pass cursor; `findOne` returns one document or `null`.
2. Iterate with `for await` / `forEach` for big data; `toArray()` loads everything into memory.
3. Always handle `null` and use `.lean()` for fast read-only Mongoose queries.

Hindi:
1. `find` lazy, एक-बार वाला cursor देता है; `findOne` एक document या `null` देता है।
2. बड़े data के लिए `for await` / `forEach` इस्तेमाल करो; `toArray()` सब कुछ memory में लाता है।
3. `null` हमेशा handle करो और read-only Mongoose queries के लिए `.lean()` लगाओ।

---

## ➡️ Next Topic
**15. Query Filters — equality and projection** — Writing filters (including nested and array fields) and choosing which fields come back.
