---

# Q116. Implement Array.find
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `Array.prototype.myFind(callback, thisArg)` that returns the FIRST element for which `callback(item, index, array)` is truthy, otherwise `undefined`.

```javascript
[5, 12, 8].myFind(x => x > 10); // 12
```

---

## 💡 Quick Concept (2 lines only)
Loop in order and return immediately on the first match — no need to check the remaining items.
हिंदी: पहला match मिलते ही तुरंत return कर दो, बाकी items देखने की ज़रूरत नहीं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: validate callback
// Step 2: loop from the start
// Step 3: return first item that passes, else undefined

Array.prototype.myFind = function (callback, thisArg) {
  if (typeof callback !== 'function') {
    throw new TypeError(`${callback} is not a function`); // same as native
  }
  for (let i = 0; i < this.length; i++) {        // find visits holes too (as undefined)
    if (callback.call(thisArg, this[i], i, this)) { // truthy -> found
      return this[i];                            // return the item (not index)
    }
  }
  return undefined;                              // nothing matched
};

// ============================================
// TEST CASES
// ============================================

console.log([5, 12, 8].myFind(x => x > 10));                 // Expected: 12
console.log([5, 12, 8].myFind(x => x > 100));                // Expected: undefined
console.log([1, 2, 3].myFind((x, i) => i === 1));            // Expected: 2

const users = [{ id: 1, n: 'A' }, { id: 2, n: 'B' }];
console.log(users.myFind(u => u.id === 2));                  // Expected: { id: 2, n: 'B' }
console.log([0, 1].myFind(x => x === 0));                    // Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
An early `return` exits the loop at the first match, so it is faster than `filter()[0]`. The function returns the element itself, unlike `findIndex`.
हिंदी: Early return से पहला match मिलते ही loop रुक जाता है, इसलिए यह `filter()[0]` से तेज़ है।

---

## ⚡ Alternative Solution
```javascript
// Using for...of
Array.prototype.myFind2 = function (cb, thisArg) {
  let i = 0;
  for (const item of this) {                   // iterate values
    if (cb.call(thisArg, item, i++, this)) return item; // return first truthy match
  }
};
console.log([3, 4, 5].myFind2(x => x % 2 === 0)); // Expected: 4
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: returning the callback result / using forEach (cannot stop)
this.forEach(x => { if (cb(x)) return x; }); // return only exits the inner arrow

// ✅ Correct: a real loop with return
for (let i = 0; i < this.length; i++) if (cb(this[i])) return this[i];
```

---

## 🎯 Interview Tip (1 line)
Distinguish: find -> element, findIndex -> index (-1 if none), some -> boolean.

---

## 🔗 Related Questions
→ Q113 (filter) | Q112 (map) | Q103 (binary search)
