---

# Q165. Explain this with 5 Examples
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain how `this` is determined in JavaScript using 5 different examples: method call, plain function, arrow function, constructor and explicit binding.

---

## 💡 Quick Concept (2 lines only)
`this` is decided by HOW a function is called, not where it is written (except arrow functions, which use the surrounding `this`).
हिंदी: `this` इस पर निर्भर है कि function कैसे call हुआ — arrow function अपने आसपास का this लेता है।

---

## ✅ Answer / Solution

```javascript
'use strict';                               // strict mode: plain call gives undefined this

// ============================================
// SOLUTION
// ============================================

// Step 1: obj.method() -> this = obj
// Step 2: plain fn() -> this = undefined (strict)
// Step 3: arrow -> lexical this; new -> new object; call/bind -> chosen object

// EXAMPLE 1: method call
const user = {
  name: 'Aditya',                           // data on object
  hello() { return this.name; }             // this = object before the dot
};
console.log(user.hello());                  // Expected: Aditya

// EXAMPLE 2: detached method loses this
const lost = user.hello;                    // copy reference only
try {
  lost();                                   // plain call -> this undefined
} catch (e) {
  console.log(e.name);                      // Expected: TypeError
}

// EXAMPLE 3: arrow function uses outer this
const timer = {
  name: 'Timer',                            // data
  run() {
    return [1].map(() => this.name);        // arrow keeps run's this
  }
};
console.log(timer.run());                   // Expected: [ 'Timer' ]

// EXAMPLE 4: constructor with new
function Car(model) {
  this.model = model;                       // this = brand new object
}
console.log(new Car('Tesla').model);        // Expected: Tesla

// EXAMPLE 5: explicit binding
function show() { return this.name; }       // depends on caller
console.log(show.call({ name: 'Call' }));   // Expected: Call
console.log(show.bind({ name: 'Bind' })()); // Expected: Bind

// ============================================
// TEST CASES
// ============================================
// Expected output order:
// Aditya
// TypeError
// [ 'Timer' ]
// Tesla
// Call
// Bind
```

---

## 🔍 Why This Works (3 lines max)
Priority: `new` > `call/apply/bind` > method call (`obj.fn()`) > plain call (undefined/global). Arrow functions ignore all of these and capture `this` from where they are defined.
हिंदी: Priority: new > bind/call > obj.method > plain call; arrow इन सबको ignore करता है।

---

## ⚡ Alternative Solution
```javascript
// Fix lost this by binding or wrapping in arrow
const u = { name: 'Fix', hi() { return this.name; } };
const bound = u.hi.bind(u);                 // permanently bind this
const wrapped = () => u.hi();               // call through object
console.log(bound(), wrapped());            // Expected: Fix Fix
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Arrow function as object method
const o = { name: 'X', get: () => typeof this };
console.log(o.get()); // not the object (module-level this)

// ✅ Use method shorthand for object methods, arrow for callbacks
const p = { name: 'X', get() { return this.name; } };
console.log(p.get()); // X
```

---

## 🎯 Interview Tip (1 line)
Say: "Look at the call site: new, explicit bind, dot call, else default — arrows are lexical."

---

## 🔗 Related Questions
→ Q018 (this regular fn) | Q019 (this arrow) | Q124 (this binding bug) | Q302 (this 5 scenarios)
