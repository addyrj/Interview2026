---

# Q049. delete Operator Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
const obj = { a: 1, b: 2 };
console.log(delete obj.a, obj);
const arr = [1, 2, 3];
delete arr[1];
console.log(arr, arr.length);
var x = 10;
console.log(delete x, x);
```

---

## 💡 Quick Concept (2 lines only)
`delete` removes an own property of an object and returns true. On arrays it leaves a hole (length unchanged); declared variables cannot be deleted.
हिंदी: delete object की property हटाता है; array में सिर्फ खाली जगह (hole) बनती है और declared variable delete नहीं होता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: delete obj.a removes the key and returns true
// Step 2: delete arr[1] leaves an empty slot, length stays 3
// Step 3: variables declared with var/let/const are non-configurable -> false

const obj = { a: 1, b: 2 };            // sample object
console.log(delete obj.a, obj);        // true { b: 2 }
const arr = [1, 2, 3];                 // sample array
delete arr[1];                         // creates a hole
console.log(arr, arr.length);          // [ 1, <1 empty item>, 3 ] 3
var x = 10;                            // declared variable
console.log(delete x, x);              // false 10 (in a CommonJS module too)

// ============================================
// TEST CASES
// ============================================

console.log(delete obj.nothing);       // Expected: true (missing key is fine)
const frozen = Object.freeze({ k: 1 }); // frozen object
console.log(delete frozen.k);          // Expected: false (silent in sloppy mode)
console.log(frozen.k);                 // Expected: 1
const s = [1, 2, 3];                   // use splice for real removal
s.splice(1, 1);                        // remove index 1 properly
console.log(s);                        // Expected: [ 1, 3 ]

// ============================================
// OUTPUT:
// ============================================
// true { b: 2 }
// [ 1, <1 empty item>, 3 ] 3
// false 10
// true
// false
// 1
// [ 1, 3 ]
```

---

## 🔍 Why This Works (3 lines max)
`delete` only works on configurable own properties and does not reindex arrays. Failed deletes return false (or throw in strict mode). It does not free memory directly; it only removes the reference.
हिंदी: delete सिर्फ configurable property हटाता है, array की indexing नहीं बदलता और fail होने पर false देता है।

---

## ⚡ Alternative Solution
```javascript
// Immutable removal with rest destructuring
const user = { id: 1, password: 'x', name: 'A' };   // sample
const { password, ...safe } = user;                 // omit password
console.log(safe);                                  // { id: 1, name: 'A' }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using delete to remove array items
const a = [1, 2, 3];
delete a[0];
console.log(a.length);   // 3 (hole at index 0)

// ✅ Correct: use splice or filter
console.log(a.filter((v, i) => i !== 0)); // [ 2, 3 ]
```

---

## 🎯 Interview Tip (1 line)
Say: "delete removes object properties but leaves array holes; for arrays I use splice or filter, and for state I prefer immutable omission."

---

## 🔗 Related Questions
→ Q050 (in operator) | Q075 (omit keys) | Q137 (fix array mutation)
