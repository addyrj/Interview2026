---

# Q199. Build Deep Diff Utility
# Category: Real World Problems
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Write `deepDiff(a, b)` that returns a list of changes between two objects/arrays: `{ path, type: 'added' | 'removed' | 'changed', from?, to? }`. Useful for audit logs and "what changed?" UIs.

```javascript
deepDiff({ a: 1, b: { c: 2 } }, { a: 1, b: { c: 3 }, d: 4 });
```

---

## 💡 Quick Concept (2 lines only)
Recurse over the union of keys; if both sides are objects go deeper, otherwise compare primitives and record added/removed/changed.
हिंदी: दोनों objects की keys पर recursion चलाओ — नया, हटा या बदला हुआ हर path record करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const isObj = (v) => v !== null && typeof v === 'object'; // Step 1: object or array

function deepDiff(a, b, path = '') {
  const changes = [];                            // Step 2: collected differences
  const keys = new Set([...Object.keys(a || {}), ...Object.keys(b || {})]); // union of keys

  for (const key of keys) {
    const p = path ? `${path}.${key}` : key;     // Step 3: build dotted path
    const inA = isObj(a) && key in a;            // key exists in old?
    const inB = isObj(b) && key in b;            // key exists in new?

    if (!inA) changes.push({ path: p, type: 'added', to: b[key] });       // only in new
    else if (!inB) changes.push({ path: p, type: 'removed', from: a[key] }); // only in old
    else if (isObj(a[key]) && isObj(b[key])) {
      changes.push(...deepDiff(a[key], b[key], p)); // Step 4: both objects -> go deeper
    } else if (!Object.is(a[key], b[key])) {
      changes.push({ path: p, type: 'changed', from: a[key], to: b[key] }); // Step 5: primitive differs
    }
  }
  return changes;                                // flat list of changes
}

// ============================================
// TEST CASES
// ============================================

const oldObj = { name: 'Adi', age: 24, address: { city: 'Delhi', pin: 110001 }, tags: ['js', 'react'] };
const newObj = { name: 'Adi', age: 25, address: { city: 'Pune' }, tags: ['js', 'node'], role: 'dev' };

console.log(deepDiff(oldObj, newObj));
// Expected (order):
// [
//   { path: 'age', type: 'changed', from: 24, to: 25 },
//   { path: 'address.city', type: 'changed', from: 'Delhi', to: 'Pune' },
//   { path: 'address.pin', type: 'removed', from: 110001 },
//   { path: 'tags.1', type: 'changed', from: 'react', to: 'node' },
//   { path: 'role', type: 'added', to: 'dev' }
// ]
console.log(deepDiff({ x: 1 }, { x: 1 }));       // Expected: []
console.log(deepDiff({ n: NaN }, { n: NaN }));   // Expected: [] (Object.is treats NaN equal)
```

---

## 🔍 Why This Works (3 lines max)
Taking the union of keys finds additions and removals; recursion handles any depth; `Object.is` compares primitives correctly (including `NaN`). Arrays work because their indices are keys.
हिंदी: Keys का union लेने से added/removed मिलते हैं, और recursion से गहरे बदलाव भी पकड़े जाते हैं।

---

## ⚡ Alternative Solution
```javascript
// Quick "did anything change?" check (order-sensitive, loses undefined/functions/Dates)
const changed = JSON.stringify(oldObj) !== JSON.stringify(newObj);
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: === on objects compares references, so equal-looking objects always "differ"
if (a.address !== b.address) changes.push('address changed');

// ✅ Correct: recurse into both objects and compare leaf values
```

---

## 🎯 Interview Tip (1 line)
Discuss cycles (use a WeakSet), Dates/Maps/Sets handling, and array diffing by index vs by id.

---

## 🔗 Related Questions
→ Q078 (deep equal) | Q071 (deep clone) | Q073 (flatten nested object) | Q200 (undo/redo)
