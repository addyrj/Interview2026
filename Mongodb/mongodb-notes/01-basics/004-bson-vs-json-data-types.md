# 4. BSON vs JSON + Data Types
# हिंदी में: BSON बनाम JSON और Data Types

---

## 🔵 Simple Definition (English)
**JSON** is a human-readable text format with only a few types (string, number, boolean, null, array, object). **BSON** (Binary JSON) is MongoDB's binary serialization of JSON-like documents. It is faster to scan and adds **extra types** that JSON lacks: `Date`, `ObjectId`, `Int32`, `Int64 (Long)`, `Double`, `Decimal128`, `BinData`, `Timestamp`, `Regex` and more. You write JSON-like syntax; the driver converts it to BSON.

## 🔵 सरल परिभाषा (Hindi)
**JSON** एक human-readable text format है जिसमें गिने-चुने types हैं (string, number, boolean, null, array, object)। **BSON** (Binary JSON) MongoDB का JSON-जैसे documents का binary रूप है। यह scan करने में तेज़ है और JSON में न मिलने वाले **अतिरिक्त types** देता है: `Date`, `ObjectId`, `Int32`, `Int64 (Long)`, `Double`, `Decimal128`, `BinData`, `Timestamp`, `Regex` आदि। आप JSON-जैसी syntax लिखते हो; driver उसे BSON में बदल देता है।

---

## 🔴 Problem it Solves
Plain JSON cannot distinguish an integer from a float, has no date type (dates become strings), no binary type, and parsing text to find a field is slow. For a database you need: precise numeric types (money!), real dates for range queries and sorting, binary data, fast field traversal (BSON stores length prefixes so the server can skip fields), and a defined **sort order across types**. BSON provides all of that, at the cost of being slightly larger than compact JSON.

## 🔴 यह क्यों बना? (Hindi)
Plain JSON integer और float में फ़र्क नहीं कर सकता, उसमें date type नहीं है (dates string बन जाती हैं), binary type नहीं है, और text parse करके field ढूँढना धीमा है। Database को चाहिए: सटीक numeric types (पैसे के लिए!), range queries और sorting के लिए असली dates, binary data, fast field traversal (BSON length prefixes रखता है ताकि server fields skip कर सके), और types के बीच तय **sort order**। BSON यह सब देता है, बदले में compact JSON से थोड़ा बड़ा होता है।

---

## 🟢 How it Works — Step by Step

Step 1 → You write a document in mongosh/JS: `{ price: 99.5, qty: NumberInt(2), at: new Date() }`.
Step 2 → The driver serializes it into BSON: each field = 1 type byte + field name (C-string) + value bytes; the document begins with a 4-byte total length.
Step 3 → The server stores BSON bytes as-is (WiredTiger compresses on disk). Because of length prefixes it can jump over fields without parsing text.
Step 4 → When you query, BSON comes back and the driver deserializes it to native types (Date, ObjectId, Long ...).
Step 5 → Type matters for queries: `{ a: 1 }` does not match the string `"1"`; use `$type` to filter by type.
Step 6 → Mixed-type fields sort by a fixed **BSON comparison order** (null < numbers < string < object < array < binData < ObjectId < bool < date < regex ...).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → mongosh/JS में document लिखो: `{ price: 99.5, qty: NumberInt(2), at: new Date() }`।
Step 2 → Driver उसे BSON में serialize करता है: हर field = 1 type byte + field name (C-string) + value bytes; document 4-byte कुल length से शुरू होता है।
Step 3 → Server BSON bytes जैसे-के-तैसे रखता है (disk पर WiredTiger compress करता है)। Length prefixes की वजह से वह text parse किए बिना fields skip कर सकता है।
Step 4 → Query पर BSON लौटता है और driver उसे native types (Date, ObjectId, Long ...) में बदलता है।
Step 5 → Query में type मायने रखता है: `{ a: 1 }` string `"1"` से match नहीं करता; type से filter के लिए `$type` इस्तेमाल करो।
Step 6 → Mixed-type fields एक तय **BSON comparison order** में sort होते हैं (null < numbers < string < object < array < binData < ObjectId < bool < date < regex ...)।

---

## 🟡 Real World Example
**Razorpay-style payments**: an amount of Rs 1,234.56 must never be stored as a floating-point `Double` (0.1 + 0.2 = 0.30000000000000004 in binary floats). It is stored either as an integer count of paise (`NumberLong("123456")`) or as `Decimal128("1234.56")`. The `createdAt` field is a real BSON `Date`, so "all payments between 1 Nov and 7 Nov" is a fast indexed range query, and the payment `_id` is an `ObjectId` that also encodes its creation time.

## 🟡 Real Example Hindi mein
**Razorpay जैसे payments**: Rs 1,234.56 की amount को कभी floating-point `Double` में नहीं रखना चाहिए (binary floats में 0.1 + 0.2 = 0.30000000000000004)। इसे या तो paise की integer गिनती (`NumberLong("123456")`) या `Decimal128("1234.56")` में रखा जाता है। `createdAt` असली BSON `Date` होता है, इसलिए "1 Nov से 7 Nov के बीच सारे payments" तेज़ indexed range query बन जाती है, और payment का `_id` एक `ObjectId` है जो creation time भी encode करता है।

---

## 💻 Code Example — Basic

Verified on mongod 8.0.4 (mongosh).

```javascript
use bson_demo

// One document with many BSON types
db.types.insertOne({
  a: 1,                          // mongosh stores a plain JS number as int when it fits int32
  b: NumberInt(2),               // explicit 32-bit int
  c: NumberLong("3"),            // 64-bit int (pass a STRING to avoid precision loss)
  d: Decimal128("1.10"),         // exact decimal, use for money
  e: new Date("2024-01-01"),     // BSON Date (UTC milliseconds since epoch)
  f: true,                       // boolean
  g: null,                       // null
  h: /ab/,                       // regular expression
  i: BinData(0, "AAEC")          // binary data (subtype 0, base64 input)
})

// Ask the server which BSON type each field really has
db.types.aggregate([{ $project: { _id: 0,
  a: { $type: "$a" }, b: { $type: "$b" }, c: { $type: "$c" }, d: { $type: "$d" },
  e: { $type: "$e" }, f: { $type: "$f" }, g: { $type: "$g" }, h: { $type: "$h" }, i: { $type: "$i" } } }])
// Output:
// [ { a: 'int', b: 'int', c: 'long', d: 'decimal', e: 'date',
//     f: 'bool', g: 'null', h: 'regex', i: 'binData' } ]

db.types.findOne({}, { _id: 0, c: 1, d: 1, e: 1 })
// Output: { c: Long('3'), d: Decimal128('1.10'), e: ISODate('2024-01-01T00:00:00.000Z') }
```

## 💻 Code Example — Advanced

```javascript
// Float trap and Decimal128 fix (mongosh)
0.1 + 0.2
// Output: 0.30000000000000004   <- binary floating point is NOT exact

// Filter by BSON type with $type (name or number both work; 1 = double, 16 = int)
db.types.find({ a: { $type: "double" } }).toArray().length
// Output: 0   (a is stored as 'int', not 'double')
db.types.find({ a: { $type: "int" } }).toArray().length
// Output: 1

// Node.js driver: types map to JS classes
const { MongoClient, Decimal128, Long, ObjectId } = require('mongodb');
async function demo() {
  const client = new MongoClient('mongodb://127.0.0.1:27017');
  await client.connect();
  const col = client.db('bson_demo').collection('payments');
  await col.insertOne({
    amount: Decimal128.fromString('1234.56'), // exact money value
    paise: Long.fromNumber(123456),           // integer paise
    createdAt: new Date(),                     // real Date -> range queries work
    merchant: new ObjectId(),                  // 12-byte id
  });
  const doc = await col.findOne({});
  console.log(doc.amount.toString());          // '1234.56' (Decimal128 -> string for display)
  console.log(doc.createdAt instanceof Date);  // true
  await client.close();
}
demo();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose schema types map to BSON types
const mongoose = require('mongoose');
const paymentSchema = new mongoose.Schema({
  amount:    { type: mongoose.Schema.Types.Decimal128, required: true }, // BSON decimal
  currency:  { type: String, default: 'INR' },                            // BSON string
  createdAt: { type: Date, default: Date.now },                           // BSON date
  meta:      { type: mongoose.Schema.Types.Mixed },                       // any BSON
  proof:     Buffer,                                                       // BSON binData
});
const Payment = mongoose.model('Payment', paymentSchema);

// Decimal128 serialises to { $numberDecimal: "..." } in JSON - convert in the route
app.get('/payments/:id', async (req, res) => {
  const p = await Payment.findById(req.params.id);
  res.json({ ...p.toObject(), amount: p.amount.toString() }); // send "1234.56" to the client
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing money as a double
```javascript
// Wrong - rounding errors accumulate
db.pay.insertOne({ amount: 0.1 + 0.2 })   // stored 0.30000000000000004

// Right - Decimal128 (or integer paise)
db.pay.insertOne({ amount: Decimal128("0.30") })
```

❌ Mistake 2: Storing dates as strings ("01/11/2024")
✅ Correct: Use `new Date()`. Strings sort alphabetically ("02/01" < "10/12" incorrectly across years) and cannot use date operators; real `Date` supports range queries, TTL indexes and `$dateToString`.

---

## 🧠 Tricky Interview Question

```javascript
db.t.insertMany([{ v: 1 }, { v: "1" }, { v: 1.0 }, { v: true }])
db.t.find({ v: 1 }).count()
```
Answer: It returns **2**. `1` and `1.0` are the same numeric value (mongosh actually stores `1.0` as an int too; a true double `1.0` from a driver compares equal as well), and MongoDB compares numbers across int/long/double/decimal by value, so both match. The string `"1"` does not match (different type) and `true` does not match either (booleans are not numbers in comparisons, unlike JavaScript). Lesson: type consistency matters; use `$type` to find stray strings that should be numbers. (Output shape of the count may show a deprecation warning in mongosh; prefer `countDocuments`.)

---

## ⚫ Interview Questions + Answers

Q1: What is BSON and why not store plain JSON?
A1: BSON is a binary, typed, length-prefixed encoding of JSON-like documents. It adds types (Date, ObjectId, Decimal128, BinData), enables fast traversal, and defines sort order; plain JSON text is slower to parse and too type-poor.

Q2: Which type for money?
A2: `Decimal128` (exact base-10) or an integer in the smallest unit (paise/cents) as `Long`. Never `Double`.

Q3: Max document size and nesting depth?
A3: 16 MB per document; nesting up to 100 levels.

Q4: How does a JS number get stored?
A4: The Node driver stores a JS number as `Int32` if it is an integer fitting in 32 bits, otherwise `Double`; to force types use `Int32`, `Long`, `Double`, `Decimal128` classes from the `bson` package.

Q5: How do you query by type?
A5: `{ field: { $type: "string" } }` (or the numeric alias), and `$type` also works in aggregation to inspect a value's type.

---

## 🔷 When to Use + When Not to Use
✅ Use `Date` / `Decimal128` / `Long` / `ObjectId` when:
- You need range queries on time, exact money, ids above 2^53, or time-embedded unique ids

❌ Avoid when:
- Mixed types in one field (`"123"` and `123`) - they break queries and sorting. Keep one type per field.

---

## 📊 Visual Diagram
```
 JSON text                      BSON bytes
 { "n": 5, "d": "x" }           ┌────────┬──────┬─────────┬────────┬──────────┬───┐
                                │ length │ 0x10 │ "n\0"   │ 5      │ 0x02 ... │ 00│
                                │ 4 bytes│ int32│ name    │ 4 bytes│ string   │end│
                                └────────┴──────┴─────────┴────────┴──────────┴───┘
 Types: double, string, object, array, binData, ObjectId, bool,
        date, null, regex, int, timestamp, long, decimal128, minKey, maxKey
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BSON | Binary JSON encoding | Binary JSON encoding |
| Int32 / Long | 32-bit / 64-bit integers | 32-bit / 64-bit integers |
| Double | 64-bit float (inexact) | 64-bit float (अनिश्चित exactness) |
| Decimal128 | Exact decimal number | सटीक decimal संख्या |
| Date | UTC milliseconds since epoch | Epoch से UTC milliseconds |
| BinData | Binary bytes | Binary bytes |
| $type | Operator to match by BSON type | BSON type से match करने वाला operator |

---

## ⚡ 3-Line Summary
English:
1. BSON is MongoDB's binary, typed, length-prefixed version of JSON with extra types like Date, ObjectId and Decimal128.
2. Use Decimal128 or integer paise for money and real Dates for time; never doubles or date strings.
3. Numbers compare by value across int/long/double, but strings and numbers never match; check with `$type`.

Hindi:
1. BSON, JSON का MongoDB वाला binary, typed, length-prefixed रूप है जिसमें Date, ObjectId, Decimal128 जैसे अतिरिक्त types हैं।
2. पैसे के लिए Decimal128 या integer paise और समय के लिए असली Date इस्तेमाल करो; double या date string कभी नहीं।
3. Numbers int/long/double में value से compare होते हैं, पर string और number कभी match नहीं होते; `$type` से जाँचो।

---

## ➡️ Next Topic
**5. ObjectId — structure and uses** — The default 12-byte `_id` type, its parts and where it is useful.
