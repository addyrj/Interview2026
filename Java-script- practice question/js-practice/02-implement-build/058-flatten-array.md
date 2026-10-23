---

# Q058. Flatten Nested Array
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a `flatten(arr)` function that flattens a nested array one level deep. Also implement `flattenDeep(arr)` that flattens to any depth.

```javascript
flatten([1, [2, 3], [4, [5, 6]]]);
// Expected: [1, 2, 3, 4, [5, 6]]  — one level

flattenDeep([1, [2, [3, [4, [5]]]]]);
// Expected: [1, 2, 3, 4, 5]  — all levels
```

---

## 💡 Quick Concept (2 lines only)
Flatten removes one level of nesting. Deep flatten recursively removes ALL nesting. ES6 `Array.flat(depth)` does this natively — implement manually to show recursion understanding.
हिंदी: Flatten array की nesting हटाता है — `flat(1)` एक level, `flat(Infinity)` सब levels।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// 1 level flatten:
function flatten(arr) {
  return arr.reduce((acc, item) => {
    if (Array.isArray(item)) {
      return acc.concat(item);  // spread one level
    }
    return acc.concat(item);    // same as [...acc, item]
  }, []);
}
// Shorter: const flatten = arr => [].concat(...arr);

// Deep flatten (all levels — recursive):
function flattenDeep(arr) {
  return arr.reduce((acc, item) => {
    if (Array.isArray(item)) {
      return acc.concat(flattenDeep(item));  // recurse into nested arrays
    }
    return acc.concat(item);
  }, []);
}

// Flatten with depth control:
function flattenDepth(arr, depth = 1) {
  if (depth === 0) return arr;
  return arr.reduce((acc, item) => {
    if (Array.isArray(item)) {
      return acc.concat(flattenDepth(item, depth - 1));  // reduce depth
    }
    return acc.concat(item);
  }, []);
}

// ============================================
// TEST CASES
// ============================================

console.log(flatten([1, [2, 3], [4, [5, 6]]]));
// Expected: [1, 2, 3, 4, [5, 6]]

console.log(flattenDeep([1, [2, [3, [4, [5]]]]]));
// Expected: [1, 2, 3, 4, 5]

console.log(flattenDepth([1, [2, [3, [4]]]], 2));
// Expected: [1, 2, 3, [4]]  — 2 levels deep

// Native alternatives:
console.log([1, [2, 3], [4, [5, 6]]].flat());          // [1, 2, 3, 4, [5, 6]]
console.log([1, [2, [3, [4]]]].flat(Infinity));          // [1, 2, 3, 4]
console.log([1, [2, [3, [4]]]].flat(2));                 // [1, 2, 3, [4]]
```

---

## 🔍 Why This Works (3 lines max)
`reduce` accumulates each element — if it's an array, spread it in (one level). For deep flatten, recursively call on nested arrays until no more nesting. `Array.isArray()` is the check.
हिंदी: हर element check करो — array है तो spread करो; deep flatten में nested arrays पर recurse करो।

---

## ⚡ Alternative Solution
```javascript
// Using spread + concat (one-liner flatten):
const flatten = arr => [].concat(...arr);

// Recursive with stack (iterative, no recursion limit):
function flattenIterative(arr) {
  const stack = [...arr];
  const result = [];
  
  while (stack.length) {
    const item = stack.pop();
    if (Array.isArray(item)) {
      stack.push(...item);  // push children back to stack
    } else {
      result.unshift(item); // add to front (maintain order)
    }
  }
  
  return result;
}

// Using generator (lazy flatten):
function* flattenGen(arr) {
  for (const item of arr) {
    if (Array.isArray(item)) {
      yield* flattenGen(item);  // delegate to recursive call
    } else {
      yield item;
    }
  }
}

console.log([...flattenGen([1, [2, [3]]])]);  // [1, 2, 3]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: mutating the original array
function flatten(arr) {
  const result = arr;  // same reference!
  // ... mutations affect original
}

// ❌ Wrong: using toString() (loses type info)
[1, [2, [3]]].toString().split(',').map(Number)  // works for numbers only!
// [1, 2, 3] — but what about strings, objects, booleans?

// ✅ Correct: use reduce with concat, or flat(Infinity)
const flattened = arr.flat(Infinity);  // native, handles all types
```

---

## 🎯 Interview Tip (1 line)
Say: "In production use `arr.flat(Infinity)`; implement manually with reduce+recursion to show you understand the algorithm."

---

## 🔗 Related Questions
→ Q059 (deep flatten) | Q117 (implement Array.flat) | Q064 (group by property) | Q058-060 related
