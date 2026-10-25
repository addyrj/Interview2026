# 166. Reverse a String
# हिंदी में: String को उलटना (Reverse a String)

---

## 🔵 Simple Definition (English)
Reverse a string means returning a new string whose characters are in the opposite order. `"hello"` becomes `"olleh"`. It looks trivial, but it is a classic interview warm-up that tests your understanding of string immutability, indexing, and Unicode (emoji) handling.

## 🔵 सरल परिभाषा (Hindi)
String को उलटने का मतलब है characters को उल्टे क्रम में रखकर एक नई string बनाना। `"hello"` से `"olleh"` बनता है। यह देखने में आसान लगता है, लेकिन यह एक classic interview सवाल है जो string immutability, indexing और Unicode (emoji) की समझ परखता है।

---

## 🔴 Problem it Solves
JavaScript strings are immutable, so you cannot change them in place. Many real features need text read backwards: palindrome checks, reading a file extension from the end (`"photo.jpg"`), or showing a reversed preview. The interview question checks whether you know that a naive index-based approach can break emoji and accented characters.

## 🔴 यह क्यों बना? (Hindi)
JavaScript में strings immutable होती हैं, यानी उन्हें in-place बदला नहीं जा सकता। कई असली features में text उल्टा पढ़ना पड़ता है: palindrome check, file extension को आखिर से पढ़ना (`"photo.jpg"`), या reversed preview दिखाना। Interview सवाल यह देखता है कि क्या तुम जानते हो कि naive index-based तरीका emoji और accented characters को तोड़ सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Convert the string into an indexable structure (an array of characters).
Step 2 → Reverse the order of the elements (built-in `reverse()` or a two-pointer swap).
Step 3 → Join the characters back into one new string.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → String को एक ऐसे structure में बदलो जिसमें हर character का index हो (array of characters)।
Step 2 → Elements का क्रम उलटो (built-in `reverse()` या two-pointer swap से)।
Step 3 → Characters को जोड़कर एक नई string बनाओ।

---

## 🟡 Real World Example
Imagine a file-upload service at a food-delivery company like Zomato that accepts restaurant menu scans. The validator needs the file extension, and the quickest way to get it is to reverse the file name, read up to the first dot, and reverse that small piece back: `"menu_scan_2024.pdf"` gives `"fdp.4202_nacs_unem"`, so the extension is `"pdf"`. Similarly, a support tool that shows only the last four digits of a masked code can reverse the string and take the first four characters.

## 🟡 Real Example Hindi mein
मान लो Razorpay की payment-link service एक slug और internal checksum string store करती है। एक background job uploaded file का extension उसके नाम के आखिर से पढ़ती है, जैसे `"menu_scan_2024.pdf"`, वह नाम को reverse करती है और शुरुआती कुछ characters लेती है, तो `fdp.` मिलता है। इसी तरह Swiggy का support tool card जैसे codes को mask करते समय string को reverse करके आखिरी चार अक्षर आसानी से निकालता है।

---

## 💻 Code Example — Basic
```javascript
// Basic: reverse a string with built-in array methods, plus a manual loop
// Run with: node 166-basic.js

const assert = require("node:assert/strict");   // strict assert: throws if values differ

// Method 1: split → reverse → join (most common interview answer)
function reverseBasic(str) {                    // function takes one string argument
  return str.split("").reverse().join("");      // split into chars, reverse array, join back
}

// Method 2: explicit loop (shows the logic clearly)
function reverseLoop(str) {                     // same goal, written manually
  let result = "";                              // start with an empty result string
  for (let i = str.length - 1; i >= 0; i--) {   // walk from the last index down to 0
    result += str[i];                           // append the current character
  }
  return result;                                // return the new reversed string
}

// Demo with a food-app style word
const word = "biryani";                         // sample input
console.log(reverseBasic(word));                // prints: inayrib
console.log(reverseLoop(word));                 // prints: inayrib

// Self-checks: if any assert fails, Node throws and the script stops
assert.equal(reverseBasic("hello"), "olleh");   // basic method on "hello"
assert.equal(reverseLoop("hello"), "olleh");    // loop method on "hello"
assert.equal(reverseBasic(""), "");             // empty string stays empty
assert.equal(reverseLoop("a"), "a");            // single char stays the same
console.log("basic checks passed");             // prints: basic checks passed
```
Expected output:
```
inayrib
inayrib
basic checks passed
```

## 💻 Code Example — Advanced
```javascript
// Advanced: Unicode-safe reversal using grapheme clusters
// Run with: node 166-advanced.js
// Time: O(n) to segment + O(n) swaps   Space: O(n) for the grapheme array

const assert = require("node:assert/strict");   // strict assertions for self-checks

function reverseUnicode(input) {                // grapheme-aware reverse
  if (typeof input !== "string") {              // guard: only strings are allowed
    throw new TypeError("reverseUnicode expects a string"); // clear error for callers
  }
  const segmenter = new Intl.Segmenter("en", { granularity: "grapheme" }); // grapheme splitter
  const graphemes = [...segmenter.segment(input)].map((s) => s.segment);  // user-visible chars
  let left = 0;                                 // left pointer starts at the first grapheme
  let right = graphemes.length - 1;             // right pointer starts at the last grapheme
  while (left < right) {                        // stop when the pointers meet or cross
    [graphemes[left], graphemes[right]] = [graphemes[right], graphemes[left]]; // swap ends
    left++;                                     // move left pointer forward
    right--;                                    // move right pointer backward
  }
  return graphemes.join("");                    // join the reversed clusters into a string
}

// Emoji stays intact (surrogate pair is one grapheme)
assert.equal(reverseUnicode("a😀b"), "b😀a");   // emoji kept whole

// Accent written as "e" + combining acute (U+0301) stays attached to its "e"
assert.equal(reverseUnicode("café"), "éfac"); // é moves as one unit

// Empty and single-character inputs
assert.equal(reverseUnicode(""), "");           // empty input
assert.equal(reverseUnicode("x"), "x");         // single input

// Flag combined as one grapheme (regional indicators "I" + "N" = 🇮🇳)
assert.equal(reverseUnicode("🇮🇳ok"), "ko🇮🇳"); // flag stays as one unit

console.log(reverseUnicode("a😀b"));            // prints: b😀a
console.log("advanced checks passed");          // prints: advanced checks passed
```
Expected output:
```
b😀a
advanced checks passed
```

---

## 🟠 Express.js Integration
In an Express app, reversal is usually a small text utility behind an endpoint. The route below validates the input type and size before calling the function, so bad input never reaches the logic. Install with `npm i express` before running.

```javascript
// Express route: POST /api/text/reverse with JSON body { "text": "..." }
const express = require("express");                 // import the Express framework
const app = express();                              // create the application
app.use(express.json());                            // parse JSON bodies into req.body

// Grapheme-aware reverse (same idea as the advanced example above)
function reverseUnicode(s) {                        // reverse text by user-visible characters
  const parts = [...new Intl.Segmenter().segment(s)].map((x) => x.segment); // split into graphemes
  return parts.reverse().join("");                  // reverse the list and join it
}

app.post("/api/text/reverse", (req, res) => {       // handle POST requests to this path
  const { text } = req.body ?? {};                  // read "text" field, default to empty object
  if (typeof text !== "string") {                   // validate the type first
    return res.status(400).json({ error: "text must be a string" }); // 400 Bad Request
  }
  if (text.length > 1000) {                         // limit the size to protect the server
    return res.status(413).json({ error: "text too long" }); // 413 Payload Too Large
  }
  return res.json({ reversed: reverseUnicode(text) }); // send the reversed text back as JSON
});

app.listen(3000, () => console.log("listening on 3000")); // start the server on port 3000
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `split("")` on emoji (breaks surrogate pairs)
✅ Correct: Use spread `[...str]` (code points) or `Intl.Segmenter` (graphemes).

```javascript
// Wrong: split("") works on UTF-16 code units, so the emoji is broken apart
const wrong = "a😀b".split("").reverse().join(""); // emoji halves get swapped
console.log(wrong.includes("😀"));                  // prints: false (emoji is destroyed)

// Right: spread iterates by code point, so the emoji stays intact
const right = [..."a😀b"].reverse().join("");       // emoji kept whole
console.log(right.includes("😀"));                  // prints: true
```

❌ Mistake 2: Calling `reverse()` directly on a string
✅ Correct: Strings have no `reverse` method. Convert to an array first.

```javascript
// Wrong: strings do not have reverse()
const s = "hello";                                  // a string
console.log(typeof s.reverse);                      // prints: undefined (method missing)
// s.reverse();                                     // would throw TypeError: s.reverse is not a function

// Right: split to an array, reverse, then join
console.log(s.split("").reverse().join(""));        // prints: olleh
```

❌ Mistake 3: Forgetting `join("")` (you get an array, not a string)
✅ Correct: `reverse()` returns an array. Always join it back.

```javascript
// Wrong: result is still an array
const arrResult = "abc".split("").reverse();        // ["c", "b", "a"]
console.log(typeof arrResult);                      // prints: object (array)

// Right: join turns it into a string
const strResult = "abc".split("").reverse().join(""); // "cba"
console.log(typeof strResult, strResult);           // prints: string cba
```

---

## 🧠 Tricky Interview Question
```javascript
// What will each line print?
let s = "abc";                       // a string
const r = s.split("").reverse();     // r is an array: ["c", "b", "a"]
s = s + r;                           // string + array: array is converted to text
console.log(s);                      // ?
console.log(s.length);               // ?
console.log(typeof r);               // ?
```
Answer:
```
abcc,b,a      ← "abc" + String(["c","b","a"]) = "abc" + "c,b,a"
8             ← "abcc,b,a" has 8 characters (3 + 5)
object        ← reverse() returns an array, not a string
```
Explanation: `reverse()` never returns a string. When `+` meets a string and an array, the array is converted with `String()`, which joins its elements with commas. So the result looks like a reversed string but is actually `"abc"` followed by `"c,b,a"`. The fix is `.reverse().join("")`.

---

## ⚫ Interview Questions + Answers

**Q1: What is the simplest way to reverse a string in JavaScript?**
A1: `str.split("").reverse().join("")`. It turns the string into an array of characters, reverses the array in place, and joins the characters back into one string. It runs in O(n) time and O(n) space.

**Q2: Why can `split("")` be wrong for interviews?**
A2: `split("")` splits by UTF-16 code units. Emoji and some other characters use two code units (a surrogate pair), so reversing them separately produces invalid text. Use `[...str]` or `Intl.Segmenter` when the input can contain emoji or accents.

**Q3: Is a string reversal in-place possible?**
A3: No. Strings are immutable, so any "in-place" change is impossible. You must build a new string. If you need in-place behaviour, work on an array of characters and join at the end.

**Q4: What is the time and space complexity?**
A4: Time is O(n) because every character is visited once. Space is O(n) because the array or the new string holds n characters. A two-pointer swap on an array still needs O(n) space because the input array itself is a copy.

**Q5: What is the difference between a code unit, a code point, and a grapheme?**
A5: A code unit is one 16-bit unit in a JavaScript string. A code point is one Unicode character, which may be one or two code units. A grapheme is what a user sees as one character, which may be several code points (for example `e` + combining accent). `split("")` uses code units, spread uses code points, and `Intl.Segmenter` uses graphemes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a quick reversed copy of plain ASCII text
- Input is known to contain only basic Latin characters
- Solving a warm-up or palindrome step in an interview

❌ Avoid when:
- Input can contain emoji, flags, or accented letters (use grapheme-aware code)
- You expect to modify a huge string repeatedly (build once, reuse the result)
- You need reversed bytes of binary data (use `Buffer.from(...).reverse()` instead)

---

## 📊 Visual Diagram
```
"hello"
   │  split("")
   ▼
['h', 'e', 'l', 'l', 'o']
   │  reverse()          two pointers meet in the middle
   ▼
['o', 'l', 'l', 'e', 'h']
   │  join("")
   ▼
"olleh"

Two-pointer swap on indexes 0..4:
  [h, e, l, l, o]   swap(0,4) → [o, e, l, l, h]
                    swap(1,3) → [o, l, l, e, h]
                    index 2 stays (pointers meet)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Immutable | String cannot be changed in place | बदला न जा सकने वाला |
| Code unit | One 16-bit unit of a JS string | एक 16-bit इकाई |
| Code point | One Unicode character | एक Unicode अक्षर |
| Grapheme | What a user sees as one character | उपयोगकर्ता को दिखने वाला एक अक्षर |
| Surrogate pair | Two code units forming one emoji | Emoji बनाने वाले दो code units |
| `split("")` | Splits string into code units | Code units में तोड़ना |
| `join("")` | Joins array items into a string | Array को string में जोड़ना |
| Two pointers | Two indexes moving toward each other | दो index जो बीच की ओर बढ़ते हैं |

---

## ⚡ 3-Line Summary
English:
1. `str.split("").reverse().join("")` reverses a plain string in O(n).
2. Strings are immutable, so you always build a new string.
3. Use `[...str]` or `Intl.Segmenter` when emoji or accents can appear.

Hindi:
1. `str.split("").reverse().join("")` plain string को O(n) में उलटता है।
2. Strings immutable हैं, इसलिए हमेशा नई string बनती है।
3. Emoji या accent हों तो `[...str]` या `Intl.Segmenter` इस्तेमाल करो।

---

## ➡️ Next Topic
**167. Check Palindrome** — अगला सवाल इसी reverse logic पर बनता है, पर यहाँ हम normalization (case और punctuation हटाना) और two-pointer approach सीखेंगे।
