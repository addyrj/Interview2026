---

# Q245. Template Literals — Advanced
# Category: ES6+ Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show advanced template literal features: expressions, nesting, multi-line, tagged templates and `String.raw`.

---

## 💡 Quick Concept (2 lines only)
Backtick strings allow `${expr}` interpolation, multi-line text, and a "tag" function that receives the string parts and values.
हिंदी: Backtick string में `${}` से expression चलता है और tag function से string को custom process कर सकते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Expressions and nesting
// Step 2: Multi-line + String.raw
// Step 3: Tagged template function

// 1. Any expression works inside ${}
const a = 2, b = 3;                              // numbers
console.log(`Sum: ${a + b}, Max: ${Math.max(a, b)}`); // Expected: Sum: 5, Max: 3

// 2. Nested templates (conditional rendering)
const items = ['x', 'y'];                        // list
const html = `<ul>${items.map(i => `<li>${i}</li>`).join('')}</ul>`; // template inside template
console.log(html);                               // Expected: <ul><li>x</li><li>y</li></ul>

// 3. Multi-line keeps newlines
const text = `line1
line2`;                                          // real newline preserved
console.log(text.split('\n').length);            // Expected: 2

// 4. String.raw ignores escape sequences
console.log(String.raw`a\nb`);                   // Expected: a\nb

// 5. Tagged template: highlight interpolated values
function hl(strings, ...vals) {                  // strings = static parts, vals = values
  return strings.reduce((out, s, i) => out + s + (i < vals.length ? `[${vals[i]}]` : ''), '');
}
const who = 'Ria', n = 3;                        // values
console.log(hl`Hi ${who}, you have ${n} msgs`);  // Expected: Hi [Ria], you have [3] msgs

// ============================================
// TEST CASES
// ============================================

console.log(`${null} ${undefined} ${[1, 2]} ${{}}`); // Expected: null undefined 1,2 [object Object]
console.log(`${'a'}${'b'}` === 'ab');            // Expected: true
function count(strings) { return strings.length; } // tag returning parts count
console.log(count`a${1}b${2}c`);                 // Expected: 3
```

---

## 🔍 Why This Works (3 lines max)
`${}` converts the result to a string via `toString`. A tag function gets `(stringsArray, ...values)` and can return anything, not just a string.
हिंदी: Tag function को static parts और values अलग-अलग मिलते हैं, return कुछ भी कर सकते हैं।

---

## ⚡ Alternative Solution
```javascript
// Old way: string concatenation
const name = 'Ria';                              // value
console.log('Hello ' + name + '!');              // Expected: Hello Ria!
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: single quotes do not interpolate
const v = 5;                                     // value
console.log('Value: ${v}');                      // prints literally: Value: ${v}

// ✅ Correct: use backticks
console.log(`Value: ${v}`);                      // Expected: Value: 5
```

---

## 🎯 Interview Tip (1 line)
Mention tagged templates power styled-components, GraphQL `gql` and safe HTML/SQL escaping.

---

## 🔗 Related Questions
→ Q175 (tagged templates) | Q031 (string + number) | Q190 (template engine)
