---

# Q190. Build Template Engine
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build `render(template, data)` that replaces `{{ path }}` placeholders (supports nested paths like `user.name`), HTML-escapes values, and supports `{{{ raw }}}` for unescaped output. Missing values become empty string.

```javascript
render('Hi {{ user.name }}!', { user: { name: 'Adi' } }); // "Hi Adi!"
```

---

## 💡 Quick Concept (2 lines only)
Use `String.replace` with a regex callback; resolve the dotted path on `data`; escape `& < > " '`.
हिंदी: Regex से {{ }} ढूँढो, data से value निकालो और XSS से बचने के लिए escape करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const escapeHtml = (s) =>
  String(s).replace(/[&<>"']/g, (c) => ({     // Step 1: escape dangerous characters
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));

const getPath = (obj, path) =>
  path.split('.').reduce((o, k) => (o == null ? undefined : o[k]), obj); // Step 2: safe nested lookup

function render(template, data) {
  return template
    .replace(/\{\{\{\s*([\w.]+)\s*\}\}\}/g, (_, p) => { // Step 3: {{{ raw }}} first
      const v = getPath(data, p);                // lookup
      return v == null ? '' : String(v);         // no escaping
    })
    .replace(/\{\{\s*([\w.]+)\s*\}\}/g, (_, p) => { // Step 4: {{ escaped }}
      const v = getPath(data, p);                // lookup
      return v == null ? '' : escapeHtml(v);     // escape for safety
    });
}

// ============================================
// TEST CASES
// ============================================

const data = { user: { name: 'Adi', bio: '<b>dev</b>' }, count: 0 };
console.log(render('Hi {{ user.name }}!', data));        // Expected: Hi Adi!
console.log(render('Bio: {{ user.bio }}', data));        // Expected: Bio: &lt;b&gt;dev&lt;/b&gt;
console.log(render('Bio: {{{ user.bio }}}', data));      // Expected: Bio: <b>dev</b>
console.log(render('Count {{count}}, age [{{ user.age }}]', data)); // Expected: Count 0, age []
```

---

## 🔍 Why This Works (3 lines max)
`replace` with a callback runs once per placeholder, so the lookup logic stays tiny. Escaping by default prevents XSS; raw output is an explicit opt-in.
हिंदी: Default में escape होता है ताकि XSS न हो; raw चाहिए तो {{{ }}} इस्तेमाल करो।

---

## ⚡ Alternative Solution
```javascript
// ES6 tagged-template/function based "template"
const tpl = ({ name, count }) => `Hi ${name}, you have ${count} items`; // JS itself is the engine
console.log(tpl({ name: 'Adi', count: 3 }));     // Hi Adi, you have 3 items
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using eval / new Function on user templates -> code injection
new Function('data', 'with(data){ return `' + template + '`}')(data);

// ✅ Correct: only substitute values by path, escape output
```

---

## 🎯 Interview Tip (1 line)
Always mention XSS escaping and why `eval`/`with` are dangerous in template engines.

---

## 🔗 Related Questions
→ Q074 (get value by path) | Q175 (tagged templates) | Q245 (template literals advanced) | Q197 (URL parser)
