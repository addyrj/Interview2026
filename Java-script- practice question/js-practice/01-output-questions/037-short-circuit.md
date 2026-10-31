---

# Q037. Short Circuit Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
console.log(0 || 'a');
console.log(1 && 'b');
console.log(null && console.log('never'));
console.log('' || null || 0);
```

---

## 💡 Quick Concept (2 lines only)
`||` returns the first truthy operand (or the last one); `&&` returns the first falsy operand (or the last one). Remaining operands are not evaluated.
हिंदी: || पहला truthy value लौटाता है और && पहला falsy; बाकी हिस्सा चलता ही नहीं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: 0 is falsy, so || moves on and returns 'a'
// Step 2: 1 is truthy, so && moves on and returns 'b'
// Step 3: null is falsy, && stops and returns null (console.log never runs)
// Step 4: all falsy for ||, so the LAST value 0 is returned

console.log(0 || 'a');                    // 'a'
console.log(1 && 'b');                    // 'b'
console.log(null && console.log('never')); // null (right side skipped)
console.log('' || null || 0);             // 0 (last operand)

// ============================================
// TEST CASES
// ============================================

const name = '';                          // empty name
console.log(name || 'Guest');             // Expected: Guest
const user = { profile: { age: 20 } };    // sample object
console.log(user && user.profile && user.profile.age); // Expected: 20
console.log(true || console.log('skip')); // Expected: true

// ============================================
// OUTPUT:
// ============================================
// a
// b
// null
// 0
// Guest
// 20
// true
```

---

## 🔍 Why This Works (3 lines max)
Logical operators return an operand, not a boolean, and stop evaluating once the result is decided. This enables default values (`||`) and guard checks (`&&`).
हिंदी: Logical operators boolean नहीं, असली operand लौटाते हैं और नतीजा तय होते ही रुक जाते हैं।

---

## ⚡ Alternative Solution
```javascript
// Replace short-circuit guards with modern syntax
const user = { profile: { age: 20 } };   // sample data
console.log(user?.profile?.age ?? 18);   // 20 (optional chaining + nullish)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: || treats 0 as missing
const count = 0;
console.log(count || 10);   // 10 (wrong, 0 was valid)

// ✅ Correct: use ?? to only skip null/undefined
console.log(count ?? 10);   // 0
```

---

## 🎯 Interview Tip (1 line)
Say: "|| and && return operand values and short-circuit; for defaults where 0 or '' are valid I use ??."

---

## 🔗 Related Questions
→ Q036 (truthy/falsy) | Q038 (nullish coalescing) | Q039 (optional chaining)
