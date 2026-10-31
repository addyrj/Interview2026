---

# Q064. Group Array by Property
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `groupBy(arr, key)` that groups an array of objects by the value of a property (or a callback), returning an object of arrays.

```javascript
groupBy([{ n: 'A', t: 'x' }, { n: 'B', t: 'y' }, { n: 'C', t: 'x' }], 't');
// { x: [A, C], y: [B] }
```

---

## 💡 Quick Concept (2 lines only)
Use `reduce` with an accumulator object; create the group array if missing, then push the item.
हिंदी: reduce में object बनाओ, हर item को उसकी key वाले group (array) में डालते जाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: accept a key name or a function
// Step 2: reduce into an accumulator object
// Step 3: create group if missing and push item

function groupBy(arr, keyOrFn) {
  const getKey = typeof keyOrFn === 'function' ? keyOrFn : (item) => item[keyOrFn]; // resolve key getter
  return arr.reduce((acc, item) => {
    const k = getKey(item);          // group name for this item
    if (!acc[k]) acc[k] = [];        // create group on first use
    acc[k].push(item);               // add item to its group
    return acc;                      // pass accumulator on
  }, {});
}

// ============================================
// TEST CASES
// ============================================

const people = [
  { name: 'Ann', city: 'Delhi' },
  { name: 'Bob', city: 'Pune' },
  { name: 'Cat', city: 'Delhi' },
];
console.log(groupBy(people, 'city'));
// Expected: { Delhi: [ { name: 'Ann', city: 'Delhi' }, { name: 'Cat', city: 'Delhi' } ], Pune: [ { name: 'Bob', city: 'Pune' } ] }
console.log(groupBy([1.2, 1.8, 2.1], Math.floor));
// Expected: { '1': [ 1.2, 1.8 ], '2': [ 2.1 ] }
console.log(groupBy([], 'x'));
// Expected: {}
```

---

## 🔍 Why This Works (3 lines max)
The accumulator object maps each key to an array, built in one pass (O(n)). Accepting a function makes it work for computed groups too.
हिंदी: एक ही loop में हर item अपनी key वाले array में चला जाता है।

---

## ⚡ Alternative Solution
```javascript
// Modern built-in (Node 21+): Object.groupBy
if (Object.groupBy) {
  console.log(Object.groupBy([1, 2, 3, 4], (n) => (n % 2 ? 'odd' : 'even')));
  // Expected: [Object: null prototype] { odd: [ 1, 3 ], even: [ 2, 4 ] }
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting to initialize the group -> push on undefined
// acc[k].push(item); // TypeError: Cannot read properties of undefined
// ✅ Correct: acc[k] ??= []
const acc = {};
(acc['a'] ??= []).push(1);
console.log(acc); // { a: [ 1 ] }
```

---

## 🎯 Interview Tip (1 line)
Say you build a lookup object in one O(n) pass, and mention `Object.groupBy` exists in newer runtimes.

---

## 🔗 Related Questions
→ Q065 (sort objects) | Q066 (count occurrences) | Q079 (count key occurrences)
