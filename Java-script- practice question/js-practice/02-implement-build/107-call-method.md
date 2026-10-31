---

# Q107. Implement Call Method
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `Function.prototype.myCall(context, ...args)` that behaves like `call`: runs the function with `this` set to `context`.

```javascript
function greet(g) { return `${g}, ${this.name}`; }
greet.myCall({ name: 'Aditya' }, 'Hi'); // "Hi, Aditya"
```

---

## 💡 Quick Concept (2 lines only)
Temporarily attach the function as a method on the context object, call it (so `this` = object), then remove it.
हिंदी: Function को object की property बनाकर call करो, तब `this` वही object बन जाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: handle null/undefined context -> globalThis
// Step 2: attach function under a unique Symbol key
// Step 3: call it as a method, delete key, return result

Function.prototype.myCall = function (context, ...args) {
  context = context == null ? globalThis : Object(context); // wrap primitives, default to global
  const key = Symbol('fn');          // unique key so we never overwrite a real property
  context[key] = this;               // `this` here is the function being called
  const result = context[key](...args); // call as method -> this = context
  delete context[key];               // clean up the temporary property
  return result;                     // return function's result
};

// ============================================
// TEST CASES
// ============================================

function greet(greeting, punct) {
  return `${greeting}, ${this.name}${punct}`;     // uses this.name
}

console.log(greet.myCall({ name: 'Aditya' }, 'Hi', '!'));   // Expected: Hi, Aditya!
console.log(greet.call({ name: 'Aditya' }, 'Hi', '!'));     // Expected: Hi, Aditya!

function sum(a, b) { return a + b; }
console.log(sum.myCall(null, 2, 3));                        // Expected: 5

function type() { return typeof this; }
console.log(type.myCall(5));                                // Expected: object
```

---

## 🔍 Why This Works (3 lines max)
When a function is called as `obj.fn()`, `this` is `obj`. We fake that by temporarily placing the function on the context. A Symbol key prevents name clashes.
हिंदी: `obj.fn()` में this हमेशा obj होता है, हम वही चाल चलते हैं।

---

## ⚡ Alternative Solution
```javascript
// Using Reflect.apply (no temporary property, but needs a real this)
Function.prototype.myCall2 = function (context, ...args) {
  return Reflect.apply(this, context, args); // directly sets this and args
};
console.log(Math.max.myCall2(null, 1, 9, 3)); // Expected: 9
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: fixed key name can overwrite a real property + leaves junk behind
context.fn = this;
context.fn(...args);

// ✅ Correct: Symbol key + delete after use
const key = Symbol();
context[key] = this;
```

---

## 🎯 Interview Tip (1 line)
Mention the 3 edge cases: null context -> global, primitive context -> wrapped, and unique key cleanup.

---

## 🔗 Related Questions
→ Q108 (apply) | Q109 (bind) | Q023 (call/apply/bind output) | Q166 (explain call/apply/bind)
