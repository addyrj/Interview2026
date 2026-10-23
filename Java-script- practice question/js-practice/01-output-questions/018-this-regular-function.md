---

# Q018. `this` in Regular Function Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
const obj = {
  name: 'Arjun',
  greet: function() {
    console.log(this.name);
  }
};

obj.greet();

const fn = obj.greet;
fn();
```

---

## 💡 Quick Concept (2 lines only)
In regular functions, `this` is determined by HOW the function is called (call-site), not where it's defined. Method call: `this` = object. Bare function call: `this` = `undefined` (strict) or `window` (non-strict).
हिंदी: Regular function में `this` call-site से decide होता है — object से call → `this` = object; bare call → `undefined`/`window`।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const obj = {
  name: 'Arjun',
  greet: function() {
    console.log(this.name);
  }
};

obj.greet();   // this = obj (method call — object before the dot)
               // Output: 'Arjun'

const fn = obj.greet;  // Just copying the function reference
fn();          // this = undefined (strict mode) or window (non-strict)
               // In browser non-strict: this.name = window.name = ''
               // In Node.js / strict: TypeError: Cannot read 'name' of undefined

// ============================================
// OUTPUT:
// ============================================

// obj.greet() → 'Arjun'
// fn()        → '' (browser) or TypeError (strict/Node)
```

---

## 🔍 Why This Works (3 lines max)
`this` in regular functions is the object that CALLS the function. `obj.greet()` — `obj` is calling, so `this = obj`. `fn()` — no object calling, so `this = global/undefined`.
हिंदी: `obj.greet()` में `obj` call कर रहा है → `this = obj`; `fn()` में कोई object नहीं → `this = undefined`।

---

## ⚡ Alternative Solution
```javascript
// Fix using bind:
const bound = obj.greet.bind(obj);  // permanently bind this = obj
bound();  // Output: 'Arjun' ✅

// Fix using arrow function (captures this from surrounding scope):
const obj2 = {
  name: 'Priya',
  greet: () => {
    console.log(this.name);  // Arrow: this = outer scope (not obj2!)
  }
};
obj2.greet();  // undefined — arrow doesn't have own 'this'

// Fix using call/apply at call time:
fn.call(obj);    // Output: 'Arjun' ✅
fn.apply(obj);   // Output: 'Arjun' ✅
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: thinking this = obj when function is detached
const greet = obj.greet;
greet();  // NOT 'Arjun' — this is undefined/window, not obj

// ❌ Wrong: using arrow function as method when you need 'this'
const obj = {
  name: 'Arjun',
  greet: () => console.log(this.name)  // Arrow! this = outer scope
};
obj.greet();  // undefined — arrow doesn't bind to the calling object
```

---

## 🎯 Interview Tip (1 line)
Say: "Regular function's `this` = the object that calls it at runtime; arrow function's `this` = lexical (the surrounding scope where it was defined)."

---

## 🔗 Related Questions
→ Q019 (this in arrow function) | Q020 (this in class) | Q023 (call/apply/bind) | Q165 (this — 5 scenarios)
