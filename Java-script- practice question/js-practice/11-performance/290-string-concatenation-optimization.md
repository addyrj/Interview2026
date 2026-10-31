---

# Q290. String Concatenation Optimization
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a large string from 100,000 pieces. Compare `+=`, `Array.join` and template literals, and explain which to use.

---

## 💡 Quick Concept (2 lines only)
Strings are immutable, but modern engines optimize `+=` with ropes. `array.push` + `join` is still a safe, predictable choice for huge builds.
हिंदी: String immutable होती है, बहुत बड़े build के लिए array में push करके आखिर में join करना सुरक्षित है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Build with +=
// Step 2: Build with array + join
// Step 3: Verify identical output and time both

const N = 100000;                                  // number of pieces

function viaPlus() {
  let s = '';                                      // start empty
  for (let i = 0; i < N; i++) s += 'x';            // repeated concatenation
  return s;                                        // final string
}

function viaJoin() {
  const parts = [];                                // collect pieces
  for (let i = 0; i < N; i++) parts.push('x');     // O(1) push
  return parts.join('');                           // single allocation at the end
}

function viaRepeat() {
  return 'x'.repeat(N);                            // best when pattern is simple
}

function time(fn) {
  const t = performance.now();                     // start
  const r = fn();                                  // run
  return { r, ms: performance.now() - t };         // result + elapsed
}

// ============================================
// TEST CASES
// ============================================

const a = time(viaPlus), b = time(viaJoin), c = time(viaRepeat); // run all
console.log(a.r.length, b.r.length, c.r.length);   // Expected: 100000 100000 100000
console.log(a.r === b.r && b.r === c.r);           // Expected: true
console.log(`+= ${a.ms.toFixed(2)}ms, join ${b.ms.toFixed(2)}ms`); // Expected: varies by engine/machine
const name = 'Ada', n = 3;                         // template literal demo
console.log(`${name} has ${n} items`);             // Expected: Ada has 3 items
```

---

## 🔍 Why This Works (3 lines max)
`join` computes the final size once and allocates once, while naive `+=` could copy repeatedly in engines without rope optimization. V8 optimizes `+=` well, so measure before micro-optimizing.
हिंदी: join एक बार में final string बनाता है, पर आजकल V8 में += भी तेज़ है, इसलिए पहले measure करो।

---

## ⚡ Alternative Solution
```javascript
// Template literal for few pieces (clearest), array join for many
const rows = [1, 2, 3].map((n) => `row ${n}`).join('\n'); // map + join pattern
console.log(rows.split('\n').length);                     // Expected: 3
// Node: for huge output use streams/Buffer instead of one giant string
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: concatenating inside a loop to build HTML then assigning innerHTML each iteration
// ✅ Correct: build once (array.join), assign once
```

---

## 🎯 Interview Tip (1 line)
Say: "Strings are immutable; use join/template for readability, profile before optimizing — V8 uses ropes."

---

## 🔗 Related Questions
→ Q276 (Measure performance) | Q289 (Efficient arrays) | Q287 (Batch DOM updates)
