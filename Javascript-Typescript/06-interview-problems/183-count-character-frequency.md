# 183. Count Character Frequency
# हिंदी में: String में Character Frequency गिनना — हर अक्षर कितनी बार आया, यह जानना

---

## 🔵 Simple Definition (English)
Character frequency means counting how many times each character appears in a string. For `"banana"`, the answer is `b: 1`, `a: 3`, `n: 2`. The usual tool is an object or a Map, where each character is a key and its count is the value.

## 🔵 सरल परिभाषा (Hindi)
Character frequency का मतलब है किसी string में हर character कितनी बार आया, यह गिनना। `"banana"` के लिए जवाब है `b: 1`, `a: 3`, `n: 2`। इसके लिए आम तौर पर object या Map इस्तेमाल होता है, जिसमें character key होता है और उसकी गिनती value।

---

## 🔴 Problem it Solves
**Problem Statement:** Given a string, return a count of each character. Optionally ignore letter case or spaces, and optionally return the most frequent characters first. The solution must handle emoji and other Unicode characters correctly.

Frequency counting is the base of many real features: password strength checks (how many distinct characters?), spell checkers (which letters are common?), search autocomplete (rank by letter usage), and plagiarism detection (compare letter profiles). Doing it wrong in a simple way causes bugs with case and emoji.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** एक string दी हो, तो हर character की गिनती लौटाओ। Chahe to case या spaces ignore कर सकते हो, और चाहो तो सबसे ज़्यादा आने वाले characters पहले दिखाओ। Emoji और बाकी Unicode characters भी सही गिने जाने चाहिए।

Frequency counting कई असली features की base है: password strength check (कितने अलग characters हैं?), spell checker, search autocomplete में letter usage के हिसाब से ranking, और plagiarism detection। सीधे तरीके से गिनने पर case और emoji की वजह से bugs आते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Create an empty object or Map to hold the counts.
Step 2 → Loop over the string one character at a time (use `for...of`, not index loops).
Step 3 → For each character, read its current count, defaulting to 0 if missing.
Step 4 → Add 1 and store the new count.
Step 5 → After the loop, the object or Map holds every character with its count.
Step 6 → Optionally sort the entries by count, highest first.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Counts रखने के लिए एक खाली object या Map बनाओ।
Step 2 → String पर एक-एक character करके loop चलाओ (index वाला loop नहीं, `for...of` इस्तेमाल करो)।
Step 3 → हर character की मौजूदा गिनती पढ़ो; नहीं है तो 0 मानो।
Step 4 → उसमें 1 जोड़कर नई गिनती store करो।
Step 5 → Loop खत्म होने पर object या Map में हर character और उसकी गिनती होगी।
Step 6 → चाहो तो entries को गिनती के हिसाब से घटते क्रम में sort कर लो।

---

## 🟡 Real World Example
A password policy page on a bank or payments app counts distinct characters to reject passwords like `aaaaaaaa`. A search box on Flipkart can rank suggestions by letter overlap. A spell checker compares the letter profile of a typed word with dictionary words. All of them start with a frequency count.

Scenario: A user types the password `Aditya@2025`. The app counts characters and finds 10 distinct characters out of 12. It accepts the password because the variety is good. A password `aaaaaaaaaa` has only one distinct character and is rejected.

## 🟡 Real Example Hindi mein
किसी bank या payments app का password policy page distinct characters गिनता है, ताकि `aaaaaaaa` जैसे password reject हों। Flipkart का search box letter overlap से suggestions rank कर सकता है। Spell checker typed word की letter profile को dictionary words से मिलाता है। इन सबकी शुरुआत frequency count से होती है।

उदाहरण: User password `Aditya@2025` डालता है। App characters गिनता है और 12 में से 10 अलग characters पाता है, तो password accept होता है। `aaaaaaaaaa` में सिर्फ़ एक अलग character है, इसलिए वो reject होता है।

---

## 💻 Code Example — Basic
```javascript
// Basic frequency counter with a plain object
function charFrequency(str) {
  const freq = {};                           // empty object: key = character, value = count
  for (const ch of str) {                    // loop over characters (safe for emoji too)
    freq[ch] = (freq[ch] || 0) + 1;          // missing -> 0, then add 1
  }
  return freq;                               // the finished table of counts
}

console.log(charFrequency("aab"));
// Expected output: { a: 2, b: 1 }

console.log(JSON.stringify(charFrequency("banana")));
// Expected output: {"b":1,"a":3,"n":2}

console.log(JSON.stringify(charFrequency("")));
// Expected output: {}
```

## 💻 Code Example — Advanced
```javascript
// Advanced frequency counter: Map, options, sorted output, input validation
function frequencyAdvanced(str, { ignoreCase = false, ignoreSpaces = false } = {}) {
  // Guard: this function only works on strings
  if (typeof str !== "string") {
    throw new TypeError("frequencyAdvanced expects a string");
  }
  // Optional: treat "A" and "a" as the same character
  const text = ignoreCase ? str.toLowerCase() : str;

  const counts = new Map();                  // Map is safer than {} for arbitrary keys
  for (const ch of text) {                   // for...of walks code points (emoji stay whole)
    if (ignoreSpaces && /\s/.test(ch)) continue; // skip spaces, tabs, and newlines when asked
    counts.set(ch, (counts.get(ch) ?? 0) + 1); // ?? 0 gives 0 for a new character
  }

  // Turn the Map into [char, count] pairs and sort: count descending, then char ascending
  return [...counts.entries()].sort(
    (a, b) => b[1] - a[1] || a[0].localeCompare(b[0]) // a tie in count is broken alphabetically
  );
}

// Top-N helper: return only the n most frequent characters
function topN(str, n, options) {
  return frequencyAdvanced(str, options).slice(0, n); // slice keeps the first n pairs
}

console.log(JSON.stringify(frequencyAdvanced("Mississippi", { ignoreCase: true })));
// Expected output: [["i",4],["s",4],["p",2],["m",1]]

console.log(JSON.stringify(topN("hello world", 2, { ignoreSpaces: true })));
// Expected output: [["l",3],["o",2]]

// Unicode: an emoji is ONE character for for...of, even though .length says 2
console.log(JSON.stringify(frequencyAdvanced("🍕🍕a")));
// Expected output: [["🍕",2],["a",1]]

// Time:  O(n) — one pass over the string, Map operations are O(1) on average
// Space: O(k) — k is the number of distinct characters (not the string length)
```

### Edge Cases
```javascript
// Edge 1: empty string -> no entries
console.log(JSON.stringify(frequencyAdvanced(""))); // Expected output: []

// Edge 2: only spaces, with spaces ignored -> nothing left
console.log(JSON.stringify(frequencyAdvanced("   ", { ignoreSpaces: true }))); // Expected output: []

// Edge 3: case sensitivity: "A" and "a" are separate by default
console.log(JSON.stringify(frequencyAdvanced("Aa"))); // Expected output: [["A",1],["a",1]]

// Edge 4: a non-string input is rejected with a clear error
try {
  frequencyAdvanced(12345);
} catch (e) {
  console.log(e.message); // Expected output: frequencyAdvanced expects a string
}
```

---

## 🟠 Express.js Integration
A password-policy endpoint that counts distinct characters and returns a verdict. It validates the body type and length first, so very long input cannot slow the server.

```javascript
// Express.js: password policy check built on character frequency
const express = require("express");          // import Express
const app = express();                       // create the app
app.use(express.json());                     // parse JSON bodies into req.body

// Count how many distinct characters the string has, plus the top character
function analyze(str) {
  const counts = new Map();                  // character -> count
  for (const ch of str) {                    // safe Unicode walk
    counts.set(ch, (counts.get(ch) ?? 0) + 1); // add one occurrence
  }
  // Find the most common character by scanning the Map once
  let top = null;                            // will hold [char, count]
  for (const pair of counts) {               // each pair is [char, count]
    if (top === null || pair[1] > top[1]) top = pair; // keep the bigger count
  }
  return { distinct: counts.size, top: top ? { char: top[0], count: top[1] } : null };
}

// POST /api/password/analyze   body: { "password": "..." }
app.post("/api/password/analyze", (req, res) => {
  const { password } = req.body;             // read the password field
  // Validate type and length before doing any work
  if (typeof password !== "string" || password.length === 0 || password.length > 128) {
    return res.status(400).json({ error: "password must be 1 to 128 characters" }); // 400
  }
  const report = analyze(password);          // count the characters
  const acceptable = report.distinct >= 5;   // policy: at least 5 distinct characters
  res.json({ ...report, acceptable });       // 200 OK with the report and the verdict
});

// Start the server on PORT from the environment, or 3000
app.listen(process.env.PORT || 3000, () => {
  console.log("Password API running");       // printed when ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using an index loop, which breaks emoji into two halves
```javascript
// Wrong: str[i] gives UTF-16 code units, so one emoji becomes two broken characters
const wrong = {};
const pizza = "🍕";
for (let i = 0; i < pizza.length; i++) {
  wrong[pizza[i]] = (wrong[pizza[i]] || 0) + 1;
}
console.log(Object.keys(wrong).length);          // Expected output: 2 (two halves, not one character)

// Right: for...of walks whole code points
const right = {};
for (const ch of pizza) right[ch] = (right[ch] || 0) + 1;
console.log(Object.keys(right).length);          // Expected output: 1
```

❌ **Mistake 2:** Incrementing a missing key without a default
```javascript
// Wrong: undefined + 1 is NaN, so the count never becomes a number
const bad = {};
bad.a++;                                         // bad.a was undefined
console.log(bad.a);                              // Expected output: NaN

// Right: default to 0 before adding
const good = {};
good.a = (good.a || 0) + 1;                      // 0 + 1 = 1
console.log(good.a);                             // Expected output: 1
```

❌ **Mistake 3:** Forgetting that "A" and "a" are different characters
```javascript
// Wrong: case-sensitive count says A:1 and a:1 for "Aa"
console.log(JSON.stringify(frequencyAdvanced("Aa")));                  // Expected output: [["A",1],["a",1]]

// Right: normalise the case first when case should not matter
console.log(JSON.stringify(frequencyAdvanced("Aa", { ignoreCase: true }))); // Expected output: [["a",2]]
```

---

## 🧠 Tricky Interview Question
```javascript
const word = "🍕a";                          // one emoji and one letter

console.log(word.length);                    // ?
console.log([...word].length);               // ?

const f = {};
for (const ch of word) f[ch] = (f[ch] ?? 0) + 1;
console.log(Object.keys(f).length);          // ?
console.log(word.split("").length);          // ?
```
Answer:
```
3   ← .length counts UTF-16 code units; the emoji takes 2 (a surrogate pair), plus "a"
2   ← spread and for...of count code points: the emoji is 1, "a" is 1
2   ← so the frequency object has two keys
3   ← split("") also splits by code unit, giving two broken halves plus "a"
```
This is why `.length` and `split("")` are unsafe for counting real characters. Use `for...of` or `[...str]` when you care about whole characters.

---

## ⚫ Interview Questions + Answers

**Q1: What is the simplest way to count characters in a string?**
A1: Loop with `for...of` and keep an object: `freq[ch] = (freq[ch] || 0) + 1`. It is O(n) time and O(k) space, where k is the number of distinct characters.

**Q2: Why use a Map instead of an object for counting?**
A2: A Map does not convert keys to strings, does not inherit prototype names, and has a clean `size` property. An object is fine for single characters, but a Map is the safer default for arbitrary keys.

**Q3: What is the difference between `.length` and `[...str].length`?**
A3: `.length` counts UTF-16 code units. Emoji and some other symbols use two code units, so `.length` can be too large. Spreading the string walks whole code points, so `[...str].length` gives the number of visible characters.

**Q4: How do you find the most frequent character?**
A4: Count everything in one pass, then scan the entries once to keep the one with the highest count. Sorting works too, but it costs O(k log k); the scan is O(k).

**Q5: How do you check if two strings have the same letters with the same counts?**
A5: Build a frequency Map for each string and compare the two maps. Equal sizes and equal counts for every key mean an anagram. This is the same idea as the anagram topic, 184.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a profile of letters for search, spell check, or strength rules
- The input is a normal string, and you want O(n) time
- You need to compare two strings by their letter counts

❌ Avoid when:
- You need to count whole words; split the text into words first, then count words
- You need only "does this character appear?" and not the count; use `includes` or a Set
- The string is extremely large and you want streaming; process chunks and merge the counts

---

## 📊 Visual Diagram
```
input: "banana"
 index:  0   1   2   3   4   5
 char:   b   a   n   a   n   a

scan one character at a time, update the table:

 step  char   table after the step
  1     b     { b:1 }
  2     a     { b:1, a:1 }
  3     n     { b:1, a:1, n:1 }
  4     a     { b:1, a:2, n:1 }
  5     n     { b:1, a:2, n:2 }
  6     a     { b:1, a:3, n:2 }   <- final counts
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Frequency | How many times a character appears | Character कितनी बार आया |
| Code point | One Unicode character, even if it takes 2 code units | एक Unicode character |
| Code unit | 16-bit piece of a string; `.length` counts these | String की 16-bit इकाई |
| Distinct | Different from each other | अलग-अलग |
| Default value | Fallback used when a key is missing | Key न मिले तो इस्तेमाल होने वाली value |
| Top-N | The N items with the highest counts | सबसे ज़्यादा आने वाले N items |

---

## ⚡ 3-Line Summary
English:
1. Count characters with a Map or object in one pass using `for...of`.
2. Default missing counts to 0 with `?? 0` or `|| 0`, or you get NaN.
3. Use `[...str]` (not `.length` or `split("")`) so emoji count as one character.

Hindi:
1. एक pass में `for...of` से Map या object में characters गिनो।
2. Missing count को `?? 0` या `|| 0` से 0 मानो, वरना NaN आएगा।
3. Emoji को एक character गिनने के लिए `[...str]` इस्तेमाल करो, `.length` या `split("")` नहीं।

---

## ➡️ Next Topic
**184. Anagram Check** — the next problem uses exactly this frequency idea: two words are anagrams when their letter counts match.
