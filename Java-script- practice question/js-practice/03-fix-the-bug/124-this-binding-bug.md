---

# Q124. Fix this Binding Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Calling the extracted method throws an error because `this` is lost. Make it print `Hi, Aman`.

```javascript
// BUGGY CODE:
class Greeter {
  constructor(name) { this.name = name; }
  greet() { return 'Hi, ' + this.name; }
}

const g = new Greeter('Aman');
const fn = g.greet;   // method detached from object
console.log(fn());    // TypeError: this is undefined
```

---

## 💡 Quick Concept (2 lines only)
`this` depends on HOW a function is called, not where it is defined. Detached methods lose their object — fix with `bind` or an arrow function.
हिंदी: method को object से अलग करने पर `this` खो जाता है — `bind` या arrow function से fix करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class Greeter {
  constructor(name) {
    this.name = name;                          // Step 1: store name
    this.greet = this.greet.bind(this);        // Step 2 (FIX): permanently bind this
  }
  greet() { return 'Hi, ' + this.name; }       // normal method
}

class Greeter2 {
  constructor(name) { this.name = name; }
  greet = () => 'Hi, ' + this.name;            // Step 3 (FIX alt): arrow class field keeps this
}

// ============================================
// TEST CASES
// ============================================

const fn = new Greeter('Aman').greet;          // detached method
console.log(fn());                             // Expected: Hi, Aman
const fn2 = new Greeter2('Riya').greet;        // detached arrow field
console.log(fn2());                            // Expected: Hi, Riya
console.log([1].map(new Greeter('Sam').greet)); // Expected: [ 'Hi, Sam' ]
```

---

## 🔍 Why This Works (3 lines max)
`bind` returns a new function with `this` fixed to the instance. Arrow functions capture `this` lexically from the constructor, so it never changes.
हिंदी: bind या arrow function `this` को instance से हमेशा के लिए जोड़ देते हैं।

---

## ⚡ Alternative Solution
```javascript
// Bind at call site
const g = new Greeter('Aman');
setTimeout(g.greet.bind(g), 0);        // bind when passing
setTimeout(() => g.greet(), 0);        // or wrap in arrow
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: passing method as callback directly
// button.addEventListener('click', obj.method);   // this = button, not obj
// ✅ Correct
// button.addEventListener('click', () => obj.method());
```

---

## 🎯 Interview Tip (1 line)
Say: "this is decided at call time; fix with bind, arrow wrapper, or arrow class field — and mention React class handlers."

---

## 🔗 Related Questions
→ Q018 (this regular function) | Q020 (this in class) | Q023 (call/apply/bind) | Q166 (call/apply/bind explained)
