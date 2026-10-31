---

# Q175. Explain Tagged Templates
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What are tagged template literals? Show how a tag function receives strings and values, and build practical examples (highlight, safe HTML, simple SQL).

---

## 💡 Quick Concept (2 lines only)
A tag is a function placed before a template literal: `` tag`a ${x} b` `` calls `tag(['a ', ' b'], x)`. It receives the static strings array and the interpolated values separately.
हिंदी: Tagged template में function को text के हिस्से और ${} की values अलग-अलग मिलती हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Define tag(strings, ...values)
// Step 2: strings.length is always values.length + 1
// Step 3: Rebuild or transform the final string

function show(strings, ...values) {            // basic tag function
  console.log(strings);                        // array of static parts
  console.log(values);                         // array of interpolated values
  return 'done';                               // tag can return anything
}
const name = 'Aditya', age = 25;               // sample values
console.log(show`Hi ${name}, age ${age}!`);    // call as tag

// Use case 1: highlight values
function highlight(strings, ...values) {
  return strings.reduce((out, str, i) =>       // join strings and values
    out + str + (i < values.length ? `<b>${values[i]}</b>` : ''), ''); // wrap value
}
console.log(highlight`Hello ${name}, you are ${age}`);

// Use case 2: escape HTML (prevent XSS)
const esc = s => String(s).replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); // map chars
function safeHtml(strings, ...values) {
  return strings.reduce((out, str, i) =>
    out + str + (i < values.length ? esc(values[i]) : ''), ''); // escape only values
}
const evil = '<script>alert(1)</script>';      // malicious input
console.log(safeHtml`<p>${evil}</p>`);         // safe output

// Use case 3: parameterised query (like SQL libs)
function sql(strings, ...values) {
  return { text: strings.join('?'), values };  // placeholders + values
}
console.log(sql`SELECT * FROM users WHERE id = ${7} AND role = ${'admin'}`);

// Raw strings
console.log(String.raw`C:\new\table`);        // backslashes kept

// ============================================
// TEST CASES
// ============================================
// Expected output:
// [ 'Hi ', ', age ', '!' ]
// [ 'Aditya', 25 ]
// done
// Hello <b>Aditya</b>, you are <b>25</b>
// <p>&lt;script&gt;alert(1)&lt;/script&gt;</p>
// { text: 'SELECT * FROM users WHERE id = ? AND role = ?', values: [ 7, 'admin' ] }
// C:\new\table
```

---

## 🔍 Why This Works (3 lines max)
The engine splits the template at each `${}` and passes pieces to the tag, so the tag controls how values are inserted. This enables escaping, localisation and safe query building.
हिंदी: Engine template को ${} पर तोड़कर tag को देता है, इसलिए tag तय करता है values कैसे जुड़ेंगी।

---

## ⚡ Alternative Solution
```javascript
// Without a tag: plain interpolation (no control over values)
const plain = `Hi ${'Aditya'}`;               // simple join
console.log(plain);                            // Expected: Hi Aditya
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Calling tag like a normal function and expecting interpolation
function t(strings, ...v) { return strings.length; }
console.log(t('a', 'b'));   // 1 -> strings is the string 'a', not an array

// ✅ Use tag syntax (no parentheses)
console.log(t`a${1}b`);     // 2
```

---

## 🎯 Interview Tip (1 line)
Say: "Tagged templates pass strings and values separately — used in styled-components, GraphQL gql and safe SQL/HTML builders."

---

## 🔗 Related Questions
→ Q245 (template literals advanced) | Q242 (spread) | Q243 (rest) | Q190 (template engine)
