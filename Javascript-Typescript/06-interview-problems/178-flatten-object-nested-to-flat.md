# 178. Flatten Object (nested to flat)
# हिंदी में: Nested Object को Flat करना — Dotted Keys बनाना और cycles से बचना

---

## 🔵 Simple Definition (English)
Flattening an object turns nested keys into one level of keys joined by dots. For example, `{ a: { b: 1 } }` becomes `{ "a.b": 1 }`. Array indexes become keys too, so `{ items: [{ sku: "A1" }] }` becomes `{ "items.0.sku": "A1" }`.

## 🔵 सरल परिभाषा (Hindi)
Object को flatten करने का मतलब है nested keys को dot से जोड़कर एक ही level की keys बनाना। जैसे `{ a: { b: 1 } }` बनता है `{ "a.b": 1 }`। Array के indexes भी keys बनते हैं, तो `{ items: [{ sku: "A1" }] }` बनता है `{ "items.0.sku": "A1" }`।

---

## 🔴 Problem it Solves
**Problem Statement:** Write `flattenObject(obj)` that returns a new object with no nested objects or arrays. Each leaf value (a number, string, boolean, `null`, Date, or function) gets a key that is the path to it, joined by dots. Empty objects and arrays are kept as values.

Many systems accept only flat key-value data. A CSV export needs one column per field. A config system such as environment variables needs keys like `DB_HOST`. A logging or analytics tool needs flat events for filtering. Without flattening, each consumer writes its own nested loop.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `flattenObject(obj)` लिखो जो एक नया object लौटाए जिसमें कोई nested object या array न हो। हर leaf value (number, string, boolean, `null`, Date या function) की key उसका path हो, जो dots से जुड़ा हो। खाली objects और arrays को value के रूप में रखो।

कई systems सिर्फ़ flat key-value data लेते हैं। CSV export को हर field के लिए एक column चाहिए। Config system को `DB_HOST` जैसी keys चाहिए। Analytics tool को filtering के लिए flat events चाहिए। Flatten के बिना हर consumer अपना nested loop लिखता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Start at the root object with an empty prefix.
Step 2 → For each own key, build the path: the prefix, a dot, and the key (no dot at the root).
Step 3 → If the value is a non-empty plain object or array, go deeper with the new path.
Step 4 → If the value is anything else, store it in the result under the path.
Step 5 → Track the objects on the current path, so a circular reference is reported instead of looping forever.
Step 6 → Return the flat result object.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Root object से शुरू करो, prefix खाली रखो।
Step 2 → हर own key के लिए path बनाओ: prefix, एक dot और key (root पर dot नहीं)।
Step 3 → अगर value खाली न होने वाला plain object या array है, तो नए path के साथ और गहराई में जाओ।
Step 4 → बाकी सभी values को path की key के नीचे result में रखो।
Step 5 → जिन objects के रास्ते पर हम हैं उन्हें याद रखो, ताकि circular reference पकड़ में आए और loop न बने।
Step 6 → Flat result object लौटाओ।

---

## 🟡 Real World Example
Razorpay's webhook payloads are nested: `payment.entity.notes.orderId`. A reporting job flattens each event into dotted columns before writing a CSV for the finance team. Amazon's product feed flattens variant data so that spreadsheets can filter by `variants.0.color`. Swiggy's analytics events are flattened before they go into a log index, so queries can search `restaurant.city`.

Scenario: An order event is `{ id: 9, customer: { name: "Ravi", address: { city: "Pune" } }, items: [{ sku: "A1" }] }`. The flat version has the keys `customer.address.city` and `items.0.sku`, ready for a CSV row.

## 🟡 Real Example Hindi mein
Razorpay के webhook payloads nested होते हैं: `payment.entity.notes.orderId`। एक reporting job finance team के लिए CSV लिखने से पहले हर event को dotted columns में flatten करता है। Amazon की product feed variant data को flatten करती है, ताकि spreadsheet में `variants.0.color` से filter हो सके। Swiggy के analytics events log index में जाने से पहले flatten होते हैं, ताकि `restaurant.city` पर search हो सके।

उदाहरण: Order event है `{ id: 9, customer: { name: "Ravi", address: { city: "Pune" } }, items: [{ sku: "A1" }] }`। Flat version में keys हैं `customer.address.city` और `items.0.sku`, जो CSV row के लिए तैयार हैं।

---

## 💻 Code Example — Basic
```javascript
// Basic: recursive flatten with dotted keys
function flattenObject(obj, prefix = "") {  // prefix holds the path so far, for example "customer.address"
  const out = {};                            // the flat result with dotted keys
  for (const key of Object.keys(obj)) {      // every own key at this level
    const path = prefix ? `${prefix}.${key}` : key; // build the full dotted path
    const value = obj[key];                  // the value stored under this key
    const isContainer = value !== null && typeof value === "object" && Object.keys(value).length > 0; // non-empty object or array
    if (isContainer) {                       // a non-empty object or array: go deeper
      Object.assign(out, flattenObject(value, path)); // merge the flat results of the child
    } else {
      out[path] = value;                     // a leaf value (or an empty container): store it under its path
    }
  }
  return out;                                // the flat object
}

// Sample: an order event with nested customer data and an array of items
const order = {
  id: 9,
  customer: { name: "Ravi", address: { city: "Pune" } },
  items: [{ sku: "A1" }, { sku: "B2" }],
  note: null,
};
console.log(JSON.stringify(flattenObject(order)));
// Expected output: {"id":9,"customer.name":"Ravi","customer.address.city":"Pune","items.0.sku":"A1","items.1.sku":"B2","note":null}

// Edge cases: empty object and empty array are kept as values, and a Date stays a leaf
console.log(JSON.stringify(flattenObject({ a: {}, b: [], c: new Date(0) })));
// Expected output: {"a":{},"b":[],"c":"1970-01-01T00:00:00.000Z"}
```

## 💻 Code Example — Advanced
```javascript
// Advanced: custom separator, empty-container option, Date and function leaves, and cycle detection
function flattenObject(input, { separator = ".", skipEmpty = false } = {}) {
  // Guard: the input must be an object or an array
  if (input === null || typeof input !== "object") throw new TypeError("input must be an object or array");

  const out = {};                            // the flat result
  const ancestors = new Set();               // objects on the current path, used to detect cycles

  function walk(node, prefix) {              // visit one node; prefix is the path so far
    if (ancestors.has(node)) {               // this object is already on the path: a cycle
      throw new TypeError(`circular reference found at ${prefix || "root"}`);
    }
    ancestors.add(node);                     // we are inside this node now

    for (const key of Object.keys(node)) {   // every own enumerable key
      const path = prefix === "" ? key : prefix + separator + key; // join with the chosen separator
      const value = node[key];               // the child value
      // A Date is a leaf even though it is an object; Object.keys(new Date()) is empty
      const isNested = value !== null && typeof value === "object" && !(value instanceof Date);

      if (isNested) {                        // object or array
        if (Object.keys(value).length === 0) { // empty container
          if (!skipEmpty) out[path] = Array.isArray(value) ? [] : {}; // keep it unless skipEmpty is set
        } else {
          walk(value, path);                 // recurse into the child with the new prefix
        }
      } else {
        out[path] = value;                   // primitive, null, Date, or function: a leaf
      }
    }

    ancestors.delete(node);                  // leaving this node: it is no longer on the path
  }

  walk(input, "");                           // start at the root with an empty prefix
  return out;                                // the flat object
}

// Test 1: a custom separator, nested arrays, an empty object, and a Date
const cfg = { db: { host: "localhost", ports: [5432, 5433] }, flags: {}, when: new Date(0) };
console.log(JSON.stringify(flattenObject(cfg, { separator: "__" })));
// Expected output: {"db__host":"localhost","db__ports__0":5432,"db__ports__1":5433,"flags":{},"when":"1970-01-01T00:00:00.000Z"}

// Test 2: skipEmpty drops the empty containers
console.log(JSON.stringify(flattenObject(cfg, { skipEmpty: true }))); // Expected output: {"db.host":"localhost","db.ports.0":5432,"db.ports.1":5433,"when":"1970-01-01T00:00:00.000Z"}

// Test 3: a circular reference is reported, not looped forever
const loop = { name: "a" };
loop.self = loop;                            // the object points to itself
try {
  flattenObject(loop);
} catch (err) {
  console.log(err.message);                  // Expected output: circular reference found at self
}

// Time:  O(n), where n is the number of keys and values in the input
// Space: O(d) for the recursion path (d = depth) plus O(n) for the result
```

### Edge Cases
- Empty object `{}` and empty array `[]` are kept as values by default, so the output does not lose the key.
- `null` is a leaf, not an object, so it is stored as `null`.
- A `Date` is a leaf, because its keys are empty; storing it as an object would lose its time.
- Functions are leaves; `typeof` is `"function"`, which is not `"object"`.
- The same object referenced twice in different places (not in a cycle) is flattened twice, which is correct. Only the current path is tracked.

---

## 🟠 Express.js Integration
A reporting endpoint returns orders as a CSV, and the CSV needs one column per field. The endpoint flattens each order before it builds the header row.

```javascript
// Express.js: export orders as CSV, with one column per flattened field
const express = require("express");          // web framework
const app = express();                       // create the app

// Simple flatten for this endpoint (same idea as the basic version)
function flatten(obj, prefix = "") {
  const out = {};                            // flat result
  for (const key of Object.keys(obj)) {      // each key at this level
    const path = prefix ? `${prefix}.${key}` : key; // dotted path
    const v = obj[key];                      // the value
    if (v && typeof v === "object" && !(v instanceof Date) && Object.keys(v).length) {
      Object.assign(out, flatten(v, path));  // go deeper for non-empty objects and arrays
    } else {
      out[path] = v;                         // store the leaf
    }
  }
  return out;                                // flat object
}

// Pretend orders from a database
const orders = [
  { id: 9, customer: { name: "Ravi", city: "Pune" }, items: [{ sku: "A1" }] },
  { id: 10, customer: { name: "Asha", city: "Delhi" }, items: [{ sku: "B2" }] },
];

// GET /api/orders/export.csv
app.get("/api/orders/export.csv", (req, res) => {
  const rows = orders.map((o) => flatten(o));          // one flat object per order
  const headers = [...new Set(rows.flatMap((r) => Object.keys(r)))]; // union of all keys, in first-seen order
  const lines = [headers.join(",")];                   // the header row
  for (const row of rows) {                            // one line per order
    lines.push(headers.map((h) => JSON.stringify(row[h] ?? "")).join(",")); // quote values, blank when missing
  }
  res.type("text/csv").send(lines.join("\n"));         // 200 OK with the CSV text
});

app.listen(process.env.PORT || 3000, () => {
  console.log("Export API running");               // printed when ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `typeof value === "object"` as the only check
✅ Correct: `null` is also `"object"`, and `Object.keys(null)` throws. Check for `null` first.

```javascript
// Wrong: null is treated as a nested object, so Object.keys throws
function badFlatten(obj, prefix = "") {
  const out = {};
  for (const key of Object.keys(obj)) {
    const v = obj[key];
    if (typeof v === "object") Object.assign(out, badFlatten(v, key)); // null also matches
    else out[key] = v;
  }
  return out;
}
try { badFlatten({ note: null }); } catch (err) { console.log(err.name); } // Expected output: TypeError

// Right: check for null before treating the value as a container
function goodFlatten(obj, prefix = "") {
  const out = {};
  for (const key of Object.keys(obj)) {
    const v = obj[key];
    const path = prefix ? `${prefix}.${key}` : key;
    if (v !== null && typeof v === "object" && Object.keys(v).length) Object.assign(out, goodFlatten(v, path));
    else out[path] = v;
  }
  return out;
}
console.log(JSON.stringify(goodFlatten({ note: null }))); // Expected output: {"note":null}
```

❌ **Mistake 2:** Forgetting the prefix when recursing, so the child keys lose their parent names
✅ Correct: pass the full path down, and join each new key onto it.

```javascript
// Wrong: the recursion does not pass the parent path, so names collide and get lost
function forgetPrefix(obj) {
  const out = {};
  for (const key of Object.keys(obj)) {
    const v = obj[key];
    if (v !== null && typeof v === "object") Object.assign(out, forgetPrefix(v)); // no prefix passed
    else out[key] = v;                       // only the last part of the key is kept
  }
  return out;
}
console.log(JSON.stringify(forgetPrefix({ a: { city: "Pune" }, b: { city: "Delhi" } }))); // Expected output: {"city":"Delhi"}

// Right: the path is built from the parent path and the key (same goodFlatten as the previous fix)
function goodFlatten2(obj, prefix = "") {
  const out = {};
  for (const key of Object.keys(obj)) {
    const v = obj[key];
    const path = prefix ? `${prefix}.${key}` : key;
    if (v !== null && typeof v === "object" && Object.keys(v).length) Object.assign(out, goodFlatten2(v, path));
    else out[path] = v;
  }
  return out;
}
console.log(JSON.stringify(goodFlatten2({ a: { city: "Pune" }, b: { city: "Delhi" } }))); // Expected output: {"a.city":"Pune","b.city":"Delhi"}
```

---

## 🧠 Tricky Interview Question
```javascript
// Basic flatten, repeated so this block runs alone
function flattenObject(obj, prefix = "") {
  const out = {};
  for (const key of Object.keys(obj)) {
    const path = prefix ? `${prefix}.${key}` : key;
    const value = obj[key];
    if (value !== null && typeof value === "object" && Object.keys(value).length > 0) Object.assign(out, flattenObject(value, path));
    else out[path] = value;
  }
  return out;
}

const data = { a: { b: 1 }, "a.b": 2 };
console.log(JSON.stringify(flattenObject(data)));  // ?

const arr = { list: [10, [20]] };
console.log(JSON.stringify(flattenObject(arr)));   // ?

console.log(JSON.stringify(flattenObject({ when: new Date(0), empty: {} }))); // ?
```
Answer:
```
{"a.b":2}                       ← both keys produce "a.b"; the later write wins, so the value is 2
{"list.0":10,"list.1.0":20}     ← array indexes become keys, and the nested array keeps its own indexes
{"when":"1970-01-01T00:00:00.000Z","empty":{}}  ← the Date is a leaf (JSON shows it as text), the empty object is kept as a value
```
The first line is a real pitfall: flattening can make two different paths collide, and the result depends on the order of keys. Mention this in an interview as a limitation, and suggest throwing an error or using a different separator when collisions matter.

---

## ⚫ Interview Questions + Answers

**Q1: Why is the path joined with a dot, and what breaks it?**
A1: A dot is the usual separator for paths, like `a.b.c`. It breaks when a key already contains a dot, such as `"a.b"`, because two different paths can then produce the same flat key. Use a separator that cannot appear in keys, or check for collisions.

**Q2: How are arrays handled, and why?**
A2: Arrays are objects with numeric keys, so `Object.keys` gives `"0"`, `"1"` and so on. The flat key becomes `items.0.sku`, which keeps the position of each element.

**Q3: Why must `null` be checked separately?**
A3: `typeof null` is `"object"`, so a plain `typeof` check treats it as a container. `Object.keys(null)` then throws, so `null` must be a leaf.

**Q4: How does the advanced version detect circular references?**
A4: It keeps a set of the objects on the current path. Entering an object that is already in the set means the object contains itself, so it throws. The set is cleared on the way out, so shared but non-circular references are still flattened.

**Q5: What is the time and space complexity?**
A5: O(n) time, where n is the number of keys and values, because each one is visited once. Space is O(n) for the result plus O(d) for the recursion path, where d is the maximum depth.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You export nested data to CSV, a spreadsheet, or a flat log index
- A config or environment system needs flat keys such as `DB_HOST`
- You need a simple diff or search over every field of a nested object

❌ Avoid when:
- You need to rebuild the original nested object later; use `unflatten` with a clear separator rule, or keep the nested form
- Keys can contain the separator, so paths would collide; choose a safer separator or store JSON
- The object is very large and only a few fields are needed; pick those fields directly

---

## 📊 Visual Diagram
```
Input                                      Output (flat)
{                                          {
  id: 9,                                     "id": 9,
  customer: {                                "customer.name": "Ravi",
    name: "Ravi",                            "customer.address.city": "Pune",
    address: { city: "Pune" }                "items.0.sku": "A1",
  },                                         "items.1.sku": "B2",
  items: [ {sku:"A1"}, {sku:"B2"} ]          "note": null
  note: null                               }
}

Path while walking:  "" -> "customer" -> "customer.address" -> "customer.address.city" (leaf)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Flatten | Turning nested data into one level | Nested data को एक level में लाना |
| Dotted key | A key made of path parts joined by dots | Dots से जुड़ी path वाली key |
| Leaf | A value that is not a container | ऐसी value जो container नहीं है |
| Path | The chain of keys from the root to a value | Root से value तक keys का रास्ता |
| Circular reference | An object that contains itself | ऐसा object जो खुद को ही contain करे |
| Separator | The character placed between path parts | Path के हिस्सों के बीच का चिह्न |

---

## ⚡ 3-Line Summary
English:
1. Flatten walks the object and joins each key path with dots, so every leaf gets one flat key.
2. Check for `null` and `Date` before treating a value as a container, and keep empty containers as values.
3. Track the current path to catch circular references, and watch out for key collisions.

Hindi:
1. Flatten object को walk करता है और हर key path को dots से जोड़ता है, ताकि हर leaf को एक flat key मिले।
2. किसी value को container मानने से पहले `null` और `Date` जाँचो, और खाली containers को value के रूप में रखो।
3. Circular reference पकड़ने के लिए current path याद रखो, और key collisions पर ध्यान दो।

---

## ➡️ Next Topic
**179. Group By in Array** — flattening turns nested data into flat keys; the next problem goes the other way around and groups a flat list of items by a chosen field.
