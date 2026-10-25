# 29. Strings — Methods
# हिंदी में: Strings के Methods — Text को खोजना, काटना, बदलना और format करना

---

## 🔵 Simple Definition (English)
A string is text in JavaScript. String methods let you search inside it (`includes`, `indexOf`), cut parts (`slice`), change it (`replace`, `toUpperCase`), split it (`split`) and pad it (`padStart`). Every method returns a new string; the original never changes.

## 🔵 सरल परिभाषा (Hindi)
JavaScript में string एक text है। String methods से उसमें खोज सकते हैं (`includes`, `indexOf`), हिस्से काट सकते हैं (`slice`), बदल सकते हैं (`replace`, `toUpperCase`), split (`split`) और pad (`padStart`) कर सकते हैं। हर method एक नई string लौटाता है; original बदलता नहीं।

---

## 🔴 Problem it Solves
Backend and frontend code constantly handles text: user input, CSV rows, URLs, phone numbers, messages and receipts. Without methods, you would loop over characters by hand. Without knowing the rules (immutability, code units, first-match `replace`), bugs appear in search, validation and formatting.

## 🔴 यह क्यों बना? (Hindi)
Backend और frontend लगातार text संभालते हैं: user input, CSV rows, URL, phone number, message और receipt। Methods न होते तो हर character को loop से हाथ से देखना पड़ता। Rules (immutable होना, code units, पहला match ही `replace` करना) न पता हों तो search, validation और formatting में bugs आते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Strings are immutable: any method returns a NEW string.
Step 2 → Search methods (`includes`, `indexOf`, `startsWith`) answer yes/no or give a position.
Step 3 → Extraction methods (`slice`, `substring`) take start and end positions.
Step 4 → Transform methods (`trim`, `toUpperCase`, `replace`, `replaceAll`) return changed text.
Step 5 → Layout methods (`split`, `join`, `padStart`, `repeat`) build or break text.

## 🟢 कैसे काम करता है? (Hindi)
चरण 1 → Strings immutable हैं: हर method एक NEW string लौटाता है।
चरण 2 → Search methods (`includes`, `indexOf`, `startsWith`) हाँ/ना या position बताते हैं।
चरण 3 → Extraction methods (`slice`, `substring`) start और end position लेते हैं।
चरण 4 → Transform methods (`trim`, `toUpperCase`, `replace`, `replaceAll`) बदला हुआ text देते हैं।
चरण 5 → Layout methods (`split`, `join`, `padStart`, `repeat`) text बनाते या तोड़ते हैं।

---

## 🟡 Real World Example
A restaurant search box: the user types " biryani ", the server must clean it, validate it, and make the match case-insensitive. Receipts also need padded columns.

```javascript
const raw = "  Biryani House  ";                 // what the user typed (with extra spaces)
const query = raw.trim().toLowerCase();         // "biryani house" — clean and normalised
const menuLine = "Chicken Biryani".padEnd(20, ".") + "₹250"; // receipt-style alignment
```

Zomato-style search, Swiggy item names and Paytm invoice lines all use these exact steps.

## 🟡 Real Example Hindi mein
Restaurant search box में user `"  Biryani House  "` लिखता है। Server पहले `trim()` करता है, फिर `toLowerCase()`, ताकि match case-insensitive हो। Receipt में `padEnd` से price एक column में आती है। Zomato, Swiggy और Paytm invoice ऐसे ही steps चलाते हैं।

---

## 💻 Code Example — Basic
```javascript
// Strings — Methods: basic examples
// Run: node 29-strings-methods.js

// 1. Length and indexing
const s = "Zomato";                  // a string literal
console.log(s.length);               // 6 — count of UTF-16 code units
console.log(s[0]);                   // Z — character at index 0
console.log(s.at(-1));               // o — negative index counts from the end

// 2. Searching
const msg = "Order placed for Biryani";
console.log(msg.includes("Biryani"));  // true — does the substring exist?
console.log(msg.indexOf("for"));       // 13 — first position, or -1 if missing
console.log(msg.startsWith("Order"));  // true
console.log(msg.endsWith("Chicken"));  // false

// 3. Extracting parts
console.log(s.slice(0, 3));          // Zom — start included, end excluded
console.log(s.slice(-3));            // ato — negative counts from the end
console.log(s.substring(1, 4));      // oma — like slice, but negatives become 0

// 4. Case and whitespace
console.log("  Hello  ".trim());     // "Hello" — spaces removed on both sides
console.log("  Hello  ".trimStart()); // "Hello  " — only the left side
console.log("Hi".toUpperCase());     // HI
console.log("Hi".toLowerCase());     // hi

// 5. Padding and repeat (useful for receipts and tables)
console.log("5".padStart(3, "0"));              // 005 — zero padding
console.log("Total".padEnd(10, ".") + "₹100");   // Total.....₹100
console.log("-".repeat(10));                     // ----------

// 6. Split and join
const csv = "pizza,burger,coke";     // comma-separated text
const items = csv.split(",");        // ["pizza", "burger", "coke"]
console.log(items.length);           // 3
console.log(items.join(" | "));      // pizza | burger | coke

// 7. replace changes the FIRST match; replaceAll changes ALL matches
const price = "₹1,000 + ₹200";
console.log(price.replace("₹", "Rs "));    // Rs 1,000 + ₹200 — only first
console.log(price.replaceAll("₹", "Rs ")); // Rs 1,000 + Rs 200 — all

// 8. Strings are immutable: methods return NEW strings
const original = "abc";
const upper = original.toUpperCase(); // a new string is created
console.log(original, upper);        // abc ABC — original unchanged
```

## 💻 Code Example — Advanced
```javascript
// Advanced: string utilities used in real backends — slugify, mask, template, emoji, validation

// 1. Slugify a restaurant name for a URL
function slugify(text) {
  return text
    .normalize("NFKD")                  // split accents: é becomes e + combining mark
    .replace(/[̀-ͯ]/g, "")    // remove the combining accent marks
    .toLowerCase()                      // lower-case everything
    .trim()                             // remove outer spaces
    .replace(/[^a-z0-9\s-]/g, "")       // drop anything that is not a letter, digit, space or dash
    .replace(/\s+/g, "-")               // collapse runs of spaces into one dash
    .replace(/-+/g, "-");               // collapse repeated dashes
}
console.log(slugify("  Café Paradise & Grill!  ")); // cafe-paradise-grill

// 2. Mask a phone number before logging it
function maskPhone(phone) {
  const digits = phone.replace(/\D/g, "");          // keep only digit characters
  // hide everything except the last 4 digits
  return digits.slice(0, -4).replace(/./g, "*") + digits.slice(-4);
}
console.log(maskPhone("+91 98765-43210"));           // ********3210

// 3. Template formatting with a placeholder map
function formatMessage(template, data) {
  // replace each {{key}} with data[key]; keep the placeholder if the key is unknown
  return template.replace(/\{\{(\w+)\}\}/g, (match, key) =>
    key in data ? String(data[key]) : match
  );
}
console.log(formatMessage("Hi {{name}}, order {{id}} is {{status}}", { name: "Riya", id: 1001 }));
// Hi Riya, order 1001 is {{status}}

// 4. Emoji: length counts code units, spread counts code points
const emoji = "🍕🍔";
console.log(emoji.length);           // 4 — each emoji uses 2 UTF-16 code units
console.log([...emoji].length);      // 2 — spread splits by code point

// 5. Validate and normalise user input (order code like ORD-1024)
function parseOrderCode(code) {
  if (typeof code !== "string") {    // reject non-strings early
    throw new TypeError("code must be a string");
  }
  const cleaned = code.trim().toUpperCase(); // normalise spaces and case
  if (!/^ORD-\d{4}$/.test(cleaned)) {        // exact format check
    throw new Error(`Invalid order code: ${code}`);
  }
  return cleaned;                    // safe, normalised value
}
console.log(parseOrderCode(" ord-1024 "));   // ORD-1024
try {
  parseOrderCode("abc");             // fails the format check
} catch (e) {
  console.log(e.message);            // Invalid order code: abc
}

// 6. Sorting names: default sort uses code units; localeCompare is human-friendly
const names = ["zebra", "apple", "Mango"];
console.log([...names].sort());      // [ 'Mango', 'apple', 'zebra' ] — uppercase first
console.log([...names].sort((a, b) => a.localeCompare(b))); // [ 'apple', 'Mango', 'zebra' ]
```

---

## 🟠 Express.js Integration
Express gives query strings as strings in `req.query`. Route handlers normalise them with string methods before using them in a search.

```javascript
const express = require("express");           // import Express
const app = express();                        // create the app

// Demo data (in real code this comes from a database)
const restaurants = [
  { id: 1, name: "Biryani House" },
  { id: 2, name: "Dosa Corner" },
];

app.get("/api/restaurants", (req, res) => {
  // req.query.q can be undefined, a string, or an array; String() makes it safe
  const q = String(req.query.q ?? "").trim().toLowerCase(); // clean the search text
  if (q.length < 2) {                         // avoid searching for one letter
    return res.status(400).json({ error: "Search needs 2+ characters" });
  }
  // includes() does a case-insensitive match because both sides are lower-cased
  const results = restaurants.filter(r => r.name.toLowerCase().includes(q));
  res.json({ query: q, results });            // send normalised query and matches
});

app.listen(3000);                             // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Changing a character in place
✅ Correct: Strings are immutable. Build a new string instead.

```javascript
// Wrong
const s = "hello";
s[0] = "J";                    // silently ignored (sloppy) or TypeError (strict)
console.log(s);                // hello

// Right
const fixed = "J" + s.slice(1); // build a new string
console.log(fixed);            // Jello
```

❌ Mistake 2: Expecting `replace` to change every match
✅ Correct: `replace` with a string changes only the first match. Use `replaceAll` or a regex with the `g` flag.

```javascript
// Wrong
console.log("a-b-c".replace("-", "/"));   // a/b-c — only one dash changed

// Right
console.log("a-b-c".replaceAll("-", "/")); // a/b/c
console.log("a-b-c".replace(/-/g, "/"));   // a/b/c
```

❌ Mistake 3: Splitting emoji or Hindi text with `split("")`
✅ Correct: `split("")` splits UTF-16 code units, which can break emoji. Use `[...text]` for code points.

```javascript
// Wrong
const broken = "🍕".split("");        // two broken halves of one emoji
console.log(broken.length);          // 2

// Right
const safe = [..."🍕"];              // splits by code point
console.log(safe.length);            // 1
```

---

## 🧠 Tricky Interview Question
```javascript
// Tricky: what will each console.log print? (non-strict script)
const s = "hello";
s[0] = "J";                                 // (1) assignment to a character
console.log(s);

console.log("a-b-c".replace("-", "+"));     // (2) first match only

console.log("🍕".length, [..."🍕"].length);  // (3) code units vs code points

console.log("abc".slice(-2), "abc".substring(-2)); // (4) negative arguments
```
Answer:
```
hello                ← (1) strings are immutable; the assignment is silently ignored
a+b-c                ← (2) only the first "-" is replaced
2 1                  ← (3) the pizza emoji is 2 UTF-16 code units, but 1 code point
bc abc               ← (4) slice(-2) takes the last 2; substring(-2) treats -2 as 0
```
Explanation: In a non-strict script, writing to a string index is ignored. In strict mode (`"use strict"`) the same line throws a TypeError. `replace` with a string pattern stops after the first match. The pizza emoji is outside the BMP, so JavaScript stores it as two code units, while spread (`[...]`) sees one code point. `slice` treats negative numbers as "from the end", but `substring` clamps negatives to 0.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `slice` and `substring`?
A1: Both take start and end (end excluded). `slice` supports negative indexes that count from the end. `substring` swaps the arguments if start is larger than end, and turns negative values into 0. Prefer `slice` for predictable behaviour.

Q2: Are strings mutable in JavaScript?
A2: No. Methods never change the original string. They return a new one, and assignment to an index is ignored in sloppy mode or throws in strict mode.

Q3: What is the difference between `replace` and `replaceAll`?
A3: `replace` with a string changes the first match only. `replaceAll` changes every match. With a regex, `replace` needs the `g` flag to replace all matches.

Q4: Why is `"🍕".length` equal to 2?
A4: `length` counts UTF-16 code units. Characters outside the Basic Multilingual Plane, such as most emoji, need two code units. Spread `[...str]` counts code points, which is closer to what users see.

Q5: How do you check whether a string contains a value without regex?
A5: Use `includes`: `"Biryani House".includes("Biryani")` returns `true`. It is case-sensitive, so lower-case both sides when you need a case-insensitive match.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cleaning user input with `trim`, `toLowerCase` and `normalize`
- Searching text with `includes` or `startsWith`
- Building receipts, tables or IDs with `padStart`, `padEnd` and `repeat`

❌ Avoid when:
- You need to parse complex formats (CSV with quotes, HTML); use a real parser
- You must handle user-visible characters (grapheme clusters); use `Intl.Segmenter`
- You build long strings in a loop with `+`; use an array and `join` for large sizes

---

## 📊 Visual Diagram
```
  s = "Zomato"
       index:  0  1  2  3  4  5
  char:        Z  o  m  a  t  o
       ◄───────── slice(0, 3) ─────►  "Zom"   (end 3 excluded)
                              ◄── slice(-3) ──► "ato"  (last 3)

  "a-b-c".replace("-", "+")     → "a+b-c"    (first only)
  "a-b-c".replaceAll("-", "+")  → "a+b+c"    (all)

  Original string is NEVER changed: every method returns a new one
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Immutable | Cannot be changed in place | बदला न जा सकने वाला |
| `slice` | Extract a part using start and end | Start-end से हिस्सा निकालना |
| `padStart` / `padEnd` | Fill text to a target length | Length तक pad करना |
| Code unit | 16-bit piece of a string | String का छोटा हिस्सा |
| Code point | One full Unicode character | एक पूरा Unicode character |
| `normalize` | Standard form for accented text | Accent वाले text का standard रूप |
| `localeCompare` | Locale-aware string comparison | Language के हिसाब से तुलना |

---

## ⚡ 3-Line Summary
**English:**
1. Strings are immutable; every method returns a new string, so save the result.
2. Use `includes`, `slice`, `trim`, `padStart` and `replaceAll` for most daily tasks.
3. Watch out for first-match `replace`, code units in emoji, and `sort()` order.

**Hindi:**
1. Strings immutable हैं; हर method नई string लौटाता है, इसलिए result को save करो।
2. ज़्यादातर काम `includes`, `slice`, `trim`, `padStart` और `replaceAll` से होते हैं।
3. `replace` पहला match ही बदलता है, emoji में code units की गिनती अलग है, और `sort()` का क्रम सावधानी से देखो।

---

## ➡️ Next Topic
**30. Math Object + Methods** — `Math.round`, `floor`, `max`, `random` और money calculations। String formatting के बाद numbers को सही तरीके से round और format करना अगला कदम है।
