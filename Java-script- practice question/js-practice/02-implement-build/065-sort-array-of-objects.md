---

# Q065. Sort Array of Objects
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `sortBy(arr, key, order)` that sorts an array of objects by a property, ascending or descending, WITHOUT mutating the original. Support both numbers and strings.

```javascript
sortBy([{ age: 30 }, { age: 20 }], 'age'); // [{ age: 20 }, { age: 30 }]
```

---

## 💡 Quick Concept (2 lines only)
Copy the array and use `sort` with a comparator that returns negative, zero or positive.
हिंदी: array की copy बनाओ और comparator function से sort करो, original को मत बदलो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: copy array so original is safe
// Step 2: compare values of the key (works for numbers + strings)
// Step 3: flip sign for descending

function sortBy(arr, key, order = 'asc') {
  const dir = order === 'desc' ? -1 : 1;     // direction multiplier
  return [...arr].sort((a, b) => {           // sort a copy
    if (a[key] < b[key]) return -1 * dir;    // a comes first
    if (a[key] > b[key]) return 1 * dir;     // b comes first
    return 0;                                // equal -> keep order (stable)
  });
}

// ============================================
// TEST CASES
// ============================================

const users = [
  { name: 'Cara', age: 30 },
  { name: 'Ann', age: 25 },
  { name: 'Bob', age: 35 },
];
console.log(sortBy(users, 'age').map((u) => u.name));          // Expected: [ 'Ann', 'Cara', 'Bob' ]
console.log(sortBy(users, 'age', 'desc').map((u) => u.name));  // Expected: [ 'Bob', 'Cara', 'Ann' ]
console.log(sortBy(users, 'name').map((u) => u.name));         // Expected: [ 'Ann', 'Bob', 'Cara' ]
console.log(users[0].name);                                    // Expected: Cara (original unchanged)
```

---

## 🔍 Why This Works (3 lines max)
The comparator returns -1/0/1 so `sort` knows the order, and `<`/`>` work for both numbers and strings. Spreading first keeps the original array untouched.
हिंदी: comparator -1/0/1 लौटाता है और copy पर sort होने से original सुरक्षित रहता है।

---

## ⚡ Alternative Solution
```javascript
// Numbers only: subtraction
const byAge = [...users].sort((a, b) => a.age - b.age); // ascending numeric sort
console.log(byAge.map((u) => u.age)); // Expected: [ 25, 30, 35 ]
// Strings with locale awareness
console.log([...users].sort((a, b) => a.name.localeCompare(b.name)).map((u) => u.name)); // Expected: [ 'Ann', 'Bob', 'Cara' ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: default sort() compares as strings and mutates
console.log([10, 9, 100].sort()); // [ 10, 100, 9 ]
// ✅ Correct: numeric comparator
console.log([10, 9, 100].sort((a, b) => a - b)); // [ 9, 10, 100 ]
```

---

## 🎯 Interview Tip (1 line)
Mention `sort` mutates in place, the comparator contract, and that modern `sort` is stable.

---

## 🔗 Related Questions
→ Q064 (group by) | Q056 (find max) | Q105 (quick sort)
