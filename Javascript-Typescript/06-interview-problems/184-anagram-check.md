# 184. Anagram Check
# हिंदी में: Anagram Check — दो strings में एक जैसे अक्षर हैं या नहीं

---

## 🔵 Simple Definition (English)
Two strings are anagrams when they use exactly the same letters, with the same count of each letter, just in a different order. `"listen"` and `"silent"` are anagrams. The check ignores case and spaces, so `"Dormitory"` and `"dirty room"` are anagrams too.

## 🔵 सरल परिभाषा (Hindi)
दो strings anagram होती हैं जब उनमें वही अक्षर, उतनी ही बार, सिर्फ़ अलग क्रम में हों। `"listen"` और `"silent"` anagram हैं। Case और spaces को नज़रअंदाज़ किया जाता है, इसलिए `"Dormitory"` और `"dirty room"` भी anagram हैं।

---

## 🔴 Problem it Solves
**Problem Statement:** Given two strings `s1` and `s2`, return `true` if they are anagrams of each other and `false` otherwise. Ignore letter case and spaces.

Before this check, a simple `===` comparison fails for `"Listen"` vs `"silent"` because the letters are in a different order. Searching for words that mean the same letters (word games, spell-check suggestions, duplicate detection in a search index) needs a fast and correct test.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** दो strings `s1` और `s2` दी हों, तो `true` लौटाओ अगर वे आपस में anagram हैं, वरना `false`। Letter case और spaces को ignore करो।

पहले सिर्फ़ `===` से तुलना करने पर `"Listen"` और `"silent"` गलत निकलते थे, क्योंकि अक्षरों का क्रम अलग है। Word games, spell-check के सुझाव और search index में duplicate words पहचानने के लिए एक तेज़ और सही तरीका चाहिए था।

---

## 🟢 How it Works — Step by Step

Step 1 → Normalise both strings: lowercase them and remove spaces and punctuation.
Step 2 → If the lengths differ after cleaning, they cannot be anagrams. Return `false`.
Step 3 → Count how many times each letter appears in the first string.
Step 4 → Walk through the second string and use up one count per letter.
Step 5 → If a letter is missing or its count is already zero, return `false`.
Step 6 → If every letter is matched, return `true`.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → दोनों strings को normalise करो: lowercase करो और spaces व punctuation हटाओ।
Step 2 → Clean करने के बाद length अलग हो तो anagram नहीं हो सकते। `false` लौटाओ।
Step 3 → पहली string में हर अक्षर कितनी बार आया, यह गिनो।
Step 4 → दूसरी string पर चलो और हर अक्षर के लिए एक count खर्च करो।
Step 5 → अगर कोई अक्षर नहीं मिला या उसकी count पहले से zero है, तो `false` लौटाओ।
Step 6 → सारे अक्षर मिल गए, तो `true` लौटाओ।

---

## 🟡 Real World Example
Flipkart's search has a "did you mean" feature. When a user types a scrambled word, the system checks candidate words that use the same letters. Word-puzzle apps like Dream11-style quiz games and Wordle clones do the same kind of check to validate a player's word against a target.

Scenario: A Paytm quiz asks players to rearrange the letters of `"PAYTM"` into a brand name. A player types `"tmpaY"`. The game lowercases both words, removes nothing else, and confirms with an anagram check that the letters match before awarding points.

## 🟡 Real Example Hindi mein
Flipkart की search में "did you mean" सुविधा है। User गलत क्रम में शब्द लिखे, तो system ऐसे शब्द ढूँढता है जिनमें वही अक्षर हों। Word-puzzle games भी player का शब्द सही है या नहीं, यह इसी तरह की anagram check से तय करते हैं।

उदाहरण: Paytm quiz में player `"PAYTM"` के अक्षरों को दोबारा जोड़ता है और लिखता है `"tmpaY"`। Game दोनों को lowercase करता है और anagram check से पुष्टि करता है, फिर point देता है।

---

## 💻 Code Example — Basic
```javascript
// Basic idea: two anagrams become identical after sorting their letters
function isAnagramBasic(s1, s2) {
  // Normalise: lowercase and remove all whitespace so case and spaces do not matter
  const clean = (s) => s.toLowerCase().replace(/\s+/g, "");  // \s+ matches every space, tab, newline
  const a = clean(s1).split("").sort().join("");  // split into letters, sort them, join back into one string
  const b = clean(s2).split("").sort().join("");  // do the same for the second string
  return a === b;                                 // equal sorted letters means the strings are anagrams
}

console.log(isAnagramBasic("listen", "silent"));          // Expected output: true
console.log(isAnagramBasic("Dormitory", "dirty room"));   // Expected output: true
console.log(isAnagramBasic("hello", "world"));            // Expected output: false
```

## 💻 Code Example — Advanced
```javascript
// Advanced: count letters with a Map instead of sorting, so the work is linear
function isAnagram(s1, s2) {
  // Guard: reject non-string input early with a clear error
  if (typeof s1 !== "string" || typeof s2 !== "string") {
    throw new TypeError("isAnagram expects two strings");  // helpful message for the caller
  }

  // Keep only letters and vowel signs (matras); drop spaces and punctuation
  // [\s\p{P}] matches whitespace or any punctuation character; the u flag makes \p work
  const norm = (s) => [...s.toLowerCase()].filter((ch) => !/[\s\p{P}]/u.test(ch));

  const a = norm(s1);                             // array of characters for the first string
  const b = norm(s2);                             // array of characters for the second string
  if (a.length !== b.length) return false;        // different lengths can never be anagrams: quick exit

  const counts = new Map();                       // letter -> how many of it are still unmatched
  for (const ch of a) {                           // go through every letter of the first string
    counts.set(ch, (counts.get(ch) || 0) + 1);    // add one to the count (missing letters start at 0)
  }

  for (const ch of b) {                           // go through every letter of the second string
    const left = counts.get(ch);                  // how many copies of this letter are still available
    if (!left) return false;                      // letter missing or already used up: not an anagram
    counts.set(ch, left - 1);                     // use one copy of this letter
  }

  return true;                                    // every letter found its match: they are anagrams
}

console.log(isAnagram("Astronomer", "Moon starer"));    // Expected output: true
console.log(isAnagram("नमक", "कमन"));                    // Expected output: true
console.log(isAnagram("aab", "abb"));                   // Expected output: false

// Time:  O(n) — each character is visited a constant number of times
// Space: O(k) — k is the number of distinct characters in the strings (at most the alphabet size)
```

### Edge Cases
```javascript
// Self-contained copy of the advanced isAnagram so this block runs on its own
function isAnagram(s1, s2) {
  const norm = (s) => [...s.toLowerCase()].filter((ch) => !/[\s\p{P}]/u.test(ch)); // clean each string
  const a = norm(s1);                             // cleaned letters of the first string
  const b = norm(s2);                             // cleaned letters of the second string
  if (a.length !== b.length) return false;        // different lengths: quick exit
  const counts = new Map();                       // letter -> unmatched count
  for (const ch of a) counts.set(ch, (counts.get(ch) || 0) + 1); // count the first string
  for (const ch of b) {                           // use up letters from the second string
    const left = counts.get(ch);                  // remaining copies of this letter
    if (!left) return false;                      // missing or exhausted: not an anagram
    counts.set(ch, left - 1);                     // use one copy
  }
  return true;                                    // all letters matched
}

// Edge 1: two empty strings are anagrams of each other
console.log(isAnagram("", ""));                         // Expected output: true

// Edge 2: case and spaces are ignored
console.log(isAnagram("Astronomer", "Moon starer"));    // Expected output: true

// Edge 3: same unique letters but different counts is NOT an anagram
console.log(isAnagram("aab", "abb"));                   // Expected output: false

// Edge 4: Hindi text works because matras are kept
console.log(isAnagram("नमक", "कमन"));                    // Expected output: true
```

---

## 🟠 Express.js Integration
In a real API, an anagram check is often exposed as a small endpoint, for example a word-game backend that validates a player's answer. The route reads two query values, validates them, and returns JSON.

```javascript
// Express.js: an endpoint that checks whether two words are anagrams
const express = require("express");              // import the Express framework
const app = express();                           // create the application

// Same helper as the advanced example, kept small for the route
function isAnagram(s1, s2) {
  const norm = (s) => [...s.toLowerCase()].filter((ch) => !/[\s\p{P}]/u.test(ch)); // clean each word
  const a = norm(s1);                            // cleaned letters of the first word
  const b = norm(s2);                            // cleaned letters of the second word
  if (a.length !== b.length) return false;       // lengths differ: cannot match
  return a.slice().sort().join("") === b.slice().sort().join(""); // sorted letters must be equal
}

// GET /api/anagram?a=listen&b=silent
app.get("/api/anagram", (req, res) => {
  const { a, b } = req.query;                    // read the two query parameters
  if (typeof a !== "string" || typeof b !== "string" || !a || !b) {  // validate both are non-empty strings
    return res.status(400).json({ error: "query params a and b are required" }); // 400 Bad Request
  }
  if (a.length > 100 || b.length > 100) {        // limit input size to protect the server
    return res.status(413).json({ error: "words must be 100 characters or fewer" }); // 413 Payload Too Large
  }
  res.json({ a, b, anagram: isAnagram(a, b) });  // 200 OK with the result as JSON
});

// Start the server on PORT from the environment, or 3000 by default
app.listen(process.env.PORT || 3000, () => {
  console.log("Anagram API running");          // message printed once the server is ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Comparing two arrays of letters with `===`
✅ **Correct:** Arrays are compared by reference, so join them into strings first

```javascript
// Wrong: two different array objects are never === to each other
console.log([..."abc"].sort() === [..."cba"].sort());        // Expected output: false

// Right: join the sorted letters into a string and compare the strings
console.log([..."abc"].sort().join("") === [..."cba"].sort().join("")); // Expected output: true
```

❌ **Mistake 2:** Forgetting to normalise case
✅ **Correct:** Lowercase both strings before comparing

```javascript
// Wrong: "L" and "l" are different characters, so the check fails
console.log("Listen".split("").sort().join("") === "silent".split("").sort().join("")); // Expected output: false

// Right: lowercase first, then compare
console.log("Listen".toLowerCase().split("").sort().join("") === "silent".split("").sort().join("")); // Expected output: true
```

❌ **Mistake 3:** Checking only whether each letter exists (no counts)
✅ **Correct:** Count letters, because duplicates must match too

```javascript
// Wrong: includes() only asks "is this letter present?", so "aab" looks like "abb"
console.log("aab".split("").every((c) => "abb".includes(c)));  // Expected output: true (wrong answer)

// Right: count every letter, then check that all net counts end at zero
const counts = {};                                             // letter -> net count
for (const c of "aab") counts[c] = (counts[c] || 0) + 1;       // add the letters of "aab"
for (const c of "abb") counts[c] = (counts[c] || 0) - 1;       // subtract the letters of "abb"
console.log(Object.values(counts).every((n) => n === 0));      // Expected output: false
```

❌ **Mistake 4:** Using `\W` to strip punctuation, which also deletes Hindi letters
✅ **Correct:** Use a Unicode property escape such as `\p{P}` with the `u` flag

```javascript
// Wrong: \W matches every non-ASCII character, so all Devanagari letters are removed
console.log("नमक".replace(/\W/g, ""));                        // Expected output: (an empty string)

// Right: \p{P} removes punctuation only, and Devanagari letters survive
console.log("नमक".replace(/[\p{P}]/gu, ""));                   // Expected output: नमक
```

---

## 🧠 Tricky Interview Question
```javascript
const x = ["a", "b"];                            // first array
const y = ["b", "a"];                            // second array, same letters in another order
console.log(x.sort().join() === y.sort().join()); // ?
console.log(x === y);                            // ?
console.log([..."cat"].sort() == [..."act"].sort()); // ?
```
Answer: `true`, `false`, `false`.
Line 1 sorts both arrays, so each becomes `["a", "b"]` and their `join()` strings are both `"a,b"`, which makes the comparison `true`. Line 2 compares two different array objects by reference, so it is `false` even though the contents match. Line 3 is also a reference comparison (`==` on objects behaves like `===`), so it is `false` even though both arrays hold `a, c, t`. The lesson is to compare strings, not array objects.

---

## ⚫ Interview Questions + Answers

**Q1: What is the simplest correct way to check an anagram?**
A1: Lowercase both strings, sort their characters, join them, and compare the results with `===`. It is easy to write, but sorting costs O(n log n).

**Q2: Why is the counting approach better?**
A2: It runs in O(n) time because it visits each character once. The `Map` holds counts, so no sorting is needed.

**Q3: How do you handle spaces and punctuation?**
A3: Clean the input first with a regex or a filter. Use `\p{P}` with the `u` flag so you do not accidentally remove non-ASCII letters such as Hindi.

**Q4: Can two anagrams have different lengths?**
A4: No. Once spaces and punctuation are removed, anagrams must have the same number of characters, so a length check is a quick early exit.

**Q5: Why does `[..."abc"] === [..."cba"]` return false?**
A5: Each spread creates a new array object. `===` compares object identity, not contents, so you must compare the joined strings or each element.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need to compare words for word games, quizzes, or spell suggestions
- Strings are short to medium length (names, words, phrases)
- You want an exact check that handles duplicate letters correctly

❌ Avoid when:
- You need fuzzy matching or typo tolerance; use edit distance or a fuzzy-search library
- You are comparing whole documents for similarity; use hashing or shingling instead
- The input is huge and streamed; a counting approach still works but you may need a bounded-memory design

---

## 📊 Visual Diagram
```
s1 = "listen"                       s2 = "silent"
counts after s1:
  l:1  i:1  s:1  t:1  e:1  n:1

walk through s2 and subtract:
  s -> 1 left -> 0
  i -> 1 left -> 0
  l -> 1 left -> 0
  e -> 1 left -> 0
  n -> 1 left -> 0
  t -> 1 left -> 0

every letter matched  ->  true
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Anagram | Same letters with the same counts, in a different order | एक जैसे अक्षरों वाले, अलग क्रम के शब्द |
| Normalise | Clean input (case, spaces, punctuation) before comparing | तुलना से पहले input साफ़ करना |
| Frequency counter | A Map that stores how often each letter appears | हर अक्षर कितनी बार आया, इसका Map |
| Reference equality | `===` on objects compares identity, not contents | Object की पहचान की तुलना, सामग्री की नहीं |
| Unicode property escape | Regex like `\p{L}` or `\p{P}` that matches a Unicode class | Unicode वर्ग से मेल खाने वाला regex |
| Early exit | Returning before finishing the work when the answer is already known | जवाब पता चलते ही रुक जाना |

---

## ⚡ 3-Line Summary
English:
1. Two strings are anagrams when they have the same letters with the same counts.
2. Normalise the input (lowercase, no spaces or punctuation), then compare sorted letters or count them with a Map.
3. Compare strings, not arrays, and use `\p{...}` so non-English letters are not deleted.

Hindi:
1. Dono strings anagram हैं जब उनमें वही अक्षर उतनी ही बार हों।
2. Input को normalise करो (lowercase, बिना spaces और punctuation), फिर sorted अक्षर मिलाओ या Map से गिनो।
3. Arrays की नहीं, strings की तुलना करो, और `\p{...}` का इस्तेमाल करो ताकि हिंदी अक्षर न हटें।

---

## ➡️ Next Topic
**185. Implement EventEmitter** — once you can count and compare, the next problem builds a small publish-subscribe system with `on`, `once`, `off`, and `emit`, which is the base of Node's own `events` module.
