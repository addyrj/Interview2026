---

# Q069. Get Unique Values
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `uniqueBy(arr, keyFn)` that returns unique items based on a key (e.g. unique objects by `id`), keeping the first occurrence. It should also work for primitives with no key function.

```javascript
uniqueBy([{ id: 1 }, { id: 2 }, { id: 1 }], (o) => o.id); // [{ id: 1 }, { id: 2 }]
```

---

## 💡 Quick Concept (2 lines only)
Track keys in a Set; keep an item only if its key has not been seen yet.
हिंदी: हर item की key Set में देखो — पहले से है तो छोड़ दो, नहीं है तो रख लो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: default keyFn is identity (works for primitives)
// Step 2: keep a Set of keys already used
// Step 3: filter items whose key is new

function uniqueBy(arr, keyFn = (x) => x) {
  const seen = new Set();               // keys already kept
  return arr.filter((item) => {
    const key = keyFn(item);            // compute identity key
    if (seen.has(key)) return false;    // duplicate -> drop
    seen.add(key);                      // first time -> remember
    return true;                        // keep this item
  });
}

// ============================================
// TEST CASES
// ============================================

console.log(uniqueBy([1, 2, 2, 3, 1]));                                // Expected: [ 1, 2, 3 ]
console.log(uniqueBy([{ id: 1 }, { id: 2 }, { id: 1 }], (o) => o.id)); // Expected: [ { id: 1 }, { id: 2 } ]
console.log(uniqueBy(['a', 'A', 'b'], (s) => s.toLowerCase()));        // Expected: [ 'a', 'b' ]
console.log(uniqueBy([]));                                             // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
The key function defines what "same" means, and the Set remembers keys in O(1). The first occurrence wins because later ones find the key already present.
हिंदी: key function तय करता है कि "same" क्या है, और Set दोहराव पकड़ लेता है।

---

## ⚡ Alternative Solution
```javascript
// Map keeps the LAST occurrence per key
const uniqueLast = (arr, fn) => [...new Map(arr.map((x) => [fn(x), x])).values()]; // later items overwrite earlier
console.log(uniqueLast([{ id: 1, v: 'a' }, { id: 1, v: 'b' }], (o) => o.id)); // Expected: [ { id: 1, v: 'b' } ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: Set on objects compares references
console.log([...new Set([{ id: 1 }, { id: 1 }])].length); // 2
// ✅ Correct: dedupe by key
console.log(uniqueBy([{ id: 1 }, { id: 1 }], (o) => o.id).length); // 1
```

---

## 🎯 Interview Tip (1 line)
Clarify "first or last wins" and show a key function for objects, since Set alone compares references.

---

## 🔗 Related Questions
→ Q055 (remove duplicates) | Q067 (find duplicates) | Q064 (group by)
