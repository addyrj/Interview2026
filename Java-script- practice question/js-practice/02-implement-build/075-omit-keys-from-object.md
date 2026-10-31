---

# Q075. Omit Keys from Object
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `omit(obj, keys)` that returns a new object without the listed keys. The original object must not change.

```javascript
omit({ a: 1, b: 2, c: 3 }, ['b', 'c']); // { a: 1 }
```

---

## 💡 Quick Concept (2 lines only)
Loop over the object's entries and keep only the ones whose key is not in the omit list.
हिंदी: object की हर entry देखो और जिन keys को हटाना है उन्हें छोड़कर बाकी नए object में रखो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: put keys to omit in a Set
// Step 2: filter entries whose key is not in the Set
// Step 3: rebuild object with Object.fromEntries

function omit(obj, keys) {
  const skip = new Set(keys);                        // fast lookup of keys to remove
  return Object.fromEntries(
    Object.entries(obj).filter(([k]) => !skip.has(k)) // keep entries not in skip list
  );
}

// ============================================
// TEST CASES
// ============================================

const user = { id: 1, name: 'Ann', password: 'secret' };
console.log(omit(user, ['password']));        // Expected: { id: 1, name: 'Ann' }
console.log(omit(user, ['id', 'name']));      // Expected: { password: 'secret' }
console.log(omit(user, ['missing']));         // Expected: { id: 1, name: 'Ann', password: 'secret' }
console.log(user.password);                   // Expected: secret (original unchanged)
```

---

## 🔍 Why This Works (3 lines max)
`entries` → `filter` → `fromEntries` is a clean copy pipeline, so the original stays intact. Unknown keys are simply ignored.
हिंदी: entries से filter करके नया object बनता है, इसलिए original नहीं बदलता।

---

## ⚡ Alternative Solution
```javascript
// Destructuring + rest (for a known key)
const { password, ...safeUser } = user; // rest collects everything except password
console.log(safeUser); // Expected: { id: 1, name: 'Ann' }
// Copy then delete
const copy = { ...user };               // shallow copy
delete copy.id;                         // remove key from copy only
console.log(copy);                      // Expected: { name: 'Ann', password: 'secret' }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: delete on the original mutates it
const o = { a: 1, b: 2 };
delete o.b;
console.log(o); // { a: 1 } (original changed)
// ✅ Correct: build a new object
console.log(omit({ a: 1, b: 2 }, ['b'])); // { a: 1 }
```

---

## 🎯 Interview Tip (1 line)
Mention immutability (don't mutate props/state) and that rest destructuring is the quickest option for static keys.

---

## 🔗 Related Questions
→ Q076 (pick keys) | Q072 (merge objects) | Q077 (check empty object)
