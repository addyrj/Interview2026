# 167. Check Palindrome
# हिंदी में: Palindrome जाँचना (Check Palindrome)

---

## 🔵 Simple Definition (English)
A palindrome is text that reads the same forwards and backwards. "racecar" is a palindrome. For interviews, we also ignore case, spaces, and punctuation, so "A man, a plan, a canal: Panama" counts as a palindrome too.

## 🔵 सरल परिभाषा (Hindi)
Palindrome वह text है जो आगे से और पीछे से एक जैसा पढ़ा जाए। "racecar" एक palindrome है। Interview में हम case, spaces और punctuation को नज़रअंदाज़ करते हैं, इसलिए "A man, a plan, a canal: Panama" भी palindrome माना जाता है।

---

## 🔴 Problem it Solves
Users type text with mixed case, commas, and spaces, but the logic should only care about the meaningful letters and digits. Without a clear rule, the same input can be judged differently by different parts of the system. This problem teaches normalization (clean the input first) and the two-pointer technique (compare from both ends without building extra copies).

## 🔴 यह क्यों बना? (Hindi)
Users mixed case, commas और spaces के साथ text लिखते हैं, पर logic को सिर्फ़ असली letters और digits से मतलब होना चाहिए। साफ़ नियम न हो तो एक ही input को system के अलग हिस्से अलग तरह से judge कर सकते हैं। यह सवाल normalization (पहले input साफ़ करना) और two-pointer technique (दोनों सिरों से तुलना) सिखाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Normalize: lowercase the text and remove everything that is not a letter or digit.
Step 2 → Compare: check whether the cleaned text equals its reverse (basic), or walk two pointers from both ends (advanced).
Step 3 → Return `true` if every pair matches, otherwise `false`.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Normalize करो: text को lowercase करो और हर वो character हटाओ जो letter या digit नहीं है।
Step 2 → Compare करो: साफ़ text की उसकी reverse copy से तुलना करो (basic), या दोनों सिरों से two pointers चलाओ (advanced)।
Step 3 → अगर हर जोड़ी match हो तो `true`, वरना `false` लौटाओ।

---

## 🟡 Real World Example
Imagine Amazon India's gift-card team running a fun promo where customers enter vanity coupon codes like "Race car" or "NOON". The validator must ignore case and spaces, so "Race car" should be accepted as a palindrome. A similar rule appears in Paytm's name-matching checks, where the system compares a normalized name with a stored name after removing spaces and punctuation.

## 🟡 Real Example Hindi mein
मान लो Amazon India की gift-card team एक मज़ेदार promo चलाती है, जहाँ customers "Race car" या "NOON" जैसे coupon codes डालते हैं। Validator को case और spaces नज़रअंदाज़ करने होंगे, इसलिए "Race car" को palindrome माना जाना चाहिए। Paytm के name-matching checks में भी ऐसा ही normalization होता है, जहाँ spaces और punctuation हटाकर नाम मिलाए जाते हैं।

---

## 💻 Code Example — Basic
```javascript
// Basic: normalize the text, then compare it with its reversed copy
// Run with: node 167-basic.js

const assert = require("node:assert/strict");   // strict assertions for self-checks

// Step 1: keep only lowercase letters and digits
function normalize(input) {                     // accepts a string or a number
  return String(input)                          // convert input to text (12321 → "12321")
    .toLowerCase()                              // "Race" → "race"
    .replace(/[^a-z0-9]/g, "");                 // delete every char that is not a-z or 0-9
}

// Step 2: compare the cleaned text with its reverse
function isPalindromeBasic(input) {             // main function
  const clean = normalize(input);               // cleaned version of the input
  const reversed = clean.split("").reverse().join(""); // reversed copy of the cleaned text
  return clean === reversed;                    // true when both read the same
}

// Examples
console.log(isPalindromeBasic("A man, a plan, a canal: Panama")); // prints: true
console.log(isPalindromeBasic("hello"));        // prints: false
console.log(isPalindromeBasic(12321));          // prints: true (number is converted to text)

// Self-checks
assert.equal(isPalindromeBasic("racecar"), true);     // simple palindrome
assert.equal(isPalindromeBasic("Was it a car or a cat I saw?"), true); // with punctuation
assert.equal(isPalindromeBasic(""), true);            // empty text is a palindrome
assert.equal(isPalindromeBasic("ab"), false);         // two different chars
console.log("basic checks passed");                   // prints: basic checks passed
```
Expected output:
```
true
false
true
basic checks passed
```

## 💻 Code Example — Advanced
```javascript
// Advanced: two pointers from both ends, skipping non-letters, no reversed copy
// Run with: node 167-advanced.js
// Time: O(n)   Space: O(n) for the lowercase copy (O(1) extra if you lowercase per character)

const assert = require("node:assert/strict");   // strict assertions

// Keep letters and digits from ANY script (Hindi, Tamil, Latin, etc.)
const isKeepable = (ch) => /[\p{L}\p{N}]/u.test(ch); // \p{L} = letter, \p{N} = number, u = Unicode mode

function isPalindromeTwoPointer(input) {        // main function
  if (typeof input !== "string" && typeof input !== "number") { // validate input type
    throw new TypeError("isPalindromeTwoPointer expects a string or number"); // clear error
  }
  const s = String(input).toLowerCase();        // one lowercase copy of the text
  let left = 0;                                 // left pointer starts at the first char
  let right = s.length - 1;                     // right pointer starts at the last char

  while (left < right) {                        // continue until the pointers meet
    if (!isKeepable(s[left])) {                 // left char is punctuation or space
      left++;                                   // skip it by moving the left pointer
      continue;                                 // go to the next loop iteration
    }
    if (!isKeepable(s[right])) {                // right char is punctuation or space
      right--;                                  // skip it by moving the right pointer
      continue;                                 // go to the next loop iteration
    }
    if (s[left] !== s[right]) {                 // two meaningful chars do not match
      return false;                             // not a palindrome, stop early
    }
    left++;                                     // matched: move left pointer inward
    right--;                                    // matched: move right pointer inward
  }
  return true;                                  // every pair matched
}

// Examples and self-checks
assert.equal(isPalindromeTwoPointer("A man, a plan, a canal: Panama"), true); // classic phrase
assert.equal(isPalindromeTwoPointer("No 'x' in Nixon"), true);                // punctuation inside
assert.equal(isPalindromeTwoPointer("नमन"), true);                            // Hindi word works too
assert.equal(isPalindromeTwoPointer("कमल"), false);                           // Hindi, not a palindrome
assert.equal(isPalindromeTwoPointer(" "), true);                              // only spaces → empty
assert.equal(isPalindromeTwoPointer(12321), true);                            // number input
assert.throws(() => isPalindromeTwoPointer(null), TypeError);                 // bad type rejected

console.log(isPalindromeTwoPointer("No 'x' in Nixon")); // prints: true
console.log("advanced checks passed");                   // prints: advanced checks passed
```
Expected output:
```
true
advanced checks passed
```

---

## 🟠 Express.js Integration
Palindrome checks are usually a validation helper behind an API. The route below validates the body, limits the size, and returns a small JSON answer. Install with `npm i express` before running.

```javascript
// Express route: POST /api/palindrome with JSON body { "text": "..." }
const express = require("express");                 // import Express
const app = express();                              // create the application
app.use(express.json());                            // parse JSON request bodies

// Two-pointer check (same logic as the advanced example, short form)
function isPalindrome(input) {                      // returns true or false
  const s = String(input).toLowerCase();            // lowercase copy of the text
  let l = 0, r = s.length - 1;                      // two pointers at both ends
  const ok = (c) => /[\p{L}\p{N}]/u.test(c);        // keep letters and digits only
  while (l < r) {                                   // loop until pointers meet
    if (!ok(s[l])) { l++; continue; }               // skip non-letter on the left
    if (!ok(s[r])) { r--; continue; }               // skip non-letter on the right
    if (s[l] !== s[r]) return false;                // mismatch → not a palindrome
    l++; r--;                                       // move both pointers inward
  }
  return true;                                      // all pairs matched
}

app.post("/api/palindrome", (req, res) => {         // handle POST requests
  const { text } = req.body ?? {};                  // read the "text" field
  if (typeof text !== "string" && typeof text !== "number") { // validate type
    return res.status(400).json({ error: "text must be a string or number" }); // 400
  }
  if (String(text).length > 500) {                  // guard against very long input
    return res.status(413).json({ error: "text too long" }); // 413 Payload Too Large
  }
  return res.json({ text, isPalindrome: isPalindrome(text) }); // respond with the result
});

app.listen(3002, () => console.log("palindrome API on 3002")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Comparing without lowercasing or cleaning the text
✅ Correct: Normalize first, then compare.

```javascript
// Wrong: "Racecar" vs "racecaR" differ only by case, so this says false
const word = "Racecar";                             // mixed-case input
console.log(word === word.split("").reverse().join("")); // prints: false (wrong answer)

// Right: normalize with toLowerCase() before comparing
const clean = word.toLowerCase();                   // "racecar"
console.log(clean === clean.split("").reverse().join("")); // prints: true
```

❌ Mistake 2: Calling string methods on a number
✅ Correct: Convert numbers to strings with `String()` first.

```javascript
// Wrong: numbers do not have split()
const n = 12321;                                    // a number, not a string
try {
  n.split("");                                      // throws because split is not a method of numbers
} catch (e) {
  console.log(e.name);                              // prints: TypeError
}

// Right: convert first
console.log(String(n).split("").reverse().join("") === String(n)); // prints: true
```

❌ Mistake 3: ASCII-only regex drops Hindi letters, so every Hindi word looks like a palindrome
✅ Correct: Use the Unicode property `\p{L}` with the `u` flag.

```javascript
// Wrong: [^a-z0-9] deletes all Devanagari letters, leaving an empty string
const wrongClean = "कमल".replace(/[^a-z0-9]/g, "");  // ""
console.log(wrongClean === "");                      // prints: true (wrong: "कमल" is not a palindrome)

// Right: keep every letter, from any script
const rightClean = "कमल".replace(/[^\p{L}\p{N}]/gu, ""); // "कमल" unchanged
console.log(rightClean === "कमल");                   // prints: true (correct text kept)
console.log(rightClean === [...rightClean].reverse().join("")); // prints: false (correctly not a palindrome)
```

---

## 🧠 Tricky Interview Question
```javascript
// What will each line print?
const word = "stop";                               // a string
const chars = word.split("");                       // ["s", "t", "o", "p"]
const back = chars.reverse();                       // reverse() mutates chars AND returns it
console.log(back === chars);                        // ?
console.log(word.split("").reverse().join("") === "pots"); // ?
console.log(word === "stop");                       // ?
console.log(word.split("").reverse().join("") === word);  // ?
```
Answer:
```
true     ← reverse() changed the array in place and returned the same object
true     ← "stop" reversed by join is "pots"
true     ← strings are immutable, so word is still "stop"
false    ← "pots" is not equal to "stop", so "stop" is not a palindrome
```
Explanation: `Array.prototype.reverse` mutates the array and returns a reference to it, so `back === chars` is `true`. Strings never change, which is why `word` is still `"stop"`. The palindrome test compares the reversed text with the original, and they differ.

---

## ⚫ Interview Questions + Answers

**Q1: What is a palindrome in an interview context?**
A1: Text that reads the same forwards and backwards after normalization. Normalization usually means lowercase and removing non-alphanumeric characters, so "Race car" is a palindrome.

**Q2: What is the two-pointer technique and why is it useful here?**
A2: Put one pointer at the start and one at the end, compare them, and move both inward. It needs no reversed copy, stops at the first mismatch, and runs in O(n) time.

**Q3: What is the time and space complexity of the basic version?**
A3: Time is O(n) for the cleaning and the reverse. Space is O(n) because the cleaned string and its reversed array are both new copies of the input.

**Q4: How do you handle non-English letters?**
A4: Use a Unicode-aware regex such as `/[\p{L}\p{N}]/u`. An ASCII-only pattern like `[^a-z0-9]` removes Hindi, Tamil, or Chinese letters and gives wrong answers.

**Q5: What edge cases should you mention?**
A5: Empty string (palindrome), single character (palindrome), only punctuation (empty after cleaning, so palindrome), numbers (convert with `String()`), and null or objects (throw a clear error).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Validating short user input such as coupon codes or usernames
- You need a simple, readable check and the input is small
- The two-pointer version is needed for large text with little extra memory

❌ Avoid when:
- You need to match sequences inside a longer text (use a substring or regex search instead)
- Input is binary or byte data (compare bytes directly)
- Locale-specific sorting or case rules matter (use `Intl.Collator` for comparison rules)

---

## 📊 Visual Diagram
```
Input: "A man, a plan"

Step 1 normalize:  "amanaplan"

Step 2 two pointers:
  index:  0 1 2 3 4 5 6 7 8
  char:   a m a n a p l a n
          L →                 ← R
          a == n ? NO → false (for the full phrase)

Two-pointer walk on "racecar":
  r a c e c a r
  L →       ← R   r==r  ✓
    L →   ← R     a==a  ✓
      L → ← R     c==c  ✓
      pointers meet → true
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Palindrome | Reads same forwards and backwards | आगे-पीछे एक जैसा पढ़ा जाने वाला |
| Normalization | Cleaning text before comparison | तुलना से पहले text साफ़ करना |
| Two pointers | Two indexes moving inward | अंदर की ओर बढ़ने वाले दो index |
| Unicode property | Regex class such as `\p{L}` | Unicode के लिए regex वर्ग |
| `String()` | Converts any value to text | किसी भी value को text बनाना |
| Early exit | Stop as soon as the answer is known | उत्तर पता चलते ही रुक जाना |

---

## ⚡ 3-Line Summary
English:
1. Normalize first: lowercase and keep only letters and digits.
2. Basic: compare the cleaned text with its reverse; advanced: two pointers from both ends in O(n).
3. Use `\p{L}` with the `u` flag so Hindi and other scripts are handled correctly.

Hindi:
1. पहले normalize करो: lowercase करो और सिर्फ़ letters और digits रखो।
2. Basic में cleaned text को उसकी reverse से मिलाओ; advanced में दोनों सिरों से two pointers O(n) में चलाओ।
3. Hindi और दूसरी scripts के लिए `\p{L}` और `u` flag इस्तेमाल करो।

---

## ➡️ Next Topic
**168. Find Duplicate in Array** — अगला सवाल array में repeated values ढूँढना सिखाता है, जहाँ `Set` और `Map` का सही चुनाव complexity बदल देता है।
