---

# Q234. Form Validation
# Category: DOM Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Validate a signup form (name, email, password min 8 chars) on submit. Show an error under each invalid field and block submission until all are valid.

---

## 💡 Quick Concept (2 lines only)
Intercept `submit`, run rule functions per field, show messages, and call `preventDefault()` if any error exists.
हिंदी: `submit` रोककर हर field के rules चलाओ, error दिखाओ, और गलती हो तो submit block करो।

---

## ✅ Answer / Solution

```html
<form id="signup" novalidate>
  <input name="name" placeholder="Name"><small data-error="name"></small><br>
  <input name="email" placeholder="Email"><small data-error="email"></small><br>
  <input name="password" type="password" placeholder="Password"><small data-error="password"></small><br>
  <button type="submit">Sign up</button>
</form>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Define rules per field (return error string or '')
// Step 2: validateField shows/clears message
// Step 3: On submit validate all, stop if invalid

const form = document.getElementById('signup');          // form element

const rules = {
  name: (v) => (v.trim().length >= 2 ? '' : 'Name must be at least 2 characters'), // name rule
  email: (v) => (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? '' : 'Enter a valid email'), // email regex
  password: (v) => (v.length >= 8 ? '' : 'Password must be 8+ characters'), // password rule
};

function validateField(name) {
  const input = form.elements[name];                     // field element
  const msg = rules[name](input.value);                  // run rule
  form.querySelector(`[data-error="${name}"]`).textContent = msg; // show or clear message
  input.setAttribute('aria-invalid', msg ? 'true' : 'false');     // accessibility
  return !msg;                                           // true if valid
}

form.addEventListener('submit', (e) => {                 // on submit
  const results = Object.keys(rules).map(validateField); // validate ALL fields (no short-circuit)
  const valid = results.every(Boolean);                  // all must pass
  if (!valid) {
    e.preventDefault();                                  // block submission
    return;                                              // stop
  }
  e.preventDefault();                                    // demo: avoid real navigation
  console.log('Submitted', Object.fromEntries(new FormData(form))); // collect data
});

form.addEventListener('blur', (e) => {                   // live feedback on leaving field
  if (rules[e.target.name]) validateField(e.target.name);
}, true);                                                // capture: blur does not bubble

// ============================================
// TEST CASES
// ============================================

// Test 1: submit empty form -> Expected: 3 error messages shown, no "Submitted" log
// Test 2: name "Al", email "a@b.co", password "12345678" -> Expected: log Submitted {name:"Al",email:"a@b.co",password:"12345678"}
// Test 3: email "abc" -> Expected: "Enter a valid email"
// Test 4: rules.password('1234567') // Expected: "Password must be 8+ characters"
```

---

## 🔍 Why This Works (3 lines max)
Each rule is a small pure function, so validation is easy to test and extend. `map` runs all validators so every error shows at once. `preventDefault` blocks submission when invalid.
हिंदी: हर rule छोटा function है, `map` से सारे errors एक साथ दिखते हैं, और invalid पर submit रुक जाता है।

---

## ⚡ Alternative Solution
```javascript
// Built-in Constraint Validation API (with required, minlength, type=email in HTML)
if (!form.checkValidity()) {                             // browser checks attributes
  form.reportValidity();                                 // show native messages
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: short-circuit stops at first invalid field
const valid = validateField('name') && validateField('email') && validateField('password');

// ✅ Correct: run all validators first, then combine (map + every)
```

---

## 🎯 Interview Tip (1 line)
Say: "Client validation is only UX; always re-validate on server. Mention accessibility (aria-invalid) and the Constraint Validation API."

---

## 🔗 Related Questions
→ Q193 (form validator) | Q232 (debounce input) | Q235 (file upload)
