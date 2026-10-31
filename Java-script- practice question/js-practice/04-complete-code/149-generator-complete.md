---

# Q149. Complete Generator Function
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks to create a generator that yields numbers from `start` to `end`.

```javascript
function____ range(start, end) {           // generator syntax
  for (let i = start; i <= end; i++) {
    ____ i;                                // pause and give value
  }
}
console.log([...range(1, 5)]);
```

---

## 💡 Quick Concept (2 lines only)
A generator (`function*`) pauses at each `yield` and resumes on `next()`. It produces values lazily.
हिंदी: Generator `yield` पर रुकता है और `next()` पर आगे बढ़ता है — values एक-एक करके बनती हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function* range(start, end) {              // blank 1: the * makes a generator
  for (let i = start; i <= end; i++) {     // Step 1: loop through range
    yield i;                               // blank 2: pause and return i
  }
}

// ============================================
// TEST CASES
// ============================================

console.log([...range(1, 5)]);             // Expected: [ 1, 2, 3, 4, 5 ]

const g = range(1, 2);                     // manual stepping
console.log(g.next());                     // Expected: { value: 1, done: false }
console.log(g.next());                     // Expected: { value: 2, done: false }
console.log(g.next());                     // Expected: { value: undefined, done: true }
```

---

## 🔍 Why This Works (3 lines max)
Calling a generator returns an iterator without running the body. Each `next()` runs until the next `yield`; spread consumes it fully.
हिंदी: Generator call करने पर body तुरंत नहीं चलती, हर `next()` अगले `yield` तक चलती है।

---

## ⚡ Alternative Solution
```javascript
// Infinite generator + take
function* naturals() { let n = 1; while (true) yield n++; }
const out = [];
for (const n of naturals()) { if (n > 3) break; out.push(n); }
console.log(out); // [ 1, 2, 3 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: arrow functions cannot be generators
// const g = *() => {};   // SyntaxError
// ✅ Correct: function* name() {}
```

---

## 🎯 Interview Tip (1 line)
Say: "Generators give lazy, pausable iteration — useful for infinite sequences and custom iterators."

---

## 🔗 Related Questions
→ Q044 (generator output) | Q169 (explain generators) | Q174 (iterators) | Q253 (generator examples)
