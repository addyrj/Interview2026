---

# Q268. Iterator Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Make a `Range(start, end, step)` class iterable so it works with `for...of`, spread and `Array.from`.

---

## 💡 Quick Concept (2 lines only)
An iterator gives sequential access to a collection without exposing its internals; JS uses `[Symbol.iterator]`.
हिंदी: Iterator collection के अंदर झांके बिना एक-एक करके items देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Implement [Symbol.iterator]
// Step 2: Return an object with next()
// Step 3: next() returns { value, done }

class Range {
  constructor(start, end, step = 1) {
    this.start = start;                          // first value
    this.end = end;                              // inclusive end
    this.step = step;                            // increment
  }

  [Symbol.iterator]() {
    let current = this.start;                    // private cursor per iteration
    const { end, step } = this;                  // capture config
    return {
      next() {
        if (current <= end) {                    // still in range?
          const value = current;                 // value to return
          current += step;                       // advance cursor
          return { value, done: false };         // yield value
        }
        return { value: undefined, done: true }; // finished
      },
    };
  }
}

// ============================================
// TEST CASES
// ============================================

const r = new Range(1, 5);                       // 1..5
console.log([...r]);                             // Expected: [ 1, 2, 3, 4, 5 ]
console.log(Array.from(new Range(0, 10, 5)));    // Expected: [ 0, 5, 10 ]
for (const n of new Range(1, 3)) console.log(n); // Expected: 1  2  3 (each on a new line)
console.log([...r]);                             // Expected: [ 1, 2, 3, 4, 5 ] (re-iterable)
```

---

## 🔍 Why This Works (3 lines max)
`for...of`, spread and destructuring call `[Symbol.iterator]()` and then `next()` until `done` is true. Each call creates a fresh cursor so the range can be reused.
हिंदी: for...of पीछे से Symbol.iterator और next() बार-बार call करता है।

---

## ⚡ Alternative Solution
```javascript
// Generator makes it a one-liner
class Range2 {
  constructor(a, b) { this.a = a; this.b = b; }          // bounds
  *[Symbol.iterator]() { for (let i = this.a; i <= this.b; i++) yield i; } // generator yields each
}
console.log([...new Range2(1, 3)]); // Expected: [ 1, 2, 3 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: keeping cursor on `this` → second loop starts at the end
// ✅ Correct: create the cursor inside [Symbol.iterator]() each time
```

---

## 🎯 Interview Tip (1 line)
Explain iterable (has Symbol.iterator) vs iterator (has next) and that generators implement both.

---

## 🔗 Related Questions
→ Q174 (Iterators) | Q169 (Generators) | Q253 (Generator examples)
