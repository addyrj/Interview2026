---

# Q023. call / apply / bind Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
function intro(greet, punct) { return `${greet}, ${this.name}${punct}`; }
const u = { name: 'Ravi' };
console.log(intro.call(u, 'Hi', '!'));
console.log(intro.apply(u, ['Hello', '?']));
const b = intro.bind(u, 'Hey');
console.log(b('.'));
console.log(b.call({ name: 'Other' }, '!'));
```

---

## 💡 Quick Concept (2 lines only)
`call` and `apply` invoke immediately (args separate vs array); `bind` returns a new function with `this` permanently fixed.
हिंदी: call/apply तुरंत चलाते हैं (args अलग बनाम array); bind नया function देता है जिसका this हमेशा के लिए fix रहता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: call(u, a, b) -> runs now with this = u
// Step 2: apply(u, [a, b]) -> same, args as array
// Step 3: bind(u, a) -> new fn; this fixed, 'Hey' preset; later call can't change this

function intro(greet, punct) {
  return `${greet}, ${this.name}${punct}`;         // uses this.name
}
const u = { name: 'Ravi' };                        // target object

console.log(intro.call(u, 'Hi', '!'));             // args one by one
console.log(intro.apply(u, ['Hello', '?']));       // args as array
const b = intro.bind(u, 'Hey');                    // partial application + this
console.log(b('.'));                               // punct = '.'
console.log(b.call({ name: 'Other' }, '!'));       // this stays Ravi

// ============================================
// TEST CASES
// ============================================

// Output:
// Hi, Ravi!
// Hello, Ravi?
// Hey, Ravi.
// Hey, Ravi!
```

---

## 🔍 Why This Works (3 lines max)
A bound function ignores a new `this` from call/apply, but extra arguments are still passed after the preset ones. So the last line prints "Ravi", not "Other".
हिंदी: Bound function का this बदला नहीं जा सकता, इसलिए आखिरी line में "Other" नहीं, "Ravi" आता है।

---

## ⚡ Alternative Solution
```javascript
// Borrowing a method with apply/spread
console.log(Math.max.apply(null, [3, 9, 2]));      // Expected: 9
console.log(Math.max(...[3, 9, 2]));               // Expected: 9
```

---

## ⚠️ Common Mistake
```javascript
// ❌ const r = intro.bind(u, 'Hi', '!');  r();  -> works, but forgetting () returns a function
// ✅ bind does NOT call; call/apply do
console.log(typeof intro.bind(u));                 // Expected: function
```

---

## 🎯 Interview Tip (1 line)
Say: "call = comma args, apply = array args, bind = returns a new function with permanent this."

---

## 🔗 Related Questions
→ Q018 (this regular function) | Q109 (implement bind) | Q107 (implement call) | Q166 (explain call/apply/bind)
