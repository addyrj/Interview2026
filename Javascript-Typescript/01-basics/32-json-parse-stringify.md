# 32. JSON (parse, stringify)
# हिंदी में: JSON (parse, stringify) — Data को text में बदलना और वापस object बनाना

---

## 🔵 Simple Definition (English)
JSON (JavaScript Object Notation) is a text format for sending data between systems. `JSON.stringify(obj)` turns a JavaScript value into a JSON string, and `JSON.parse(text)` turns that string back into a JavaScript value.

## 🔵 सरल परिभाषा (Hindi)
JSON (JavaScript Object Notation) systems के बीच data भेजने का एक text format है। `JSON.stringify(obj)` JavaScript value को JSON string में बदलता है, और `JSON.parse(text)` उस string को वापस JavaScript value में बदलता है।

---

## 🔴 Problem it Solves
Two systems cannot share a JavaScript object directly. A browser, a Node server and a mobile app are separate programs with separate memory. They need one agreed text format to send data over HTTP, store it in a file, or put it in a queue. Before JSON, XML was heavy and hard to read; JSON is smaller and maps closely to JavaScript objects.

## 🔴 यह क्यों बना? (Hindi)
दो systems एक JavaScript object को सीधे share नहीं कर सकते। Browser, Node server और mobile app अलग programs हैं और उनकी memory भी अलग है। HTTP पर data भेजने, file में रखने या queue में डालने के लिए एक तय text format चाहिए। पहले XML भारी और पढ़ने में मुश्किल था; JSON छोटा है और JavaScript objects से सीधा मेल खाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `JSON.stringify(value)` walks the object and writes it as text (serialization).
Step 2 → Values JSON cannot represent are skipped (`undefined`, functions, symbols) or changed (`NaN` → `null`, `Date` → ISO string).
Step 3 → The text is sent over HTTP, saved to a file, or stored in a queue.
Step 4 → `JSON.parse(text)` reads the text and builds a new JavaScript object (deserialization).
Step 5 → Invalid text throws a `SyntaxError`, so always wrap `JSON.parse` in `try/catch` for untrusted input.

## 🟢 कैसे काम करता है? (Hindi)
चरण 1 → `JSON.stringify(value)` object को पढ़कर उसे text में लिखता है (serialization)।
चरण 2 → जो values JSON में नहीं आ सकतीं वे हट जाती हैं (`undefined`, functions, symbols) या बदल जाती हैं (`NaN` → `null`, `Date` → ISO string)।
चरण 3 → यह text HTTP से भेजा जाता है, file में save होता है, या queue में जाता है।
चरण 4 → `JSON.parse(text)` text को पढ़कर नया JavaScript object बनाता है (deserialization)।
चरण 5 → गलत text पर `SyntaxError` आता है, इसलिए untrusted input के लिए `JSON.parse` को `try/catch` में लिखो।

---

## 🟡 Real World Example
A Razorpay-style webhook sends a JSON body. Your server parses it, validates the fields, and stores the event. When your API responds, it sends JSON back to the Swiggy or Zomato app.

```javascript
// The request body arrives as text; the framework parses it for you
const body = '{"event":"payment.captured","amount":49900,"currency":"INR"}';
const event = JSON.parse(body);            // text -> object
console.log(event.event, event.amount);    // payment.captured 49900
const reply = JSON.stringify({ ok: true }); // object -> text for the response
```

Every REST API you will use, from Razorpay to Paytm to Flipkart, sends and receives JSON in exactly this way.

## 🟡 Real Example Hindi mein
Razorpay जैसे webhook में JSON body आती है। Server उसे `JSON.parse` से object बनाता है, fields validate करता है और event store करता है। Response भेजते समय `JSON.stringify` से object को वापस text बनाया जाता है। Razorpay, Paytm और Flipkart के REST APIs इसी तरह JSON भेजते और लेते हैं।

---

## 💻 Code Example — Basic
```javascript
// JSON parse & stringify — basic examples
// Run: node 32-json-parse-stringify.js

// 1. Object -> JSON string (for sending over the network or saving)
const order = { id: 1001, items: ["pizza", "coke"], total: 348, paid: true };
const text = JSON.stringify(order);       // serialize the object to text
console.log(text);                        // {"id":1001,"items":["pizza","coke"],"total":348,"paid":true}
console.log(typeof text);                 // string

// 2. Pretty print: third argument = indentation (2 spaces)
console.log(JSON.stringify(order, null, 2)); // multi-line, easy to read

// 3. JSON string -> object
const parsed = JSON.parse(text);          // deserialize text back to an object
console.log(parsed.items[0]);             // pizza
console.log(parsed.total + 2);            // 350 — total is a real number again

// 4. Values JSON drops or changes
const messy = {
  name: "Riya",                           // normal string, kept
  secret: undefined,                      // undefined properties are skipped
  greet() { return "hi"; },               // functions are skipped
  createdAt: new Date("2024-01-15T00:00:00Z"), // Date becomes an ISO string
  score: NaN,                             // NaN becomes null
};
console.log(JSON.stringify(messy));
// {"name":"Riya","createdAt":"2024-01-15T00:00:00.000Z","score":null}

// 5. Inside arrays, undefined and functions become null (positions are kept)
console.log(JSON.stringify([1, undefined, () => 2])); // [1,null,null]

// 6. Replacer function: return undefined to drop a key
const user = { name: "Aditya", password: "abc123", city: "Pune" };
const safe = JSON.stringify(user, (key, value) => (key === "password" ? undefined : value));
console.log(safe);                        // {"name":"Aditya","city":"Pune"}

// 7. Invalid JSON throws a SyntaxError — always wrap parse in try/catch
try {
  JSON.parse("{name: 'Riya'}");           // keys need double quotes; single quotes are invalid
} catch (err) {
  console.log(err.name);                  // SyntaxError
}
```

## 💻 Code Example — Advanced
```javascript
// Advanced: safe parsing, reviver for dates, circular-safe stringify, BigInt handling

// 1. Safe parse helper: returns a result object instead of throwing
function safeParse(text, fallback = null) {
  try {
    return { ok: true, data: JSON.parse(text) };         // success path
  } catch (err) {
    return { ok: false, data: fallback, error: err.message }; // failure path
  }
}
console.log(safeParse('{"id": 7}'));       // { ok: true, data: { id: 7 } }
console.log(safeParse("{bad json}").ok);   // false

// 2. Reviver: turn ISO date strings back into Date objects while parsing
const payload = '{"orderId":"o1","placedAt":"2024-01-15T10:00:00.000Z"}';
const revived = JSON.parse(payload, (key, value) => {
  // only convert the value stored under "placedAt"
  if (key === "placedAt" && typeof value === "string") {
    return new Date(value);               // string -> Date object
  }
  return value;                           // leave everything else unchanged
});
console.log(revived.placedAt instanceof Date); // true

// 3. Circular-safe stringify: plain JSON.stringify throws on cycles
function safeStringify(obj) {
  const seen = new WeakSet();              // remembers objects already visited
  return JSON.stringify(obj, (key, value) => {
    if (typeof value === "object" && value !== null) {
      if (seen.has(value)) return "[Circular]"; // repeated reference (cycle or shared)
      seen.add(value);                     // mark this object as visited
    }
    return value;                          // keep the value
  });
}
const driver = { name: "Ravi" };
const trip = { id: "t1", driver };
driver.currentTrip = trip;                 // creates a cycle: trip -> driver -> trip
console.log(safeStringify(trip));
// {"id":"t1","driver":{"name":"Ravi","currentTrip":"[Circular]"}}

// 4. BigInt cannot be stringified: convert it in a replacer
const ledger = { txnId: 9007199254740993n, amount: 500 }; // n suffix = BigInt
const ledgerText = JSON.stringify(ledger, (key, value) =>
  typeof value === "bigint" ? value.toString() : value // send big ids as strings
);
console.log(ledgerText);                   // {"txnId":"9007199254740993","amount":500}

// 5. The JSON copy trick and its limits
const original = { when: new Date("2024-01-15T00:00:00Z"), tags: ["a"], skip: undefined };
const copy = JSON.parse(JSON.stringify(original));
console.log(copy.when instanceof Date);    // false — it became a string
console.log("skip" in copy);               // false — undefined was dropped
const better = structuredClone(original);  // Node 17+: keeps Date objects
console.log(better.when instanceof Date);  // true

// 6. Validate the shape of parsed data before trusting it
function parseOrder(text) {
  const { ok, data, error } = safeParse(text); // destructure the result object
  if (!ok) throw new Error(`Bad JSON: ${error}`);
  if (typeof data.id !== "string" || !Array.isArray(data.items)) {
    throw new Error("Order must have string id and items array");
  }
  return data;                             // now safe to use
}
try {
  parseOrder('{"id":"x","items":"nope"}'); // items is not an array
} catch (e) {
  console.log(e.message);                  // Order must have string id and items array
}
```

---

## 🟠 Express.js Integration
`express.json()` is middleware that calls `JSON.parse` for you on incoming bodies. `res.json()` calls `JSON.stringify` before sending the response.

```javascript
const express = require("express");           // import Express
const app = express();                        // create the app

// express.json() parses JSON request bodies into req.body (it uses JSON.parse)
app.use(express.json({ limit: "100kb" }));    // reject bodies larger than 100 KB

app.post("/api/payments/webhook", (req, res) => {
  // req.body is already an object — do NOT call JSON.parse on it again
  const { event, payload } = req.body;        // destructure the fields we need
  res.json({ received: true, event });        // res.json calls JSON.stringify for you
});

// Error middleware: return a clean 400 when the client sends malformed JSON
app.use((err, req, res, next) => {
  if (err.type === "entity.parse.failed") {   // body-parser error type
    return res.status(400).json({ error: "Malformed JSON" });
  }
  next(err);                                  // let other errors continue
});

app.listen(3000);                             // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling `JSON.parse` on data that is already an object
✅ Correct: Check the type first, or let the framework parse it once.

```javascript
// Wrong
const body = { event: "captured" };        // Express already parsed this
JSON.parse(body);                           // SyntaxError: "[object Object]" is not valid JSON

// Right
const parsedBody = typeof body === "string" ? JSON.parse(body) : body;
```

❌ Mistake 2: Expecting Map, Set or Date to survive a JSON round trip
✅ Correct: Convert them before stringify, and rebuild them after parse.

```javascript
// Wrong
const cart = new Map([["pizza", 2]]);
console.log(JSON.stringify(cart));          // {} — Map has no own enumerable properties

// Right
const cartArr = JSON.stringify([...cart]);  // [["pizza",2]] — keep the entries
const rebuilt = new Map(JSON.parse(cartArr)); // Map { 'pizza' => 2 }
```

❌ Mistake 3: Using single quotes, trailing commas or comments in JSON
✅ Correct: JSON needs double-quoted keys and strings, no trailing commas, and no comments.

```javascript
// Wrong
JSON.parse("{'name': 'Riya',}");            // SyntaxError: single quotes and trailing comma

// Right
JSON.parse('{"name": "Riya"}');             // { name: 'Riya' }
```

---

## 🧠 Tricky Interview Question
```javascript
// Tricky: what will each console.log print?
const data = {
  a: undefined,                                  // (1) property
  b: () => 1,                                    // (2) function property
  c: NaN,                                        // (3) special number
  d: new Map([[1, 2]]),                          // (4) Map object
  e: [undefined, () => 2],                       // (5) array with undefined and a function
};
console.log(JSON.stringify(data));

console.log(JSON.stringify("hi"), JSON.stringify(undefined), JSON.stringify(null)); // (6)
console.log(JSON.parse("1e3") + 1);                                              // (7)
console.log(JSON.stringify({ toJSON() { return { x: 1 }; } }));                  // (8)
```
Answer:
```
{"c":null,"d":{},"e":[null,null]}   ← (1)(2) a and b are dropped; (3) NaN -> null; (4) Map -> {}; (5) both array items -> null
"hi" undefined null                 ← (6) "hi" keeps its quotes; undefined is not a string, so it prints as undefined
1001                                ← (7) "1e3" is valid JSON for 1000, then + 1
{"x":1}                             ← (8) toJSON() is called and its result is serialized
```
Explanation: JSON has no `undefined`, functions, symbols, `NaN`, `Infinity` or `Map`. Object properties with these values are dropped or converted, but array items keep their position, so they become `null`. `JSON.stringify(undefined)` returns the value `undefined`, not a string. `toJSON` is a hook that lets an object choose its own JSON form, which is how `Date` produces its ISO string.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `JSON.parse` and `JSON.stringify`?
A1: `stringify` converts a JavaScript value to a JSON string (serialization). `parse` converts a JSON string back to a JavaScript value (deserialization).

Q2: Which values are dropped or changed by `JSON.stringify`?
A2: Properties with `undefined`, functions and symbols are dropped. `NaN` and `Infinity` become `null`. `Date` becomes an ISO string through `toJSON`. `Map` and `Set` become `{}`. BigInt throws a TypeError.

Q3: What is a replacer and a reviver?
A3: A replacer is the second argument of `stringify`; it transforms or removes values while writing. A reviver is the second argument of `parse`; it transforms values while reading, for example turning strings into Date objects.

Q4: Why does `JSON.stringify` throw on circular references, and how do you handle them?
A4: A cycle would produce infinite output. The function throws a TypeError. Handle it with a replacer that tracks visited objects (a `WeakSet`), or avoid cycles in the data you send.

Q5: Is `JSON.parse(JSON.stringify(obj))` a good deep copy?
A5: Only for plain data. It loses Date objects, undefined, functions, Map and Set. Use `structuredClone` when you need a faithful deep copy in modern Node and browsers.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Sending data over HTTP (REST APIs, webhooks, responses)
- Saving plain configuration or state to a file or a cache
- Logging structured data as a single line

❌ Avoid when:
- The data includes Map, Set, BigInt or class instances that must keep their type; convert them first
- You parse untrusted input without `try/catch` and validation
- Storing very large binary data; use a binary format or a file store instead

---

## 📊 Visual Diagram
```
  JavaScript object                JSON text                   JavaScript object
  ─────────────────   stringify   ───────────   parse/network   ─────────────────
  { id: 1, ok: true }  ───────────►  '{"id":1,"ok":true}'  ─────►  { id: 1, ok: true }
                                          │
                              network / file / queue (text only)

  Dropped on stringify:  undefined, functions, symbols
  Changed on stringify:  NaN → null, Date → ISO string, Map/Set → {}
  Error:                 BigInt → TypeError, cycles → TypeError
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Serialization | Object to text | Object को text में बदलना |
| Deserialization | Text to object | Text से object बनाना |
| Replacer | Function that changes values during stringify | Stringify के समय value बदलने वाला function |
| Reviver | Function that changes values during parse | Parse के समय value बदलने वाला function |
| `toJSON` | Hook that defines an object's JSON form | JSON में कैसा दिखेगा, यह तय करने वाला hook |
| Circular reference | Object that refers back to itself | ख़ुद को वापस refer करने वाला object |
| SyntaxError | Error thrown for invalid JSON text | गलत JSON text पर आने वाली error |

---

## ⚡ 3-Line Summary
**English:**
1. `JSON.stringify` makes text from an object; `JSON.parse` makes an object from text.
2. Undefined, functions, Map and Set do not survive; NaN becomes null and Date becomes a string.
3. Wrap `JSON.parse` in `try/catch` for untrusted input, and never parse a body that is already an object.

**Hindi:**
1. `JSON.stringify` object से text बनाता है; `JSON.parse` text से object बनाता है।
2. Undefined, functions, Map और Set बचते नहीं; NaN `null` बनता है और Date string बनती है।
3. Untrusted input के लिए `JSON.parse` को `try/catch` में लिखो, और ऐसे body को parse मत करो जो पहले से object है।

---

## ➡️ Next Topic
**34. typeof + instanceof** — JSON parse के बाद value का type जाँचना सीखो। `JSON.parse` `null`, arrays और numbers लौटाता है, और उन्हें सही तरीके से पहचानना अगला कदम है।
