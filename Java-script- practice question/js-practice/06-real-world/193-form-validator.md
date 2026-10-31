---

# Q193. Build Form Validator
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build `validate(values, schema)` where schema maps each field to an array of rules (`required`, `minLength`, `email`, `matches`). Return an `errors` object (first error per field) and an `isValid` flag.

```javascript
validate({ email: 'x' }, { email: [required(), email()] });
// { isValid: false, errors: { email: 'Invalid email' } }
```

---

## 💡 Quick Concept (2 lines only)
Each rule is a function `(value, all) => errorMessage | null`; run rules in order and stop at the first failure per field.
हिंदी: हर rule एक छोटा function है जो error message या null देता है — field का पहला error दिखाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: rule factories -> each returns (value, all) => message | null
const required = (msg = 'Required') => (v) => (v === undefined || v === null || String(v).trim() === '' ? msg : null);
const minLength = (n, msg) => (v) => (String(v ?? '').length < n ? msg || `Min ${n} characters` : null);
const email = (msg = 'Invalid email') => (v) => (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v || '') ? null : msg);
const matches = (field, msg = 'Does not match') => (v, all) => (v === all[field] ? null : msg);

function validate(values, schema) {
  const errors = {};                             // Step 2: collect errors per field
  for (const field of Object.keys(schema)) {     // loop over fields in schema
    for (const rule of schema[field]) {          // Step 3: run rules in order
      const message = rule(values[field], values); // pass whole form for cross-field rules
      if (message) { errors[field] = message; break; } // keep first error only
    }
  }
  return { isValid: Object.keys(errors).length === 0, errors }; // Step 4: summary
}

// ============================================
// TEST CASES
// ============================================

const schema = {
  email: [required(), email()],
  password: [required(), minLength(6)],
  confirm: [matches('password', 'Passwords differ')],
};

console.log(validate({ email: '', password: '123', confirm: '1' }, schema));
// Expected: { isValid: false, errors: { email: 'Required', password: 'Min 6 characters', confirm: 'Passwords differ' } }

console.log(validate({ email: 'a@b.com', password: 'secret1', confirm: 'secret1' }, schema));
// Expected: { isValid: true, errors: {} }
```

---

## 🔍 Why This Works (3 lines max)
Rules are small pure functions, so they are reusable and easy to test. Passing the whole `values` object enables cross-field checks like "confirm password".
हिंदी: Rules छोटे pure functions हैं, इसलिए reuse आसान है और पूरा form पास करने से confirm-password जैसी checks भी हो जाती हैं।

---

## ⚡ Alternative Solution
```javascript
// Async rule support (e.g. "username already taken?")
async function validateAsync(values, schema) {
  const errors = {};
  for (const [field, rules] of Object.entries(schema)) {
    for (const rule of rules) {
      const msg = await rule(values[field], values); // await works for sync + async rules
      if (msg) { errors[field] = msg; break; }
    }
  }
  return { isValid: !Object.keys(errors).length, errors };
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: one giant if/else block, no reuse, only checks client side
if (!email || !email.includes('@') || pwd.length < 6) alert('error');

// ✅ Correct: composable rules + ALWAYS re-validate on the server too
```

---

## 🎯 Interview Tip (1 line)
Say "client validation is UX, server validation is security" and mention schema libs (Zod/Yup).

---

## 🔗 Related Questions
→ Q077 (check if object empty) | Q234 (form validation) | Q084 (curry) | Q194 (data fetcher)
